from pathlib import Path
from typing import Any, Dict, List
import json
import pandas as pd


def save_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def save_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dataframe(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)


def list_files_recursive(root: Path, suffixes: List[str] | None = None) -> List[Path]:
    if not root.exists():
        return []

    files = [p for p in root.rglob("*") if p.is_file()]
    if suffixes:
        suffixes_lower = {s.lower() for s in suffixes}
        files = [p for p in files if p.suffix.lower() in suffixes_lower]
    return files