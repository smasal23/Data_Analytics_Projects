from __future__ import annotations

import pandas as pd


def _markdown_image(path: str, alt_text: str):
    return f"[{alt_text}]({path})"


def build_eda_report(
        df: pd.DataFrame,
        univariate_summary_df: pd.DataFrame,
        carat_price_summary: pd.DataFrame,
        avg_price_by_cut_df: pd.DataFrame,
        avg_price_by_color_df: pd.DataFrame,
        avg_price_by_clarity_df: pd.DataFrame,
        corr_df: pd.DataFrame,
        observations: list[str],
        figure_paths: dict[str, str]
):
    visual_order = [
        ("dist_price", "Distribution of Price"),
        ("dist_carat", "Distribution of Carat"),
        ("dist_x", "Distribution of X"),
        ("dist_y", "Distribution of Y"),
        ("dist_z", "Distribution of Z"),
        ("count_cut", "Countplot of Cut"),
        ("count_color", "Countplot of Color"),
        ("count_clarity", "Countplot of Clarity"),
        ("carat_vs_price_regplot", "Carat vs Price Regression Plot"),
        ("avg_price_by_cut", "Average Price by Cut"),
        ("avg_price_by_color", "Average Price by Color"),
        ("avg_price_by_clarity", "Average Price by Clarity"),
        ("pairplot", "Pairplot"),
        ("correlation_heatmap", "Correlation Heatmap"),
        ("boxplots_numeric_features", "Numeric Feature Boxplots")
    ]

    visuals_section = "\n\n".join(
        _markdown_image(figure_paths[key], alt_text)
        for key, alt_text in visual_order
        if key in figure_paths
    )

    observations_section = "\n".join(
        f"{idx}. {obs}" for idx, obs in enumerate(observations, start=1)
    )

    report_text = f"""# EDA Report — Diamond Price Prediction and Market Segmentation

    ## 1. Dataset Overview
    - Shape: `{df.shape[0]} rows × {df.shape[1]} columns`
    - Columns: `{df.columns.tolist()}`
    - Missing cells total: `{int(df.isna().sum().sum())}`

    ## 2. Univariate Summary
    {univariate_summary_df.to_markdown(index=False)}

    ## 3. Carat vs Price Summary
    {carat_price_summary.to_markdown(index=False)}

    ## 4. Average Price by Cut
    {avg_price_by_cut_df.to_markdown(index=False)}

    ## 5. Average Price by Color
    {avg_price_by_color_df.to_markdown(index=False)}

    ## 6. Average Price by Clarity
    {avg_price_by_clarity_df.to_markdown(index=False)}

    ## 7. Correlation Matrix
    {corr_df.round(4).to_markdown()}

    ## 8. Key Visuals
    {visuals_section}

    ## 9. EDA Observations
    {observations_section}
    """

    return report_text