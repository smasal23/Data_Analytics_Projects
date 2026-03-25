import pandas as pd

from src.modeling.metrics import compute_regression_metrics, build_metrics_dataframe
from src.modeling.model_factory import infer_feature_types, get_supported_regression_estimators, build_model_pipeline


def _sample_regression_df() -> pd.DataFrame:
    return pd.DataFrame({
        "carat": [0.3, 0.5, 0.7, 1.0, 1.2, 1.5, 2.0, 2.2],
        "depth": [61.0, 62.0, 61.5, 63.0, 60.5, 62.3, 61.8, 62.1],
        "table": [55.0, 57.0, 58.0, 56.0, 57.5, 58.0, 59.0, 60.0],
        "x": [4.3, 5.1, 5.7, 6.2, 6.6, 7.0, 8.0, 8.2],
        "y": [4.2, 5.0, 5.6, 6.1, 6.5, 6.9, 7.9, 8.1],
        "z": [2.6, 3.1, 3.5, 3.8, 4.0, 4.3, 4.9, 5.0],
        "cut": ["Ideal", "Premium", "Very Good", "Good", "Ideal", "Premium", "Good", "Very Good"],
        "color": ["E", "F", "G", "H", "D", "E", "F", "G"],
        "clarity": ["VS1", "VS2", "SI1", "SI2", "VVS2", "VS1", "SI1", "IF"],
        "price": [800, 1500, 2300, 3500, 4200, 5500, 9000, 11000],
    })


def test_compute_regression_metrics_returns_expected_keys():
    y_true = [10, 20, 30]
    y_pred = [12, 18, 31]

    metrics = compute_regression_metrics(y_true, y_pred)

    assert set(metrics.keys()) == {"mae", "mse", "rmse", "r2"}


def test_build_metrics_dataframe_adds_rank():
    records = [
        {"model_name": "a", "mae": 10.0, "mse": 100.0, "rmse": 10.0, "r2": 0.80},
        {"model_name": "b", "mae": 8.0, "mse": 81.0, "rmse": 9.0, "r2": 0.82},
    ]

    df = build_metrics_dataframe(records)

    assert "rank" in df.columns
    assert df.iloc[0]["model_name"] == "b"


def test_linear_pipeline_trains_and_predicts():
    df = _sample_regression_df()

    X = df.drop(columns = ["price"])
    y = df["price"]

    numeric_cols, categorical_cols = infer_feature_types(df, target_col = "price")
    estimators = get_supported_regression_estimators(random_state = 42)

    pipeline = build_model_pipeline(
        model_name = "linear_regression",
        estimator = estimators["linear_regression"],
        numeric_cols = numeric_cols,
        categorical_cols = categorical_cols,
    )

    pipeline.fit(X, y)
    preds = pipeline.predict(X)

    assert len(preds) == len(y)