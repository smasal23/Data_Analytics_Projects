from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inference.predict_cluster import predict_cluster_from_dict


class DummyPreprocessor:
    def transform(self, X):
        return X


class DummyClusterModel:
    def predict(self, X):
        return [2]


def test_predict_cluster_from_dict():
    configs = {"streamlit_config": {"segmentation": {}}}

    payload = {
        "carat": 1.0,
        "cut": "Ideal",
        "color": "G",
        "clarity": "VS2",
        "depth": 61.5,
        "table": 57.0,
        "x": 6.4,
        "y": 6.3,
        "z": 4.0,
    }

    cluster_bundle = {
        "cluster_bundle": {
            "model_name": "kmeans",
            "model": DummyClusterModel(),
            "preprocessor": DummyPreprocessor(),
            "feature_cols": ["carat", "depth", "table", "x", "y", "z", "cut", "color", "clarity"],
            "cluster_name_mapping": {2: "Premium Segment - Ideal"},
        }
    }

    result = predict_cluster_from_dict(payload, configs, cluster_bundle, usd_inr_rate=80.0)

    assert result["cluster"] == 2
    assert result["cluster_name"] == "Premium Segment - Ideal"