from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.modeling.metrics import compute_regression_metrics, build_metrics_dataframe
from src.visualization.plot_feature_importance import plot_feature_importance
from src.visualization.plot_regression import (
    plot_actual_vs_predicted,
    plot_residuals,
    plot_model_comparison,
)


# Inverse transform predictions/targets when the model was trained on log1p(target).
def inverse_log1p_if_needed(values, use_inverse: bool = True):
    values = np.asarray(values)
    return np.expm1(values) if use_inverse else values


# Evaluate one trained regression pipeline on the test split.
def evaluate_single_regression_model(
    model_name: str,
    pipeline,
    X_test: pd.DataFrame,
    y_test,
    target_logged: bool = False,
    inverse_for_reporting: bool = True,
):
    y_pred = pipeline.predict(X_test)

    y_true_report = inverse_log1p_if_needed(y_test, use_inverse = (target_logged and inverse_for_reporting))
    y_pred_report = inverse_log1p_if_needed(y_pred, use_inverse = (target_logged and inverse_for_reporting))

    metrics = compute_regression_metrics(y_true_report, y_pred_report)
    metrics["model_name"] = model_name

    predictions_df = pd.DataFrame({
        "model_name": model_name,
        "actual": y_true_report,
        "predicted": y_pred_report,
        "residual": y_true_report - y_pred_report,
    })

    return metrics, predictions_df


# Rank models by RMSE, then MAE.
def rank_regression_models(metrics_records: list[dict]):
    return build_metrics_dataframe(metrics_records)


# Extract feature importance from a fitted pipeline if the underlying model supports it.
def build_tree_feature_importance_dataframe(trained_pipeline):
    preprocessor = trained_pipeline.named_steps["preprocessor"]
    model = trained_pipeline.named_steps["model"]

    if not hasattr(model, "feature_importances_"):
        return pd.DataFrame(columns = ["feature", "importance"])

    feature_names = preprocessor.get_feature_names_out()
    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending = False).reset_index(drop = True)

    return importance_df


# Create all regression evaluation visual outputs for the best model and comparison chart.
def create_regression_evaluation_outputs(
    best_model_name: str,
    best_pipeline,
    X_test: pd.DataFrame,
    y_test,
    metrics_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
    figures_dir: str | Path,
    target_logged: bool = False,
    inverse_for_reporting: bool = True,
):
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents = True, exist_ok = True)

    best_pred_df = predictions_df[predictions_df["model_name"] == best_model_name].copy()

    actual_vs_predicted_path = figures_dir / "actual_vs_predicted_best_model.png"
    residual_plot_path = figures_dir / "residual_plot_best_model.png"
    comparison_plot_path = figures_dir / "regression_models_comparison.png"

    plot_actual_vs_predicted(
        y_true = best_pred_df["actual"],
        y_pred = best_pred_df["predicted"],
        output_path = actual_vs_predicted_path,
        title = f"Actual vs Predicted - {best_model_name}",
    )

    plot_residuals(
        y_true = best_pred_df["actual"],
        y_pred = best_pred_df["predicted"],
        output_path = residual_plot_path,
        title = f"Residual Plot - {best_model_name}",
    )

    plot_model_comparison(
        metrics_df = metrics_df,
        output_path = comparison_plot_path,
        metric_col = "rmse",
        title = "Regression Models Comparison (RMSE)",
    )

    outputs = {
        "actual_vs_predicted_path": actual_vs_predicted_path,
        "residual_plot_path": residual_plot_path,
        "comparison_plot_path": comparison_plot_path,
    }

    feature_importance_df = build_tree_feature_importance_dataframe(best_pipeline)
    if not feature_importance_df.empty:
        fi_path = figures_dir / "random_forest_feature_importance.png"
        plot_feature_importance(
            feature_importance_df = feature_importance_df,
            output_path = fi_path,
            title = f"Feature Importance - {best_model_name}",
        )
        outputs["feature_importance_path"] = fi_path
        outputs["feature_importance_df"] = feature_importance_df

    return outputs


# Build markdown summary report for regression models.
def build_regression_markdown_report(
    metrics_df: pd.DataFrame,
    best_model_name: str,
):
    lines: list[str] = []

    lines.append("# Regression Evaluation Report\n")
    lines.append(f"## Best Model\n")
    lines.append(f"- Selected model: `{best_model_name}`\n")

    lines.append("## Model Comparison\n")
    lines.append(metrics_df.to_markdown(index = False))
    lines.append("")

    return "\n".join(lines)