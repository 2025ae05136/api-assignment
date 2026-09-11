"""
Activity 1.5 - DataOps

Orchestrates ingestion -> preprocessing -> EDA as a single pipeline run,
logging the status of every stage into SQLite (via logger_config) so the
Streamlit dashboard and FastAPI app can display run history.

This module is what the scheduler (scheduler.py) calls every 2 minutes.
"""

import json
import traceback
from datetime import datetime, timezone

from ingest import ingest_data
from preprocess import preprocess_data
from eda import run_eda
from logger_config import log_stage


def run_pipeline():
    run_id = datetime.now(timezone.utc).isoformat()

    try:
        df = ingest_data()
        log_stage(run_id, "ingest", "SUCCESS", f"rows={len(df)}, cols={len(df.columns)}")
    except Exception as e:
        log_stage(run_id, "ingest", "FAILED", str(e))
        traceback.print_exc()
        return

    try:
        processed_df, prep_report = preprocess_data(df)
        missing_summary = json.dumps(prep_report["missing_values"])
        log_stage(run_id, "preprocess", "SUCCESS", f"missing_values={missing_summary}")
    except Exception as e:
        log_stage(run_id, "preprocess", "FAILED", str(e))
        traceback.print_exc()
        return

    try:
        eda_report = run_eda(processed_df)
        top_feature = list(eda_report["feature_importance"].items())[0]
        log_stage(
            run_id,
            "eda",
            "SUCCESS",
            f"top_feature={top_feature[0]} ({top_feature[1]})",
        )
    except Exception as e:
        log_stage(run_id, "eda", "FAILED", str(e))
        traceback.print_exc()
        return

    log_stage(run_id, "pipeline", "COMPLETE", "all stages finished successfully")


if __name__ == "__main__":
    run_pipeline()
