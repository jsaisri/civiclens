"""
CivicLens Data Cleaning Script
--------------------------------
Reads a raw CSV/Excel upload, applies validation and cleaning rules,
and returns a cleaned DataFrame ready for database ingestion.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_file(filepath: str) -> pd.DataFrame:
    """Load a CSV or Excel file into a DataFrame."""
    path = Path(filepath)
    if path.suffix == ".csv":
        return pd.read_csv(filepath)
    elif path.suffix in (".xlsx", ".xls"):
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def clean_dataframe(df: pd.DataFrame) -> dict:
    """
    Apply cleaning rules and return a result dict with:
      - cleaned_df: the cleaned DataFrame
      - report: summary of issues found and fixed
    """
    report = {
        "original_rows": len(df),
        "duplicates_removed": 0,
        "nulls_filled": 0,
        "type_fixes": [],
        "flagged_rows": [],
    }

    # 1. Strip whitespace from column names and string columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # 2. Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = before - len(df)

    # 3. Parse date columns
    for col in df.columns:
        if "date" in col:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                report["type_fixes"].append(f"Parsed '{col}' as datetime")
            except Exception:
                pass

    # 4. Fill numeric nulls with 0 and track count
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    null_count = df[numeric_cols].isnull().sum().sum()
    df[numeric_cols] = df[numeric_cols].fillna(0)
    report["nulls_filled"] = int(null_count)

    # 5. Flag rows with remaining nulls
    null_rows = df[df.isnull().any(axis=1)].index.tolist()
    report["flagged_rows"] = null_rows

    report["cleaned_rows"] = len(df)
    return {"cleaned_df": df, "report": report}


def summarize(df: pd.DataFrame) -> dict:
    """Return descriptive statistics for use in Claude prompts."""
    summary = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "date_range": None,
        "numeric_summary": {},
    }

    for col in df.columns:
        if "date" in col and pd.api.types.is_datetime64_any_dtype(df[col]):
            summary["date_range"] = {
                "start": str(df[col].min()),
                "end": str(df[col].max()),
            }

    for col in df.select_dtypes(include=[np.number]).columns:
        summary["numeric_summary"][col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": round(float(df[col].mean()), 2),
            "sum": float(df[col].sum()),
        }

    return summary


if __name__ == "__main__":
    sample_path = Path(__file__).parent.parent / "sample_data" / "sample_dataset.csv"
    df = load_file(str(sample_path))
    result = clean_dataframe(df)
    print("Cleaning report:", result["report"])
    print("\nSummary:", summarize(result["cleaned_df"]))
