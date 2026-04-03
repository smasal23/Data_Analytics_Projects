from pathlib import Path
from typing import Dict, List
import pandas as pd


def get_detection_split_paths(dataset_root: Path, split: str) -> Dict[str, Path]:
    """
    Return image and label directories for a split.
    """
    return {
        "images": dataset_root / split / "images",
        "labels": dataset_root / split / "labels",
    }


def count_detection_split_files(dataset_root: Path, splits: List[str]) -> pd.DataFrame:
    """
    Count image and label files by detection split.
    """
    records = []

    for split in splits:
        split_paths = get_detection_split_paths(dataset_root, split)
        image_dir = split_paths["images"]
        label_dir = split_paths["labels"]

        image_count = len(list(image_dir.glob("*.jpg"))) if image_dir.exists() else 0
        label_count = len(list(label_dir.glob("*.txt"))) if label_dir.exists() else 0

        records.append(
            {
                "split": split,
                "image_dir_exists": image_dir.exists(),
                "label_dir_exists": label_dir.exists(),
                "image_count": image_count,
                "label_count": label_count,
            }
        )

    return pd.DataFrame(records)