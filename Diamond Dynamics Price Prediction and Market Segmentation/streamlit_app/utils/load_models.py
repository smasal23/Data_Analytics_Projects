from __future__ import annotations

from pathlib import Path
import pickle

try:
    import joblib
except Exception:  # pragma: no cover
    joblib = None

from src.utils.paths import resolve_project_path


def _load_serialized_object(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")

    suffix = path.suffix.lower()
    if suffix in {".joblib", ".jl"} and joblib is not None:
        return joblib.load(path)

    with open(path, "rb") as f:
        return pickle.load(f)


def _first_existing_path(project_root: Path, candidates: list[str]) -> Path:
    for rel in candidates:
        path = resolve_project_path(project_root, rel)
        if path.exists():
            return path
    raise FileNotFoundError(f"No artifact found in candidates: {candidates}")


def load_regression_artifacts(project_root: Path, configs: dict) -> dict:
    streamlit_cfg = configs["streamlit_config"]
    regression_cfg = configs["regression_config"]

    candidates = [
        streamlit_cfg["prediction"].get("pipeline_artifact"),
        streamlit_cfg["prediction"].get("model_artifact"),
        regression_cfg["artifacts"].get("best_pipeline_file"),
        regression_cfg["artifacts"].get("best_model_file"),
        "artifacts/regression/best_regression_model.pkl",
        "artifacts/regression/preprocessing_pipeline.pkl",
    ]
    candidates = [c for c in candidates if c]

    artifact_path = _first_existing_path(project_root, candidates)
    model_or_pipeline = _load_serialized_object(artifact_path)

    return {
        "artifact_path": artifact_path,
        "model_bundle": model_or_pipeline,
    }


def load_clustering_artifacts(project_root: Path, configs: dict) -> dict:
    streamlit_cfg = configs["streamlit_config"]
    clustering_cfg = configs["clustering_config"]

    candidates = [
        streamlit_cfg["segmentation"].get("cluster_model_artifact"),
        clustering_cfg["artifacts"].get("cluster_model_file"),
        "artifacts/clustering/best_clustering_model.pkl",
    ]
    candidates = [c for c in candidates if c]

    artifact_path = _first_existing_path(project_root, candidates)
    cluster_bundle = _load_serialized_object(artifact_path)

    return {
        "artifact_path": artifact_path,
        "cluster_bundle": cluster_bundle,
    }