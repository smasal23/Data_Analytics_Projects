from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.utils.io import ensure_dir


def _prepare_output_path(output_path: str | Path) -> Path:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    return output_path


# Plot feature importance for a tree-based winning model.
def plot_feature_importance(
    feature_importance_df: pd.DataFrame,
    output_path: str | Path,
    top_n: int = 20,
    title: str = "Feature Importance",
):
    output_path = _prepare_output_path(output_path)

    plot_df = feature_importance_df.head(top_n).sort_values("importance", ascending = True)

    plt.figure(figsize = (10, 7))
    plt.barh(plot_df["feature"], plot_df["importance"])
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi = 140, bbox_inches = "tight")
    plt.close()

    return output_path