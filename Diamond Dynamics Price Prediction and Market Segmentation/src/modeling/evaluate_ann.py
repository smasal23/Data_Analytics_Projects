from __future__ import annotations

from pathlib import Path

import torch
import pandas as pd

from src.utils.io import read_csv_file
from src.utils.paths import find_project_root, resolve_project_path


# Same architecture used in training.
class DiamondANNRegressor(torch.nn.Module):

    def __init__(self, input_dim: int):
        super().__init__()

        self.network = torch.nn.Sequential(
            torch.nn.Linear(input_dim, 256),
            torch.nn.ReLU(),
            torch.nn.BatchNorm1d(256),
            torch.nn.Dropout(0.20),

            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.BatchNorm1d(128),
            torch.nn.Dropout(0.15),

            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),

            torch.nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.network(x)


# Load saved PyTorch ANN artifacts.
def load_ann_artifacts(project_root: str | Path | None = None):
    root = find_project_root(project_root) if project_root else find_project_root()

    checkpoint_path = resolve_project_path(root, "artifacts/ann/ann_regressor.pt")
    history_path = resolve_project_path(root, "artifacts/ann/ann_training_history.csv")
    metrics_path = resolve_project_path(root, "artifacts/ann/ann_metrics.csv")

    checkpoint = torch.load(checkpoint_path, map_location = "cpu")
    input_dim = checkpoint["input_dim"]

    model = DiamondANNRegressor(input_dim = input_dim)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    history_df = read_csv_file(history_path)
    metrics_df = read_csv_file(metrics_path)

    return model, history_df, metrics_df, checkpoint


# Lightweight loader for ANN notebook usage.
def summarize_ann_results(project_root: str | Path | None = None) -> dict:
    model, history_df, metrics_df, checkpoint = load_ann_artifacts(project_root)

    return {
        "model": model,
        "history_df": history_df,
        "metrics_df": metrics_df,
        "checkpoint": checkpoint,
        "best_val_loss": float(history_df["val_loss"].min()) if "val_loss" in history_df.columns else None,
        "final_train_loss": float(history_df["loss"].iloc[-1]) if not history_df.empty else None,
    }