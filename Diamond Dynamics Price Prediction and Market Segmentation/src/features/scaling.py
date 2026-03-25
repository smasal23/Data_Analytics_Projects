from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler


def build_standard_scaler():
    return StandardScaler()


def fit_numeric_scaler(df: pd.DataFrame, numeric_cols: list[str]):
    scaler = build_standard_scaler()
    scaler.fit(df[numeric_cols])
    return scaler


def transform_numeric_features(
    df: pd.DataFrame,
    scaler: StandardScaler,
    numeric_cols: list[str],
):
    scaled = scaler.transform(df[numeric_cols])
    scaled_df = pd.DataFrame(scaled, columns = numeric_cols, index = df.index)
    return scaled_df