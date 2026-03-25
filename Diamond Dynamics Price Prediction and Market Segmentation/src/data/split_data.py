from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils.config import load_project_configs
from src.utils.io import read_csv_file, save_csv_file, ensure_dir
from src.utils.logger import get_logger
from src.utils.paths import find_project_root, resolve_project_path


# Load the regression-ready dataset created by the feature pipeline.
def load_regression_model_input(project_root: str | Path | None = None):
    root = find_project_root(project_root) if project_root else find_project_root()
    input_path = resolve_project_path(root, "data/processed/regression_model_input.csv")
    return read_csv_file(input_path)


# Split the modeling dataframe into train and test datasets.
def split_regression_data(
    df: pd.DataFrame,
    target_col: str = "price",
    test_size: float = 0.2,
    random_state: int = 42,
    shuffle: bool = True,
):
    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found in dataframe.")

    train_df, test_df = train_test_split(
        df,
        test_size = test_size,
        random_state = random_state,
        shuffle = shuffle,
    )

    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


# Save train and test datasets under data/processed/.
def save_train_test_data(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    project_root: str | Path | None = None,
):
    root = find_project_root(project_root) if project_root else find_project_root()

    train_path = resolve_project_path(root, "data/processed/train.csv")
    test_path = resolve_project_path(root, "data/processed/test.csv")

    save_csv_file(train_df, train_path, index = False)
    save_csv_file(test_df, test_path, index = False)

    return {
        "train_path": train_path,
        "test_path": test_path,
    }


# End-to-end split runner for the regression dataset.
def run_train_test_split(project_root: str | Path | None = None):
    logger = get_logger("src.data.split_data")
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    regression_cfg = configs["regression_config"]
    target_col = regression_cfg["regression"]["target_column"]
    training_cfg = regression_cfg["training"]

    logger.info("Loading regression modeling dataset...")
    df = load_regression_model_input(root)

    logger.info("Splitting dataset into train/test...")
    train_df, test_df = split_regression_data(
        df = df,
        target_col = target_col,
        test_size = training_cfg["test_size"],
        random_state = training_cfg["random_state"],
        shuffle = training_cfg["shuffle"],
    )

    logger.info("Saving train/test splits...")
    paths = save_train_test_data(train_df, test_df, root)

    logger.info("Train/test split completed.")
    return {
        "train_shape": train_df.shape,
        "test_shape": test_df.shape,
        **paths,
    }


if __name__ == "__main__":
    results = run_train_test_split()
    print("Train shape:", results["train_shape"])
    print("Test shape:", results["test_shape"])
    print("Train file:", results["train_path"])
    print("Test file:", results["test_path"])