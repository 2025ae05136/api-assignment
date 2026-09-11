"""
Activity 1.3 - Data Pre-processing

- Summary statistics
- Missing value check
- Imputation for numeric columns
- Display data types
- Normalization (Min-Max scaling) of numeric columns
"""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def preprocess_data(df: pd.DataFrame):
    report = {}

    # TotalCharges is numeric but stored as string with some blank values in
    # this dataset -> coerce to numeric first.
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # 1. Data types
    report["dtypes"] = df.dtypes.astype(str).to_dict()

    # 2. Summary statistics (numeric columns)
    report["summary_statistics"] = df.describe().to_dict()

    # 3. Missing values check
    missing = df.isnull().sum()
    report["missing_values"] = missing[missing > 0].to_dict()

    # 4. Impute missing numeric values with column median
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # 5. Normalize numeric columns (Min-Max scaling) into new *_norm columns
    scaler = MinMaxScaler()
    norm_cols = [f"{c}_norm" for c in numeric_cols]
    df[norm_cols] = scaler.fit_transform(df[numeric_cols])

    report["numeric_columns_normalized"] = numeric_cols
    report["rows_after_preprocessing"] = len(df)

    return df, report


if __name__ == "__main__":
    from ingest import ingest_data

    raw = ingest_data()
    processed, rep = preprocess_data(raw)
    print("Missing values found:", rep["missing_values"])
    print("Columns normalized:", rep["numeric_columns_normalized"])
    print(processed.head())
