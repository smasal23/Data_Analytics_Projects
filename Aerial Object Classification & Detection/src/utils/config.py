from pathlib import Path
from typing import Any, Dict
import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    """
    Load a YAML file and return it as a dictionary.
    """
    if not path.exists():
        raise FileNotFoundError(f"YAML config not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: Dict[str, Any], path: Path) -> None:
    """
    Save a dictionary to a YAML file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)