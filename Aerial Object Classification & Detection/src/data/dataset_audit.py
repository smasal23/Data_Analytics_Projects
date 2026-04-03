from pathlib import Path
from typing import Dict, List
import random
import pandas as pd
from PIL import Image


def inspect_folder_structure(root: Path) -> Dict[str, List[str]]:
    """
    Return a dictionary describing immediate subdirectories and files.
    """
    structure = {}
    if not root.exists():
        return structure

    for item in sorted(root.iterdir()):
        if item.is_dir():
            structure[item.name] = sorted([child.name for child in item.iterdir()])
    return structure


def count_classification_images_by_split_and_class(
    dataset_root: Path,
    expected_splits: List[str],
    expected_classes: List[str],
    extension: str = ".jpg",
) -> pd.DataFrame:
    """
    Count images in classification dataset by split and class.
    """
    records = []

    for split in expected_splits:
        for class_name in expected_classes:
            class_dir = dataset_root / split / class_name
            count = 0
            if class_dir.exists():
                count = len([p for p in class_dir.glob(f"*{extension}") if p.is_file()])

            records.append(
                {
                    "split": split,
                    "class_name": class_name,
                    "image_count": count,
                }
            )

    return pd.DataFrame(records)


def collect_non_jpg_files(dataset_root: Path) -> List[Path]:
    """
    Find files that are not .jpg under classification dataset.
    """
    non_jpg_files = []
    for p in dataset_root.rglob("*"):
        if p.is_file() and p.suffix.lower() != ".jpg":
            non_jpg_files.append(p)
    return sorted(non_jpg_files)


def get_sample_images(
    class_dir: Path,
    n_samples: int = 8,
    seed: int = 42,
) -> List[Path]:
    """
    Return a reproducible sample of .jpg images from a class directory.
    """
    image_paths = sorted([p for p in class_dir.glob("*.jpg") if p.is_file()])
    if not image_paths:
        return []

    random.seed(seed)
    n = min(n_samples, len(image_paths))
    return random.sample(image_paths, n)


def summarize_image_sizes(image_paths: List[Path]) -> pd.DataFrame:
    """
    Summarize image dimensions for a list of images.
    """
    records = []

    for path in image_paths:
        with Image.open(path) as img:
            width, height = img.size
        records.append(
            {
                "file_name": path.name,
                "width": width,
                "height": height,
                "aspect_ratio": round(width / height, 4) if height != 0 else None,
            }
        )

    return pd.DataFrame(records)


def build_classification_audit_summary(
    counts_df: pd.DataFrame,
    non_jpg_files: List[Path],
    expected_classes: List[str],
) -> str:
    """
    Create a markdown summary for the classification audit.
    """
    found_classes = sorted(counts_df["class_name"].unique().tolist())
    total_images = int(counts_df["image_count"].sum())

    lines = []
    lines.append("# Classification Dataset Audit Summary")
    lines.append("")
    lines.append(f"- Expected classes: {expected_classes}")
    lines.append(f"- Found classes: {found_classes}")
    lines.append(f"- Total counted .jpg images: {total_images}")
    lines.append(f"- Non-.jpg files found: {len(non_jpg_files)}")
    lines.append("")
    lines.append("## Split-wise counts")
    lines.append("")
    lines.append(counts_df.to_markdown(index=False))

    if non_jpg_files:
        lines.append("")
        lines.append("## Non-.jpg files")
        lines.append("")
        for f in non_jpg_files[:50]:
            lines.append(f"- {f}")

    return "\n".join(lines)