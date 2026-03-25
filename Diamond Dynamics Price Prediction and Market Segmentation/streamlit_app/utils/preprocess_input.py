from __future__ import annotations

import pandas as pd

from src.features.build_features import add_engineered_features, load_usd_inr_rate


def build_input_dataframe(payload: dict) -> pd.DataFrame:
    ordered_cols = ["carat", "cut", "color", "clarity", "depth", "table", "x", "y", "z"]
    row = {col: payload[col] for col in ordered_cols}
    return pd.DataFrame([row])


def add_runtime_engineered_features(df: pd.DataFrame, project_root) -> tuple[pd.DataFrame, float]:
    # add_engineered_features expects a price column because it also derives
    # reporting-only features like price_inr and price_per_carat.
    working = df.copy()
    working["price"] = 0.0

    usd_inr_rate = load_usd_inr_rate(project_root)
    engineered_df, _ = add_engineered_features(working, usd_inr_rate=usd_inr_rate)
    return engineered_df, usd_inr_rate