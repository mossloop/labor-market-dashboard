"""
Labor Market Dashboard — Streamlit app.

Run with: streamlit run dashboard/app.py
"""
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "labor_market.db")

st.set_page_config(page_title="Labor Market Dashboard", layout="wide")


@st.cache_data
def load_data():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    bls_df = pd.read_sql("SELECT * FROM bls_timeseries", engine, parse_dates=["date"])
    census_df = pd.read_sql("SELECT * FROM census_state_snapshot", engine)
    return bls_df, census_df


st.title("U.S. Labor Market Dashboard")
st.caption("Data from the BLS Public Data API and Census ACS 1-year estimates.")

try:
    bls_df, census_df = load_data()
except Exception as e:
    st.error(
        "Couldn't load the database. Run the ETL pipeline first:\n\n"
        "```\npython etl/fetch_bls.py\npython etl/fetch_census.py\npython etl/transform.py\n```"
    )
    st.stop()

tab1, tab2, tab3 = st.tabs(["National Trends", "State Comparison", "Demographics (Census)"])

# --- Tab 1: National trends ---
with tab1:
    st.subheader("National Indicators Over Time")

    national_series = [
        series for series in [
            "unemployment_rate_national",
            "nonfarm_payrolls",
            "avg_hourly_earnings",
        ]
        if series in bls_df["series_name"].unique()
    ]
    selected_series = st.multiselect(
        "Select indicators", national_series, default=["unemployment_rate_national"]
    )

    if selected_series:
        plot_df = bls_df[bls_df["series_name"].isin(selected_series)]
        fig = px.line(
            plot_df, x="date", y="value", color="series_name",
            title="Selected Indicators", labels={"value": "Value", "date": "Date"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one indicator above.")

# --- Tab 2: State comparison ---
with tab2:
    st.subheader("State Unemployment Rate Comparison")

    state_series = [s for s in bls_df["series_name"].unique() if s.startswith("unemployment_rate_")
                     and s != "unemployment_rate_national"]
    state_df = bls_df[bls_df["series_name"].isin(state_series)]

    if not state_df.empty:
        fig = px.line(
            state_df, x="date", y="value", color="series_name",
            title="State Unemployment Rates", labels={"value": "Unemployment Rate (%)", "date": "Date"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No state-level series found. Add more state series IDs in etl/fetch_bls.py.")

# --- Tab 3: Census demographics ---
with tab3:
    st.subheader("Labor Force & Education by State (ACS 1-Year)")

    metric = st.selectbox(
        "Metric", ["unemployment_rate_pct", "bachelors_rate_pct", "labor_force", "total_population"]
    )

    fig = px.bar(
        census_df.sort_values(metric, ascending=False).head(20),
        x="state_name", y=metric, title=f"Top 20 States by {metric}"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(census_df.sort_values(metric, ascending=False), use_container_width=True)

st.divider()
st.caption(
    "Sources: U.S. Bureau of Labor Statistics (bls.gov/developers) and "
    "U.S. Census Bureau ACS (census.gov/data/developers)."
)
