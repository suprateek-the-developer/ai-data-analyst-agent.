
import streamlit as st
import plotly.express as px
import pandas as pd

from analyzer import (
    load_data,
    profile_data,
    prepare_dates,
    numeric_summary,
)
from agent import answer_question, explain_with_local_ai


st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI-Powered Data Analyst Agent")
st.caption(
    "Upload your data, explore it, and ask analytical questions."
)

uploaded = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"],
)

if uploaded is not None:
    try:
        df = load_data(uploaded)
    except Exception as exc:
        st.error(f"Could not load the file: {exc}")
        st.stop()
else:
    st.info(
        "Upload a dataset in the sidebar, or use the sample "
        "sales dataset to explore the application."
    )
    try:
        df = pd.read_csv("data/sample_sales.csv")
    except FileNotFoundError:
        st.warning("Create data/sample_sales.csv first.")
        st.stop()

df = prepare_dates(df)
profile = profile_data(df)

# Main dashboard KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{profile['rows']:,}")
c2.metric("Columns", profile["columns"])
c3.metric("Missing cells", profile["missing_cells"])
c4.metric("Duplicate rows", profile["duplicates"])

overview_tab, chart_tab, agent_tab = st.tabs(
    ["Data Overview", "Visualizations", "Ask the Agent"]
)

with overview_tab:
    st.subheader("Data Preview")
    st.dataframe(df.head(100), use_container_width=True)

    st.subheader("Column Information")
    schema = pd.DataFrame({
        "column": df.columns,
        "data_type": df.dtypes.astype(str).values,
        "missing_values": df.isna().sum().values,
        "unique_values": df.nunique(dropna=True).values,
    })
    st.dataframe(schema, use_container_width=True)

    st.subheader("Numeric Summary")
    summary = numeric_summary(df)
    if not summary.empty:
        st.dataframe(summary, use_container_width=True)
    else:
        st.info("No numeric columns found.")

    st.subheader("Missing Values by Column")
    missing = profile["missing_by_column"]
    missing = missing[missing > 0].sort_values(ascending=False)
    if not missing.empty:
        st.bar_chart(missing)
    else:
        st.success("No missing values found.")

with chart_tab:
    st.subheader("Explore Your Data")

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_cols = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    if numeric_cols:
        y_col = st.selectbox(
            "Metric",
            numeric_cols,
            key="chart_metric",
        )

        if categorical_cols:
            x_col = st.selectbox(
                "Category",
                categorical_cols,
                key="chart_category",
            )

            chart_data = (
                df.groupby(x_col, dropna=False)[y_col]
                .sum()
                .reset_index()
                .sort_values(y_col, ascending=False)
            )

            fig = px.bar(
                chart_data,
                x=x_col,
                y=y_col,
                title=f"{y_col} by {x_col}",
                text_auto=".2s",
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            fig = px.histogram(
                df,
                x=y_col,
                title=f"Distribution of {y_col}",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric columns available for charts.")

with agent_tab:
    st.subheader("Ask Questions About Your Data")
    st.write(
        "Examples: What is the total sales? "
        "What is average profit? "
        "Which region has the highest sales?"
    )

    question = st.text_input(
        "Your question",
        placeholder="Which region has the highest sales?",
    )

    
    if st.button("Analyze", type="primary"):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            result = answer_question(df, question)
            st.markdown("### Answer")
            st.write(result["answer"])

            with st.spinner("Generating explanation with local AI..."):
                explanation = explain_with_local_ai(
                    question,
                    result["answer"],
                )

            st.markdown("### AI Explanation")
            st.write(explanation)

            if "table" in result:
                st.dataframe(
                    result["table"],
                    use_container_width=True,
                )

                st.download_button(
                    "Download results as CSV",
                    data=result["table"].to_csv(index=False),
                    file_name="analysis_results.csv",
                    mime="text/csv",
                )


            if "table" in result:
                st.dataframe(
                    result["table"],
                    use_container_width=True,
                )

                st.download_button(
                    "Download results as CSV",
                    data=result["table"].to_csv(index=False),
                    file_name="analysis_results.csv",
                    mime="text/csv",
                )

st.sidebar.divider()
st.sidebar.caption("AI Data Analyst Agent · Portfolio Project")
