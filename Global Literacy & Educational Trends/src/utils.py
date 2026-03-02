import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging
from typing import Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Normalization
def normalize_column(series: pd.Series):
    """
    Min-Max normalize a pandas Series.

    Parameters
    ----------
    series : pd.Series

    Returns
    -------
    pd.Series
        Normalized series scaled between 0 and 1.
    """

    if series.isnull().all():
        logger.warning("Series contains only NaN values.")
        return series

    min_val = series.min()
    max_val = series.max()

    if min_val == max_val:
        logger.warning("Series has constant value. Returning zeros.")
        return pd.Series(np.zeros(len(series)), index=series.index)

    normalized = (series - min_val) / (max_val - min_val)

    logger.info("Column normalized using Min-Max scaling.")
    return normalized


# Z-Score Standardization
def calculate_zscore(series: pd.Series):
    """
    Calculate Z-score standardized values.

    Parameters
    ----------
    series : pd.Series

    Returns
    -------
    pd.Series
        Standardized series.
    """

    mean = series.mean()
    std = series.std()

    if std == 0:
        logger.warning("Standard deviation is zero. Returning zeros.")
        return pd.Series(np.zeros(len(series)), index=series.index)

    zscore = (series - mean) / std

    logger.info("Z-score standardization applied.")
    return zscore


# Log Transformation
def log_transform(series: pd.Series):
    """
    Apply natural log transformation safely.

    Adds small epsilon to avoid log(0) errors.

    Parameters
    ----------
    series : pd.Series

    Returns
    -------
    pd.Series
    """

    epsilon = 1e-9

    if (series < 0).any():
        raise ValueError("Log transformation cannot be applied to negative values.")

    transformed = np.log(series + epsilon)

    logger.info("Log transformation applied.")
    return transformed


# Save Matplotlib Figure
def save_figure(path: str, dpi: int = 300):
    """
    Save current matplotlib figure.

    Parameters
    ----------
    path : str
        File path to save figure.
    dpi : int
        Resolution of image.
    """

    try:
        plt.savefig(path, dpi=dpi, bbox_inches="tight")
        logger.info(f"Figure saved at {path}")
    except Exception as e:
        logger.error(f"Failed to save figure: {e}")
        raise


# Summary Statistics
def print_summary_stats(df: pd.DataFrame):
    """
    Generate summary statistics for numerical columns.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Summary statistics table.
    """

    numeric_df = df.select_dtypes(include="number")

    summary = numeric_df.describe().T
    summary["median"] = numeric_df.median()
    summary["missing_values"] = numeric_df.isnull().sum()

    logger.info("Summary statistics generated.")

    return summary