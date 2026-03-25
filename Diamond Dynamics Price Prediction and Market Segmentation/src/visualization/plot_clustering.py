from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.utils.io import ensure_dir


def _prepare_output_path(output_path: str | Path):
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    return output_path


def plot_elbow_method(elbow_df: pd.DataFrame, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    plt.figure(figsize = (8, 5))
    plt.plot(elbow_df["k"], elbow_df["inertia"], marker = "o")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.title("Elbow Method")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path


def plot_silhouette_scores(results_df: pd.DataFrame, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    plot_df = results_df.dropna(subset = ["silhouette_score"]).copy()
    plot_df["label"] = plot_df.apply(
        lambda row: (
            f"{row['model_name']}-k{int(row['k'])}"
            if pd.notna(row["k"])
            else f"{row['model_name']}-eps{row['eps']}"
        ),
        axis=1,
    )

    plt.figure(figsize = (11, 6))
    plt.bar(plot_df["label"], plot_df["silhouette_score"])
    plt.xticks(rotation = 60, ha = "right")
    plt.xlabel("Model / Setting")
    plt.ylabel("Silhouette Score")
    plt.title("Silhouette Score Comparison")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path


def plot_cluster_count(clustered_df: pd.DataFrame, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    counts = clustered_df["cluster"].value_counts().sort_index()

    plt.figure(figsize = (8, 5))
    plt.bar(counts.index.astype(str), counts.values)
    plt.xlabel("Cluster")
    plt.ylabel("Count")
    plt.title("Cluster Count Plot")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path


def plot_clusterwise_carat_price_summary(cluster_summary_df: pd.DataFrame, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    plot_df = cluster_summary_df[["cluster", "avg_carat", "avg_price"]].copy()
    x = range(len(plot_df))

    plt.figure(figsize = (10, 6))
    plt.bar([i - 0.2 for i in x], plot_df["avg_carat"], width = 0.4, label = "Avg Carat")
    plt.bar([i + 0.2 for i in x], plot_df["avg_price"], width = 0.4, label = "Avg Price")
    plt.xticks(list(x), plot_df["cluster"].astype(str))
    plt.xlabel("Cluster")
    plt.ylabel("Value")
    plt.title("Clusterwise Average Carat and Price")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path


def plot_pca_2d_clusters(pca_df: pd.DataFrame, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    plt.figure(figsize = (8, 6))
    scatter = plt.scatter(
        pca_df["PC1"],
        pca_df["PC2"],
        c = pca_df["cluster"],
        alpha = 0.7,
    )
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("PCA 2D Cluster Visualization")
    plt.legend(*scatter.legend_elements(), title = "Cluster")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path


def plot_pca_3d_clusters(pca_df: pd.DataFrame, output_path: str | Path):
    output_path = _prepare_output_path(output_path)

    fig = plt.figure(figsize = (9, 7))
    ax = fig.add_subplot(111, projection = "3d")

    scatter = ax.scatter(
        pca_df["PC1"],
        pca_df["PC2"],
        pca_df["PC3"],
        c = pca_df["cluster"],
        alpha = 0.7,
    )
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_zlabel("PC3")
    ax.set_title("PCA 3D Cluster Visualization")
    ax.legend(*scatter.legend_elements(), title = "Cluster")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close(fig)

    return output_path