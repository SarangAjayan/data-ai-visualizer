import streamlit as st
import pandas as pd
import plotly.express as px
from cleaning_module import clean_data

st.set_page_config(page_title="📊 Multi-Graph AI Data Visualizer", layout="wide")
st.title("📊 Multi-Graph AI Data Visualizer")
st.markdown("Upload your dataset, clean it instantly, explore with filters, and create multiple visualizations.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Raw Data")
    st.dataframe(df.head())

    # Clean data
    df_clean = clean_data(df)
    st.subheader("🧹 Cleaned Data")
    st.dataframe(df_clean.head())

    # Column types
    numeric_cols = df_clean.select_dtypes(include=['int64', 'float64']).columns.tolist()
    all_cols = df_clean.columns.tolist()

    st.markdown("---")
    st.header("🔍 Data Filters")
    
    # Filtering options
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
    st.header("📈 Visualizations")

    num_charts = st.slider("How many charts to show?", 1, 10, 3)

    for i in range(num_charts):
        st.markdown(f"### 📊 Chart {i+1}")
        cols = st.columns([1, 1, 2])

        with cols[0]:
            x = st.selectbox(f"X-axis (Chart {i+1})", options=all_cols, key=f"x_{i}")
            y = st.selectbox(f"Y-axis (Chart {i+1})", options=numeric_cols, key=f"y_{i}")

        with cols[1]:
            chart_type = st.selectbox(
                f"Chart Type (Chart {i+1})",
                ["Line", "Bar", "Scatter", "Box", "Histogram", "Pie", "Heatmap"],
                key=f"type_{i}"
            )

        with cols[2]:
            fig = None
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

    st.markdown("---")
    st.download_button("📤 Download Cleaned Data as CSV", df_clean.to_csv(index=False), "cleaned_data.csv", "text/csv")
    st.caption("Built with ❤️ using Streamlit and Plotly")
