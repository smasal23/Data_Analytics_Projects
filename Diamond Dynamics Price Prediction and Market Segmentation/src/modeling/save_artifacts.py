from __future__ import annotations

from pathlib import Path
import pickle

import pandas as pd
import yaml

from src.utils.io import ensure_dir


# Save a Python object as a .pkl file.
def save_pickle_artifact(obj, filepath: str | Path):
    filepath = Path(filepath)
    ensure_dir(filepath.parent)

    with open(filepath, "wb") as f:
        pickle.dump(obj, f)

    return filepath


# Save a dataframe as CSV.
def save_dataframe_artifact(df: pd.DataFrame, filepath: str | Path, index: bool = False):
    filepath = Path(filepath)
    ensure_dir(filepath.parent)
    df.to_csv(filepath, index = index)
    return filepath


# Save metadata or report dictionary as YAML.
def save_yaml_artifact(data: dict, filepath: str | Path):
    filepath = Path(filepath)
    ensure_dir(filepath.parent)

    with open(filepath, "w", encoding = "utf-8") as f:
        yaml.safe_dump(data, f, sort_keys = False, allow_unicode = True)

    return filepath