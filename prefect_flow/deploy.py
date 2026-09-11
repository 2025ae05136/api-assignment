"""
Creates a Prefect MANAGED deployment of churn_pipeline_flow.

IMPORTANT: Prefect Cloud's free tier no longer allows hybrid work pools
(type "process"), which need a worker running on your own machine — that
now requires a paid plan. Instead, this uses a "Prefect Managed" work
pool: Prefect runs your flow on ITS OWN infrastructure, in a container,
on schedule. No worker, no local machine needed to be on at all.

Because there's no worker pulling code from your local disk, Prefect needs
to fetch your flow code from somewhere reachable at run time — your public
GitHub repo. That's why `flow.from_source(...)` below points at your repo
URL instead of just importing flow.py directly.

One-time setup (in your terminal):

    pip install prefect
    prefect cloud login
    prefect work-pool create my-managed-pool --type prefect:managed

Then run this script once to register the deployment:

    python deploy.py

No worker to start. Prefect Cloud's scheduler will trigger a new container
run every 2 minutes on its own. Open cloud.prefect.io -> Deployments ->
"churn-data-pipeline/every-2-minutes" (or -> Flow Runs) and you'll see runs
firing every 2 minutes with full logs, duration, and status - this is your
screenshot for Activity 1.5 (Cloud dashboard) and proof of scheduled
execution actually happening in the cloud.

NOTE: every time you push a code change to GitHub, Prefect Managed picks
up the latest commit on the branch automatically on the next run - you
don't need to re-run deploy.py unless you change the schedule or pool.
"""

from prefect import flow
from prefect.client.schemas.schedules import IntervalSchedule
from datetime import timedelta

REPO_URL = "https://github.com/2025ae05136/api-assignment.git"
ENTRYPOINT = "prefect_flow/flow.py:churn_pipeline_flow"

if __name__ == "__main__":
    flow.from_source(
        source=REPO_URL,
        entrypoint=ENTRYPOINT,
    ).deploy(
        name="every-2-minutes",
        work_pool_name="my-managed-pool",
        schedule=IntervalSchedule(interval=timedelta(minutes=2)),
        job_variables={
            "pip_packages": [
                "pandas",
                "scikit-learn",
                "matplotlib",
                "seaborn",
                "requests",
            ]
        },
    )