from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder
from statsmodels.stats.outliers_influence import variance_inflation_factor

from src.utils.io import ensure_dir

sns.set_theme(style = "whitegrid")

eda_only_features = ["price_per_carat", "price_inr"]


#
def _prepare_baseline_encoded_frame(df: pd.DataFrame, feature_cols: list[str], categorical_cols: list[str]):
    X = df[feature_cols].copy()

    present_cats = [col for col in categorical_cols if col in X.columns]
    if present_cats:
        encoder = OrdinalEncoder(handle_unknown = "use_encoded_value", unknown_value = -1)
        X[present_cats] = encoder.fit_transform(X[present_cats].astype(str))

    for col in X.columns:
        if X[col].dtype == "object":
            X[col] = X[col].astype("category").cat.codes

    return X


#
def compute_regression_feature_importance(
        df: pd.DataFrame,
        feature_cols: list[str],
        target_col: str = "price",
        categorical_cols: list[str] | None = None,
        random_state: int = 42,
        n_estimators: int = 300
):
    categorical_cols = categorical_cols or []

    if target_col not in df.columns:
        raise KeyError(f"{target_col} not present in dataframe.")

    candidate_features = [col for col in feature_cols if col in df.columns and col not in eda_only_features]
    X = _prepare_baseline_encoded_frame(df, candidate_features, categorical_cols)
    y = pd.to_numeric(df[target_col], errors = "coerce")

    working = pd.concat([X, y.rename(target_col)], axis = 1).dropna()
    X_clean = working[candidate_features]
    y_clean = working[target_col]

    model = RandomForestRegressor(n_estimators = n_estimators, random_state = random_state, n_jobs = -1)
    model.fit(X_clean, y_clean)

    importance_df = pd.DataFrame({
        "feature": candidate_features,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending = False).reset_index(drop = True)

    importance_df["importance_rank"] = np.arange(1, len(importance_df) + 1)

    return importance_df


#
def plot_feature_importance(
    importance_df: pd.DataFrame,
    output_path: str | Path,
    top_n: int = 15,
):
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    plot_df = importance_df.head(top_n).sort_values("importance", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(plot_df["feature"], plot_df["importance"])
    plt.title("Baseline Random Forest Feature Importance")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close()

    return output_path


#
def identify_high_correlation_pairs(df: pd.DataFrame, columns: list[str], threshold: float = 0.90):
    numeric_cols = [col for col in columns if col in df.columns]
    corr = df[numeric_cols].corr(numeric_only=True).abs()

    rows: list[dict[str, Any]] = []
    for i, col_i in enumerate(corr.columns):
        for j, col_j in enumerate(corr.columns):
            if j <= i:
                continue
            corr_val = corr.iloc[i, j]
            if pd.notna(corr_val) and corr_val >= threshold:
                rows.append({
                    "feature_1": col_i,
                    "feature_2": col_j,
                    "abs_correlation": float(corr_val),
                })

    return pd.DataFrame(rows).sort_values("abs_correlation", ascending=False).reset_index(drop=True)


#
def compute_vif_table(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    numeric_cols = [col for col in columns if col in df.columns]
    if len(numeric_cols) == 0:
        return pd.DataFrame(columns=["feature", "vif"])

    numeric_df = df[numeric_cols].copy()
    numeric_df = numeric_df.apply(pd.to_numeric, errors="coerce").dropna()

    if numeric_df.empty:
        return pd.DataFrame(columns=["feature", "vif"])

    # VIF is not meaningful for a single predictor
    if numeric_df.shape[1] == 1:
        return pd.DataFrame({
            "feature": numeric_df.columns,
            "vif": [1.0],
        })

    vif_rows = []
    values = numeric_df.values

    for idx, col in enumerate(numeric_df.columns):
        vif_rows.append({
            "feature": col,
            "vif": float(variance_inflation_factor(values, idx)),
        })

    return (
        pd.DataFrame(vif_rows)
        .sort_values("vif", ascending=False)
        .reset_index(drop=True)
    )


#
def plot_vif_summary(vif_df: pd.DataFrame, output_path: str | Path):
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    plot_df = vif_df.sort_values("vif", ascending = True)

    plt.figure(figsize = (10, 6))
    plt.barh(plot_df["feature"], plot_df["vif"])
    plt.axvline(5, linestyle = "--", linewidth=1)
    plt.axvline(10, linestyle = "--", linewidth=1)
    plt.title("VIF Summary")
    plt.xlabel("VIF")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()
    return output_path


def plot_correlation_heatmap_for_selected(
    df: pd.DataFrame,
    columns: list[str],
    output_path: str | Path,
):
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    corr = df[columns].corr(numeric_only = True)

    plt.figure(figsize = (10, 8))
    sns.heatmap(corr, annot = True, fmt = ".2f", cmap = "coolwarm", square = True)
    plt.title("Correlation Heatmap - Selected Numeric Features")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()
    return output_path


def _resolve_redundant_features(
        correlation_pairs_df: pd.DataFrame,
        importance_df: pd.DataFrame,
):
    importance_map = dict(zip(importance_df["feature"], importance_df["importance"]))
    features_to_drop: set[str] = set()

    for _, row in correlation_pairs_df.iterrows():
        f1 = row["feature_1"]
        f2 = row["feature_2"]

        if f1 in features_to_drop or f2 in features_to_drop:
            continue

        i1 = importance_map.get(f1, 0.0)
        i2 = importance_map.get(f2, 0.0)

        if i1 >= i2:
            features_to_drop.add(f2)
        else:
            features_to_drop.add(f1)

    return features_to_drop


#
def select_regression_features(
        df: pd.DataFrame,
        raw_numeric_cols: list[str],
        raw_categorical_cols: list[str],
        engineered_numeric_cols: list[str],
        engineered_categorical_cols: list[str],
        target_col: str = "price",
        importance_threshold: float = 0.01,
        corr_threshold: float = 0.90,
        vif_threshold: float = 10.0,
        random_state: int = 42,
):
    candidate_features = (
        raw_numeric_cols
        + raw_categorical_cols
        + engineered_numeric_cols
        + engineered_categorical_cols
    )
    candidate_features = [col for col in candidate_features if col in df.columns and col not in eda_only_features]

    importance_df = compute_regression_feature_importance(
        df = df,
        feature_cols = candidate_features,
        target_col = target_col,
        categorical_cols = raw_categorical_cols + engineered_categorical_cols,
        random_state = random_state,
    )

    important_features = importance_df.loc[
        importance_df["importance"] >= importance_threshold, "feature"].tolist()

    numeric_candidates = [
        col for col in important_features
        if col in (raw_numeric_cols + engineered_numeric_cols)
    ]

    correlation_pairs_df = identify_high_correlation_pairs(
        df = df,
        columns = numeric_candidates,
        threshold = corr_threshold,
    )

    redundant_features = _resolve_redundant_features(
        correlation_pairs_df = correlation_pairs_df,
        importance_df = importance_df,
    )

    kept_numeric = [col for col in numeric_candidates if col not in redundant_features]

    if len(kept_numeric) == 0 and len(numeric_candidates) > 0:
        # fallback: keep the most important numeric feature
        numeric_importance_df = importance_df[importance_df["feature"].isin(numeric_candidates)]
        kept_numeric = numeric_importance_df.head(1)["feature"].tolist()

    vif_df = compute_vif_table(df, kept_numeric)

    if vif_df.empty:
        high_vif_features = []
    else:
        high_vif_features = vif_df.loc[vif_df["vif"] > vif_threshold, "feature"].tolist()

    final_numeric = [col for col in kept_numeric if col not in high_vif_features]

    if len(final_numeric) == 0 and len(kept_numeric) > 0:
        final_numeric = kept_numeric.copy()

    final_categorical = [
        col for col in important_features
        if col in (raw_categorical_cols + engineered_categorical_cols)
    ]

    # Ensure core predictors survive if importance threshold is too aggressive.
    for core_col in ["carat", "cut", "color", "clarity", "depth", "table"]:
        if core_col in candidate_features and core_col not in final_numeric + final_categorical:
            if core_col in raw_categorical_cols:
                final_categorical.append(core_col)
            else:
                final_numeric.append(core_col)

    final_features = final_numeric + final_categorical

    return {
        "importance_df": importance_df,
        "correlation_pairs_df": correlation_pairs_df,
        "vif_df": vif_df,
        "redundant_features": sorted(redundant_features.union(high_vif_features)),
        "selected_numeric_features": final_numeric,
        "selected_categorical_features": final_categorical,
        "selected_features": final_features,
    }


#
def select_clustering_features(
        df: pd.DataFrame,
        raw_numeric_cols: list[str],
        raw_categorical_cols: list[str],
        engineered_numeric_cols: list[str],
        engineered_categorical_cols: list[str],
        corr_threshold: float = 0.90,
):
    numeric_candidates = [
        col for col in (
                raw_numeric_cols
                + engineered_numeric_cols
        )
        if col in df.columns and col not in {"price", "price_inr", "price_per_carat"}
    ]

    correlation_pairs_df = identify_high_correlation_pairs(
        df = df,
        columns = numeric_candidates,
        threshold = corr_threshold,
    )

    # No target available, so use a stable domain priority.
    domain_priority = [
        "carat",
        "depth",
        "table",
        "volume",
        "volume_proxy",
        "dimension_ratio",
        "length_width_ratio",
        "depth_pct_from_dimensions",
        "face_area",
        "table_to_depth_ratio",
        "x",
        "y",
        "z",
        "table_depth_interaction",
        "carat_squared",
    ]

    priority_rank = {feat: idx for idx, feat in enumerate(domain_priority)}
    redundant_features: set[str] = set()

    for _, row in correlation_pairs_df.iterrows():
        f1 = row["feature_1"]
        f2 = row["feature_2"]
        if f1 in redundant_features or f2 in redundant_features:
            continue

        r1 = priority_rank.get(f1, 999)
        r2 = priority_rank.get(f2, 999)

        if r1 <= r2:
            redundant_features.add(f2)
        else:
            redundant_features.add(f1)

    selected_numeric = [col for col in numeric_candidates if col not in redundant_features]

    selected_categorical = [
        col for col in (raw_categorical_cols + engineered_categorical_cols)
        if col in df.columns and col not in {"carat_category"}  # keep clustering simpler and cleaner
    ]

    selected_features = selected_numeric + selected_categorical

    return {
        "correlation_pairs_df": correlation_pairs_df,
        "redundant_features": sorted(redundant_features),
        "selected_numeric_features": selected_numeric,
        "selected_categorical_features": selected_categorical,
        "selected_features": selected_features,
    }