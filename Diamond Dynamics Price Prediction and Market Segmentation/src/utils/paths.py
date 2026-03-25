from pathlib import Path

# Resolve the project root
def find_project_root(start: str | Path | None = None, required_dirs: tuple[str, ...] = ("configs", "data", "src")):
    current = Path(start).resolve() if start else Path.cwd().resolve()

    # Check the current directory and all parent directories
    for candidate in [current] + list(current.parents):
        if all((candidate / dirname).exists() for dirname in required_dirs):
            return candidate

    raise FileNotFoundError(
        "Project root could not be found."
        "Make sure you are running inside the project repository."
    )

# Convert a relative path from config into an absolute project path
def resolve_project_path(project_root: str | Path, relative_path: str | None):
    if relative_path is None:
        return None

    return Path(project_root)/relative_path

# Return paths to all config files.
def get_config_paths(project_root):
    project_root = Path(project_root)
    configs_dir = project_root/"configs"

    return {
        "configs_dir": configs_dir,
        "config_yaml": configs_dir/"config.yaml",
        "paths_yaml": configs_dir/"paths.yaml",
        "features_yaml": configs_dir/"features.yaml",
        "model_registry_yaml": configs_dir/"model_registry.yaml",
        "regression_config_yaml": configs_dir/"regression_config.yaml",
        "clustering_config_yaml": configs_dir/"clustering_config.yaml",
        "streamlit_config_yaml": configs_dir/"streamlit_config.yaml"
    }

# Return common project directory paths.
def get_project_subdirs(project_root):
    project_root = Path(project_root)

    return {
        "project_root": project_root,
        "data_dir": project_root/"data",
        "raw_dir": project_root/"data"/"raw",
        "interim_dir": project_root/"data"/"interim",
        "processed_dir": project_root/"data"/"processed",
        "external_dir": project_root/"data"/"external",
        "docs_dir": project_root/"docs",
        "notebooks_dir": project_root/"notebooks",
        "src_dir": project_root/"src",
        "artifacts": project_root/"artifacts",
        "tests_dir": project_root/"tests"
    }