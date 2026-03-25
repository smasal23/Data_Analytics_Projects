from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Compute Root Mean Squared Error.
def rmse_score(y_true, y_pred):
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


# Compute the core regression metrics required for the project.
def compute_regression_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    return {
        "mae": float(mae),
        "mse": float(mse),
        "rmse": float(rmse),
        "r2": float(r2),
    }


# Convert a list of metrics dictionaries into a sorted comparison dataframe.
def build_metrics_dataframe(metrics_records: list[dict]):
    if not metrics_records:
        return pd.DataFrame(columns = ["model_name", "mae", "mse", "rmse", "r2", "rank"])

    df = pd.DataFrame(metrics_records).copy()
    df = df.sort_values(["rmse", "mae", "mse", "r2"], ascending = [True, True, True, False]).reset_index(drop = True)
    df["rank"] = np.arange(1, len(df) + 1)
    return df