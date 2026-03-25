import pandas as pd
import numpy as np

from src.features.build_features import (
    add_engineered_features,
    build_feature_documentation,
)
from src.features.feature_selection import (
    identify_high_correlation_pairs,
    select_clustering_features,
)
from src.features.encoding import get_ordinal_category_orders


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "carat": [0.5, 1.0, 1.5, 2.0],
        "cut": ["Ideal", "Premium", "Good", "Very Good"],
        "color": ["E", "G", "H", "D"],
        "clarity": ["VS1", "SI1", "VVS2", "IF"],
        "depth": [61.0, 62.5, 63.0, 60.5],
        "table": [55.0, 58.0, 57.0, 56.0],
        "price": [1500, 4500, 8000, 12000],
        "x": [5.1, 6.2, 7.1, 8.0],
        "y": [5.0, 6.1, 7.0, 7.9],
        "z": [3.1, 3.8, 4.3, 4.8],
    })


def test_add_engineered_features_creates_required_columns():
    df = _sample_df()
    result_df, feature_doc = add_engineered_features(df, usd_inr_rate=83.0)

    required_cols = {
        "price_inr",
        "volume",
        "volume_proxy",
        "price_per_carat",
        "dimension_ratio",
        "carat_category",
        "length_width_ratio",
        "depth_pct_from_dimensions",
        "table_depth_interaction",
        "carat_squared",
        "table_to_depth_ratio",
        "face_area",
    }

    assert required_cols.issubset(set(result_df.columns))
    assert "price_per_carat" in feature_doc["feature"].tolist()


def test_volume_formula_is_correct():
    df = _sample_df()
    result_df, _ = add_engineered_features(df, usd_inr_rate=83.0)

    expected = df.loc[0, "x"] * df.loc[0, "y"] * df.loc[0, "z"]
    assert np.isclose(result_df.loc[0, "volume"], expected)
    assert np.isclose(result_df.loc[0, "volume_proxy"], expected)


def test_identify_high_correlation_pairs_detects_redundancy():
    df = pd.DataFrame({
        "a": [1, 2, 3, 4, 5],
        "b": [2, 4, 6, 8, 10],
        "c": [5, 3, 6, 2, 1],
    })

    pairs = identify_high_correlation_pairs(df, ["a", "b", "c"], threshold=0.95)
    assert not pairs.empty
    assert {"feature_1", "feature_2", "abs_correlation"} == set(pairs.columns)


def test_clustering_features_exclude_price():
    df = _sample_df()
    df_fe, _ = add_engineered_features(df, usd_inr_rate=83.0)

    selection = select_clustering_features(
        df=df_fe,
        raw_numeric_cols=["carat", "depth", "table", "x", "y", "z"],
        raw_categorical_cols=["cut", "color", "clarity"],
        engineered_numeric_cols=[
            "volume",
            "volume_proxy",
            "dimension_ratio",
            "length_width_ratio",
            "depth_pct_from_dimensions",
            "table_depth_interaction",
            "carat_squared",
            "table_to_depth_ratio",
            "face_area",
        ],
        engineered_categorical_cols=["carat_category"],
        corr_threshold=0.90,
    )

    assert "price" not in selection["selected_features"]
    assert "price_inr" not in selection["selected_features"]
    assert "price_per_carat" not in selection["selected_features"]


def test_ordinal_orders_present():
    orders = get_ordinal_category_orders()
    assert "cut" in orders
    assert "color" in orders
    assert "clarity" in orders