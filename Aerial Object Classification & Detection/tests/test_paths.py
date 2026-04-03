from pathlib import Path
from src.utils.paths import build_project_paths


def test_build_project_paths_returns_dict():
    project_root = Path("/tmp/demo_project")
    paths = build_project_paths(project_root)

    assert isinstance(paths, dict)
    assert "project_root" in paths
    assert paths["project_root"] == project_root
    assert paths["classification_dataset"] == project_root / "data" / "raw" / "classification_dataset"