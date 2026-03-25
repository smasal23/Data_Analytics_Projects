import pandas as pd

from src.features.build_features import add_engineered_features
from src.modeling.train_clustering import (
    prepare_clustering_input_dataset,
    train_clustering_pipeline,
)
from src.modeling.evaluate_clustering import (
    build_cluster_summary,
    build_cluster_name_mapping,
    apply_cluster_name_mapping,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "carat": [0.3, 0.35, 0.4, 1.0, 1.1, 1.2, 2.0, 2.1, 2.2, 0.9],
            "cut": ["Ideal", "Ideal", "Premium", "Good", "Very Good", "Premium", "Fair", "Good", "Premium", "Ideal"],
            "color": ["E", "F", "G", "H", "G", "F", "J", "I", "H", "E"],
            "clarity": ["VS1", "VS2", "SI1", "SI2", "VS2", "VS1", "I1", "SI2", "SI1", "VVS2"],
            "depth": [61.0, 61.2, 61.5, 62.5, 63.0, 62.8, 64.0, 63.5, 63.8, 61.8],
            "table": [55.0, 55.5, 56.0, 58.0, 58.5, 57.8, 60.0, 59.5, 59.8, 56.5],
            "price": [700, 850, 1000, 4500, 5200, 6000, 12000, 13500, 14500, 4100],
            "x": [4.2, 4.3, 4.5, 6.2, 6.4, 6.6, 8.1, 8.3, 8.4, 6.0],
            "y": [4.1, 4.2, 4.4, 6.1, 6.3, 6.5, 8.0, 8.2, 8.3, 5.9],
            "z": [2.5, 2.6, 2.7, 3.9, 4.0, 4.1, 5.1, 5.2, 5.3, 3.8],
        }
    )


def test_prepare_clustering_input_dataset_excludes_price():
    df = _sample_df()
    df_fe, _ = add_engineered_features(df, usd_inr_rate = 83.0)

    prepared = prepare_clustering_input_dataset(df_fe)

    assert "price" not in prepared["feature_cols"]
    assert "price" not in prepared["numeric_cols"]
    assert "cut" in prepared["categorical_cols"]
    assert "color" in prepared["categorical_cols"]
    assert "clarity" in prepared["categorical_cols"]


def test_train_clustering_pipeline_produces_cluster_labels():
    df = _sample_df()
    df_fe, _ = add_engineered_features(df, usd_inr_rate = 83.0)

    results = train_clustering_pipeline(df_fe)

    assert "best_model_name" in results
    assert len(results["best_labels"]) == len(df_fe)
    assert "cluster" in results["cluster_analysis_df"].columns


def test_cluster_summary_and_mapping_work():
    df = _sample_df()
    df["cluster"] = [0, 0, 0, 1, 1, 1, 2, 2, 2, 1]

    summary_df = build_cluster_summary(df)
    mapping = build_cluster_name_mapping(summary_df)
    named_df = apply_cluster_name_mapping(df, mapping)

    assert not summary_df.empty
    assert isinstance(mapping, dict)
    assert "cluster_name" in named_df.columns