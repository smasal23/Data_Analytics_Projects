from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils.io import ensure_dir


sns.set_theme(style = "whitegrid")


#
def _prepare_output_path(output_path: str | Path):
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    return output_path


#
def plot_outlier_boxplots_before_after(
        before_df: pd.DataFrame,
        after_df: pd.DataFrame | None,
        columns: list[str],
        before_path: str | Path | None,
        after_path: str | Path | None,
        mode: str = "both"
):
    if mode in ("before_only", "both") and before_path is not None:
        output_path = _prepare_output_path(before_path)
        plt.figure(figsize = (12, 6))
        before_df[columns].boxplot(rot = 45)
        plt.title("Outlier Inspection Before Treatment")
        plt.ylabel("Value")
        plt.tight_layout()
        plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
        plt.close()

    if mode in ("after_only", "both") and after_df is not None and after_path is not None:
        output_path = _prepare_output_path(after_path)
        plt.figure(figsize = (12, 6))
        after_df[columns].boxplot(rot = 45)
        plt.title("Outlier Inspection After Treatment")
        plt.ylabel("Value")
        plt.tight_layout()
        plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
        plt.close()


#
def plot_skewness_before_after(
    skew_before_df: pd.DataFrame,
    skew_after_df: pd.DataFrame,
    before_path: str | Path,
    after_path: str | Path,
):
    before_path = _prepare_output_path(before_path)
    after_path = _prepare_output_path(after_path)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=skew_before_df, x="column", y="skewness")
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title("Skewness Before Treatment")
    plt.xlabel("Feature")
    plt.ylabel("Skewness")
    plt.tight_layout()
    plt.savefig(before_path, dpi=140, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.barplot(data=skew_after_df, x="column", y="skewness")
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title("Skewness After Treatment")
    plt.xlabel("Feature")
    plt.ylabel("Skewness")
    plt.tight_layout()
    plt.savefig(after_path, dpi=140, bbox_inches="tight")
    plt.close()


#
def plot_distribution(df: pd.DataFrame, column: str, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    plt.figure(figsize=(8, 5))
    sns.histplot(df[column].dropna(), kde=True, bins=40)
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close()


#
def plot_countplot(df: pd.DataFrame, column: str, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    plt.figure(figsize=(8, 5))
    order = df[column].value_counts().index
    sns.countplot(data=df, x=column, order=order)
    plt.title(f"Countplot of {column}")
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close()


#
def plot_regplot(df: pd.DataFrame, x_col: str, y_col: str, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    plt.figure(figsize=(8, 5))
    sns.regplot(data=df, x=x_col, y=y_col, scatter_kws={"alpha": 0.25, "s": 10}, line_kws={"linewidth": 2})
    plt.title(f"{x_col} vs {y_col}")
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.tight_layout()
    plt.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close()


#
def plot_avg_price_barplot(summary_df: pd.DataFrame, category_col: str, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    plt.figure(figsize=(8, 5))
    sns.barplot(data=summary_df, x=category_col, y="mean_price")
    plt.title(f"Average Price by {category_col}")
    plt.xlabel(category_col)
    plt.ylabel("Average Price")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close()


#
def plot_pairplot(df: pd.DataFrame, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    pair_grid = sns.pairplot(df, corner=True, diag_kind="hist")
    pair_grid.fig.suptitle("Pairplot of Numeric Features", y=1.02)
    pair_grid.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close("all")


#
def plot_correlation_heatmap(corr_df: pd.DataFrame, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    plt.figure(figsize=(9, 7))
    sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="coolwarm", square=True)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close()


#
def plot_numeric_boxplot_grid(df: pd.DataFrame, columns: list[str], output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    n_cols = 3
    n_rows = (len(columns) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
    axes = axes.flatten()

    for idx, col in enumerate(columns):
        sns.boxplot(y=df[col], ax=axes[idx])
        axes[idx].set_title(f"Boxplot - {col}")
        axes[idx].set_ylabel(col)

    for idx in range(len(columns), len(axes)):
        axes[idx].axis("off")

    fig.suptitle("Numeric Feature Boxplots", y=1.01)
    fig.tight_layout()
    fig.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close(fig)