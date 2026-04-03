from pathlib import Path
from typing import Dict


def get_project_root_from_drive(
    drive_root: str = "/content/drive/MyDrive",
    project_dir_name: str = "Aerial_Object_Classification_Detection",
) -> Path:
    """
    Build the project root path inside Google Drive.
    """
    return Path(drive_root) / project_dir_name


def build_project_paths(project_root: Path) -> Dict[str, Path]:
    """
    Build a dictionary of key project directories.
    """
    return {
        "project_root": project_root,
        "data_root": project_root / "data",
        "raw_root": project_root / "data" / "raw",
        "interim_root": project_root / "data" / "interim",
        "processed_root": project_root / "data" / "processed",
        "classification_dataset": project_root / "data" / "raw" / "classification_dataset",
        "object_detection_dataset": project_root / "data" / "raw" / "object_detection_dataset",
        "dataset_audit_dir": project_root / "data" / "interim" / "dataset_audit",
        "previews_dir": project_root / "data" / "interim" / "previews",
        "label_checks_dir": project_root / "data" / "interim" / "label_checks",
        "notebooks_dir": project_root / "notebooks",
        "src_dir": project_root / "src",
        "configs_dir": project_root / "configs",
        "docs_dir": project_root / "docs",
        "reports_dir": project_root / "reports",
        "figures_dir": project_root / "figures",
        "figures_dataset_audit_dir": project_root / "figures" / "dataset_audit",
        "app_dir": project_root / "app",
        "models_root": project_root / "models",
        "classification_models_dir": project_root / "models" / "classification",
        "detection_models_dir": project_root / "models" / "detection",
        "tests_dir": project_root / "tests",
        "logs_dir": project_root / "logs",
    }


def create_project_directories(paths: Dict[str, Path]) -> None:
    """
    Create all project directories if they do not exist.
    """
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)