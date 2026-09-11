"""
Creates a Prefect deployment of churn_pipeline_flow that Prefect Cloud will
trigger every 2 minutes. The actual code still runs wherever your worker is
running (your laptop) — Prefect Cloud only handles scheduling + the
dashboard/UI + logs.

One-time setup (do this in your terminal, not this script):

    pip install prefect
    prefect cloud login                      # opens browser, log in / sign up free
    prefect work-pool create local-pool --type process

Then run this script once to register the deployment:

    python deploy.py

Then start a worker (leave this running during your demo/video — this is
the process that actually executes the flow every 2 minutes):

    prefect worker start --pool local-pool

After that, open the Prefect Cloud UI (cloud.prefect.io) -> Deployments ->
"churn-data-pipeline/every-2-minutes" and you'll see flow runs firing every
2 minutes with full logs, duration, and status - this is your screenshot
for Activity 1.5 (Cloud dashboard) and proof of scheduled execution.
"""

from flow import churn_pipeline_flow
from prefect.client.schemas.schedules import IntervalSchedule
from datetime import timedelta

if __name__ == "__main__":
    churn_pipeline_flow.deploy(
        name="every-2-minutes",
        work_pool_name="local-pool",
        schedule=IntervalSchedule(interval=timedelta(minutes=2)),
        # Prefect Cloud only needs the flow entrypoint; the worker pulls and
        # runs the code from this same machine/repo, so no image build step
        # is required for a local-process work pool.
    )
