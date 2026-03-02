import os
import logging
import pandas as pd


# Import project modules
from src.data_loader import download_csv
from src.cleaning import convert_and_filter_year, rename_columns, remove_aggregates, drop_high_missing_countries, interpolate_by_country, drop_missing_rows, remove_duplicates
from src.feature_engineering import (
    create_illiteracy_percentage,
    calculate_gender_gap,
    compute_gdp_per_schooling,
    build_education_index,
    calculate_growth_rate,
    create_efficiency_score,
    calculate_burden_index
)
from src.eda import (
    plot_univariate_distributions,
    plot_correlation_heatmap,
    plot_gdp_vs_literacy,
    plot_time_series,
    generate_ranking_tables,
    continental_analysis
)
from src.utils import save_figure


# Configuration
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"
FIGURES_PATH = "reports/figures/"

os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
os.makedirs(FIGURES_PATH, exist_ok=True)


# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Main Pipeline
def run_pipeline():
    logger.info("🚀 Starting Global Literacy & Education Pipeline")

    # Load Data
    df_adult = download_csv(os.path.join(RAW_DATA_PATH, "adult_literacy.csv"))
    df_youth = download_csv(os.path.join(RAW_DATA_PATH, "youth_literacy.csv"))

    logger.info("Data loaded successfully.")


    # Cleaning
    # Convert & filter year
    df = convert_and_filter_year()

    # Rename columns if needed
    df = rename_columns(df, rename_dict)

    # Remove aggregate regions
    df = remove_aggregates(
        df,
        country_col="entity",
        aggregate_list=[
            "World",
            "High-income countries",
            "Low-income countries"
        ]
    )

    # Remove duplicates
    df = remove_duplicates(
        df,
        subset_cols=["entity", "year"]
    )

    # Drop countries fully missing literacy
    df = drop_high_missing_countries(
        df,
        group_col="entity",
        target_col="adult_literacy_rate",
        threshold=1.0
    )

    # Interpolate literacy within country
    df = interpolate_by_country(
        df,
        group_col="entity",
        target_col="adult_literacy_rate"
    )

    # Drop any critical missing rows
    df = drop_missing_rows(
        df,
        columns=["adult_literacy_rate", "gdp_per_capita"]
    )

    logger.info("Cleaning completed.")


    # Feature Engineering
    df = create_illiteracy_percentage(df)
    df = calculate_gender_gap(df)
    df = compute_gdp_per_schooling(df)
    df = build_education_index(df)
    df = calculate_growth_rate(df)
    df = create_efficiency_score(df)
    df = calculate_burden_index(df)

    logger.info("Feature engineering completed.")

    # Save processed dataset
    processed_path = os.path.join(PROCESSED_DATA_PATH, "final_dataset.csv")
    df.to_csv(processed_path, index=False)
    logger.info(f"Processed dataset saved at {processed_path}")


    # Exploratory Data Analysis

    plot_univariate_distributions(df)
    save_figure(os.path.join(FIGURES_PATH, "univariate.png"))

    plot_correlation_heatmap(df)
    save_figure(os.path.join(FIGURES_PATH, "correlation_heatmap.png"))

    plot_gdp_vs_literacy(df)
    save_figure(os.path.join(FIGURES_PATH, "gdp_vs_literacy.png"))

    # Example time series
    sample_country = df["entity"].iloc[0]
    plot_time_series(df, sample_country)
    save_figure(os.path.join(FIGURES_PATH, f"time_series_{sample_country}.png"))

    rankings = generate_ranking_tables(df)
    rankings["literacy_top10"].to_csv(
        os.path.join(PROCESSED_DATA_PATH, "literacy_top10.csv"),
        index=False
    )

    rankings["gdp_top10"].to_csv(
        os.path.join(PROCESSED_DATA_PATH, "gdp_top10.csv"),
        index=False
    )

    continent_summary = continental_analysis(df)
    continent_summary.to_csv(
        os.path.join(PROCESSED_DATA_PATH, "continent_summary.csv"),
        index=False
    )

    logger.info("EDA completed.")

    logger.info("✅ Pipeline finished successfully.")


# Entry Point

if __name__ == "__main__":
    run_pipeline()