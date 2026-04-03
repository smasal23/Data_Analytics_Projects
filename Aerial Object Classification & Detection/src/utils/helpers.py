from pathlib import Path
from typing import Iterable, List
import random
import numpy as np


def ensure_directories(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def sorted_subdirs(path: Path) -> List[Path]:
    if not path.exists():
        return []
    return sorted([p for p in path.iterdir() if p.is_dir()])


def is_jpg_file(path: Path) -> bool:
    return path.suffix.lower() == ".jpg"


def set_basic_random_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)