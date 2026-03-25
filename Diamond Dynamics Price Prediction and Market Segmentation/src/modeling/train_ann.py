from __future__ import annotations

from pathlib import Path
import copy
import random

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split

from src.data.split_data import run_train_test_split
from src.modeling.metrics import compute_regression_metrics
from src.modeling.model_factory import (
    infer_feature_types,
    build_dynamic_regression_preprocessor,
)
from src.modeling.save_artifacts import (
    save_dataframe_artifact,
    save_yaml_artifact,
)
from src.visualization.plot_regression import plot_ann_loss_curve
from src.utils.config import load_project_configs
from src.utils.io import read_csv_file, save_text_file, ensure_dir
from src.utils.logger import get_logger
from src.utils.paths import find_project_root, resolve_project_path


# Set seeds for reproducibility.
def set_global_seeds(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


# Feedforward ANN for tabular regression.
class DiamondANNRegressor(nn.Module):

    def __init__(self, input_dim: int):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.20),

            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.15),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.network(x)


# Split train/test dataframes into X and y, optionally applying log1p to target.
def _prepare_xy(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str,
    use_log_target: bool,
):
    X_train_df = train_df.drop(columns=[target_col]).copy()
    X_test_df = test_df.drop(columns=[target_col]).copy()

    y_train = train_df[target_col].astype(float).to_numpy()
    y_test = test_df[target_col].astype(float).to_numpy()

    if use_log_target:
        y_train = np.log1p(y_train)
        y_test_model = np.log1p(y_test)
    else:
        y_test_model = y_test.copy()

    return X_train_df, X_test_df, y_train, y_test, y_test_model


# Split into sub-train/validation and return PyTorch dataloaders.
def _build_dataloaders(
    X_train: np.ndarray,
    y_train: np.ndarray,
    batch_size: int,
    random_state: int,
):
    X_subtrain, X_val, y_subtrain, y_val = train_test_split(
        X_train,
        y_train,
        test_size = 0.15,
        random_state = random_state,
        shuffle = True,
    )

    train_dataset = TensorDataset(
        torch.tensor(X_subtrain, dtype = torch.float32),
        torch.tensor(y_subtrain, dtype = torch.float32).view(-1, 1),
    )
    val_dataset = TensorDataset(
        torch.tensor(X_val, dtype = torch.float32),
        torch.tensor(y_val, dtype = torch.float32).view(-1, 1),
    )

    train_loader = DataLoader(train_dataset, batch_size = batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size = batch_size, shuffle=False)

    return train_loader, val_loader


# Train ANN regression model using PyTorch.
def train_ann_regression_model(project_root: str | Path | None = None):
    logger = get_logger("src.modeling.train_ann")
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    regression_cfg = configs["regression_config"]
    main_cfg = configs["main_config"]

    target_col = regression_cfg["regression"]["target_column"]
    use_log_target = regression_cfg["regression"]["use_log_target"]
    inverse_transform_predictions = regression_cfg["regression"]["inverse_transform_predictions_for_reporting"]
    random_state = main_cfg["project"]["random_state"]

    set_global_seeds(random_state)

    # Ensure train/test files exist
    run_train_test_split(root)

    train_df = read_csv_file(resolve_project_path(root, "data/processed/train.csv"))
    test_df = read_csv_file(resolve_project_path(root, "data/processed/test.csv"))

    X_train_df, X_test_df, y_train, y_test_raw, y_test_model = _prepare_xy(
        train_df = train_df,
        test_df = test_df,
        target_col = target_col,
        use_log_target = use_log_target,
    )

    numeric_cols, categorical_cols = infer_feature_types(train_df, target_col = target_col)

    # ANN benefits from scaling numeric features
    preprocessor = build_dynamic_regression_preprocessor(
        numeric_cols = numeric_cols,
        categorical_cols = categorical_cols,
        scale_numeric = True,
        numeric_imputation = regression_cfg["preprocessing"]["numeric_imputation"],
        categorical_imputation = regression_cfg["preprocessing"]["categorical_imputation"],
        handle_unknown = regression_cfg["preprocessing"]["handle_unknown_categories"],
        drop_first = regression_cfg["preprocessing"]["drop_first"],
    )

    logger.info("Fitting ANN preprocessor...")
    X_train = preprocessor.fit_transform(X_train_df)
    X_test = preprocessor.transform(X_test_df)

    if hasattr(X_train, "toarray"):
        X_train = X_train.toarray()
    if hasattr(X_test, "toarray"):
        X_test = X_test.toarray()

    X_train = np.asarray(X_train, dtype = np.float32)
    X_test = np.asarray(X_test, dtype = np.float32)

    batch_size = 64
    epochs = 120
    learning_rate = 0.001
    patience = 15

    train_loader, val_loader = _build_dataloaders(
        X_train = X_train,
        y_train = y_train,
        batch_size = batch_size,
        random_state = random_state,
    )

    device = torch.device("cpu")
    model = DiamondANNRegressor(input_dim = X_train.shape[1]).to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr = learning_rate)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode = "min",
        factor = 0.5,
        patience = 5,
    )

    history_records: list[dict] = []
    best_state = None
    best_val_loss = float("inf")
    epochs_without_improvement = 0

    logger.info("Starting PyTorch ANN training...")

    for epoch in range(1, epochs + 1):
        model.train()
        train_losses = []

        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

            train_losses.append(loss.item())

        model.eval()
        val_losses = []

        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)

                preds = model(batch_x)
                loss = criterion(preds, batch_y)
                val_losses.append(loss.item())

        train_loss = float(np.mean(train_losses))
        val_loss = float(np.mean(val_losses))
        current_lr = float(optimizer.param_groups[0]["lr"])

        history_records.append(
            {
                "epoch": epoch,
                "loss": train_loss,
                "val_loss": val_loss,
                "learning_rate": current_lr,
            }
        )

        scheduler.step(val_loss)

        logger.info(
            "Epoch %d/%d | train_loss=%.6f | val_loss=%.6f | lr=%.6f",
            epoch,
            epochs,
            train_loss,
            val_loss,
            current_lr,
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = copy.deepcopy(model.state_dict())
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= patience:
            logger.info("Early stopping triggered at epoch %d", epoch)
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    # Final test inference
    model.eval()
    with torch.no_grad():
        X_test_tensor = torch.tensor(X_test, dtype = torch.float32).to(device)
        y_pred_model = model(X_test_tensor).cpu().numpy().reshape(-1)

    if use_log_target and inverse_transform_predictions:
        y_pred_report = np.expm1(y_pred_model)
        y_true_report = y_test_raw
    else:
        y_pred_report = y_pred_model
        y_true_report = y_test_model

    metrics = compute_regression_metrics(y_true_report, y_pred_report)

    history_df = pd.DataFrame(history_records)
    metrics_df = pd.DataFrame([{
        "model_name": "ann_regressor_pytorch",
        **metrics,
    }])

    predictions_df = pd.DataFrame({
        "actual": y_true_report,
        "predicted": y_pred_report,
        "residual": y_true_report - y_pred_report,
    })

    artifacts_ann_dir = resolve_project_path(root, "artifacts/ann")
    figures_reg_dir = resolve_project_path(root, "figures/regression")
    reports_dir = resolve_project_path(root, "reports")

    for path in [artifacts_ann_dir, figures_reg_dir, reports_dir]:
        ensure_dir(path)

    model_path = artifacts_ann_dir / "ann_regressor.pt"
    preprocessor_path = artifacts_ann_dir / "ann_preprocessor.pkl"
    history_path = artifacts_ann_dir / "ann_training_history.csv"
    metrics_path = artifacts_ann_dir / "ann_metrics.csv"
    predictions_path = artifacts_ann_dir / "ann_predictions.csv"
    metadata_path = artifacts_ann_dir / "ann_model_metadata.yaml"
    loss_curve_path = figures_reg_dir / "ann_loss_curve.png"

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "input_dim": int(X_train.shape[1]),
            "model_class": "DiamondANNRegressor",
        },
        model_path,
    )

    # reuse pickle helper already used elsewhere in project
    from src.modeling.save_artifacts import save_pickle_artifact
    save_pickle_artifact(preprocessor, preprocessor_path)

    save_dataframe_artifact(history_df, history_path, index = False)
    save_dataframe_artifact(metrics_df, metrics_path, index = False)
    save_dataframe_artifact(predictions_df, predictions_path, index = False)

    metadata = {
        "model_type": "pytorch_ann_regressor",
        "target_column": target_col,
        "use_log_target": use_log_target,
        "inverse_transform_predictions_for_reporting": inverse_transform_predictions,
        "input_dim": int(X_train.shape[1]),
        "epochs_completed": int(len(history_df)),
        "best_val_loss": float(best_val_loss),
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols,
        "metrics": metrics,
        "model_file": str(model_path),
        "preprocessor_file": str(preprocessor_path),
    }
    save_yaml_artifact(metadata, metadata_path)

    plot_ann_loss_curve(
        history_df = history_df,
        output_path = loss_curve_path,
        title = "ANN Training Loss Curve (PyTorch)",
    )

    report_lines = [
        "# ANN Evaluation Report",
        "",
        "## Model Summary",
        "- Framework: `PyTorch`",
        "- Model type: `Feedforward ANN Regressor`",
        f"- Input dimension: `{X_train.shape[1]}`",
        f"- Epochs completed: `{len(history_df)}`",
        f"- Best validation loss: `{best_val_loss:.6f}`",
        "",
        "## Test Metrics",
        f"- MAE: `{metrics['mae']:.4f}`",
        f"- MSE: `{metrics['mse']:.4f}`",
        f"- RMSE: `{metrics['rmse']:.4f}`",
        f"- R²: `{metrics['r2']:.4f}`",
        "",
    ]
    save_text_file("\n".join(report_lines), reports_dir / "ann_evaluation_report.md")

    logger.info("PyTorch ANN training completed.")

    return {
        "model_path": model_path,
        "preprocessor_path": preprocessor_path,
        "history_path": history_path,
        "metrics_path": metrics_path,
        "predictions_path": predictions_path,
        "metadata_path": metadata_path,
        "loss_curve_path": loss_curve_path,
        "metrics": metrics,
        "history_df": history_df,
        "metrics_df": metrics_df,
    }


if __name__ == "__main__":
    results = train_ann_regression_model()
    print("ANN training completed.")
    print("Saved model:", results["model_path"])
    print("Metrics:")
    print(results["metrics"])