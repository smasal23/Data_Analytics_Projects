# Imports

from pathlib import Path
import yaml

# Load a yaml file and return its contents as a Python dictionary.
def load_yaml(filepath: str | Path):
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"YAML file not found: {filepath}")

    with open(filepath, "r", encoding = "utf-8") as file:
        return yaml.safe_load(file)

# Load the main project config file from the configs/directory.
def load_project_configs(project_root: str | Path):
    project_root = Path(project_root)
    configs_dir = project_root/"configs"

    config_files = {
        "main_config": configs_dir/"config.yaml",
        "paths_config": configs_dir/"paths.yaml",
        "features_config": configs_dir/"features.yaml",
        "model_registry": configs_dir/"model_registry.yaml",
        "regression_config": configs_dir/"regression_config.yaml",
        "clustering_config": configs_dir/"clustering_config.yaml",
        "streamlit_config": configs_dir/"streamlit_config.yaml"
    }

    loaded_configs = {}
    for name, path in config_files.items():
        loaded_configs[name] = load_yaml(path)

    return loaded_configs