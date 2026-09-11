"""
Prefect flow version of the churn pipeline, for use with Prefect Cloud.

Why this satisfies the "cloud dashboard" requirement without needing
AWS/Azure/GCP access (per Prof. Ankita's guidance):

    - Prefect Cloud (cloud.prefect.io) is a free, hosted orchestration UI.
    - You run a Prefect *worker* on your own laptop, which polls Prefect
      Cloud for scheduled work and executes it locally.
    - Every flow run's status, logs, duration, and retries are pushed to
      and visible on the Prefect Cloud dashboard in real time — this IS
      your "Cloud dashboard" (Activity 1.5), no separate Streamlit app
      or hosting needed.

Each @task below wraps one already-tested pipeline stage
(ingest.py / preprocess.py / eda.py), so the underlying logic is
unchanged from the standalone version - Prefect just adds
orchestration, retries, logging, and cloud scheduling on top of it.
"""

from prefect import flow, task, get_run_logger

from ingest import ingest_data
from preprocess import preprocess_data
from eda import run_eda


@task(name="ingest-data", retries=2, retry_delay_seconds=10)
def ingest_task():
    logger = get_run_logger()
    df = ingest_data()
    logger.info(f"Ingested {len(df)} rows, {len(df.columns)} columns")
    return df


@task(name="preprocess-data")
def preprocess_task(df):
    logger = get_run_logger()
    processed_df, report = preprocess_data(df)
    logger.info(f"Missing values handled: {report['missing_values']}")
    logger.info(f"Normalized columns: {report['numeric_columns_normalized']}")
    return processed_df


@task(name="run-eda")
def eda_task(processed_df):
    logger = get_run_logger()
    report = run_eda(processed_df)
    top_feature = list(report["feature_importance"].items())[0]
    logger.info(f"Top churn-driving feature: {top_feature[0]} ({top_feature[1]})")
    logger.info(f"Churn rate by contract: {report['churn_rate_by_contract']}")
    return report


@flow(name="churn-data-pipeline", log_prints=True)
def churn_pipeline_flow():
    """Full ingest -> preprocess -> EDA pipeline, orchestrated by Prefect."""
    raw_df = ingest_task()
    processed_df = preprocess_task(raw_df)
    eda_report = eda_task(processed_df)
    print("Pipeline run complete.")
    return eda_report


if __name__ == "__main__":
    churn_pipeline_flow()
