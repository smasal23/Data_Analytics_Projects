from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils.config import load_project_configs
from src.utils.paths import find_project_root, resolve_project_path
from src.utils.io import ensure_dir, read_csv_file, save_csv_file, save_text_file
from src.utils.logger import get_logger
from src.data.clean_data import clean_diamonds_dataset
from src.data.load_data import load_external_reference_data

sns.set_theme(style = "whitegrid")


#
def load_feature_context(project_root: str | Path | None = None):
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    return {
        "project_root": root,
        "main_config": configs["main_config"],
        "paths_config": configs["paths_config"],
        "features_config": configs["features_config"],
        "regression_config": configs["regression_config"],
        "clustering_config": configs["clustering_config"]
    }


def load_feature_input_dataset(project_root: str | Path | None = None):
    logger = get_logger("src.features.build_features")
    ctx = load_feature_context(project_root)
    root = ctx["project_root"]

    processed_path = resolve_project_path(root, "data/processed/diamonds_processed.csv")
    if not Path(processed_path).exists():
        logger.info("Processed dataset missing. Running cleaning pipeline first.")
        clean_diamonds_dataset(root)

    return read_csv_file(processed_path)


def _extract_last_numeric_value(df: pd.DataFrame):
    candidate_columns = [
        "usd to inr",
        "exchange_rate",
        "rate",
        "inr_per_usd",
        "value"
    ]

    for col in candidate_columns:
        if col in df.columns:
            series = pd.to_numeric(df[col], errors = "coerce").dropna()
            if not series.empty:
                return float(series.iloc[-1])

    numeric_cols = df.select_dtypes(include = [np.number]).columns.tolist()
    if len(numeric_cols) == 1:
        series = pd.to_numeric(df[numeric_cols[0]], errors = "coerce").dropna()
        if not series.empty:
            return float(series.iloc[-1])

    flattened = pd.to_numeric(df.stack(), errors = "coerce").dropna()
    if not flattened.empty:
        return float(flattened.iloc[-1])

    raise ValueError("Could not infer USD to INR exchange rate from external reference file.")


#
def load_usd_inr_rate(project_root: str | Path | None = None):
    ctx = load_feature_context(project_root)
    main_cfg = ctx["main_config"]

    if not main_cfg["currency"]["enable_currency_reference"]:
        raise ValueError("Currency reference is disabled in config.")

    ref_df = load_external_reference_data(ctx["project_root"])
    return _extract_last_numeric_value(ref_df)


#
def safe_divide(numerator: pd.Series | np.ndarray, denominator: pd.Series | np.ndarray, fill_value: float | int | None = np.nan):
    numerator_s = pd.Series(numerator)
    denominator_s = pd.Series(denominator)
    result = np.divide(numerator_s, denominator_s, out = np.full(len(numerator_s), np.nan, dtype = float), where = (pd.to_numeric(denominator_s, errors = "coerce") != 0))

    result = pd.Series(result, index = numerator_s.index)

    if fill_value is not None:
        result = result.fillna(fill_value)

    return result


#
def create_carat_category(carat_series: pd.Series):
    bins = [0, 0.50, 1.00, 1.50, 2.50, np.inf]
    labels = ["small", "medium", "large", "very_large", "premium_large"]
    return pd.cut(carat_series, bins = bins, labels = labels, include_lowest = True, right = True).astype("object")


#
def add_engineered_features(df: pd.DataFrame, usd_inr_rate: float):
    required_cols = ["carat", "depth", "table", "price", "x", "y", "z"]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise KeyError(f"Missing required columns for feature engineering: {missing}")

    engineered = df.copy()

    engineered["price_inr"] = pd.to_numeric(engineered["price"], errors = "coerce") * float(usd_inr_rate)

    engineered["volume"] = (
        pd.to_numeric(engineered["x"], errors = "coerce")
        * pd.to_numeric(engineered["y"], errors = "coerce")
        * pd.to_numeric(engineered["z"], errors = "coerce")
    )

    engineered["volume_proxy"] = engineered["volume"]

    engineered["price_per_carat"] = safe_divide(
        pd.to_numeric(engineered["price"], errors = "coerce"),
        pd.to_numeric(engineered["carat"], errors = "coerce")
    )

    engineered["dimension_ratio"] = safe_divide(
        pd.to_numeric(engineered["x"], errors = "coerce") + pd.to_numeric(engineered["y"], errors = "coerce"),
        2 * pd.to_numeric(engineered["z"], errors = "coerce")
    )

    engineered["carat_category"] = create_carat_category(pd.to_numeric(engineered["carat"], errors = "coerce"))

    engineered["length_width_ratio"] = safe_divide(
        pd.to_numeric(engineered["x"], errors = "coerce"),
        pd.to_numeric(engineered["y"], errors = "coerce")
    )

    engineered["depth_pct_from_dimensions"] = safe_divide(
        2 * pd.to_numeric(engineered["z"], errors = "coerce"),
        pd.to_numeric(engineered["x"], errors = "coerce") + pd.to_numeric(engineered["y"], errors = "coerce")
    ) * 100

    engineered["table_depth_interaction"] = (
        pd.to_numeric(engineered["table"], errors="coerce") * pd.to_numeric(engineered["depth"], errors = "coerce")
    )

    engineered["carat_squared"] = pd.to_numeric(engineered["carat"], errors = "coerce") ** 2

    engineered["table_to_depth_ratio"] = safe_divide(
        pd.to_numeric(engineered["table"], errors="coerce"),
        pd.to_numeric(engineered["depth"], errors="coerce")
    )

    engineered["face_area"] = (
        pd.to_numeric(engineered["x"], errors="coerce") * pd.to_numeric(engineered["y"], errors = "coerce")
    )

    feature_doc = build_feature_documentation(usd_inr_rate = usd_inr_rate)

    return engineered, feature_doc


#
def build_feature_documentation(usd_inr_rate: float):
    rows = [
        {
            "feature": "price_inr",
            "feature_type": "engineered",
            "formula": f"price * {usd_inr_rate}",
            "reason": "Converts target price from USD to INR for business-facing interpretation and reporting.",
            "use_for_regression": False,
            "use_for_clustering": False,
            "notes": "Reporting-only target currency transformation.",
        },
        {
            "feature": "volume",
            "feature_type": "engineered",
            "formula": "x * y * z",
            "reason": "Captures a simple geometric size proxy from the 3 physical dimensions.",
            "use_for_regression": True,
            "use_for_clustering": True,
            "notes": "Equivalent to volume_proxy in current project naming.",
        },
        {
            "feature": "volume_proxy",
            "feature_type": "engineered",
            "formula": "x * y * z",
            "reason": "Keeps compatibility with existing project feature dictionary and clustering config.",
            "use_for_regression": True,
            "use_for_clustering": True,
            "notes": "Alias of volume.",
        },
        {
            "feature": "price_per_carat",
            "feature_type": "engineered",
            "formula": "price / carat",
            "reason": "Useful for descriptive pricing-efficiency analysis.",
            "use_for_regression": False,
            "use_for_clustering": False,
            "notes": "EDA-only because it is derived from the target.",
        },
        {
            "feature": "dimension_ratio",
            "feature_type": "engineered",
            "formula": "(x + y) / (2 * z)",
            "reason": "Summarizes average planar spread relative to depth.",
            "use_for_regression": True,
            "use_for_clustering": True,
            "notes": "Helpful proportion feature.",
        },
        {
            "feature": "carat_category",
            "feature_type": "engineered",
            "formula": "binned carat",
            "reason": "Captures non-linear price behavior by size band.",
            "use_for_regression": True,
            "use_for_clustering": True,
            "notes": "Categorical engineered feature.",
        },
        {
            "feature": "length_width_ratio",
            "feature_type": "engineered",
            "formula": "x / y",
            "reason": "Captures aspect ratio and shape variation.",
            "use_for_regression": True,
            "use_for_clustering": True,
            "notes": "Existing candidate feature from project docs.",
        },
        {
            "feature": "depth_pct_from_dimensions",
            "feature_type": "engineered",
            "formula": "(2 * z / (x + y)) * 100",
            "reason": "Provides alternate dimensional depth proportion.",
            "use_for_regression": True,
            "use_for_clustering": True,
            "notes": "Existing candidate feature from project docs.",
        },
        {
            "feature": "table_depth_interaction",
            "feature_type": "engineered",
            "formula": "table * depth",
            "reason": "Captures interaction between two proportion-related measurements.",
            "use_for_regression": True,
            "use_for_clustering": False,
            "notes": "More relevant for regression nonlinearity.",
        },
        {
            "feature": "carat_squared",
            "feature_type": "engineered",
            "formula": "carat ** 2",
            "reason": "Allows simple nonlinear effect of size.",
            "use_for_regression": True,
            "use_for_clustering": False,
            "notes": "Especially useful for linear baselines.",
        },
        {
            "feature": "table_to_depth_ratio",
            "feature_type": "engineered",
            "formula": "table / depth",
            "reason": "Summarizes relative top-width proportion against depth.",
            "use_for_regression": True,
            "use_for_clustering": True,
            "notes": "Additional interpretable ratio feature.",
        },
        {
            "feature": "face_area",
            "feature_type": "engineered",
            "formula": "x * y",
            "reason": "Represents top-view spread independent of full depth.",
            "use_for_regression": True,
            "use_for_clustering": True,
            "notes": "Additional geometric feature.",
        },
    ]
    return pd.DataFrame(rows)


#
def plot_engineered_feature_distributions(
    df: pd.DataFrame,
    output_path: str | Path,
    columns: list[str] | None = None,
):
    if columns is None:
        columns = [
            "volume",
            "price_per_carat",
            "dimension_ratio",
            "length_width_ratio",
            "depth_pct_from_dimensions",
            "carat_squared",
        ]

    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    valid_cols = [col for col in columns if col in df.columns]
    n_cols = 3
    n_rows = int(np.ceil(len(valid_cols) / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize = (18, 4.5 * n_rows))
    axes = np.array(axes).reshape(-1)

    for idx, col in enumerate(valid_cols):
        sns.histplot(df[col].dropna(), kde = True, bins = 40, ax = axes[idx])
        axes[idx].set_title(f"Distribution - {col}")
        axes[idx].set_xlabel(col)

    for idx in range(len(valid_cols), len(axes)):
        axes[idx].axis("off")

    fig.suptitle("Engineered Feature Distributions", y=1.02)
    fig.tight_layout()
    fig.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close(fig)
    return output_path


#
def build_feature_engineering_report(
    df: pd.DataFrame,
    feature_doc_df: pd.DataFrame,
    usd_inr_rate: float,
    selected_regression_features: list[str] | None = None,
    selected_clustering_features: list[str] | None = None,
):
    selected_regression_features = selected_regression_features or []
    selected_clustering_features = selected_clustering_features or []

    summary_cols = [
        col for col in [
            "volume",
            "price_per_carat",
            "dimension_ratio",
            "carat_category",
            "length_width_ratio",
            "depth_pct_from_dimensions",
            "table_depth_interaction",
            "carat_squared",
            "table_to_depth_ratio",
            "face_area",
        ] if col in df.columns
    ]

    summary_df = df[summary_cols].describe(include = "all").transpose()

    report_text = f"""# Feature Engineering Report0

    ## 1. Phase Summary
    - Input dataset shape: `{df.shape[0]} rows × {df.shape[1]} columns`
    - USD to INR exchange rate used: `{usd_inr_rate}`
    - Target column: `price`
    
    ## 2. Engineered Feature Documentation
    {feature_doc_df.to_markdown(index = False)}
    
    ## 3. Engineered Feature Summary
    {summary_df.to_markdown()}
    
    ## 4. Modeling Rules
    - `price_per_carat` is retained for analysis only and excluded from regression/clustering inputs.
    - `price_inr` is retained for reporting only and excluded from regression/clustering inputs.
    - Clustering-ready dataset excludes `price` as requested for the deliverable.
    
    ## 5. Final Regression Features
    `{selected_regression_features}`
    
    ## 6. Final Clustering Features
    `{selected_clustering_features}`
    
    ## 7. Saved Outputs
    - `data/processed/diamonds_feature_engineered.csv`
    - `data/processed/regression_model_input.csv`
    - `data/processed/clustering_model_input.csv`
    - `figures/feature_engineering/engineered_feature_distributions.png`
    - `figures/feature_engineering/feature_importance_baseline.png`
    - `figures/feature_engineering/correlation_selected_features.png`
    - `figures/feature_engineering/vif_summary_plot.png`
    """
    return report_text


#
def save_feature_engineered_dataset(
    df: pd.DataFrame,
    project_root: str | Path | None = None,
):
    ctx = load_feature_context(project_root)
    root = ctx["project_root"]
    output_path = resolve_project_path(root, "data/processed/diamonds_feature_engineered.csv")
    return save_csv_file(df, output_path, index = False)