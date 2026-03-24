<<<<<<< HEAD
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="HR Dashboard", layout="wide")
st.title("HR Workforce Intelligence")

df = pd.read_csv('HRDataset.csv')

col1, col2 = st.columns(2)
fig1 = px.bar(df.groupby(['Department', 'Attrition']).size().reset_index(name='count'), 
              x='Department', y='count', color='Attrition')
col1.plotly_chart(fig1)

fig2 = px.scatter(df, x='Age', y='MonthlyIncome', color='Attrition')
col2.plotly_chart(fig2)

st.success("Dashboard deployed!")
=======
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="HR Dashboard", layout="wide")
st.title("HR Workforce Intelligence")

df = pd.read_csv('HRDataset.csv')

col1, col2 = st.columns(2)
fig1 = px.bar(df.groupby(['Department', 'Attrition']).size().reset_index(name='count'), 
              x='Department', y='count', color='Attrition')
col1.plotly_chart(fig1)

fig2 = px.scatter(df, x='Age', y='MonthlyIncome', color='Attrition')
col2.plotly_chart(fig2)

st.success("Dashboard deployed!")
>>>>>>> c4ac6bd8190a5c6ef5649d9115f170ce48a6451a
