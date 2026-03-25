from pathlib import Path
import pandas as pd

from src.utils.config import load_project_configs
from src.utils.paths import resolve_project_path
from src.utils.paths import find_project_root


# Generic CSV loader
def load_csv_data(filepath: str | Path, **read_csv_kwargs):
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    return pd.read_csv(filepath, **read_csv_kwargs)


# Load the raw diamonds dataset using the path defined in paths.yaml
def load_raw_dataset(project_root: str | Path):
    project_root = Path(project_root)
    configs = load_project_configs(project_root)

    raw_data_relative_path = configs["paths_config"]["data"]["raw_data_file"]
    raw_data_path = resolve_project_path(project_root, raw_data_relative_path)

    return load_csv_data(raw_data_path)


# Load the external reference dataset, such as USD-INR conversion reference
def load_external_reference_data(project_root: str | Path):
    project_root = Path(project_root)
    configs = load_project_configs(project_root)

    external_relative_path = configs["paths_config"]["data"]["external_reference_file"]
    external_path = resolve_project_path(project_root, external_relative_path)

    return load_csv_data(external_path)

if __name__ == "main":
    project_root = find_project_root()
    df = load_raw_dataset(project_root)

    print("Dataset loaded successfully")
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())