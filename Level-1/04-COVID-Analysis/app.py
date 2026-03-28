# ============================================================
# 🦠 COVID-19 DASHBOARD (✅ STREAMLIT CLOUD READY!)
# Author: Jothi Madesh | Direct URL Data
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ── PRO THEME ──────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:linear-gradient(135deg,#0c1445 0%,#1a237e 25%,#283593 50%,#3949ab 75%,#1a237e 100%);background-attachment:fixed;}
h1{font-size:4rem!important;background:linear-gradient(45deg,#00d4ff,#0099cc,#007acc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;text-shadow:0 0 30px rgba(0,212,255,.5);font-weight:900!important;margin-bottom:.5rem!important;}
[data-testid="metric-container"]{background:rgba(255,255,255,.1)!important;backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.2);border-radius:20px!important;box-shadow:0 8px 32px rgba(0,0,0,.3);padding:2rem!important;}
[data-testid="metric-value"]{color:#00d4ff!important;font-size:2.5rem!important;font-weight:700!important;}
.plotly-graph-div{border-radius:20px!important;box-shadow:0 10px 40px rgba(0,0,0,.4)!important;margin-bottom:2rem!important;}
.plotly-graph-div .modebar{background:rgba(0,0,0,.8)!important;}
.mapboxgl-map{border-radius:20px!important;box-shadow:0 10px 40px rgba(0,0,0,.5)!important;}
[data-testid="stSidebar"]{background:rgba(12,20,69,.95)!important;backdrop-filter:blur(20px);border-right:1px solid rgba(255,255,255,.1);}
.stSelectbox>div>div>div,.stDateInput>div>div>div{background:rgba(255,255,255,.1)!important;border-radius:15px!important;border:1px solid rgba(255,255,255,.2);color:#e0e7ff!important;}
h2,h3{color:#60a5fa!important;text-shadow:0 2px 10px rgba(96,165,250,.3)!important;}
.stMarkdown{color:#e0e7ff!important;}
hr{border:none!important;height:3px!important;background:linear-gradient(90deg,transparent,#00d4ff,transparent)!important;border-radius:2px!important;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="COVID Dashboard", layout="wide", page_icon="🦠")

st.title("🦠 **COVID-19 Global Dashboard**")
st.markdown("*Interactive Analysis | Jothi Madesh*")

# ── ✅ DIRECT URL DATA (No local files!) ───────────────────
@st.cache_data
def load_data():
    # ✅ STREAMLIT CLOUD SAFE URL
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    df = pd.read_csv(url)
    
    df['date'] = pd.to_datetime(df['date'])
    df['Active'] = df['total_cases'] - df['total_deaths']
    df['new_cases'] = df['new_cases'].fillna(0)
    
    st.sidebar.success(f"✅ Loaded: {len(df):,} rows from OWID")
    return df

df = load_data()

# ── FILTERS ────────────────────────────────────────────────
st.sidebar.header("🔍 **Filters**")
countries = sorted(df['location'].unique())
selected_country = st.sidebar.selectbox("**Country**", ["Global"] + list(countries))

min_date = df['date'].min().date()
max_date = df['date'].max().date()
date_range = st.sidebar.date_input("**Date Range**", [min_date, max_date])

# ── FILTER DATA ────────────────────────────────────────────
filtered_df = df[
    (df['date'] >= pd.to_datetime(date_range[0])) & 
    (df['date'] <= pd.to_datetime(date_range[1]))
].copy()

if selected_country != "Global":
    filtered_df = filtered_df[filtered_df['location'] == selected_country]

# ── METRICS ────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
total_cases = int(filtered_df['total_cases'].sum())
total_deaths = int(filtered_df['total_deaths'].sum())
total_active = int(filtered_df['Active'].sum())

with col1: st.metric("🔴 **Confirmed**", f"{total_cases:,}")
with col2: st.metric("⚫ **Deaths**", f"{total_deaths:,}")
with col3: st.metric("🟡 **Active**", f"{total_active:,}")
with col4: st.metric("🧪 **Tests**", f"{int(filtered_df['total_tests'].sum()):,}")

st.markdown("---")

# ── CHARTS ─────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    ts = filtered_df.groupby('date')[['total_cases','total_deaths']].sum().reset_index()
    fig_line = px.line(ts, x='date', y=['total_cases','total_deaths'],
                      title="📈 **Trend Over Time**",
                      color_discrete_map={'total_cases': '#ff6b6b', 'total_deaths': '#4ecdc4'})
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    country_summary = filtered_df.groupby('location')['total_cases'].sum().reset_index()
    top10 = country_summary.nlargest(10, 'total_cases')
    fig_bar = px.bar(top10, x='total_cases', y='location', orientation='h',
                    title="🌍 **Top 10 Countries**",
                    color='total_cases', color_continuous_scale='Viridis')
    fig_bar.update_layout(height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    pie_data = [total_cases - total_deaths, total_deaths]
    fig_pie = px.pie(values=pie_data, names=['Active', 'Deaths'],
                    title="📊 **Case Status**",
                    color_discrete_sequence=['#45b7d1', '#ff6b6b'])
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    map_data = filtered_df.groupby('location')['total_cases'].sum().reset_index()
    fig_map = px.choropleth(map_data, locations="location",
                           locationmode="country names",
                           color="total_cases",
                           title="🗺️ **Global Heatmap**",
                           color_continuous_scale="Reds")
    fig_map.update_layout(height=400)
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")
daily_new = filtered_df.groupby('date')['new_cases'].sum().reset_index()
fig_hist = px.bar(daily_new.tail(30), x='date', y='new_cases',
                 title="📅 **Last 30 Days New Cases**",
                 color='new_cases', color_continuous_scale='Plasma')
fig_hist.update_layout(height=400)
st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")
st.markdown("*🚀 Data Science Portfolio | Jothi Madesh*")