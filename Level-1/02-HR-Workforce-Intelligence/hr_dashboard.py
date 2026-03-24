import streamlit as st
import pandas as pd
import plotly.express as px

# PASTEL COLORS
PASTEL_BLUE = "#A3C6E6"
PASTEL_GRAY = "#E8ECEF" 
DARK_BLUE = "#2C5282"
LIGHT_GRAY = "#F7FAFC"

st.set_page_config(page_title="HR PRO Dashboard", layout="wide", page_icon="📊")

# FULL BACKGROUND
st.markdown(f"""
    <style>
    .stApp {{background: linear-gradient(135deg, {PASTEL_GRAY} 0%, {LIGHT_GRAY} 100%)}}
    .stMetric > div {{background-color: white; border-radius: 12px; padding: 1.5rem; border-left: 6px solid {PASTEL_BLUE}; box-shadow: 0 4px 6px rgba(0,0,0,0.1)}}
    h1 {{color: {DARK_BLUE} !important; text-align: center; font-size: 2.5rem}}
    </style>
""", unsafe_allow_html=True)

st.title("HR Workforce Intelligence")
st.markdown("---")

@st.cache_data
def load_data():
    return pd.read_csv("WA_Fn-UseC_-HR-Employee-Attrition-4.csv")

df = load_data()
filtered_df = df.copy()

# 🔥 NEW UNIQUE FILTER DESIGN - Horizontal Tabs + Dropdowns
tab1, tab2 = st.tabs(["📊 Quick Filters", "⚙️ Advanced"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        dept_filter = st.selectbox("Department", ["All"] + sorted(df["Department"].unique().tolist()))
    with col2:
        gender_filter = st.selectbox("Gender", ["All"] + sorted(df["Gender"].unique().tolist()))
    with col3:
        attrition_filter = st.selectbox("Attrition", ["All", "Yes", "No"])

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        age_range = st.slider("Age Range", 18, 60, (18, 60))
    with col2:
        perf_rating = st.selectbox("Performance Rating", ["All"] + sorted(df["PerformanceRating"].unique().tolist()))

# Apply filters
if dept_filter != "All": filtered_df = filtered_df[filtered_df["Department"] == dept_filter]
if gender_filter != "All": filtered_df = filtered_df[filtered_df["Gender"] == gender_filter]
if attrition_filter != "All": filtered_df = filtered_df[filtered_df["Attrition"] == attrition_filter]
filtered_df = filtered_df[(filtered_df["Age"] >= age_range[0]) & (filtered_df["Age"] <= age_range[1])]
if perf_rating != "All": filtered_df = filtered_df[filtered_df["PerformanceRating"] == perf_rating]

# KPI CARDS
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("👥 Total Employees", f"{len(filtered_df):,}", "1.2%")
col2.metric("⚠️ Attrition Rate", f"{filtered_df['Attrition'].eq('Yes').mean()*100:.1f}%", "+0.5%")
col3.metric("💰 Avg Salary", f"${filtered_df['MonthlyIncome'].mean():,.0f}", "+3.1%")
col4.metric("📊 Avg Age", f"{filtered_df['Age'].mean():.0f} years", "-0.8%")
col5.metric("⭐ Avg Performance", f"{filtered_df['PerformanceRating'].mean():.1f}", "+0.2")

st.markdown("---")

# CHARTS
col1, col2 = st.columns([2,1])
attr_dept = filtered_df.groupby(['Department', 'Attrition']).size().unstack(fill_value=0)
fig1 = px.imshow(attr_dept.T, title="Attrition Heatmap", 
                color_continuous_scale=[LIGHT_GRAY, PASTEL_BLUE, DARK_BLUE],
                aspect="auto", text_auto=True)
fig1.update_layout(plot_bgcolor=LIGHT_GRAY, paper_bgcolor=LIGHT_GRAY)
col1.plotly_chart(fig1, use_container_width=True)

fig2 = px.pie(filtered_df, names='Gender', title="Gender Distribution",
             color_discrete_sequence=[PASTEL_BLUE, "#CBD5E0"])
fig2.update_traces(textposition='inside')
fig2.update_layout(plot_bgcolor=LIGHT_GRAY, paper_bgcolor=LIGHT_GRAY)
col2.plotly_chart(fig2, use_container_width=True)

col1, col2 = st.columns(2)
fig3 = px.scatter(filtered_df, x='YearsAtCompany', y='MonthlyIncome', 
                size='TotalWorkingYears', color='Attrition', hover_name='JobRole',
                title="Salary vs Experience", size_max=25,
                color_discrete_map={'Yes': DARK_BLUE, 'No': PASTEL_BLUE})
fig3.update_layout(plot_bgcolor=LIGHT_GRAY, paper_bgcolor=LIGHT_GRAY)
col1.plotly_chart(fig3, use_container_width=True)

overtime_data = filtered_df.groupby(['OverTime', 'Attrition']).size().reset_index(name='Count')
fig4 = px.bar(overtime_data, x='OverTime', y='Count', color='Attrition',
             title="Overtime Impact", color_discrete_map={'Yes': DARK_BLUE, 'No': PASTEL_BLUE})
fig4.update_layout(plot_bgcolor=LIGHT_GRAY, paper_bgcolor=LIGHT_GRAY)
col2.plotly_chart(fig4, use_container_width=True)

col1, col2 = st.columns(2)
fig5 = px.histogram(filtered_df, x='Age', color='Attrition', title="Age Distribution",
                   color_discrete_map={'Yes': DARK_BLUE, 'No': PASTEL_BLUE}, nbins=30)
fig5.update_layout(plot_bgcolor=LIGHT_GRAY, paper_bgcolor=LIGHT_GRAY)
col1.plotly_chart(fig5, use_container_width=True)

job_role_count = filtered_df['JobRole'].value_counts().head(10)
fig6 = px.bar(x=job_role_count.index, y=job_role_count.values, title="Top Job Roles",
             color=job_role_count.values, color_continuous_scale=[PASTEL_BLUE, DARK_BLUE])
fig6.update_layout(plot_bgcolor=LIGHT_GRAY, paper_bgcolor=LIGHT_GRAY)
col2.plotly_chart(fig6, use_container_width=True)
