import streamlit as st
import pandas as pd
import plotly.express as px
from cleaning_module import clean_data

st.title("📊 Auto Data Analyzer")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📄 Raw Data", df.head())

    df_clean = clean_data(df)
    st.write("🧹 Cleaned Data", df_clean.head())

    column = st.selectbox("📈 Select column to visualize", df_clean.columns)
    st.plotly_chart(px.histogram(df_clean, x=column))
