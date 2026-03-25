from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)

from src.features.encoding import build_clustering_preprocessor, transform_with_preprocessor
from src.features.feature_selection import select_clustering_features
from src.features.pca_utils import fit_pca, build_explained_variance_table
from src.modeling.save_artifacts import (
    save_pickle_artifact,
    save_dataframe_artifact,
    save_yaml_artifact,
)
from src.modeling.evaluate_clustering import (
    build_cluster_summary,
    build_cluster_name_mapping,
    apply_cluster_name_mapping,
    build_clustering_markdown_report,
    build_pca_markdown_report,
    build_model_selection_markdown_report,
)
from src.visualization.plot_clustering import (
    plot_elbow_method,
    plot_silhouette_scores,
    plot_cluster_count,
    plot_clusterwise_carat_price_summary,
    plot_pca_2d_clusters,
    plot_pca_3d_clusters,
)
from src.utils.config import load_project_configs
from src.utils.io import ensure_dir, save_text_file
from src.utils.paths import find_project_root, resolve_project_path


# -----------------------------
# Config / path helpers
# -----------------------------
def load_clustering_context(project_root: str | Path | None = None) -> dict[str, Any]:
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    return {
        "project_root": root,
        "main_config": configs["main_config"],
        "paths_config": configs["paths_config"],
        "features_config": configs["features_config"],
        "clustering_config": configs["clustering_config"],
    }


def get_default_engineered_numeric_cols() -> list[str]:
    return [
        "volume",
        "volume_proxy",
        "dimension_ratio",
        "length_width_ratio",
        "depth_pct_from_dimensions",
        "table_depth_interaction",
        "carat_squared",
        "table_to_depth_ratio",
        "face_area",
    ]


def get_default_engineered_categorical_cols() -> list[str]:
    return ["carat_category"]


# -----------------------------
# Dataset preparation
# -----------------------------
def prepare_clustering_input_dataset(
    df: pd.DataFrame,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    """
    Prepare clustering-ready inputs by:
    - selecting clustering-safe features
    - removing price-related columns from clustering inputs
    - encoding cut/color/clarity through existing project preprocessor
    - scaling through existing clustering preprocessor
    """
    ctx = load_clustering_context(project_root)
    features_cfg = ctx["features_config"]

    raw_numeric_cols = list(features_cfg["schema"]["numeric_features"])
    raw_categorical_cols = list(features_cfg["schema"]["categorical_features"])

    selection = select_clustering_features(
        df=df,
        raw_numeric_cols=raw_numeric_cols,
        raw_categorical_cols=raw_categorical_cols,
        engineered_numeric_cols=get_default_engineered_numeric_cols(),
        engineered_categorical_cols=get_default_engineered_categorical_cols(),
        corr_threshold=0.90,
    )

    numeric_cols = [
        col for col in selection["selected_numeric_features"]
        if col in df.columns and col not in {"price", "price_inr", "price_per_carat"}
    ]

    categorical_cols = [
        col for col in ["cut", "color", "clarity"]
        if col in selection["selected_categorical_features"] and col in df.columns
    ]

    feature_cols = numeric_cols + categorical_cols
    X_raw = df[feature_cols].copy()

    preprocessor = build_clustering_preprocessor(
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        project_root=ctx["project_root"],
    )

    X_processed = transform_with_preprocessor(
        df=X_raw,
        preprocessor=preprocessor,
        fit=True,
    )

    return {
        "X_raw": X_raw,
        "X_processed": X_processed,
        "preprocessor": preprocessor,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "feature_cols": feature_cols,
        "selection": selection,
    }


# -----------------------------
# PCA
# -----------------------------
def apply_optional_pca(
    X_processed: pd.DataFrame,
    n_components: int = 2,
    random_state: int = 42,
) -> dict[str, Any]:
    pca = fit_pca(
        X=X_processed,
        n_components=n_components,
        random_state=random_state,
    )

    component_names = [f"PC{i + 1}" for i in range(n_components)]
    X_pca = pd.DataFrame(
        pca.transform(X_processed),
        columns=component_names,
        index=X_processed.index,
    )

    explained_variance_df = build_explained_variance_table(pca)

    return {
        "pca": pca,
        "X_pca": X_pca,
        "explained_variance_df": explained_variance_df,
    }


# -----------------------------
# Metrics helpers
# -----------------------------
def compute_internal_clustering_metrics(X, labels) -> dict[str, float | int | None]:
    labels = np.asarray(labels)
    unique_labels = sorted(set(labels))
    non_noise_labels = [label for label in unique_labels if label != -1]

    if len(non_noise_labels) <= 1:
        return {
            "n_clusters": len(non_noise_labels),
            "silhouette_score": None,
            "davies_bouldin_score": None,
            "calinski_harabasz_score": None,
        }

    valid_mask = labels != -1
    X_eval = X[valid_mask] if hasattr(X, "__getitem__") else np.asarray(X)[valid_mask]
    labels_eval = labels[valid_mask]

    return {
        "n_clusters": int(len(non_noise_labels)),
        "silhouette_score": float(silhouette_score(X_eval, labels_eval)),
        "davies_bouldin_score": float(davies_bouldin_score(X_eval, labels_eval)),
        "calinski_harabasz_score": float(calinski_harabasz_score(X_eval, labels_eval)),
    }


# -----------------------------
# Search / training
# -----------------------------
def run_elbow_search(
    X_processed: pd.DataFrame,
    min_k: int = 2,
    max_k: int = 10,
    step: int = 1,
    n_init: int = 20,
    max_iter: int = 500,
    random_state: int = 42,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for k in range(min_k, max_k + 1, step):
        model = KMeans(
            n_clusters=k,
            init="k-means++",
            n_init=n_init,
            max_iter=max_iter,
            random_state=random_state,
        )
        labels = model.fit_predict(X_processed)

        rows.append(
            {
                "k": k,
                "inertia": float(model.inertia_),
                "silhouette_score": float(silhouette_score(X_processed, labels)),
            }
        )

    return pd.DataFrame(rows)


def train_kmeans_candidates(
    X_processed: pd.DataFrame,
    min_k: int = 2,
    max_k: int = 10,
    step: int = 1,
    n_init: int = 20,
    max_iter: int = 500,
    random_state: int = 42,
) -> tuple[pd.DataFrame, KMeans, np.ndarray]:
    rows: list[dict[str, Any]] = []
    best_model = None
    best_labels = None
    best_score = -np.inf

    for k in range(min_k, max_k + 1, step):
        model = KMeans(
            n_clusters=k,
            init="k-means++",
            n_init=n_init,
            max_iter=max_iter,
            random_state=random_state,
        )
        labels = model.fit_predict(X_processed)
        metrics = compute_internal_clustering_metrics(X_processed, labels)

        row = {
            "model_name": "kmeans",
            "k": k,
            "linkage": None,
            "eps": None,
            "min_samples": None,
            "noise_ratio": 0.0,
            "inertia": float(model.inertia_),
            "fit_rows": int(len(X_processed)),
            "used_sampling": False,
            "can_assign_full_dataset": True,
            "status": "ok",
            **metrics,
        }
        rows.append(row)

        score = row["silhouette_score"] if row["silhouette_score"] is not None else -np.inf
        if score > best_score:
            best_score = score
            best_model = model
            best_labels = labels

    return pd.DataFrame(rows), best_model, best_labels


def train_dbscan_candidates(
    X_processed: pd.DataFrame,
    eps_values: list[float] | None = None,
    min_samples_values: list[int] | None = None,
) -> tuple[pd.DataFrame, DBSCAN | None, np.ndarray | None]:
    eps_values = eps_values or [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    min_samples_values = min_samples_values or [5, 8, 10]

    rows: list[dict[str, Any]] = []
    best_model = None
    best_labels = None
    best_score = -np.inf

    for eps in eps_values:
        for min_samples in min_samples_values:
            model = DBSCAN(eps=eps, min_samples=min_samples)
            labels = model.fit_predict(X_processed)

            unique_non_noise = sorted({label for label in labels if label != -1})
            noise_ratio = float(np.mean(labels == -1))

            if len(unique_non_noise) <= 1:
                rows.append(
                    {
                        "model_name": "dbscan",
                        "k": None,
                        "linkage": None,
                        "eps": eps,
                        "min_samples": min_samples,
                        "noise_ratio": noise_ratio,
                        "inertia": None,
                        "fit_rows": int(len(X_processed)),
                        "used_sampling": False,
                        "can_assign_full_dataset": True,
                        "status": "insufficient_clusters",
                        "n_clusters": len(unique_non_noise),
                        "silhouette_score": None,
                        "davies_bouldin_score": None,
                        "calinski_harabasz_score": None,
                    }
                )
                continue

            metrics = compute_internal_clustering_metrics(X_processed, labels)
            row = {
                "model_name": "dbscan",
                "k": None,
                "linkage": None,
                "eps": eps,
                "min_samples": min_samples,
                "noise_ratio": noise_ratio,
                "inertia": None,
                "fit_rows": int(len(X_processed)),
                "used_sampling": False,
                "can_assign_full_dataset": True,
                "status": "ok",
                **metrics,
            }
            rows.append(row)

            score = row["silhouette_score"] if row["silhouette_score"] is not None else -np.inf
            if score > best_score:
                best_score = score
                best_model = model
                best_labels = labels

    return pd.DataFrame(rows), best_model, best_labels


def train_agglomerative_candidates(
    X_processed: pd.DataFrame,
    min_k: int = 2,
    max_k: int = 10,
    step: int = 1,
    linkage_options: list[str] | None = None,
    max_samples_for_hierarchical: int = 2000,
    random_state: int = 42,
) -> tuple[pd.DataFrame, AgglomerativeClustering | None, np.ndarray | None]:
    """
    Safe hierarchical clustering search.

    Important:
    - hierarchical clustering is O(n^2) memory-heavy
    - run only on a capped sample
    - if sampled fit fails, skip gracefully
    """
    linkage_options = linkage_options or ["ward", "complete", "average"]

    n_rows = len(X_processed)
    used_sampling = n_rows > max_samples_for_hierarchical

    if used_sampling:
        X_fit = X_processed.sample(
            n=max_samples_for_hierarchical,
            random_state=random_state,
        ).copy()
    else:
        X_fit = X_processed.copy()

    rows: list[dict[str, Any]] = []
    best_model = None
    best_labels = None
    best_score = -np.inf

    for linkage in linkage_options:
        for k in range(min_k, max_k + 1, step):
            kwargs = {
                "n_clusters": k,
                "linkage": linkage,
            }
            if linkage != "ward":
                kwargs["metric"] = "euclidean"

            try:
                model = AgglomerativeClustering(**kwargs)
                labels = model.fit_predict(X_fit)
                metrics = compute_internal_clustering_metrics(X_fit, labels)

                row = {
                    "model_name": "agglomerative",
                    "k": k,
                    "linkage": linkage,
                    "eps": None,
                    "min_samples": None,
                    "noise_ratio": 0.0,
                    "inertia": None,
                    "fit_rows": int(len(X_fit)),
                    "used_sampling": bool(used_sampling),
                    "can_assign_full_dataset": not used_sampling,
                    "status": "ok",
                    **metrics,
                }
                rows.append(row)

                score = row["silhouette_score"] if row["silhouette_score"] is not None else -np.inf
                if score > best_score:
                    best_score = score
                    best_model = model
                    best_labels = labels

            except MemoryError:
                rows.append(
                    {
                        "model_name": "agglomerative",
                        "k": k,
                        "linkage": linkage,
                        "eps": None,
                        "min_samples": None,
                        "noise_ratio": None,
                        "inertia": None,
                        "fit_rows": int(len(X_fit)),
                        "used_sampling": bool(used_sampling),
                        "can_assign_full_dataset": False,
                        "n_clusters": None,
                        "silhouette_score": None,
                        "davies_bouldin_score": None,
                        "calinski_harabasz_score": None,
                        "status": "memory_error_skipped",
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "model_name": "agglomerative",
                        "k": k,
                        "linkage": linkage,
                        "eps": None,
                        "min_samples": None,
                        "noise_ratio": None,
                        "inertia": None,
                        "fit_rows": int(len(X_fit)),
                        "used_sampling": bool(used_sampling),
                        "can_assign_full_dataset": False,
                        "n_clusters": None,
                        "silhouette_score": None,
                        "davies_bouldin_score": None,
                        "calinski_harabasz_score": None,
                        "status": f"skipped: {type(exc).__name__}",
                    }
                )

    return pd.DataFrame(rows), best_model, best_labels


def compare_clustering_models(results_df: pd.DataFrame) -> pd.DataFrame:
    comparison = results_df.copy()

    for col in [
        "silhouette_score",
        "davies_bouldin_score",
        "calinski_harabasz_score",
        "noise_ratio",
    ]:
        if col in comparison.columns:
            comparison[col] = pd.to_numeric(comparison[col], errors="coerce")

    if "status" not in comparison.columns:
        comparison["status"] = "ok"
    else:
        comparison["status"] = comparison["status"].fillna("ok")

    if "can_assign_full_dataset" not in comparison.columns:
        comparison["can_assign_full_dataset"] = True

    comparison = comparison.sort_values(
        by=["silhouette_score", "calinski_harabasz_score", "davies_bouldin_score", "noise_ratio"],
        ascending=[False, False, True, True],
        na_position="last",
    ).reset_index(drop=True)

    comparison["rank"] = np.arange(1, len(comparison) + 1)
    return comparison


def select_best_model_bundle(
    kmeans_model,
    kmeans_labels,
    agglomerative_model,
    agglomerative_labels,
    dbscan_model,
    dbscan_labels,
    comparison_df: pd.DataFrame,
) -> tuple[str, Any, np.ndarray]:
    valid_df = comparison_df.dropna(subset=["silhouette_score"]).copy()

    if "can_assign_full_dataset" in valid_df.columns:
        valid_df = valid_df[valid_df["can_assign_full_dataset"] == True].copy()

    valid_df = valid_df.reset_index(drop=True)

    if valid_df.empty:
        raise ValueError(
            "No valid full-dataset clustering candidate produced a usable silhouette score."
        )

    best_row = valid_df.iloc[0]
    model_name = best_row["model_name"]

    if model_name == "kmeans":
        return "kmeans", kmeans_model, kmeans_labels
    if model_name == "agglomerative":
        return "agglomerative", agglomerative_model, agglomerative_labels
    return "dbscan", dbscan_model, dbscan_labels


# -----------------------------
# Full pipeline
# -----------------------------
def train_clustering_pipeline(
    df: pd.DataFrame,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    ctx = load_clustering_context(project_root)
    root = ctx["project_root"]
    model_selection_cfg = ctx["clustering_config"]["model_selection"]

    prep = prepare_clustering_input_dataset(df=df, project_root=root)
    X_raw = prep["X_raw"]
    X_processed = prep["X_processed"]
    preprocessor = prep["preprocessor"]

    cluster_range = model_selection_cfg["cluster_range"]
    min_k = int(cluster_range["min_k"])
    max_k = int(cluster_range["max_k"])
    step = int(cluster_range["step"])

    elbow_df = run_elbow_search(
        X_processed=X_processed,
        min_k=min_k,
        max_k=max_k,
        step=step,
        n_init=int(ctx["clustering_config"]["kmeans"]["n_init"]),
        max_iter=int(ctx["clustering_config"]["kmeans"]["max_iter"]),
        random_state=int(ctx["clustering_config"]["kmeans"]["random_state"]),
    )

    kmeans_results_df, kmeans_model, kmeans_labels = train_kmeans_candidates(
        X_processed=X_processed,
        min_k=min_k,
        max_k=max_k,
        step=step,
        n_init=int(ctx["clustering_config"]["kmeans"]["n_init"]),
        max_iter=int(ctx["clustering_config"]["kmeans"]["max_iter"]),
        random_state=int(ctx["clustering_config"]["kmeans"]["random_state"]),
    )

    agg_results_df, agg_model, agg_labels = train_agglomerative_candidates(
        X_processed=X_processed,
        min_k=min_k,
        max_k=max_k,
        step=step,
        linkage_options=list(ctx["clustering_config"]["agglomerative"]["linkage_options"]),
        max_samples_for_hierarchical=2000,
        random_state=42,
    )

    dbscan_results_df, dbscan_model, dbscan_labels = train_dbscan_candidates(
        X_processed=X_processed,
    )

    all_results_df = pd.concat(
        [kmeans_results_df, agg_results_df, dbscan_results_df],
        axis=0,
        ignore_index=True,
    )
    comparison_df = compare_clustering_models(all_results_df)

    best_model_name, best_model, best_labels = select_best_model_bundle(
        kmeans_model=kmeans_model,
        kmeans_labels=kmeans_labels,
        agglomerative_model=agg_model,
        agglomerative_labels=agg_labels,
        dbscan_model=dbscan_model,
        dbscan_labels=dbscan_labels,
        comparison_df=comparison_df,
    )

    pca_2 = apply_optional_pca(X_processed=X_processed, n_components=2, random_state=42)
    pca_3 = apply_optional_pca(X_processed=X_processed, n_components=3, random_state=42)

    if len(best_labels) != len(df):
        raise ValueError(
            f"Best model labels length ({len(best_labels)}) does not match dataset length ({len(df)}). "
            "This usually means a sampled clustering candidate was selected as final."
        )

    cluster_analysis_df = df.copy()
    cluster_analysis_df["cluster"] = best_labels

    cluster_summary_df = build_cluster_summary(cluster_analysis_df)
    cluster_name_mapping = build_cluster_name_mapping(cluster_summary_df)
    cluster_analysis_df = apply_cluster_name_mapping(
        cluster_analysis_df,
        cluster_name_mapping=cluster_name_mapping,
    )

    best_row = comparison_df.iloc[0].to_dict()

    return {
        "X_raw": X_raw,
        "X_processed": X_processed,
        "preprocessor": preprocessor,
        "selection": prep["selection"],
        "feature_cols": prep["feature_cols"],
        "numeric_cols": prep["numeric_cols"],
        "categorical_cols": prep["categorical_cols"],
        "elbow_df": elbow_df,
        "silhouette_results_df": comparison_df.copy(),
        "all_results_df": all_results_df,
        "comparison_df": comparison_df,
        "best_model_name": best_model_name,
        "best_model": best_model,
        "best_labels": best_labels,
        "best_result_row": best_row,
        "cluster_analysis_df": cluster_analysis_df,
        "cluster_summary_df": cluster_summary_df,
        "cluster_name_mapping": cluster_name_mapping,
        "pca_2": pca_2,
        "pca_3": pca_3,
        "project_root": root,
        "best_model_bundle": {
            "model_name": best_model_name,
            "model": best_model,
            "preprocessor": preprocessor,
            "feature_cols": prep["feature_cols"],
            "numeric_cols": prep["numeric_cols"],
            "categorical_cols": prep["categorical_cols"],
            "pca_2": pca_2["pca"],
            "pca_3": pca_3["pca"],
            "cluster_name_mapping": cluster_name_mapping,
        },
    }


# -----------------------------
# Saving
# -----------------------------
def save_clustering_outputs(results: dict[str, Any]) -> dict[str, Path]:
    root = results["project_root"]

    paths = {
        "cluster_analysis_dataset": resolve_project_path(root, "data/processed/cluster_analysis_dataset.csv"),
        "kmeans_model": resolve_project_path(root, "artifacts/clustering/kmeans_model.pkl"),
        "dbscan_model": resolve_project_path(root, "artifacts/clustering/dbscan_model.pkl"),
        "hierarchical_model": resolve_project_path(root, "artifacts/clustering/hierarchical_model.pkl"),
        "best_clustering_model": resolve_project_path(root, "artifacts/clustering/best_clustering_model.pkl"),
        "cluster_assignments": resolve_project_path(root, "artifacts/clustering/cluster_assignments.csv"),
        "cluster_summary": resolve_project_path(root, "artifacts/clustering/cluster_summary.csv"),
        "silhouette_results": resolve_project_path(root, "artifacts/clustering/silhouette_results.csv"),
        "inertia_results": resolve_project_path(root, "artifacts/clustering/inertia_results.csv"),
        "cluster_name_mapping": resolve_project_path(root, "artifacts/clustering/cluster_name_mapping.yaml"),
        "best_model_metadata": resolve_project_path(root, "artifacts/clustering/best_clustering_model_metadata.yaml"),
        "pca_transformer": resolve_project_path(root, "artifacts/preprocessing/pca_transformer.pkl"),
        "final_selected_models": resolve_project_path(root, "artifacts/comparison/final_selected_models.yaml"),
        "elbow_plot": resolve_project_path(root, "figures/clustering/elbow_method.png"),
        "silhouette_plot": resolve_project_path(root, "figures/clustering/silhouette_scores.png"),
        "cluster_count_plot": resolve_project_path(root, "figures/clustering/cluster_count_plot.png"),
        "clusterwise_summary_plot": resolve_project_path(root, "figures/clustering/clusterwise_carat_price_summary.png"),
        "pca_2d_plot": resolve_project_path(root, "figures/clustering/pca_2d_clusters.png"),
        "pca_3d_plot": resolve_project_path(root, "figures/clustering/pca_3d_clusters.png"),
        "clustering_report": resolve_project_path(root, "reports/clustering_report.md"),
        "pca_report": resolve_project_path(root, "reports/pca_report.md"),
        "model_selection_report": resolve_project_path(root, "reports/model_selection_report.md"),
    }

    for path in paths.values():
        ensure_dir(Path(path).parent)

    save_pickle_artifact(
        {
            "model_name": "kmeans",
            "note": "KMeans artifact slot",
        },
        paths["kmeans_model"],
    )

    save_pickle_artifact(
        {
            "model_name": "dbscan",
            "note": "DBSCAN artifact slot",
        },
        paths["dbscan_model"],
    )

    save_pickle_artifact(
        {
            "model_name": "agglomerative",
            "note": "Agglomerative artifact slot",
        },
        paths["hierarchical_model"],
    )

    save_pickle_artifact(results["best_model_bundle"], paths["best_clustering_model"])
    save_pickle_artifact(results["pca_2"]["pca"], paths["pca_transformer"])

    save_dataframe_artifact(results["cluster_analysis_df"], paths["cluster_analysis_dataset"], index=False)
    save_dataframe_artifact(results["cluster_analysis_df"], paths["cluster_assignments"], index=False)
    save_dataframe_artifact(results["cluster_summary_df"], paths["cluster_summary"], index=False)
    save_dataframe_artifact(results["comparison_df"], paths["silhouette_results"], index=False)
    save_dataframe_artifact(results["elbow_df"], paths["inertia_results"], index=False)

    save_yaml_artifact(results["cluster_name_mapping"], paths["cluster_name_mapping"])
    save_yaml_artifact(
        {
            "best_model_name": results["best_model_name"],
            "best_result_row": results["best_result_row"],
            "feature_cols": results["feature_cols"],
            "numeric_cols": results["numeric_cols"],
            "categorical_cols": results["categorical_cols"],
            "n_clusters": int(results["cluster_summary_df"]["cluster"].nunique()),
            "scaler_saved_with_preprocessor": True,
            "pca_saved": True,
        },
        paths["best_model_metadata"],
    )

    save_yaml_artifact(
        {
            "regression_best_model": "to_be_read_from_existing_comparison_artifact",
            "clustering_best_model": results["best_model_name"],
        },
        paths["final_selected_models"],
    )

    plot_elbow_method(results["elbow_df"], paths["elbow_plot"])
    plot_silhouette_scores(results["comparison_df"], paths["silhouette_plot"])
    plot_cluster_count(results["cluster_analysis_df"], paths["cluster_count_plot"])
    plot_clusterwise_carat_price_summary(results["cluster_summary_df"], paths["clusterwise_summary_plot"])

    pca2_df = results["pca_2"]["X_pca"].copy()
    pca2_df["cluster"] = results["best_labels"]
    plot_pca_2d_clusters(pca2_df, paths["pca_2d_plot"])

    pca3_df = results["pca_3"]["X_pca"].copy()
    pca3_df["cluster"] = results["best_labels"]
    plot_pca_3d_clusters(pca3_df, paths["pca_3d_plot"])

    clustering_report = build_clustering_markdown_report(
        comparison_df=results["comparison_df"],
        cluster_summary_df=results["cluster_summary_df"],
        best_model_name=results["best_model_name"],
        feature_cols=results["feature_cols"],
    )
    pca_report = build_pca_markdown_report(
        explained_variance_df=results["pca_2"]["explained_variance_df"],
        pca_feature_count=len(results["feature_cols"]),
    )
    model_selection_report = build_model_selection_markdown_report(
        comparison_df=results["comparison_df"],
        best_model_name=results["best_model_name"],
    )

    save_text_file(clustering_report, paths["clustering_report"])
    save_text_file(pca_report, paths["pca_report"])
    save_text_file(model_selection_report, paths["model_selection_report"])

    return paths