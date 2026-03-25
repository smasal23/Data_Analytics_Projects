# Imports
from __future__ import annotations

from pathlib import Path
import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.utils.config import load_project_configs
from src.utils.paths import find_project_root, resolve_project_path
from src.utils.io import save_csv_file, save_text_file, ensure_dir
from src.utils.logger import get_logger
from src.data.load_data import load_raw_dataset
from src.data.validate_data import build_missing_summary, build_dataset_summary, get_unexpected_columns


def _get_logger():
    return get_logger(name = "src.data.clean_data", level = logging.INFO)


# Load project root and all configs needed for cleaning
def load_cleaning_context(project_root: str | Path | None = None):
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    return {
        "project_root": root,
        "configs": configs,
        "main_config": configs["main_config"],
        "paths_config": configs["paths_config"],
        "features_config": configs["features_config"],
        "regression_config": configs["regression_config"],
        "clustering_config": configs["clustering_config"]
    }


def get_schema_details(features_config: dict):
    schema = features_config["schema"]
    validation_rules = features_config["validation_rules"]
    preprocessing_cfg = features_config["preprocessing"]

    return {
        "target_col": schema["target"],
        "numeric_cols": schema["numeric_features"],
        "categorical_cols": schema["categorical_features"],
        "required_columns": schema["required_columns"],
        "expected_columns": schema["all_expected_features"],
        "strictly_positive_columns": validation_rules["strictly_positive_columns"],
        "dimension_columns": validation_rules["dimension_columns"],
        "suspicious_zero_check_columns": validation_rules["suspicious_zero_check_columns"],
        "missing_strategy": preprocessing_cfg["missing_value_strategy"]
    }


# Build all cleaning diagnostics required for reporting
def detect_missing_and_invalid_values(
    df: pd.DataFrame,
    numeric_cols: list[str],
    categorical_cols: list[str],
    target_col: str,
    dimension_cols: list[str],
):
    missing_summary = build_missing_summary(df)

    zero_xyz_summary = pd.DataFrame({
        "column": dimension_cols,
        "zero_count": [int((df[col] == 0).sum()) for col in dimension_cols],
        "zero_pct": [round((df[col] == 0).mean() * 100, 4) for col in dimension_cols],
    })

    impossible_numeric_summary = pd.DataFrame({
        "column": numeric_cols + [target_col],
        "non_positive_count": [
            int((df[col] <= 0).sum()) if col in df.columns else 0
            for col in numeric_cols + [target_col]
        ],
        "negative_count": [
            int((df[col] < 0).sum()) if col in df.columns else 0
            for col in numeric_cols + [target_col]
        ],
    })

    return {
        "missing_summary": missing_summary,
        "zero_xyz_summary": zero_xyz_summary,
        "impossible_numeric_summary": impossible_numeric_summary,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
    }


# Drop only unexpected/irrelevant columns.If the incoming dataset already matches schema, nothing is dropped.
def decide_columns_to_drop(df: pd.DataFrame, expected_columns: list[str]):
    unexpected_cols = get_unexpected_columns(df, expected_columns)
    return unexpected_cols


# Replace impossible dimension values with NaN.
def mark_invalid_xyz_as_missing(df: pd.DataFrame, dimension_cols: list[str]):
    cleaned = df.copy()

    for col in dimension_cols:
        cleaned[col] = cleaned[col].mask(cleaned[col] <= 0, np.nan)

    return cleaned


# Remove rows where core strictly-positive fields are invalid.
def remove_impossible_core_rows(df: pd.DataFrame, strictly_positive_columns: list[str]):
    cleaned = df.copy()

    invalid_mask = pd.Series(False, index = cleaned.index)
    for col in strictly_positive_columns:
        invalid_mask = invalid_mask | (cleaned[col] <= 0)

    removed_rows = cleaned.loc[invalid_mask].copy()
    kept_rows = cleaned.loc[~invalid_mask].copy()

    return kept_rows, removed_rows


# Lightweight dataset-level imputation for creation of cleaned interim/processed data.
def impute_missing_values(df: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str], numeric_strategy: str = "median", categorical_strategy: str = "most_frequent"):
    cleaned = df.copy()
    imputation_values: dict[str, object] = {}

    if numeric_strategy != "median":
        raise ValueError(f"Unsupported numeric strategy: {numeric_strategy}")

    if categorical_strategy != "most_frequent":
        raise ValueError(f"Unsupported categorical strategy: {categorical_strategy}")

    for col in numeric_cols:
        fill_value = cleaned[col].median()
        cleaned[col] = cleaned[col].fillna(fill_value)
        imputation_values[col] = float(fill_value) if pd.notna(fill_value) else None

    for col in categorical_cols:
        mode_series = cleaned[col].mode(dropna = True)
        fill_value = mode_series.iloc[0] if not mode_series.empty else "Unknown"
        cleaned[col] = cleaned[col].fillna(fill_value)
        imputation_values[col] = fill_value

    return cleaned, imputation_values


# Plot missing values by column
def create_missing_values_figure(missing_summary: pd.DataFrame, output_path: str | Path):
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    plot_df = missing_summary.loc[missing_summary["missing_count"] > 0].copy()

    plt.figure(figsize = (10, 5))
    if plot_df.empty:
        plt.text(0.5, 0.5, "No missing values detected", ha = "center", va = "center")
        plt.axis("off")
    else:
        plt.bar(plot_df["column"], plot_df["missing_count"])
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Missing Count")
        plt.title("Missing Values Summary")
        plt.tight_layout()

    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()
    return output_path


# Plot zero-value counts for x/y/z.
def create_invalid_xyz_figure(zero_xyz_summary: pd.DataFrame, output_path: str | Path):
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    plt.figure(figsize=(8, 5))
    plt.bar(zero_xyz_summary["column"], zero_xyz_summary["zero_count"])
    plt.ylabel("Zero Count")
    plt.title("Invalid x/y/z Zero Value Analysis")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()

    return output_path


#  Markdown report for this phase.
def build_preprocessing_report(
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    missing_summary_before: pd.DataFrame,
    missing_summary_after: pd.DataFrame,
    zero_xyz_summary: pd.DataFrame,
    impossible_numeric_summary: pd.DataFrame,
    dropped_columns: list[str],
    removed_row_count: int,
    numeric_cols: list[str],
    categorical_cols: list[str],
    imputation_values: dict,
):
    dropped_columns_text = dropped_columns if dropped_columns else "None"

    report_text = f"""# Preprocessing Report

    ## 1. Dataset Snapshot
    - Raw shape: `{raw_df.shape[0]} rows × {raw_df.shape[1]} columns`
    - Cleaned shape: `{cleaned_df.shape[0]} rows × {cleaned_df.shape[1]} columns`
    - Rows removed due to impossible core values (`carat <= 0` or `price <= 0`): `{removed_row_count}`
    - Dropped unexpected columns: `{dropped_columns_text}`
    
    ## 2. Missing Value Review
    {missing_summary_before.to_markdown(index=False)}
    
    ### Missing values after cleaning/imputation
    {missing_summary_after.to_markdown(index=False)}
    
    ## 3. Invalid x, y, z Review
    - Rule applied: `x`, `y`, `z` values of 0 or negative are treated as invalid and converted to null before imputation.
    
    {zero_xyz_summary.to_markdown(index=False)}
    
    ## 4. Impossible Numeric Values
    - Rule applied:
      - `carat <= 0` -> row removed
      - `price <= 0` -> row removed
      - invalid `x`, `y`, `z` -> set to null, then imputed
    
    {impossible_numeric_summary.to_markdown(index=False)}
    
    ## 5. Column Separation
    - Numeric columns: `{numeric_cols}`
    - Categorical columns: `{categorical_cols}`
    
    ## 6. Preprocessing Strategy
    - Numeric missing value strategy: `median`
    - Categorical missing value strategy: `most_frequent`
    - Categorical encoding for downstream modeling: `onehot` for regression; `ordinal` for clustering
    - Numeric scaling for downstream modeling: `standard` where required by model family
    
    ## 7. Dataset-level Imputation Values Used
    ```python
    {imputation_values}
    """
    return report_text
    
    
#  End-to-end cleaning pipeline for the diamond dataset.
def clean_diamonds_dataset(project_root: str | Path | None = None):
    logger = get_logger()
    ctx = load_cleaning_context(project_root)
    root = ctx["project_root"]
    paths_cfg = ctx["paths_config"]
    features_cfg = ctx["features_config"]

    schema = get_schema_details(features_cfg)

    logger.info("Loading raw dataset...")
    raw_df = load_raw_dataset(root)

    logger.info("Building initial diagnostics...")
    initial_diagnostics = detect_missing_and_invalid_values(
        df = raw_df,
        numeric_cols = schema["numeric_cols"],
        categorical_cols = schema["categorical_cols"],
        target_col = schema["target_col"],
        dimension_cols = schema["dimension_columns"]
    )

    dropped_columns = decide_columns_to_drop(raw_df, schema["expected_columns"])
    working_df = raw_df.drop(columns = dropped_columns, errors = "ignore").copy()

    logger.info("Marking invalid x/y/z values are missing...")
    working_df = mark_invalid_xyz_as_missing(working_df, schema["dimension_columns"])

    logger.info("Removing impossible core rows...")
    working_df, removed_rows_df = remove_impossible_core_rows(
        working_df,
        schema["strictly_positive_columns"],
    )

    logger.info("Imputing remaining missing values...")
    cleaned_df, imputation_values = impute_missing_values(
        df = working_df,
        numeric_cols = schema["numeric_cols"],
        categorical_cols = schema["categorical_cols"],
        numeric_strategy = schema["missing_strategy"]["numeric"],
        categorical_strategy = schema["missing_strategy"]["categorical"]
    )

    missing_summary_after = build_missing_summary(cleaned_df)
    dataset_summary = build_dataset_summary(
        cleaned_df,
        target_col = schema["target_col"],
        required_columns = schema["required_columns"],
        expected_columns = schema["expected_columns"],
    )

    interim_output = resolve_project_path(root, "data/interim/diamonds_cleaned.csv")
    processed_output = resolve_project_path(root, "data/processed/diamonds_processed.csv")
    report_output = resolve_project_path(root, "reports/processing_report.md")
    missing_fig_output = resolve_project_path(root, "figures/preprocessing/missing_values_summary.png")
    invalid_xyz_fig_output = resolve_project_path(root, "figures/preprocessing/invalid_xyz_analysis.png")

    logger.info("Saving figures...")
    create_missing_values_figure(initial_diagnostics["missing_summary"], missing_fig_output)
    create_invalid_xyz_figure(initial_diagnostics["zero_xyz_summary"], invalid_xyz_fig_output)

    logger.info("Saving markdown report...")
    report_text = build_preprocessing_report(
        raw_df = raw_df,
        cleaned_df = cleaned_df,
        missing_summary_before = initial_diagnostics["missing_summary"],
        missing_summary_after = missing_summary_after,
        zero_xyz_summary = initial_diagnostics["zero_xyz_summary"],
        impossible_numeric_summary = initial_diagnostics["impossible_numeric_summary"],
        dropped_columns = dropped_columns,
        removed_row_count = len(removed_rows_df),
        numeric_cols = schema["numeric_cols"],
        categorical_cols = schema["categorical_cols"],
        imputation_values = imputation_values,
    )
    save_text_file(report_text, report_output)

    logger.info("Saving cleaned datasets...")
    save_csv_file(cleaned_df, interim_output, index=False)
    save_csv_file(cleaned_df, processed_output, index=False)

    return {
        "raw_df": raw_df,
        "cleaned_df": cleaned_df,
        "removed_rows_df": removed_rows_df,
        "missing_summary_before": initial_diagnostics["missing_summary"],
        "missing_summary_after": missing_summary_after,
        "zero_xyz_summary": initial_diagnostics["zero_xyz_summary"],
        "impossible_numeric_summary": initial_diagnostics["impossible_numeric_summary"],
        "dataset_summary": dataset_summary,
        "numeric_cols": schema["numeric_cols"],
        "categorical_cols": schema["categorical_cols"],
        "dropped_columns": dropped_columns,
        "imputation_values": imputation_values,
        "interim_output": interim_output,
        "processed_output": processed_output,
        "report_output": report_output,
        "missing_fig_output": missing_fig_output,
        "invalid_xyz_fig_output": invalid_xyz_fig_output,
    }

if __name__ == "__main__":
    results = clean_diamonds_dataset()
    print("Cleaning completed successfully")
    print(f"Cleaned dataset saved to: {results['processed_output']}")