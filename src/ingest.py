"""
Activity 1.2 - Data Ingestion

Downloads the Telco Customer Churn dataset (public, IBM sample dataset,
mirrored on GitHub) if not already present locally, and returns a DataFrame.

Business problem: Predict which telecom customers are likely to churn
(cancel their subscription), so the business can target retention offers
at high-risk customers.
"""

import os
import pandas as pd
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOCAL_PATH = os.path.join(DATA_DIR, "telco_churn.csv")
SOURCE_URL = (
    "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/"
    "master/data/Telco-Customer-Churn.csv"
)


def ingest_data() -> pd.DataFrame:
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(LOCAL_PATH):
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        with open(LOCAL_PATH, "wb") as f:
            f.write(resp.content)

    df = pd.read_csv(LOCAL_PATH)
    return df


if __name__ == "__main__":
    df = ingest_data()
    print(f"Ingested {len(df)} rows, {len(df.columns)} columns")
    print(df.head())
