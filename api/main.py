"""
Sub-Objective 2 - API Access

Exposes application details via built-in FastAPI mechanisms:
  - Auto-generated OpenAPI docs at /docs (this itself is a "built-in API"
    you can screenshot for 3.1/3.3 - it documents every endpoint, request
    schema, and response schema automatically)
  - Custom endpoints exposing >= 4 pieces of application info (3.2):
      1. GET /health            -> app/deployment liveness info
      2. GET /pipeline/status   -> last pipeline run status + timestamp
      3. GET /pipeline/runs     -> full run history (from SQLite log)
      4. GET /dataset/info      -> dataset shape, columns, source
      5. GET /eda/top-features  -> top churn-driving features (from last EDA run)

Run locally:
    cd api
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000/docs for interactive Swagger UI (built-in
API doc tool) to test each endpoint and capture screenshots of the request/
response + status code, as required by Activity 3.3.

Deploy on Render (free web service):
    Start command -> uvicorn api.main:app --host 0.0.0.0 --port $PORT
"""

import os
import sys
import platform
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from logger_config import get_recent_runs, DB_PATH  # noqa: E402
from ingest import LOCAL_PATH, ingest_data  # noqa: E402

app = FastAPI(
    title="Churn Pipeline Monitoring API",
    description="Exposes pipeline run status, dataset info, and EDA highlights.",
    version="1.0.0",
)

APP_START_TIME = datetime.now(timezone.utc)


@app.get("/health")
def health():
    """Deployment / liveness info."""
    return {
        "status": "healthy",
        "app_version": app.version,
        "python_version": platform.python_version(),
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": (datetime.now(timezone.utc) - APP_START_TIME).total_seconds(),
    }


@app.get("/pipeline/status")
def pipeline_status():
    """Latest pipeline run: stage, status, and when it completed."""
    rows = get_recent_runs(limit=10)
    if not rows:
        raise HTTPException(status_code=404, detail="No pipeline runs logged yet")
    latest = rows[0]
    return {
        "run_started": latest[0],
        "run_finished": latest[1],
        "stage": latest[2],
        "status": latest[3],
        "details": latest[4],
    }


@app.get("/pipeline/runs")
def pipeline_runs(limit: int = 20):
    """Full run history for the dashboard / audit trail."""
    rows = get_recent_runs(limit=limit)
    return {
        "count": len(rows),
        "runs": [
            {
                "run_started": r[0],
                "run_finished": r[1],
                "stage": r[2],
                "status": r[3],
                "details": r[4],
            }
            for r in rows
        ],
    }


@app.get("/dataset/info")
def dataset_info():
    """Details about the ingested dataset."""
    df = ingest_data()
    return {
        "source_file": os.path.basename(LOCAL_PATH),
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "target_variable": "Churn",
    }


@app.get("/eda/top-features")
def top_features():
    """Top churn-driving features from the most recent EDA run's log line."""
    rows = get_recent_runs(limit=50)
    eda_rows = [r for r in rows if r[2] == "eda" and r[3] == "SUCCESS"]
    if not eda_rows:
        raise HTTPException(status_code=404, detail="No successful EDA run logged yet")
    return {"latest_eda_result": eda_rows[0][4], "logged_at": eda_rows[0][1]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
