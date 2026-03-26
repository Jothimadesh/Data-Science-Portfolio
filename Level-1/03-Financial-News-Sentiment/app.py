# ================================================
# Financial News Sentiment Dashboard (PRO UI)
# Author: Jothi Madesh | Data Science Portfolio 2026
# ================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px

# ── PAGE CONFIG ────────────────────────────────
st.set_page_config(
    page_title="Financial News Sentiment Engine",
    page_icon="📈",
    layout="wide"
)

# ── CUSTOM DARK THEME ─────────────────────────
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: #e2e8f0;
}

/* Header */
.main-header {
    font-size: 3rem;
    color: #38bdf8;
    text-align: center;
    font-weight: bold;
}

/* Subtext */
.subtext {
    text-align: center;
    color: #94a3b8;
}

/* KPI Cards */
.metric-card {
    background: linear-gradient(135deg, #1d4ed8, #9333ea);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
}

/* Button */
.stButton > button {
    background: linear-gradient(90deg, #22c55e, #16a34a);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    font-weight: bold;
}

/* Text Area */
textarea {
    background-color: #020617 !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Headings */
h2, h3 {
    color: #38bdf8 !important;
}

</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('all-data-5.csv', encoding='latin-1', header=None)
    df.columns = ['sentiment', 'news_headline']
    df = df.drop_duplicates().reset_index(drop=True)
    df['news_headline'] = df['news_headline'].str.strip()

    analyzer = SentimentIntensityAnalyzer()
    df['vader_score'] = df['news_headline'].apply(
        lambda x: analyzer.polarity_scores(x)['compound']
    )

    df['vader_sentiment'] = df['vader_score'].apply(
        lambda x: 'positive' if x >= 0.05 else ('negative' if x <= -0.05 else 'neutral')
    )

    return df

df = load_data()

# ── HEADER ────────────────────────────────
st.markdown('<h1 class="main-header">📈 Financial News Intelligence Platform</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtext">AI-Powered Sentiment Analysis for Financial Markets</p>', unsafe_allow_html=True)
st.markdown('<p class="subtext">👤 Jothi Madesh | Data Science Portfolio 2026</p>', unsafe_allow_html=True)
st.divider()

# ── KPI DASHBOARD ─────────────────────────
st.markdown("## 🎯 Executive Summary")

col1, col2, col3, col4 = st.columns(4)

total = len(df)
positive = (df['sentiment'] == 'positive').sum()
negative = (df['sentiment'] == 'negative').sum()
accuracy = (df['sentiment'] == df['vader_sentiment']).mean() * 100

col1.markdown(f'<div class="metric-card"><h4>Total News</h4><h2>{total}</h2></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="metric-card"><h4>Positive</h4><h2>{positive}</h2></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="metric-card"><h4>Negative</h4><h2>{negative}</h2></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="metric-card"><h4>Accuracy</h4><h2>{accuracy:.1f}%</h2></div>', unsafe_allow_html=True)

# ── PIE CHART ─────────────────────────────
st.markdown("## 📊 Sentiment Distribution")

fig = px.pie(
    df,
    names='sentiment',
    title='Overall Sentiment',
    color_discrete_sequence=px.colors.sequential.RdBu
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)

# ── HISTOGRAM ─────────────────────────────
st.markdown("## 📉 Sentiment Score Distribution")

fig = px.histogram(df, x="vader_score", nbins=50)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)

# ── WORD CLOUDS ───────────────────────────
st.markdown("## 🌩️ Word Cloud Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Positive Headlines")
    text = " ".join(df[df['sentiment'] == 'positive']['news_headline'])
    wc = WordCloud(width=500, height=400, background_color='white', colormap='Greens').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)

with col2:
    st.subheader("🔴 Negative Headlines")
    text = " ".join(df[df['sentiment'] == 'negative']['news_headline'])
    wc = WordCloud(width=500, height=400, background_color='black', colormap='Reds').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)

# ── LIVE ANALYZER ─────────────────────────
st.markdown("## ⚡ Live Financial Analyzer")

col1, col2 = st.columns([3,1])

with col1:
    user_input = st.text_area("", placeholder="Enter financial news headline...", label_visibility="collapsed")

with col2:
    analyze = st.button("Analyze", key="analyze_btn")

if analyze:
    if user_input.strip() == "":
        st.warning("Please enter a headline")
    else:
        analyzer = SentimentIntensityAnalyzer()
        score = analyzer.polarity_scores(user_input)['compound']

        if score >= 0.05:
            st.success(f"🟢 BULLISH | Score: {score:.3f}")
        elif score <= -0.05:
            st.error(f"🔴 BEARISH | Score: {score:.3f}")
        else:
            st.info(f"🔵 NEUTRAL | Score: {score:.3f}")

# ── INSIGHTS ─────────────────────────────
st.markdown("## 💼 Strategic Insights")

st.success("✅ Market shows high neutral sentiment → Stability")
st.info("📊 VADER baseline can be improved using ML models")
st.warning("⚠️ Negative sentiment detection is weaker → Opportunity")

# ── FOOTER ───────────────────────────────
st.markdown("---")
st.markdown("🚀 Built by Jothi Madesh | Data Science Portfolio 2026")