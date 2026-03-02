import matplotlib.pyplot as plt
import seaborn as sns
import logging
from typing import List

logger = logging.getLogger(__name__)


# plot_univariate_distributions(df)
def plot_univariate_distributions(df, columns: List[str] = None):
    """
    Plot histograms with KDE for selected numerical columns.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataset.
    columns : List[str], optional
        Columns to visualize. If None, defaults to core indicators.
    """

    if columns is None:
        columns = [
            "adult_literacy_rate",
            "gdp_per_capita",
            "education_expenditure_pct_gdp",
            "school_enrollment_secondary",
            "education_index"
        ]

    for col in columns:
        if col in df.columns:
            plt.figure(figsize=(8, 5))
            sns.histplot(df[col].dropna(), kde=True)
            plt.title(f"Distribution of {col}")
            plt.xlabel(col)
            plt.ylabel("Frequency")
            plt.tight_layout()
            plt.show()
        else:
            logger.warning(f"{col} not found in dataframe.")


# plot_correlation_heatmap(df)
def plot_correlation_heatmap(df) -> None:
    """
    Plot correlation heatmap of numerical features.
    """

    plt.figure(figsize=(12, 8))
    numeric_df = df.select_dtypes(include="number")

    corr = numeric_df.corr()

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        linewidths=0.5
    )

    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.show()


# plot_gdp_vs_literacy(df)
def plot_gdp_vs_literacy(df) -> None:
    """
    Scatter plot of GDP per capita vs literacy rate.
    """

    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=df,
        x="gdp_per_capita",
        y="adult_literacy_rate",
        hue="continent",
        alpha=0.7
    )

    plt.title("GDP per Capita vs Adult Literacy Rate")
    plt.tight_layout()
    plt.show()


# plot_time_series(df, country)
def plot_time_series(df, country: str) -> None:
    """
    Plot literacy and GDP trends for a specific country.

    Parameters
    ----------
    df : pd.DataFrame
    country : str
        Country name.
    """

    country_df = df[df["entity"] == country].sort_values("year")

    if country_df.empty:
        raise ValueError(f"No data found for country: {country}")

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(
        country_df["year"],
        country_df["adult_literacy_rate"],
        label="Literacy Rate"
    )
    ax1.set_ylabel("Literacy Rate")

    ax2 = ax1.twinx()
    ax2.plot(
        country_df["year"],
        country_df["gdp_per_capita"],
        color="orange",
        label="GDP per Capita"
    )
    ax2.set_ylabel("GDP per Capita")

    plt.title(f"Time Series Trends - {country}")
    plt.tight_layout()
    plt.show()


# generate_ranking_tables(df)
def generate_ranking_tables(df, year: int = None):
    """
    Generate country rankings for literacy and GDP.

    Returns
    -------
    dict of DataFrames
    """

    if year is None:
        year = df["year"].max()

    snapshot = df[df["year"] == year]

    rankings = {
        "literacy_top10": snapshot.sort_values(
            "adult_literacy_rate",
            ascending=False
        ).head(10),

        "gdp_top10": snapshot.sort_values(
            "gdp_per_capita",
            ascending=False
        ).head(10)
    }

    return rankings


# continental_analysis(df)
def continental_analysis(df):
    """
    Aggregate metrics by continent.

    Returns
    -------
    pd.DataFrame
    """

    grouped = df.groupby("continent").agg({
        "adult_literacy_rate": "mean",
        "gdp_per_capita": "mean",
        "education_expenditure_pct_gdp": "mean",
        "education_index": "mean"
    }).reset_index()

    return grouped