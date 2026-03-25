from __future__ import annotations

from typing import Callable
import numpy as np
import pandas as pd
from scipy import stats


#
def compute_iqr_bounds(series: pd.Series, whisker_width: float = 1.5):
    clean = pd.to_numeric(series, errors = "coerce").dropna()

    if clean.empty:
        return {
            "q1": np.nan,
            "q3": np.nan,
            "iqr": np.nan,
            "lower_bound": np.nan,
            "upper_bound": np.nan
        }

    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - (whisker_width * iqr)
    upper_bound = q3 + (whisker_width * iqr)

    return {
        "q1": float(q1),
        "q3": float(q3),
        "iqr":float(iqr),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound)
    }


#
def count_iqr_outliers(series: pd.Series, whisker_width: float = 1.5):
    bounds = compute_iqr_bounds(series, whisker_width = whisker_width)
    clean = pd.to_numeric(series, errors="coerce").dropna()

    if clean.empty:
        return 0

    mask = (clean < bounds["lower_bound"]) | (clean > bounds["upper_bound"])
    return int(mask.sum())


#
def build_outlier_summary(df: pd.DataFrame, columns: list[str], whisker_width: float = 1.5):
    rows: list[dict] = []

    for col in columns:
        series = pd.to_numeric(df[col], errors = "coerce")
        bounds = compute_iqr_bounds(series, whisker_width = whisker_width)
        outlier_count = count_iqr_outliers(series, whisker_width = whisker_width)
        non_null_count = int(series.notna().sum())
        outlier_pct = (outlier_count / non_null_count * 100) if non_null_count else 0.0

        rows.append(
            {
                "column": col,
                "non_null_count": non_null_count,
                "q1": bounds["q1"],
                "q3": bounds["q3"],
                "iqr": bounds["iqr"],
                "lower_bound": bounds["lower_bound"],
                "upper_bound": bounds["upper_bound"],
                "outlier_count": outlier_count,
                "outlier_pct": round(outlier_pct, 4)
            }
        )

    return pd.DataFrame(rows)


#
def clip_outliers_iqr(df: pd.DataFrame, columns: list[str], whisker_width: float = 1.5):
    clipped_df = df.copy()
    bounds_rows: list[dict] = []

    for col in columns:
        bounds = compute_iqr_bounds(clipped_df[col], whisker_width = whisker_width)
        lower_bound = bounds["lower_bound"]
        upper_bound = bounds["upper_bound"]

        clipped_df[col] = pd.to_numeric(clipped_df[col], errors = "coerce").clip(lower = lower_bound, upper = upper_bound)

        bounds_rows.append(
            {
                "column": col,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound
            }
        )

    return clipped_df, pd.DataFrame(bounds_rows)


#
def compute_skewness_table(df: pd.DataFrame, columns: list[str]):
    rows: list[dict] = []

    for col in columns:
        series = pd.to_numeric(df[col], errors = "coerce")
        skew_val = series.dropna().skew()

        rows.append(
            {
                "column": col,
                "skewness": float(skew_val) if pd.notna(skew_val) else np.nan,
                "abs_skewness": float(abs(skew_val)) if pd.notna(skew_val) else np.nan
            }
        )

    result = pd.DataFrame(rows).sort_values("abs_skewness", ascending = False).reset_index(drop = True)
    return result


#
def find_high_skew_columns(skewness_df: pd.DataFrame, threshold: float = 1.0):
    mask = skewness_df["abs_skewness"] > threshold
    return skewness_df.loc[mask, "column"].tolist()


#
def _safe_log1p(series: pd.Series):
    clean = pd.to_numeric(series, errors = "coerce")

    if clean.dropna().min() <= 1:
        return pd.Series(np.nan, index = clean.index)

    return np.log1p(clean)


#
def _safe_sqrt(series: pd.Series):
    clean = pd.to_numeric(series, errors = "coerce")

    if clean.dropna().min() < 0:
        return pd.Series(np.nan, index = clean.index)

    return np.sqrt(clean)


#
def _safe_boxcox(series: pd.Series):
    clean = pd.to_numeric(series, errors = "coerce")
    non_null = clean.dropna()

    if non_null.empty or (non_null <= 0).any():
        return pd.Series(np.nan, index = clean.index), None

    transformed_values, lam = stats.boxcox(non_null.values)
    transformed = pd.Series(np.nan, index = clean.index, dtype = float)
    transformed.loc[non_null.index] = transformed_values

    return transformed, float(lam)


#
def evaluate_skew_transforms(df: pd.DataFrame, columns: list[str]):
    rows: list[dict] = []

    for col in columns:
        original = pd.to_numeric(df[col], errors = "coerce")
        original_skew = original.dropna().skew()

        log_series = _safe_log1p(original)
        sqrt_series = _safe_sqrt(original)
        boxcox_series, lam = _safe_boxcox(original)

        candidate_scores = {
            "none": abs(original_skew) if pd.notna(original_skew) else np.inf,
            "log1p": abs(log_series.dropna().skew()) if log_series.notna().any() else np.inf,
            "sqrt": abs(sqrt_series.dropna().skew()) if sqrt_series.notna().any() else np.inf,
            "boxcox": abs(boxcox_series.dropna().skew()) if boxcox_series.notna().any() else np.inf
        }

        best_transform = min(candidate_scores, key = candidate_scores.get)
        best_abs_skew = candidate_scores[best_transform]

        rows.append(
            {
                "column": col,
                "original_skewness": float(original_skew) if pd.notna(original_skew) else np.nan,
                "log1p_abs_skewness": float(candidate_scores["log1p"]) if np.isfinite(candidate_scores["log1p"]) else np.nan,
                "sqrt_abs_skewness": float(candidate_scores["sqrt"]) if np.isfinite(candidate_scores["sqrt"]) else np.nan,
                "boxcox_abs_skewness": float(candidate_scores["boxcox"]) if np.isfinite(candidate_scores["boxcox"]) else np.nan,
                "boxcox_lambda": lam,
                "selected_transformation": best_transform,
                "selected_abs_skewness": float(best_abs_skew) if np.isfinite(best_abs_skew) else np.nan,
            }
        )

    return pd.DataFrame(rows).sort_values("original_skewness", key = lambda s: s.abs(), ascending = False).reset_index(drop = True)


#
def apply_selected_transformations(df: pd.DataFrame, transform_evaluation_df: pd.DataFrame):
    transformed_df = df.copy()
    applied_rows: list[dict] = []

    for _, row in transform_evaluation_df.iterrows():
        col = row["column"]
        selected = row["selected_transformation"]

        if selected == "log1p":
            transformed_df[col] = _safe_log1p(transformed_df[col])
        elif selected == "sqrt":
            transformed_df[col] = _safe_sqrt(transformed_df[col])
        elif selected == "boxcox":
            transformed_df[col], lam = _safe_boxcox(transformed_df[col])
            row["boxcox_lambda"] = lam
        elif selected == "none":
            pass
        else:
            raise ValueError(f"Unsupported transformation selected for {col}: {selected}")

        applied_rows.append(
            {
                "column": col,
                "selected_transformation": selected,
                "boxcox_lambda": row.get("boxcox_lambda", None)
            }
        )

        return transformed_df, pd.DataFrame(applied_rows)


#
def build_univariate_summary(df: pd.DataFrame, columns: list[str]):
    rows: list[dict] = []

    for col in columns:
        series = pd.to_numeric(df[col], errors = "coerce")
        clean = series.dropna()

        rows.append(
            {
                "column": col,
                "count": int(clean.shape[0]),
                "missing_count": int(series.isna().sum()),
                "mean": float(clean.mean()) if not clean.empty else np.nan,
                "median": float(clean.median()) if not clean.empty else np.nan,
                "std": float(clean.std()) if not clean.empty else np.nan,
                "min": float(clean.min()) if not clean.empty else np.nan,
                "q1": float(clean.quantile(0.25)) if not clean.empty else np.nan,
                "q3": float(clean.quantile(0.75)) if not clean.empty else np.nan,
                "max": float(clean.max()) if not clean.empty else np.nan,
                "skewness": float(clean.skew()) if not clean.empty else np.nan
            }
        )

    return pd.DataFrame(rows)