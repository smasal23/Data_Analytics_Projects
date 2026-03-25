from __future__ import annotations

import numpy as np
import pandas as pd


def _safe_mode(series: pd.Series):
    series = series.dropna()
    if series.empty:
        return None
    mode_vals = series.mode()
    return mode_vals.iloc[0] if not mode_vals.empty else None


# Build descriptive cluster summary
def build_cluster_summary(clustered_df: pd.DataFrame):
    working = clustered_df.copy()

    group = working.groupby("cluster", dropna = False)

    summary_df = group.agg(
        record_count = ("cluster", "size"),
        avg_carat = ("carat", "mean"),
        median_carat = ("carat", "median"),
        avg_price = ("price", "mean"),
        median_price = ("price", "median"),
        avg_depth = ("depth", "mean"),
        avg_table = ("table", "mean"),
        dominant_cut = ("cut", _safe_mode),
        dominant_color = ("color", _safe_mode),
        dominant_clarity = ("clarity", _safe_mode),
    ).reset_index()

    total_count = len(working)
    summary_df["cluster_pct"] = summary_df["record_count"] / total_count

    summary_df["cut_distribution"] = summary_df["cluster"].map(
        working.groupby("cluster")["cut"].apply(
            lambda s: s.value_counts(normalize = True).round(3).to_dict()
        )
    )

    summary_df["color_distribution"] = summary_df["cluster"].map(
        working.groupby("cluster")["color"].apply(
            lambda s: s.value_counts(normalize = True).round(3).to_dict()
        )
    )

    summary_df["clarity_distribution"] = summary_df["cluster"].map(
        working.groupby("cluster")["clarity"].apply(
            lambda s: s.value_counts(normalize = True).round(3).to_dict()
        )
    )

    return summary_df.sort_values("avg_price").reset_index(drop = True)


# Create human-readable cluster names based on price/carat profile.
def build_cluster_name_mapping(cluster_summary_df: pd.DataFrame):
    summary = cluster_summary_df.copy().sort_values(["avg_price", "avg_carat"]).reset_index(drop=True)

    n = len(summary)
    labels = []

    if n == 1:
        labels = ["Core Segment"]
    elif n == 2:
        labels = ["Value Segment", "Premium Segment"]
    elif n == 3:
        labels = ["Small Value Segment", "Mid-Market Segment", "Large Premium Segment"]
    else:
        base_names = [
            "Entry Segment",
            "Value Segment",
            "Mid Segment",
            "Premium Segment",
            "Luxury Segment",
            "Elite Segment",
        ]
        labels = base_names[:n]
        if len(labels) < n:
            labels.extend([f"Segment {i}" for i in range(len(labels) + 1, n + 1)])

    mapping: dict[int, str] = {}
    for idx, row in summary.iterrows():
        dominant_cut = row.get("dominant_cut")
        suffix = f" - {dominant_cut}" if pd.notna(dominant_cut) else ""
        mapping[int(row["cluster"])] = f"{labels[idx]}{suffix}"

    return mapping


def apply_cluster_name_mapping(
    clustered_df: pd.DataFrame,
    cluster_name_mapping: dict[int, str],
):
    output_df = clustered_df.copy()
    output_df["cluster_name"] = output_df["cluster"].map(cluster_name_mapping)
    return output_df


def build_clustering_markdown_report(
    comparison_df: pd.DataFrame,
    cluster_summary_df: pd.DataFrame,
    best_model_name: str,
    feature_cols: list[str],
):
    lines: list[str] = []

    lines.append("# Clustering Report\n")
    lines.append("## Selected Clustering Features\n")
    for col in feature_cols:
        lines.append(f"- {col}")
    lines.append("")

    lines.append("## Best Clustering Model\n")
    lines.append(f"- Selected model: `{best_model_name}`")
    lines.append("")

    lines.append("## Candidate Model Comparison\n")
    lines.append(comparison_df.to_markdown(index = False))
    lines.append("")

    lines.append("## Cluster Profiles\n")
    lines.append(cluster_summary_df.to_markdown(index = False))
    lines.append("")

    return "\n".join(lines)


def build_pca_markdown_report(
    explained_variance_df: pd.DataFrame,
    pca_feature_count: int,
):
    lines: list[str] = []

    lines.append("# PCA Report\n")
    lines.append(f"- Input feature count before PCA: `{pca_feature_count}`")
    lines.append("")
    lines.append("## Explained Variance\n")
    lines.append(explained_variance_df.to_markdown(index = False))
    lines.append("")

    if not explained_variance_df.empty:
        top2 = explained_variance_df["explained_variance_ratio"].head(2).sum()
        lines.append(f"- Combined explained variance of first 2 PCs: `{top2:.4f}`")
        lines.append("")

    return "\n".join(lines)


def build_model_selection_markdown_report(
    comparison_df: pd.DataFrame,
    best_model_name: str,
) -> str:
    lines: list[str] = []

    lines.append("# Model Selection Report\n")
    lines.append("## Clustering Model Ranking\n")
    lines.append(comparison_df.to_markdown(index = False))
    lines.append("")
    lines.append("## Final Selection\n")
    lines.append(f"- Best clustering model: `{best_model_name}`")
    lines.append("")

    return "\n".join(lines)