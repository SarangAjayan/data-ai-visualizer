import streamlit as st
import pandas as pd
import plotly.express as px
import random
import openai
from cleaning_module import clean_data

st.set_page_config(page_title="📊 Auto-Insight AI Dashboard", layout="wide")
st.title("📊 AI Data Insight Dashboard")
st.markdown("Upload your dataset to get automatic insights in a Power BI-style visual layout.")

openai.api_key = st.secrets["OPENAI_API_KEY"]  # Store your OpenAI API key in Streamlit secrets

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Raw Data")
    st.dataframe(df.head())

    # Clean data
    df_clean = clean_data(df)
    st.subheader("🧹 Cleaned Data")
    st.dataframe(df_clean.head())

    numeric_cols = df_clean.select_dtypes(include=['int64', 'float64']).columns.tolist()
    all_cols = df_clean.columns.tolist()

    st.markdown("---")
    st.header("🔍 Auto Data Filters")

    for col in df_clean.select_dtypes(include=['object']).columns:
        unique_vals = df_clean[col].dropna().unique().tolist()
        selected = st.multiselect(f"Filter by {col}", unique_vals, default=unique_vals)
        df_clean = df_clean[df_clean[col].isin(selected)]

    if 'date' in "".join(df_clean.columns).lower():
        for col in df_clean.columns:
            if 'date' in col.lower():
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col])
                    min_date = df_clean[col].min()
                    max_date = df_clean[col].max()
                    date_range = st.date_input("Filter by date range", [min_date, max_date])
                    if len(date_range) == 2:
                        df_clean = df_clean[(df_clean[col] >= date_range[0]) & (df_clean[col] <= date_range[1])]
                except:
                    pass

    st.markdown("---")
    st.header("📈 Auto Insights Dashboard")

    regenerate = st.button("🔁 Regenerate Insights")
    if regenerate or 'regenerate_count' not in st.session_state:
        st.session_state.regenerate_count = st.session_state.get('regenerate_count', 0) + 1

    num_charts = st.slider("How many charts to generate?", 1, 9, 6)
    chart_types = ["Line", "Bar", "Scatter", "Box", "Histogram", "Pie", "Heatmap"]

    chart_cols = st.columns(3)

    for i in range(num_charts):
        with chart_cols[i % 3]:
            x = random.choice(all_cols)
            y = random.choice(numeric_cols) if numeric_cols else x
            chart_type = random.choice(chart_types)
            fig = None

            try:
                if chart_type == "Line":
                    fig = px.line(df_clean, x=x, y=y, title=f"Line: {y} vs {x}")
                elif chart_type == "Bar":
                    fig = px.bar(df_clean, x=x, y=y, title=f"Bar: {y} by {x}")
                elif chart_type == "Scatter":
                    fig = px.scatter(df_clean, x=x, y=y, title=f"Scatter: {y} vs {x}")
                elif chart_type == "Box":
                    fig = px.box(df_clean, x=x, y=y, title=f"Box Plot: {y} by {x}")
                elif chart_type == "Histogram":
                    fig = px.histogram(df_clean, x=x, title=f"Histogram of {x}")
                elif chart_type == "Pie":
                    fig = px.pie(df_clean, names=x, title=f"Pie Chart of {x}")
                elif chart_type == "Heatmap":
                    fig = px.density_heatmap(df_clean, x=x, y=y, title=f"Heatmap: {x} vs {y}")

                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Chart {i+1} failed: {e}")

    st.markdown("---")
    st.header("🧠 GPT-Powered Business Insights")

    from openai import OpenAI  # Add this to your imports at the top
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if st.button("📌 Generate AI Insights"):
    with st.spinner("Analyzing with ChatGPT..."):
        try:
            sample = df_clean.sample(min(50, len(df_clean)))
            prompt = f"""
            You are a data analyst. Provide a brief summary of the dataset below, insights about key trends or patterns, potential issues, and suggestions a company can act on.

            Dataset (first few rows):
            {sample.to_csv(index=False)}
            """

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional data analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            insight_text = response.choices[0].message.content
            st.success("Insights generated successfully!")
            st.markdown(insight_text)
        except Exception as e:
            st.error(f"Failed to generate insights: {e}")


    st.markdown("---")
    st.download_button("📤 Download Cleaned Data as CSV", df_clean.to_csv(index=False), "cleaned_data.csv", "text/csv")
    st.caption("Built with ❤️ using Streamlit, Plotly, and GPT")

