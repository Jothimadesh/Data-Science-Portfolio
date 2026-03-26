# ============================================================
# 🦠 COVID-19 REACTIVE DASHBOARD (PRO VERSION)
# Author: Jothi Madesh
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="COVID Dashboard", layout="wide")

st.title("🦠 COVID-19 Global Dashboard")
st.markdown("Interactive & Real-Time Analysis")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/covid_19_data.csv")

    df['ObservationDate'] = pd.to_datetime(df['ObservationDate'])
    df['Last Update'] = pd.to_datetime(df['Last Update'], errors='coerce')

    df['Active'] = df['Confirmed'] - df['Deaths'] - df['Recovered']
    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS (REACTIVE)
# -----------------------------
st.sidebar.header("🔍 Filters")

countries = df['Country/Region'].unique()
selected_country = st.sidebar.selectbox("Select Country", ["All"] + list(countries))

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['ObservationDate'].min(), df['ObservationDate'].max()]
)

# -----------------------------
# FILTER DATA
# -----------------------------
filtered_df = df.copy()

if selected_country != "All":
    filtered_df = filtered_df[filtered_df['Country/Region'] == selected_country]

filtered_df = filtered_df[
    (filtered_df['ObservationDate'] >= pd.to_datetime(date_range[0])) &
    (filtered_df['ObservationDate'] <= pd.to_datetime(date_range[1]))
]

# -----------------------------
# KPI METRICS
# -----------------------------
total_confirmed = int(filtered_df['Confirmed'].sum())
total_deaths = int(filtered_df['Deaths'].sum())
total_recovered = int(filtered_df['Recovered'].sum())
total_active = int(filtered_df['Active'].sum())

col1, col2, col3, col4 = st.columns(4)

col1.metric("Confirmed", f"{total_confirmed:,}")
col2.metric("Deaths", f"{total_deaths:,}")
col3.metric("Recovered", f"{total_recovered:,}")
col4.metric("Active", f"{total_active:,}")

# -----------------------------
# TIME SERIES
# -----------------------------
ts = filtered_df.groupby('ObservationDate')[['Confirmed','Deaths','Recovered']].sum().reset_index()

fig = px.line(
    ts,
    x='ObservationDate',
    y=['Confirmed','Deaths','Recovered'],
    title="📈 Trend Over Time"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TOP COUNTRIES BAR CHART
# -----------------------------
country_df = filtered_df.groupby('Country/Region')[['Confirmed']].sum().reset_index()
top10 = country_df.sort_values(by='Confirmed', ascending=False).head(10)

fig = px.bar(
    top10,
    x='Confirmed',
    y='Country/Region',
    orientation='h',
    title="🌍 Top Countries by Cases"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# PIE CHART
# -----------------------------
fig = px.pie(
    names=['Confirmed','Deaths','Recovered'],
    values=[total_confirmed, total_deaths, total_recovered],
    title="📊 Case Distribution"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# WORLD MAP
# -----------------------------
map_df = filtered_df.groupby('Country/Region')[['Confirmed']].sum().reset_index()

fig = px.choropleth(
    map_df,
    locations="Country/Region",
    locationmode="country names",
    color="Confirmed",
    title="🌍 Global Spread"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# DAILY CASES
# -----------------------------
ts['New Cases'] = ts['Confirmed'].diff().fillna(0)

fig = px.bar(ts, x='ObservationDate', y='New Cases', title="📅 Daily New Cases")

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("🚀 Built by Jothi Madesh | Data Science Portfolio")