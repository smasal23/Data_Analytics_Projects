from __future__ import annotations

import numpy as np
import pandas as pd


#
def build_price_category_summary(df: pd.DataFrame, category_col: str):
    if category_col not in df.columns:
        raise KeyError(f"{category_col} not found in dataframe.")

    summary = (
        df.groupby(category_col, dropna = False)["price"]
        .agg(count = "count", mean_price = "mean", median_price = "median", min_price = "min", max_price = "max")
        .reset_index().sort_values("mean_price", ascending = False).reset_index(drop = True)
    )

    numeric_cols = ["mean_price", "median_price", "min_price", "max_price"]

    for col in numeric_cols:
        summary[col] = summary[col].round(4)

    return summary


#
def build_carat_price_summary(df: pd.DataFrame):
    required_cols = ["carat", "price"]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    working = df[required_cols].copy()
    working["carat"] = pd.to_numeric(working["carat"], errors = "coerce")
    working["price"] = pd.to_numeric(working["price"], errors="coerce")
    working = working.dropna()

    corr_val = working["carat"].corr(working["price"])

    summary = pd.DataFrame(
        [
            {
                "metric": "pearson_correlation_carat_price",
                "value": float(corr_val) if pd.notna(corr_val) else np.nan
            },
            {
                "metric": "carat_mean",
                "value": float(working["carat"].mean())
            },
            {
                "metric": "price_mean",
                "value": float(working["price"].mean())
            },
            {
                "metric": "sample_size",
                "value": int(working.shape[0])
            }
        ]
    )

    return summary