from pathlib import Path
from typing import Dict, List, Tuple
import cv2
import pandas as pd


def image_to_label_path(image_path: Path) -> Path:
    """
    Convert image path to the expected YOLO label path.
    """
    label_dir = image_path.parent.parent / "labels"
    return label_dir / f"{image_path.stem}.txt"


def label_to_image_path(label_path: Path) -> Path:
    """
    Convert label path to the expected image path.
    """
    image_dir = label_path.parent.parent / "images"
    return image_dir / f"{label_path.stem}.jpg"


def find_unmatched_pairs(split_root: Path) -> Dict[str, List[Path]]:
    """
    Find images without labels and labels without images.
    """
    image_dir = split_root / "images"
    label_dir = split_root / "labels"

    images = sorted(image_dir.glob("*.jpg")) if image_dir.exists() else []
    labels = sorted(label_dir.glob("*.txt")) if label_dir.exists() else []

    images_without_labels = [img for img in images if not image_to_label_path(img).exists()]
    labels_without_images = [lab for lab in labels if not label_to_image_path(lab).exists()]

    return {
        "images_without_labels": images_without_labels,
        "labels_without_images": labels_without_images,
    }


def validate_yolo_line(values: List[str]) -> Tuple[bool, str]:
    """
    Validate one YOLO annotation row.
    Format: class_id x_center y_center width height
    """
    if len(values) != 5:
        return False, "Expected exactly 5 values"

    try:
        class_id = int(float(values[0]))
        x_center = float(values[1])
        y_center = float(values[2])
        width = float(values[3])
        height = float(values[4])
    except ValueError:
        return False, "Non-numeric values present"

    if class_id < 0:
        return False, "Class ID must be >= 0"

    for name, val in [("x_center", x_center), ("y_center", y_center), ("width", width), ("height", height)]:
        if not (0.0 <= val <= 1.0):
            return False, f"{name} must be in [0, 1]"

    return True, "OK"


def validate_yolo_label_file(label_path: Path) -> List[Dict]:
    """
    Validate each line in a YOLO label file.
    """
    results = []

    if not label_path.exists():
        results.append(
            {
                "label_file": str(label_path),
                "line_number": None,
                "is_valid": False,
                "message": "Label file does not exist",
            }
        )
        return results

    lines = label_path.read_text(encoding="utf-8").strip().splitlines()

    if len(lines) == 0:
        results.append(
            {
                "label_file": str(label_path),
                "line_number": None,
                "is_valid": False,
                "message": "Empty label file",
            }
        )
        return results

    for i, line in enumerate(lines, start=1):
        values = line.strip().split()
        is_valid, message = validate_yolo_line(values)
        results.append(
            {
                "label_file": str(label_path),
                "line_number": i,
                "is_valid": is_valid,
                "message": message,
            }
        )

    return results


def validate_detection_dataset(dataset_root: Path, splits: List[str]) -> pd.DataFrame:
    """
    Validate label-image pairing and YOLO line format across all splits.
    """
    records = []

    for split in splits:
        split_root = dataset_root / split
        image_dir = split_root / "images"
        label_dir = split_root / "labels"

        pair_issues = find_unmatched_pairs(split_root)
        for img in pair_issues["images_without_labels"]:
            records.append(
                {
                    "split": split,
                    "file_type": "image",
                    "file_path": str(img),
                    "issue": "missing_label",
                    "is_valid": False,
                }
            )

        for lab in pair_issues["labels_without_images"]:
            records.append(
                {
                    "split": split,
                    "file_type": "label",
                    "file_path": str(lab),
                    "issue": "missing_image",
                    "is_valid": False,
                }
            )

        if label_dir.exists():
            for label_path in sorted(label_dir.glob("*.txt")):
                line_results = validate_yolo_label_file(label_path)
                for row in line_results:
                    records.append(
                        {
                            "split": split,
                            "file_type": "label",
                            "file_path": row["label_file"],
                            "issue": row["message"],
                            "is_valid": row["is_valid"],
                        }
                    )

    return pd.DataFrame(records)


def overlay_yolo_boxes_on_image(image_path: Path, label_path: Path):
    """
    Return an OpenCV image with YOLO boxes drawn.
    """
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    h, w = image.shape[:2]

    if label_path.exists():
        for line in label_path.read_text(encoding="utf-8").strip().splitlines():
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            class_id, xc, yc, bw, bh = parts
            xc = float(xc)
            yc = float(yc)
            bw = float(bw)
            bh = float(bh)

            box_w = int(bw * w)
            box_h = int(bh * h)
            center_x = int(xc * w)
            center_y = int(yc * h)

            x1 = max(center_x - box_w // 2, 0)
            y1 = max(center_y - box_h // 2, 0)
            x2 = min(center_x + box_w // 2, w - 1)
            y2 = min(center_y + box_h // 2, h - 1)

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image,
                f"class {class_id}",
                (x1, max(y1 - 10, 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb