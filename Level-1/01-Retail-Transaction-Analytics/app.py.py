import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")

# ---------------- THEME ----------------
st.markdown("""
<style>

[data-testid="stSidebar"]{
background-color:white;
} 

div[data-testid="metric-container"]{
background-color:white !important;
padding:15px;
border-radius:10px;
border:1px solid #e5e7eb;
box-shadow:0px 4px 10px rgba(0,0,0,0.2);
}

div[data-testid="metric-container"] label{
color:black !important;
font-weight:600;
}

div[data-testid="metric-container"] div{
color:black !important;
font-size:22px;
} 
/* KPI container */
div[data-testid="metric-container"] {
background-color: #ffffff !important;
border-radius: 12px;
padding: 20px;
border: 1px solid white;
box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

/* KPI title */
div[data-testid="metric-container"] label {
color: white;
font-weight: bold;
}

/* KPI value */
div[data-testid="metric-container"] > div {
color: white;
font-size: 26px;
font-weight: bold;
}

/* Multiselect box */
div[data-baseweb="select"]{
background-color:#1e3a8a;
border-radius:8px;
}

/* Selected options */
span[data-baseweb="tag"]{
background-color:#6366f1 !important;
color:white !important;
} 

.stApp{
background-color:#0f2a44;
color:white;
}

h1{
text-align:center;
color:#c7d2fe;
}

div[data-testid="metric-container"]{
background-color:white;
padding:15px;
border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "clean_superstore.csv"))

palette = ["#3b82f6","#6366f1","#8b5cf6","#94a3b8"]

st.title("Retail Sales Analytics Dashboard")

# ================= KPI ROW =================

total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_quantity = df["Quantity"].sum()
avg_discount = df["Discount"].mean()

k1,k2,k3,k4 = st.columns(4)

k1.metric("Total Sales", f"${total_sales:,.0f}")
k2.metric("Total Profit", f"${total_profit:,.0f}")
k3.metric("Total Quantity", total_quantity)
k4.metric("Avg Discount", round(avg_discount,2))

st.markdown("---")

# ================= SECOND ROW =================
# 3 PANEL GRID

col1,col2,col3 = st.columns([2,2,3])

# -------- Sales by Category --------
with col1:

    st.subheader("Sales by Category")

    cat_sales = df.groupby("Category")["Sales"].sum().reset_index()

    fig1 = px.bar(
        cat_sales,
        x="Category",
        y="Sales",
        color="Category",
        color_discrete_sequence=palette,
        template="plotly_dark"
    )

    st.plotly_chart(fig1,use_container_width=True)

# -------- Sales by Region --------
with col2:

    st.subheader("Sales by Region")

    region_sales = df.groupby("Region")["Sales"].sum().reset_index()

    fig2 = px.pie(
        region_sales,
        values="Sales",
        names="Region",
        color_discrete_sequence=palette
    )

    st.plotly_chart(fig2,use_container_width=True)

# -------- Sales Map --------
with col3:

    st.subheader("Geographical Sales")

    state_map = df.groupby("State")["Sales"].sum().reset_index()

    state_codes = {
        "California":"CA",
        "Texas":"TX",
        "New York":"NY",
        "Washington":"WA",
        "Florida":"FL",
        "Illinois":"IL",
        "Pennsylvania":"PA",
        "Ohio":"OH",
        "Michigan":"MI",
        "Arizona":"AZ",
        "Georgia":"GA",
        "North Carolina":"NC",
        "Virginia":"VA",
        "Colorado":"CO",
        "Oregon":"OR"
    }

    state_map["code"] = state_map["State"].map(state_codes)

    fig3 = px.choropleth(
        state_map,
        locations="code",
        locationmode="USA-states",
        color="Sales",
        scope="usa",
        color_continuous_scale=["#1e3a5f","#3b82f6","#6366f1"]
    )

    st.plotly_chart(fig3, use_container_width=True)
# ================= THIRD ROW =================

col4,col5 = st.columns(2)

# -------- Top Subcategories --------
with col4:

    st.subheader("Top 10 Sub-Categories")

    sub_sales = df.groupby("Sub-Category")["Sales"].sum().nlargest(10).reset_index()

    fig4 = px.bar(
        sub_sales,
        x="Sales",
        y="Sub-Category",
        orientation="h",
        color="Sales",
        color_continuous_scale=["#1e3a5f","#3b82f6","#6366f1"],
        template="plotly_dark"
    )

    st.plotly_chart(fig4,use_container_width=True)

# -------- Discount vs Profit --------
with col5:

    st.subheader("Impact of Discount on Profit")

    fig5 = px.scatter(
        df,
        x="Discount",
        y="Profit",
        color="Category",
        color_discrete_sequence=palette,
        template="plotly_dark"
    )

    st.plotly_chart(fig5,use_container_width=True)

# ================= FOURTH ROW =================

col6,col7 = st.columns(2)

# -------- Customer Segment --------
with col6:

    st.subheader("Customer Segment Performance")

    seg_sales = df.groupby("Segment")["Sales"].sum().reset_index()

    fig6 = px.bar(
        seg_sales,
        x="Segment",
        y="Sales",
        color="Segment",
        color_discrete_sequence=palette,
        template="plotly_dark"
    )

    st.plotly_chart(fig6,use_container_width=True)

# -------- Sales vs Profit --------
with col7:

    st.subheader("Sales vs Profit Relation")

    fig7 = px.scatter(
        df,
        x="Sales",
        y="Profit",
        color="Category",
        color_discrete_sequence=palette,
        template="plotly_dark"
    )

    st.plotly_chart(fig7,use_container_width=True)

# ================= HEATMAP =================

st.subheader("Variable Correlation Heatmap")

corr = df[["Sales","Profit","Quantity","Discount"]].corr()

fig8 = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale=["#0f2a44","#3b82f6","#6366f1"]
)

st.plotly_chart(fig8,use_container_width=True)


st.sidebar.title("Analytics Control Panel")
palette = ["#3b82f6","#6366f1","#8b5cf6","#94a3b8"]
region = st.sidebar.multiselect(
    "Region",
    df["Region"].unique(),
    default=df["Region"].unique()
)

category = st.sidebar.multiselect(
    "Category",
    df["Category"].unique(),
    default=df["Category"].unique()
)

segment = st.sidebar.multiselect(
    "Segment",
    df["Segment"].unique(),
    default=df["Segment"].unique()
)
df = df[
    (df["Region"].isin(region)) &
    (df["Category"].isin(category)) &
    (df["Segment"].isin(segment))
]