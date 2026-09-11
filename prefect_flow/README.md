# Prefect Cloud Version (confirmed acceptable by Prof. Ankita)

This folder is an alternative to `src/` + `api/` + `dashboard/` in the main
project. Instead of a custom Streamlit dashboard + APScheduler + Render
deployment, it uses **Prefect Cloud** for orchestration, scheduling, and
the "cloud dashboard" requirement — while the flow code executes on your
own machine via a local Prefect worker. This is the setup confirmed with
the professor for groups without cloud (AWS/Azure/GCP) access.

## Files
- `ingest.py`, `preprocess.py`, `eda.py` — same tested pipeline stages as
  the main project (unchanged logic)
- `flow.py` — wraps the three stages as Prefect `@task`s inside one
  `@flow`, with retries and structured logging
- `deploy.py` — registers a Prefect deployment scheduled to run every
  2 minutes
- `requirements.txt`

## One-time setup

```bash
pip install -r requirements.txt

# Sign up / log in (free) — opens a browser to authenticate
prefect cloud login

# Create a work pool that runs flows as local processes
prefect work-pool create local-pool --type process
```

## Register the 2-minute schedule

```bash
python deploy.py
```

## Run the worker (leave running during your demo/video)

```bash
prefect worker start --pool local-pool
```

The worker polls Prefect Cloud, picks up the scheduled run every 2 minutes,
and executes `flow.py` locally.

## What to screenshot for the report

1. **Prefect Cloud → Deployments** page showing `churn-data-pipeline /
   every-2-minutes` with its schedule
2. **Prefect Cloud → Flow Runs** page showing multiple completed runs, each
   ~2 minutes apart, with green "Completed" status
3. Click into one flow run → the **task graph** (ingest → preprocess → eda)
   and the **logs panel** showing the info messages from `flow.py`
   (row counts, missing values handled, top churn feature)
4. Your terminal running `prefect worker start` during a live 2-minute
   cycle, for the video demo

## How this maps to the assignment activities

| Assignment requirement | How Prefect Cloud satisfies it |
|---|---|
| Schedule workflow every 2 minutes | `IntervalSchedule(minutes=2)` in `deploy.py` |
| Log all activity details | Prefect automatically captures every task's logs, duration, retries, and state |
| Display on a Cloud dashboard | Prefect Cloud's hosted web UI (cloud.prefect.io) — no separate hosting needed |

## Note on Sub-Objective 2 (API Access)

Prefect Cloud also exposes everything above through its own **REST API**
(https://docs.prefect.io/latest/api-ref/rest-api/), which you can use
*instead of or alongside* the custom FastAPI app in `../api/`:

```bash
# Example: list recent flow runs via Prefect's API (needs your API key)
curl -H "Authorization: Bearer $PREFECT_API_KEY" \
  "https://api.prefect.cloud/api/accounts/<account_id>/workspaces/<workspace_id>/flow_runs/filter"
```

If you'd rather keep the custom FastAPI app (recommended — it's simpler to
demo and test in Postman, and clearly shows *your* API design work for
grading), just point it at the same `logs/pipeline_runs.db` — or better,
run `flow.py`'s tasks unchanged and let the custom `pipeline.py` +
FastAPI stack keep doing the logging/API job while Prefect Cloud handles
scheduling + its own dashboard as a second, complementary piece of
evidence. Either is defensible; using both is the strongest submission.
