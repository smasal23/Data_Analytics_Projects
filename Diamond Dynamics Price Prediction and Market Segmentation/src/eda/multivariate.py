from __future__ import annotations

import pandas as pd


def build_pairplot_frame(
    df: pd.DataFrame,
    columns: list[str],
    sample_size: int = 3000,
    random_state: int = 42,
) -> pd.DataFrame:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise KeyError(f"Missing columns for pairplot: {missing}")

    pair_df = df[columns].copy().dropna()

    if len(pair_df) > sample_size:
        pair_df = pair_df.sample(n=sample_size, random_state=random_state)

    return pair_df.reset_index(drop=True)


def build_correlation_matrix(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise KeyError(f"Missing columns for correlation matrix: {missing}")

    numeric_df = df[columns].copy().apply(pd.to_numeric, errors="coerce")
    return numeric_df.corr(numeric_only=True)