
import pandas as pd
import numpy as np


def load_data(file):
    """Load CSV or Excel data and normalize column names."""
    if hasattr(file, "name"):
        filename = file.name.lower()
    else:
        filename = str(file).lower()

    if filename.endswith(".csv"):
        df = pd.read_csv(file)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        raise ValueError("Upload a CSV or Excel file.")

    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    df.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    if not df.columns.is_unique:
        raise ValueError("Column names must be unique.")

    return df


def profile_data(df):
    """Return basic data-quality statistics."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "duplicates": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "missing_by_column": df.isna().sum(),
        "dtypes": df.dtypes.astype(str),
        "numeric_columns": df.select_dtypes(
            include=np.number
        ).columns.tolist(),
        "categorical_columns": df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist(),
    }


def prepare_dates(df):
    """Convert likely date columns when parsing is successful."""
    result = df.copy()

    for col in result.columns:
        if "date" in col or col.endswith("_at"):
            parsed = pd.to_datetime(
                result[col], errors="coerce"
            )
            if parsed.notna().any():
                result[col] = parsed

    return result


def numeric_summary(df):
    """Summarize all numeric columns."""
    numeric = df.select_dtypes(include=np.number)
    if numeric.empty:
        return pd.DataFrame()
    return numeric.describe().T.round(2)































