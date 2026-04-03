from pathlib import Path
from typing import List, Optional
import math
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


def save_current_figure(output_path: Path, dpi: int = 150) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()


def plot_image_grid(
    image_paths: List[Path],
    title: str,
    output_path: Optional[Path] = None,
    ncols: int = 4,
    figsize: tuple = (16, 10),
    dpi: int = 150,
) -> None:
    """
    Plot a grid of images from file paths.
    """
    if not image_paths:
        raise ValueError("No images provided to plot_image_grid.")

    n_images = len(image_paths)
    nrows = math.ceil(n_images / ncols)

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    axes = np.array(axes).reshape(-1)

    for ax in axes:
        ax.axis("off")

    for ax, image_path in zip(axes, image_paths):
        img = Image.open(image_path).convert("RGB")
        ax.imshow(img)
        ax.set_title(image_path.name, fontsize=9)
        ax.axis("off")

    fig.suptitle(title, fontsize=16)

    if output_path:
        save_current_figure(output_path, dpi=dpi)
    else:
        plt.show()