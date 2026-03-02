import pandas as pd
import numpy as np

# convert_filter_year(df)
def convert_and_filter_year(
    df: pd.DataFrame,
    year_col: str = "year",
    start_year: int = 1990,
    end_year: int = 2023
):
    df = df.copy()

    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    df = df.dropna(subset=[year_col])
    df[year_col] = df[year_col].astype(int)

    df = df[(df[year_col] >= start_year) & (df[year_col] <= end_year)]

    return df


# rename_columns(df)
def rename_columns(df: pd.DataFrame, rename_dict: dict):
    """
    Rename columns using provided dictionary.
    """
    return df.rename(columns=rename_dict)


def drop_columns(df: pd.DataFrame, columns: list):
    """
    Drop unnecessary columns.
    """
    return df.drop(columns=columns, errors="ignore")


# country_region_filtering(df)
def remove_aggregates(
    df: pd.DataFrame,
    country_col: str,
    aggregate_list: list
    ):
    """
    Remove aggregate regions like 'World', 'High-income countries'.
    """
    return df[~df[country_col].isin(aggregate_list)]


def fill_missing_continents(
    df: pd.DataFrame,
    country_col: str,
    continent_col: str,
    mapping_dict: dict
    ):
    """
    Fill missing continent values using mapping dictionary.
    """
    df = df.copy()
    df.loc[
        df[country_col].isin(mapping_dict.keys()),
        continent_col
    ] = df[country_col].map(mapping_dict)
    return df


# handling_missing_values(df)
def calculate_missing_ratio(
    df: pd.DataFrame,
    group_col: str,
    target_col: str
):
    """
    Calculate missing value ratio per group.
    """
    return df.groupby(group_col)[target_col].apply(lambda x: x.isnull().mean())


def drop_high_missing_countries(
    df: pd.DataFrame,
    group_col: str,
    target_col: str,
    threshold: float = 1.0
):
    """
    Drop groups with missing ratio above threshold.
    """
    missing_ratio = calculate_missing_ratio(df, group_col, target_col)
    to_drop = missing_ratio[missing_ratio >= threshold].index
    return df[~df[group_col].isin(to_drop)]


def interpolate_by_country(
    df: pd.DataFrame,
    group_col: str,
    target_col: str
):
    """
    Interpolate missing values within each country.
    """
    df = df.copy()

    df[target_col] = (
        df.groupby(group_col)[target_col]
        .transform(lambda x: x.interpolate().ffill().bfill())
    )

    return df


def drop_missing_rows(
    df: pd.DataFrame,
    columns: list
):
    """
    Drop rows where critical columns still contain NaN.
    """
    return df.dropna(subset=columns)


# duplicate_handling(df)
def remove_duplicates(
    df: pd.DataFrame,
    subset_cols: list
):
    """
    Remove duplicate rows based on subset columns.
    """
    return df.drop_duplicates(subset=subset_cols)


# detect_outliers(df)
def detect_zscore_outliers(
    df: pd.DataFrame,
    column: str,
    threshold: float = 3
):
    """
    Return boolean Series indicating Z-score outliers.
    """
    mean = df[column].mean()
    std = df[column].std()

    z_scores = (df[column] - mean) / std
    return z_scores.abs() > threshold


def detect_iqr_outliers(
    df: pd.DataFrame,
    column: str
):
    """
    Return boolean Series indicating IQR-based outliers.
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    return (df[column] < lower) | (df[column] > upper)