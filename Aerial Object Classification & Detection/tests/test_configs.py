from pathlib import Path
from src.utils.config import load_yaml


def test_paths_yaml_loads():
    path = Path("configs/paths.yaml")
    data = load_yaml(path)
    assert isinstance(data, dict)
    assert "paths" in data


def test_classification_config_loads():
    path = Path("configs/classification_config.yaml")
    data = load_yaml(path)
    assert "dataset" in data
    assert "expected_classes" in data["dataset"]