from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.utils.io import ensure_dir


def _prepare_output_path(output_path: str | Path) -> Path:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    return output_path


# Scatter plot of actual target values against predictions.
def plot_actual_vs_predicted(
    y_true,
    y_pred,
    output_path: str | Path,
    title: str = "Actual vs Predicted",
):
    output_path = _prepare_output_path(output_path)

    plt.figure(figsize = (8, 6))
    plt.scatter(y_true, y_pred, alpha=0.35)
    min_val = min(float(pd.Series(y_true).min()), float(pd.Series(y_pred).min()))
    max_val = max(float(pd.Series(y_true).max()), float(pd.Series(y_pred).max()))
    plt.plot([min_val, max_val], [min_val, max_val], linestyle = "--")
    plt.xlabel("Actual Price")
    plt.ylabel("Predicted Price")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path


# Residual plot: residuals versus predictions.
def plot_residuals(
    y_true,
    y_pred,
    output_path: str | Path,
    title: str = "Residual Plot",
):
    output_path = _prepare_output_path(output_path)
    residuals = pd.Series(y_true) - pd.Series(y_pred)

    plt.figure(figsize = (8, 6))
    plt.scatter(y_pred, residuals, alpha = 0.35)
    plt.axhline(0.0, linestyle = "--")
    plt.xlabel("Predicted Price")
    plt.ylabel("Residual (Actual - Predicted)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path


# Horizontal bar chart for model comparison.
def plot_model_comparison(
    metrics_df: pd.DataFrame,
    output_path: str | Path,
    metric_col: str = "rmse",
    title: str = "Regression Model Comparison",
):
    output_path = _prepare_output_path(output_path)
    plot_df = metrics_df.sort_values(metric_col, ascending = True)

    plt.figure(figsize = (10, 6))
    plt.barh(plot_df["model_name"], plot_df[metric_col])
    plt.xlabel(metric_col.upper())
    plt.ylabel("Model")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path


# Plot ANN train/validation loss over epochs.
def plot_ann_loss_curve(
    history_df: pd.DataFrame,
    output_path: str | Path,
    title: str = "ANN Training Loss Curve",
):
    output_path = _prepare_output_path(output_path)

    plt.figure(figsize = (9, 5))
    plt.plot(history_df["epoch"], history_df["loss"], label = "train_loss")
    if "val_loss" in history_df.columns:
        plt.plot(history_df["epoch"], history_df["val_loss"], label = "val_loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path