# Import
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame


# Check whether target column exists in the dataframe
def check_target_present(df: pd.DataFrame, target_col: str):
    return target_col in df.columns


# Return required columns that are missing from the dataframe.
def get_missing_required_columns(df: pd.DataFrame, required_columns: list[str]):
    return [col for col in required_columns if col not in df.columns]


# Return columns present in the dataframe that are not part of the expected schema.
def get_unexpected_columns(df: pd.DataFrame, expected_columns: list[str]):
    return [col for col in df.columns if col not in expected_columns]


# Count duplicate rows in the dataframe
def count_duplicates(df: pd.DataFrame):
    return int(df.duplicated().sum())


# Build a missing value summary table
def build_missing_summary(df: DataFrame):
    summary = pd.DataFrame({
        "column": df.columns,
        "missing_count": df.isna().sum().values,
        "missing_pct": (df.isna().mean() * 100).round(3).values
    })

    return summary.sort_values(
        by = ["missing_count", "column"],
        ascending = [False, True]
    ).reset_index(drop = True)


# Build an initial column level review table
def build_column_summary(df: pd.DataFrame):
    return pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.astype(str).values,
        "non null_count": df.notna().sum().values,
        "null_count": df.isna().sum().values,
        "null_pct": (df.isna().mean() * 100).round(3).values,
        "n_unique": df.nunique(dropna = True).values,
        "sample_values": [list(df[col].dropna().astype(str).head(3).values) for col in df.columns]
    })


# Build a compact dataset summary dictionary for JSON/reporting use.
def build_dataset_summary(df: pd.DataFrame, target_col: str, required_columns: list[str], expected_columns: list[str] | None = None):
    if expected_columns is None:
        expected_columns = required_columns

    return {
        "shape": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1])
        },
        "columns": df.columns.tolist(),
        "target_present": check_target_present(df, target_col),
        "missing_required_columns": get_missing_required_columns(df, required_columns),
        "unexpected_columns": get_unexpected_columns(df, expected_columns),
        "duplicate_rows": count_duplicates(df),
        "dtypes": df.dtypes.astype(str).to_dict()
    }
