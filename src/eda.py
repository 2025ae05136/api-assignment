"""
Activity 1.4 - Exploratory Data Analysis

- Correlation coefficients (numeric-numeric)
- Numeric-vs-categorical relationship (churn rate by category)
- Binning (tenure -> tenure groups)
- Encoding (label encoding of categorical columns)
- Feature importance (Random Forest on encoded data)
- Visualizations: univariate (histogram) + bivariate (boxplot, heatmap,
  bar chart) saved as PNG files that the dashboard displays.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no display needed on a server
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS_DIR = os.path.join(BASE_DIR, "logs", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)


def run_eda(df: pd.DataFrame):
    report = {}
    df = df.copy()

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    numeric_cols = [c for c in numeric_cols if not c.endswith("_norm")]

    # 1. Correlation coefficients (numeric-numeric)
    corr_matrix = df[numeric_cols].corr()
    report["correlation_matrix"] = corr_matrix.round(3).to_dict()

    plt.figure(figsize=(6, 5))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Heatmap (numeric features)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "correlation_heatmap.png"))
    plt.close()

    # 2. Binning: tenure (months) -> tenure groups
    df["tenure_group"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 60, 72],
        labels=["0-1yr", "1-2yr", "2-4yr", "4-5yr", "5-6yr"],
        include_lowest=True,
    )
    report["tenure_group_counts"] = df["tenure_group"].value_counts().to_dict()

    # 3. Numeric vs categorical relationship: churn rate by contract type
    churn_by_contract = (
        df.groupby("Contract")["Churn"].apply(lambda s: (s == "Yes").mean())
    )
    report["churn_rate_by_contract"] = churn_by_contract.round(3).to_dict()

    plt.figure(figsize=(6, 4))
    churn_by_contract.plot(kind="bar", color="teal")
    plt.ylabel("Churn rate")
    plt.title("Churn Rate by Contract Type")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "churn_rate_by_contract.png"))
    plt.close()

    # 4. Univariate: distribution of monthly charges
    plt.figure(figsize=(6, 4))
    sns.histplot(df["MonthlyCharges"], bins=30, kde=True, color="steelblue")
    plt.title("Distribution of Monthly Charges")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "monthly_charges_hist.png"))
    plt.close()

    # 5. Bivariate: tenure vs monthly charges by churn
    plt.figure(figsize=(6, 4))
    sns.boxplot(data=df, x="Churn", y="tenure")
    plt.title("Tenure Distribution by Churn Status")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "tenure_by_churn_boxplot.png"))
    plt.close()

    # 6. Encoding: label-encode all categorical columns for modeling
    encoded_df = df.copy()
    cat_cols = encoded_df.select_dtypes(include="object").columns.tolist()
    cat_cols = [c for c in cat_cols if c not in ("customerID",)]
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        encoded_df[col] = le.fit_transform(encoded_df[col].astype(str))
        encoders[col] = le
    report["encoded_columns"] = cat_cols

    # 7. Feature importance via Random Forest
    target = "Churn"
    feature_cols = [
        c for c in encoded_df.columns
        if c not in (target, "customerID", "tenure_group") and not c.endswith("_norm")
    ]
    X = encoded_df[feature_cols]
    y = encoded_df[target]

    rf = RandomForestClassifier(n_estimators=200, random_state=42)
    rf.fit(X, y)
    importances = pd.Series(rf.feature_importances_, index=feature_cols)
    importances = importances.sort_values(ascending=False)
    report["feature_importance"] = importances.round(4).to_dict()

    plt.figure(figsize=(7, 6))
    importances.head(10).sort_values().plot(kind="barh", color="darkorange")
    plt.title("Top 10 Feature Importances (Random Forest)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "feature_importance.png"))
    plt.close()

    return report


if __name__ == "__main__":
    from ingest import ingest_data
    from preprocess import preprocess_data

    raw = ingest_data()
    processed, _ = preprocess_data(raw)
    eda_report = run_eda(processed)
    print("Top 5 important features:")
    for k, v in list(eda_report["feature_importance"].items())[:5]:
        print(f"  {k}: {v}")
