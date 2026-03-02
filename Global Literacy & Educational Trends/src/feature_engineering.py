import pandas as pd
import numpy as np


# Basic Derived Metrics
# create_illiteracy_percentage(df)
def create_illiteracy_percentage(
    df: pd.DataFrame,
    literacy_col: str = "adult_literacy_rate",
    new_col: str = "illiteracy_rate"
):
    """
    Create illiteracy percentage from literacy rate.
    """
    df = df.copy()
    df[new_col] = 100 - df[literacy_col]
    return df

# calculate_gender_gap(df)

def calculate_gender_gap(
    df: pd.DataFrame,
    male_col: str = "youth_literacy_rate_M",
    female_col: str = "youth_literacy_rate_F",
    new_col: str = "gender_gap"
):
    """
    Calculate gender literacy gap (Male - Female).
    """
    df = df.copy()
    df[new_col] = df[male_col] - df[female_col]
    return df

# compute_gdp_per_schooling(df)
def compute_gdp_per_schooling(
    df: pd.DataFrame,
    gdp_col: str = "gdp",
    schooling_col: str = "avg_schooling_years",
    new_col: str = "gdp_per_schooling"
):
    """
    Compute GDP per average schooling year.
    """
    df = df.copy()
    df[new_col] = df[gdp_col] / df[schooling_col]
    return df


# COMPOSITE INDEX
# build_education_index(df)
def build_education_index(
    df: pd.DataFrame,
    literacy_col: str = "adult_literacy_rate",
    schooling_col: str = "avg_schooling_years",
    illiteracy_col: str = "illiteracy_rate",
    new_col: str = "education_index"
):
    """
    Build composite education development index
    using min-max normalization.
    """
    df = df.copy()

    def min_max(series):
        return (series - series.min()) / (series.max() - series.min())

    literacy_norm = min_max(df[literacy_col])
    schooling_norm = min_max(df[schooling_col])
    illiteracy_norm = min_max(df[illiteracy_col])

    df[new_col] = (
        literacy_norm +
        schooling_norm +
        (1 - illiteracy_norm)
    ) / 3

    return df


# Time Series Feature
# calculate_growth_rate(df)
def calculate_growth_rate(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    new_col: str = None
):
    """
    Calculate year-over-year percentage growth.
    """
    df = df.copy()

    if new_col is None:
        new_col = f"{value_col}_growth_rate"

    df[new_col] = (
        df.sort_values("year")
          .groupby(group_col)[value_col]
          .pct_change() * 100
    )

    return df


# Advanced Development Metrics
# create_efficiency_score(df)
def create_efficiency_score(
    df: pd.DataFrame,
    education_index_col: str = "education_index",
    gdp_col: str = "log_gdp",
    new_col: str = "efficiency_score"
):
    """
    Measure economic efficiency of education.
    """
    df = df.copy()
    df[new_col] = df[education_index_col] * df[gdp_col]
    return df

# calculate_burden_index(df)
def calculate_burden_index(
    df: pd.DataFrame,
    illiteracy_col: str = "illiteracy_rate",
    population_col: str = None,
    new_col: str = "burden_index"
):
    """
    Calculate development burden index.
    If population available:
        burden = illiteracy_rate * population
    Else:
        burden = illiteracy_rate
    """
    df = df.copy()

    if population_col and population_col in df.columns:
        df[new_col] = df[illiteracy_col] * df[population_col]
    else:
        df[new_col] = df[illiteracy_col]

    return df