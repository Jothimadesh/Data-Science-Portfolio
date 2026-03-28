# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from matplotlib import cm, colors as mcolors

st.set_page_config(page_title="Ecommerce Dashboard", layout="wide")

@st.cache_data
def load_and_prepare(orders_path='data/orders.csv', products_path='data/products.csv'):
    orders = pd.read_csv(orders_path, parse_dates=['order_date'])
    products = pd.read_csv(products_path)
    if 'product_name' not in orders.columns or 'category' not in orders.columns:
        if 'product_id' in orders.columns and 'product_id' in products.columns:
            orders = orders.merge(products[['product_id','product_name','category']], on='product_id', how='left')
    orders['product_name'] = orders.get('product_name').astype(str).fillna('Unknown Product')
    orders['category'] = orders.get('category').astype(str).fillna('Unknown Category')
    orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
    orders['order_month'] = orders['order_date'].dt.to_period('M').astype(str)
    orders['order_month_dt'] = pd.to_datetime(orders['order_month'] + '-01', errors='coerce')
    orders['quantity'] = orders['quantity'].fillna(1).astype(int)
    orders['unit_price'] = orders['unit_price'].fillna(0).astype(float)
    orders['revenue'] = orders['quantity'] * orders['unit_price']
    return orders, products

orders, products = load_and_prepare()

# Sidebar controls
st.sidebar.header("Filters")
min_date = orders['order_date'].min().date() if not orders['order_date'].isna().all() else None
max_date = orders['order_date'].max().date() if not orders['order_date'].isna().all() else None
date_range = st.sidebar.date_input("Date range", [min_date, max_date]) if min_date is not None else None
top_n = st.sidebar.slider("Top N products for Sankey", min_value=5, max_value=30, value=12, step=1)
show_segments = st.sidebar.checkbox("Segment customers by revenue", value=True)

# Apply date filter
if date_range:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = orders[(orders['order_date'] >= start) & (orders['order_date'] <= end)].copy()
else:
    filtered = orders.copy()

# KPI row (last 30 days vs previous 30 days)
with st.container():
    st.markdown("### Key metrics")
    end_dt = filtered['order_date'].max()
    start_dt = end_dt - pd.Timedelta(days=29) if pd.notna(end_dt) else filtered['order_date'].min()
    prev_start = start_dt - pd.Timedelta(days=30)
    prev_end = start_dt - pd.Timedelta(days=1)
    cur = filtered[(filtered['order_date'] >= start_dt) & (filtered['order_date'] <= end_dt)]
    prev = filtered[(filtered['order_date'] >= prev_start) & (filtered['order_date'] <= prev_end)]
    def pct_change(a,b): return (a-b)/b*100 if b else 0
    total_revenue = cur['revenue'].sum()
    prev_revenue = prev['revenue'].sum()
    total_orders = cur['order_id'].nunique()
    prev_orders = prev['order_id'].nunique()
    aov = total_revenue / total_orders if total_orders else 0
    prev_aov = prev_revenue / prev_orders if prev_orders else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue (last 30d)", f"₹{total_revenue:,.0f}", f"{pct_change(total_revenue, prev_revenue):+.1f}%")
    col2.metric("Total Orders (last 30d)", f"{total_orders}", f"{pct_change(total_orders, prev_orders):+.1f}%")
    col3.metric("Avg Order Value (last 30d)", f"₹{aov:,.0f}", f"{pct_change(aov, prev_aov):+.1f}%")

# Tabs for charts
tab1, tab2, tab3 = st.tabs(["Sankey Flow", "Composition & Trend", "Export & Data"])

#### Tab 1: Sankey Flow
with tab1:
    st.header("Revenue Flow: Category → Product → Customer Segment")
    df = filtered.copy()
    top_products = df.groupby('product_name', as_index=False)['revenue'].sum().nlargest(top_n, 'revenue')['product_name'].tolist()
    df = df[df['product_name'].isin(top_products)].copy()
    if show_segments:
        cust_rev = df.groupby('customer_id', as_index=False)['revenue'].sum()
        if cust_rev['revenue'].nunique() < 3:
            cust_rev['segment'] = pd.qcut(cust_rev['revenue'].rank(method='first'), q=2, labels=['Low','High'])
        else:
            cust_rev['segment'] = pd.qcut(cust_rev['revenue'], q=3, labels=['Low','Mid','High'])
        cust_rev['segment'] = cust_rev['segment'].astype(str).fillna('Unknown')
        df = df.merge(cust_rev[['customer_id','segment']], on='customer_id', how='left')
    else:
        df['segment'] = 'All Customers'

    cats = list(df['category'].unique())
    prods = list(df['product_name'].unique())
    segs = list(df['segment'].unique())
    nodes = list(dict.fromkeys(cats + prods + segs))
    node_index = {n:i for i,n in enumerate(nodes)}
    links = []
    cat_prod = df.groupby(['category','product_name'], observed=True, as_index=False)['revenue'].sum()
    for _, r in cat_prod.iterrows():
        s = node_index.get(r['category']); t = node_index.get(r['product_name'])
        if s is not None and t is not None and r['revenue']>0:
            links.append((s,t,r['revenue']))
    prod_seg = df.groupby(['product_name','segment'], observed=True, as_index=False)['revenue'].sum()
    for _, r in prod_seg.iterrows():
        s = node_index.get(r['product_name']); t = node_index.get(r['segment'])
        if s is not None and t is not None and r['revenue']>0:
            links.append((s,t,r['revenue']))

    if not links:
        st.info("Not enough data to build Sankey. Try widening the date range or increasing Top N.")
    else:
        source = [l[0] for l in links]; target = [l[1] for l in links]; value = [l[2] for l in links]
        palette = cm.get_cmap('tab20')
        node_colors = []
        for i, name in enumerate(nodes):
            if name in cats:
                color = mcolors.to_hex(palette(i % 20))
            elif name in prods:
                color = mcolors.to_hex(palette((i+5) % 20))
            else:
                color = mcolors.to_hex(palette((i+10) % 20))
            node_colors.append(color)
        fig = go.Figure(go.Sankey(
            arrangement='snap',
            node=dict(label=nodes, pad=12, thickness=18, color=node_colors, hovertemplate='%{label}<extra></extra>'),
            link=dict(source=source, target=target, value=value,
                      hovertemplate=['Revenue: ₹{:,.0f}<extra></extra>'.format(v) for v in value])
        ))
        fig.update_layout(title_text='Revenue Flow', template='plotly_white', height=650)
        st.plotly_chart(fig, use_container_width=True)
        links_df = pd.DataFrame({'source_label':[nodes[s] for s in source],
                                 'target_label':[nodes[t] for t in target],
                                 'value':value})
        st.download_button("Download Sankey links CSV", data=links_df.to_csv(index=False).encode('utf-8'),
                           file_name='sankey_links.csv', mime='text/csv')

#### Tab 2: Composition & Trend
with tab2:
    st.header("Revenue Composition and Trend")
    treemap_df = filtered.groupby(['category','product_name'], as_index=False)['revenue'].sum()
    fig_treemap = px.treemap(treemap_df, path=['category','product_name'], values='revenue',
                             title='Revenue Treemap by Category and Product', template='plotly_white')
    fig_treemap.update_traces(root_color="lightgrey")
    st.plotly_chart(fig_treemap, use_container_width=True)

    monthly = filtered.groupby('order_month_dt', as_index=False)['revenue'].sum().sort_values('order_month_dt')
    if not monthly.empty:
        monthly['trend'] = monthly['revenue'].rolling(3, center=True, min_periods=1).mean()
        fig_area = px.area(monthly, x='order_month_dt', y='revenue', title='Monthly Revenue with 3-month Trend',
                           labels={'order_month_dt':'Month','revenue':'Revenue (₹)'}, template='plotly_white')
        fig_area.add_scatter(x=monthly['order_month_dt'], y=monthly['trend'],
                             mode='lines', line=dict(color='black', dash='dash'), name='3-month trend')
        fig_area.update_layout(hovermode='x unified')
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("No monthly data available for the selected range.")

#### Tab 3: Export & Data
with tab3:
    st.header("Filtered Data & Exports")
    st.write("Rows in filtered dataset:", len(filtered))
    with st.expander("Show filtered raw data"):
        st.dataframe(filtered.reset_index(drop=True))
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download filtered orders CSV", data=csv, file_name='filtered_orders.csv', mime='text/csv')