from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.data.split_data import run_train_test_split
from src.modeling.evaluate_regression import (
    evaluate_single_regression_model,
    rank_regression_models,
    create_regression_evaluation_outputs,
    build_regression_markdown_report,
)
from src.modeling.model_factory import (
    infer_feature_types,
    get_supported_regression_estimators,
    build_model_pipeline,
)
from src.modeling.save_artifacts import (
    save_pickle_artifact,
    save_dataframe_artifact,
    save_yaml_artifact,
)
from src.utils.config import load_project_configs
from src.utils.io import read_csv_file, save_text_file, ensure_dir
from src.utils.logger import get_logger
from src.utils.paths import find_project_root, resolve_project_path


def _prepare_training_data(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str,
    use_log_target: bool,
):
    X_train = train_df.drop(columns=[target_col]).copy()
    X_test = test_df.drop(columns=[target_col]).copy()

    y_train = train_df[target_col].copy()
    y_test = test_df[target_col].copy()

    if use_log_target:
        y_train = np.log1p(y_train)
        y_test = np.log1p(y_test)

    return X_train, X_test, y_train, y_test


# Train all required regression models, evaluate them, rank them, and save outputs.
def train_regression_models(project_root: str | Path | None = None):
    logger = get_logger("src.modeling.train_regression")
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    regression_cfg = configs["regression_config"]
    main_cfg = configs["main_config"]

    target_col = regression_cfg["regression"]["target_column"]
    use_log_target = regression_cfg["regression"]["use_log_target"]
    inverse_transform_predictions = regression_cfg["regression"]["inverse_transform_predictions_for_reporting"]
    random_state = regression_cfg["training"]["random_state"]

    # Ensure processed train/test files exist
    split_results = run_train_test_split(root)
    logger.info("Train/test split ready: %s", split_results)

    train_path = resolve_project_path(root, "data/processed/train.csv")
    test_path = resolve_project_path(root, "data/processed/test.csv")

    train_df = read_csv_file(train_path)
    test_df = read_csv_file(test_path)

    X_train, X_test, y_train, y_test = _prepare_training_data(
        train_df = train_df,
        test_df = test_df,
        target_col = target_col,
        use_log_target = use_log_target,
    )

    numeric_cols, categorical_cols = infer_feature_types(train_df, target_col = target_col)

    artifacts_reg_dir = resolve_project_path(root, "artifacts/regression")
    artifacts_ann_dir = resolve_project_path(root, "artifacts/ann")
    artifacts_comp_dir = resolve_project_path(root, "artifacts/comparison")
    figures_reg_dir = resolve_project_path(root, "figures/regression")
    reports_dir = resolve_project_path(root, "reports")

    for path in [artifacts_reg_dir, artifacts_ann_dir, artifacts_comp_dir, figures_reg_dir, reports_dir]:
        ensure_dir(path)

    estimators = get_supported_regression_estimators(random_state = random_state)

    trained_models: dict[str, object] = {}
    metrics_records: list[dict] = []
    predictions_frames: list[pd.DataFrame] = []

    for model_name, estimator in estimators.items():
        logger.info("Training model: %s", model_name)

        pipeline = build_model_pipeline(
            model_name = model_name,
            estimator = estimator,
            numeric_cols = numeric_cols,
            categorical_cols = categorical_cols,
            project_root = root,
        )

        pipeline.fit(X_train, y_train)

        metrics, preds_df = evaluate_single_regression_model(
            model_name = model_name,
            pipeline = pipeline,
            X_test = X_test,
            y_test = y_test,
            target_logged = use_log_target,
            inverse_for_reporting = inverse_transform_predictions,
        )

        trained_models[model_name] = pipeline
        metrics_records.append(metrics)
        predictions_frames.append(preds_df)

    metrics_df = rank_regression_models(metrics_records)
    predictions_df = pd.concat(predictions_frames, axis = 0, ignore_index = True)

    best_model_name = metrics_df.iloc[0]["model_name"]
    best_pipeline = trained_models[best_model_name]

    logger.info("Best regression model selected: %s", best_model_name)

    # Save all model artifacts requested by the project
    model_file_map = {
        "linear_regression": "linear_regression_model.pkl",
        "decision_tree_regressor": "decision_tree_regressor.pkl",
        "random_forest_regressor": "random_forest_regressor.pkl",
        "knn_regressor": "knn_regressor.pkl",
        "xgboost_regressor": "xgboost_regressor.pkl",
    }

    for model_name, pipeline in trained_models.items():
        if model_name in model_file_map:
            save_pickle_artifact(pipeline, artifacts_reg_dir / model_file_map[model_name])

    save_pickle_artifact(best_pipeline, artifacts_reg_dir / "best_regression_model.pkl")
    save_pickle_artifact(best_pipeline.named_steps["preprocessor"], artifacts_reg_dir / "preprocessing_pipeline.pkl")

    save_dataframe_artifact(metrics_df, artifacts_reg_dir / "regression_metrics.csv", index = False)
    save_dataframe_artifact(predictions_df, artifacts_reg_dir / "regression_predictions.csv", index = False)

    save_dataframe_artifact(metrics_df, artifacts_comp_dir / "model_comparison_table.csv", index = False)
    save_dataframe_artifact(metrics_df, artifacts_comp_dir / "experiment_tracking.csv", index = False)

    eval_outputs = create_regression_evaluation_outputs(
        best_model_name = best_model_name,
        best_pipeline = best_pipeline,
        X_test = X_test,
        y_test = y_test,
        metrics_df = metrics_df,
        predictions_df = predictions_df,
        figures_dir = figures_reg_dir,
        target_logged = use_log_target,
        inverse_for_reporting = inverse_transform_predictions,
    )

    metadata = {
        "best_model_name": best_model_name,
        "target_column": target_col,
        "use_log_target": use_log_target,
        "inverse_transform_predictions_for_reporting": inverse_transform_predictions,
        "train_shape": list(train_df.shape),
        "test_shape": list(test_df.shape),
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols,
        "metrics_summary": metrics_df.to_dict(orient = "records"),
    }
    save_yaml_artifact(metadata, artifacts_reg_dir / "best_regression_model_metadata.yaml")

    report_text = build_regression_markdown_report(metrics_df = metrics_df, best_model_name = best_model_name)
    save_text_file(report_text, reports_dir / "regression_evaluation_report.md")

    return {
        "best_model_name": best_model_name,
        "metrics_df": metrics_df,
        "predictions_df": predictions_df,
        "metadata": metadata,
        "evaluation_outputs": eval_outputs,
    }


if __name__ == "__main__":
    results = train_regression_models()
    print("Best regression model:", results["best_model_name"])
    print(results["metrics_df"])