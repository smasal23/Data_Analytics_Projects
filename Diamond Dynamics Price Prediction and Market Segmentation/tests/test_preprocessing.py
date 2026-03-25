from sklearn.compose import ColumnTransformer

from src.data.preprocess import (
    build_regression_preprocessor,
    build_clustering_preprocessor,
    summarize_preprocessing_strategy,
)


def test_build_regression_preprocessor():
    preprocessor = build_regression_preprocessor()
    assert isinstance(preprocessor, ColumnTransformer)

    transformer_names = [name for name, _, _ in preprocessor.transformers]
    assert "num" in transformer_names
    assert "cat" in transformer_names


def test_build_clustering_preprocessor():
    preprocessor = build_clustering_preprocessor()
    assert isinstance(preprocessor, ColumnTransformer)

    transformer_names = [name for name, _, _ in preprocessor.transformers]
    assert "num" in transformer_names
    assert "cat" in transformer_names


def test_summarize_preprocessing_strategy():
    summary = summarize_preprocessing_strategy()

    assert "numeric_columns" in summary
    assert "categorical_columns" in summary
    assert "dataset_level_cleaning_strategy" in summary
    assert summary["dataset_level_cleaning_strategy"]["numeric_missing"] == "median"
    assert summary["dataset_level_cleaning_strategy"]["categorical_missing"] == "most_frequent"