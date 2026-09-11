"""
Cloud Dashboard (Activity 1.5)

Streamlit app that displays:
  - Pipeline run history (from SQLite log written by src/pipeline.py)
  - Latest EDA charts (correlation heatmap, churn rate by contract, etc.)
  - Live auto-refresh every 30 seconds so it reflects the 2-minute
    scheduled pipeline runs

Run locally:
    cd dashboard
    streamlit run app.py

Deploy on Streamlit Community Cloud (free) or Render (free web service):
    Start command -> streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
"""

import os
import sys
import time

import pandas as pd
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from logger_config import get_recent_runs  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS_DIR = os.path.join(BASE_DIR, "logs", "charts")

st.set_page_config(page_title="Churn Pipeline Dashboard", layout="wide")
st.title("📊 Customer Churn Pipeline — DataOps Dashboard")
st.caption("Auto-refreshes to reflect scheduled pipeline runs (every 2 minutes)")

# ---- Pipeline run history ----
st.header("Pipeline Run History")
rows = get_recent_runs(limit=50)

if not rows:
    st.warning("No pipeline runs logged yet. Run `python src/pipeline.py` or start the scheduler.")
else:
    df_runs = pd.DataFrame(
        rows, columns=["run_started", "run_finished", "stage", "status", "details"]
    )

    latest_complete = df_runs[df_runs["stage"] == "pipeline"].head(1)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total logged events", len(df_runs))
    with col2:
        last_status = latest_complete["status"].values[0] if len(latest_complete) else "N/A"
        st.metric("Last full run status", last_status)
    with col3:
        last_time = latest_complete["run_finished"].values[0] if len(latest_complete) else "N/A"
        st.metric("Last completed at (UTC)", str(last_time)[:19])

    def highlight_status(val):
        color = "#c6f6d5" if val in ("SUCCESS", "COMPLETE") else "#fed7d7"
        return f"background-color: {color}"

    st.dataframe(
        df_runs.style.map(highlight_status, subset=["status"]),
        use_container_width=True,
        height=350,
    )

# ---- Latest EDA charts ----
st.header("Latest EDA Visualizations")
chart_files = {
    "Correlation Heatmap": "correlation_heatmap.png",
    "Churn Rate by Contract Type": "churn_rate_by_contract.png",
    "Monthly Charges Distribution": "monthly_charges_hist.png",
    "Tenure by Churn Status": "tenure_by_churn_boxplot.png",
    "Top 10 Feature Importances": "feature_importance.png",
}

cols = st.columns(2)
for i, (title, filename) in enumerate(chart_files.items()):
    path = os.path.join(CHARTS_DIR, filename)
    with cols[i % 2]:
        st.subheader(title)
        if os.path.exists(path):
            st.image(path, use_container_width=True)
        else:
            st.info("Chart not generated yet — run the pipeline first.")

st.divider()
if st.button("🔄 Refresh now"):
    st.rerun()

# Light auto-refresh
time.sleep(1)
