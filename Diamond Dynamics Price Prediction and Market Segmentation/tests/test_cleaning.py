from pathlib import Path
import numpy as np
import pandas as pd

from src.data.clean_data import (
    mark_invalid_xyz_as_missing,
    remove_impossible_core_rows,
    impute_missing_values,
    decide_columns_to_drop,
)


def test_mark_invalid_xyz_as_missing():
    df = pd.DataFrame({
        "x": [1.0, 0.0, -1.0, 2.5],
        "y": [2.0, 3.0, 0.0, -2.0],
        "z": [1.0, 0.0, 3.0, -1.0],
    })

    result = mark_invalid_xyz_as_missing(df, ["x", "y", "z"])

    assert pd.isna(result.loc[1, "x"])
    assert pd.isna(result.loc[2, "x"])
    assert pd.isna(result.loc[2, "y"])
    assert pd.isna(result.loc[3, "y"])
    assert pd.isna(result.loc[1, "z"])
    assert pd.isna(result.loc[3, "z"])


def test_remove_impossible_core_rows():
    df = pd.DataFrame({
        "carat": [0.5, 0.0, 1.2, -0.1],
        "price": [1000, 2000, 0, 5000],
        "x": [5.0, 5.1, 5.2, 5.3],
    })

    kept, removed = remove_impossible_core_rows(df, ["carat", "price"])

    assert len(kept) == 1
    assert len(removed) == 3
    assert kept.iloc[0]["carat"] == 0.5
    assert kept.iloc[0]["price"] == 1000


def test_impute_missing_values():
    df = pd.DataFrame({
        "carat": [0.5, np.nan, 1.5],
        "depth": [61.0, 62.0, np.nan],
        "cut": ["Ideal", None, "Premium"],
        "color": ["G", "G", None],
    })

    cleaned, imputation_values = impute_missing_values(
        df=df,
        numeric_cols=["carat", "depth"],
        categorical_cols=["cut", "color"],
        numeric_strategy="median",
        categorical_strategy="most_frequent",
    )

    assert cleaned.isna().sum().sum() == 0
    assert imputation_values["carat"] == 1.0
    assert imputation_values["depth"] == 61.5
    assert imputation_values["cut"] in {"Ideal", "Premium"}
    assert imputation_values["color"] == "G"


def test_decide_columns_to_drop():
    df = pd.DataFrame(columns=["carat", "cut", "price", "extra_col"])
    expected_columns = ["carat", "cut", "price"]

    dropped = decide_columns_to_drop(df, expected_columns)

    assert dropped == ["extra_col"]