"""
Centralized logging for the pipeline.
Every pipeline run writes rows into a SQLite table (logs/pipeline_runs.db)
AND a plain-text log file (logs/pipeline.log).

The SQLite table is what the Streamlit dashboard and the FastAPI app read from,
which is how "logging all activity details and displaying them on a Cloud
dashboard" (Activity 1.5) is satisfied.
"""

import sqlite3
import logging
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(LOG_DIR, "pipeline_runs.db")
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

os.makedirs(LOG_DIR, exist_ok=True)

# ---- plain text logger ----
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logging.getLogger().addHandler(console)

logger = logging.getLogger("churn_pipeline")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_started TEXT,
            run_finished TEXT,
            stage TEXT,
            status TEXT,
            details TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log_stage(run_id, stage, status, details=""):
    """Insert one row per pipeline stage (ingest / preprocess / eda) into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO pipeline_runs (run_started, run_finished, stage, status, details) "
        "VALUES (?, ?, ?, ?, ?)",
        (run_id, datetime.now(timezone.utc).isoformat(), stage, status, details),
    )
    conn.commit()
    conn.close()
    logger.info(f"[run={run_id}] stage={stage} status={status} details={details}")


def get_recent_runs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT run_started, run_finished, stage, status, details "
        "FROM pipeline_runs ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


init_db()
