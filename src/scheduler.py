"""
Runs the pipeline every 2 minutes, forever.

WHY NOT GITHUB ACTIONS CRON:
GitHub Actions' scheduled workflows have a hard minimum interval of 5 minutes
(and in practice often fire late under load), so they cannot satisfy a strict
"every 2 minutes" requirement. Instead, this script is deployed as an
always-on background worker (e.g. Render "Background Worker" free tier,
or a Railway/Fly.io worker, or just `python scheduler.py` left running in a
terminal / tmux session on your own machine for the demo).

Deployment note for the report/video:
  Render free background worker start command -> python src/scheduler.py
"""

import time
from apscheduler.schedulers.blocking import BlockingScheduler
from pipeline import run_pipeline
from logger_config import logger

INTERVAL_MINUTES = 2


def job():
    logger.info("Scheduled pipeline run triggered")
    run_pipeline()


if __name__ == "__main__":
    logger.info(f"Starting scheduler: pipeline will run every {INTERVAL_MINUTES} minutes")

    # Run once immediately on startup so the dashboard/API have data right away
    job()

    scheduler = BlockingScheduler()
    scheduler.add_job(job, "interval", minutes=INTERVAL_MINUTES, id="churn_pipeline_job")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
