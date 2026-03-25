from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.utils.paths import find_project_root, resolve_project_path
from src.utils.config import load_project_configs
from src.utils.io import save_csv_file, save_text_file, ensure_dir
from src.utils.logger import get_logger

from src.data.clean_data import clean_diamonds_dataset

from src.eda.univariate import (
    build_outlier_summary,
    clip_outliers_iqr,
    compute_skewness_table,
    find_high_skew_columns,
    evaluate_skew_transforms,
    apply_selected_transformations,
    build_univariate_summary,
)
from src.eda.bivariate import (
    build_price_category_summary,
    build_carat_price_summary,
)
from src.eda.multivariate import (
    build_pairplot_frame,
    build_correlation_matrix,
)
from src.eda.eda_report import build_eda_report

from src.visualization.plot_eda import (
    plot_outlier_boxplots_before_after,
    plot_skewness_before_after,
    plot_distribution,
    plot_countplot,
    plot_regplot,
    plot_avg_price_barplot,
    plot_pairplot,
    plot_correlation_heatmap,
    plot_numeric_boxplot_grid,
)


def run_eda_pipeline(project_root: str | Path | None = None) -> dict:
    logger = get_logger("scripts.run_eda")
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    processed_input_path = resolve_project_path(root, "data/processed/diamonds_processed.csv")
    outliers_treated_path = resolve_project_path(root, "data/interim/diamonds_outliers_treated.csv")
    skewness_treated_path = resolve_project_path(root, "data/interim/diamonds_skewness_treated.csv")
    report_path = resolve_project_path(root, "reports/eda_report.md")

    preprocessing_fig_dir = resolve_project_path(root, "figures/preprocessing")
    eda_fig_dir = resolve_project_path(root, "figures/eda")
    ensure_dir(preprocessing_fig_dir)
    ensure_dir(eda_fig_dir)

    if not Path(processed_input_path).exists():
        logger.info("Processed dataset missing. Running cleaning pipeline first.")
        clean_diamonds_dataset(root)

    logger.info("Loading processed dataset...")
    df = pd.read_csv(processed_input_path)

    focus_numeric_cols = ["carat", "price", "x", "y", "z"]
    logger.info("Building outlier summary before treatment...")
    outlier_summary_before = build_outlier_summary(df=df, columns=focus_numeric_cols)

    logger.info("Creating outlier boxplot before treatment...")
    plot_outlier_boxplots_before_after(
        before_df=df,
        after_df=None,
        columns=focus_numeric_cols,
        before_path=resolve_project_path(root, "figures/preprocessing/outlier_boxplot_before.png"),
        after_path=None,
        mode="before_only",
    )

    logger.info("Applying IQR clipping...")
    df_outliers_treated, outlier_bounds_df = clip_outliers_iqr(df=df, columns=focus_numeric_cols)

    logger.info("Creating outlier boxplot after treatment...")
    plot_outlier_boxplots_before_after(
        before_df=df,
        after_df=df_outliers_treated,
        columns=focus_numeric_cols,
        before_path=None,
        after_path=resolve_project_path(root, "figures/preprocessing/outlier_boxplot_after.png"),
        mode="after_only",
    )

    logger.info("Saving outlier-treated dataset...")
    save_csv_file(df_outliers_treated, outliers_treated_path, index=False)

    logger.info("Computing skewness before transformation...")
    skewness_before = compute_skewness_table(df_outliers_treated, focus_numeric_cols)
    high_skew_cols = find_high_skew_columns(skewness_before, threshold=1.0)

    logger.info("Evaluating skewness transformations...")
    transform_eval_df = evaluate_skew_transforms(df_outliers_treated, high_skew_cols)

    logger.info("Applying selected skewness transformations...")
    df_skewness_treated, selected_transformations = apply_selected_transformations(
        df_outliers_treated,
        transform_eval_df,
    )
    skewness_after = compute_skewness_table(df_skewness_treated, focus_numeric_cols)

    logger.info("Saving skewness plots...")
    plot_skewness_before_after(
        skew_before_df=skewness_before,
        skew_after_df=skewness_after,
        before_path=resolve_project_path(root, "figures/preprocessing/skewness_before.png"),
        after_path=resolve_project_path(root, "figures/preprocessing/skewness_after.png"),
    )

    logger.info("Saving skewness-treated dataset...")
    save_csv_file(df_skewness_treated, skewness_treated_path, index=False)

    logger.info("Generating EDA plots...")
    for col in ["price", "carat", "x", "y", "z"]:
        plot_distribution(
            df=df_skewness_treated,
            column=col,
            output_path=resolve_project_path(root, f"figures/eda/dist_{col}.png"),
        )

    for col in ["cut", "color", "clarity"]:
        plot_countplot(
            df=df_skewness_treated,
            column=col,
            output_path=resolve_project_path(root, f"figures/eda/count_{col}.png"),
        )

    plot_regplot(
        df=df_skewness_treated,
        x_col="carat",
        y_col="price",
        output_path=resolve_project_path(root, "figures/eda/carat_vs_price_regplot.png"),
    )

    avg_price_by_cut = build_price_category_summary(df_skewness_treated, "cut")
    avg_price_by_color = build_price_category_summary(df_skewness_treated, "color")
    avg_price_by_clarity = build_price_category_summary(df_skewness_treated, "clarity")

    plot_avg_price_barplot(
        summary_df=avg_price_by_cut,
        category_col="cut",
        output_path=resolve_project_path(root, "figures/eda/avg_price_by_cut.png"),
    )
    plot_avg_price_barplot(
        summary_df=avg_price_by_color,
        category_col="color",
        output_path=resolve_project_path(root, "figures/eda/avg_price_by_color.png"),
    )
    plot_avg_price_barplot(
        summary_df=avg_price_by_clarity,
        category_col="clarity",
        output_path=resolve_project_path(root, "figures/eda/avg_price_by_clarity.png"),
    )

    pairplot_df = build_pairplot_frame(
        df=df_skewness_treated,
        columns=["price", "carat", "x", "y", "z"],
        sample_size=3000,
        random_state=42,
    )
    plot_pairplot(
        df=pairplot_df,
        output_path=resolve_project_path(root, "figures/eda/pairplot.png"),
    )

    corr_df = build_correlation_matrix(
        df=df_skewness_treated,
        columns=["price", "carat", "depth", "table", "x", "y", "z"],
    )
    plot_correlation_heatmap(
        corr_df=corr_df,
        output_path=resolve_project_path(root, "figures/eda/correlation_heatmap.png"),
    )

    plot_numeric_boxplot_grid(
        df=df_skewness_treated,
        columns=["price", "carat", "depth", "table", "x", "y", "z"],
        output_path=resolve_project_path(root, "figures/eda/boxplots_numeric_features.png"),
    )

    logger.info("Building EDA report...")
    univariate_summary = build_univariate_summary(
        df_skewness_treated,
        columns=["price", "carat", "depth", "table", "x", "y", "z"],
    )
    carat_price_summary = build_carat_price_summary(df_skewness_treated)

    observations = [
        "Price increases strongly with carat, making carat one of the most important explanatory variables.",
        "x, y, and z remain highly related to carat and likely introduce multicollinearity in linear-style models.",
        "Cut, color, and clarity each show meaningful average price differences and should contribute predictive value.",
        "Outlier clipping and skewness treatment reduce the influence of extreme values while preserving row count.",
        "Even after treatment, non-linearity is still likely present, so both transformed linear models and tree-based models should be compared later.",
    ]

    report_text = build_eda_report(
        df=df_skewness_treated,
        univariate_summary_df=univariate_summary,
        carat_price_summary=carat_price_summary,
        avg_price_by_cut_df=avg_price_by_cut,
        avg_price_by_color_df=avg_price_by_color,
        avg_price_by_clarity_df=avg_price_by_clarity,
        corr_df=corr_df,
        observations=observations,
        figure_paths={
            "dist_price": "figures/eda/dist_price.png",
            "dist_carat": "figures/eda/dist_carat.png",
            "dist_x": "figures/eda/dist_x.png",
            "dist_y": "figures/eda/dist_y.png",
            "dist_z": "figures/eda/dist_z.png",
            "count_cut": "figures/eda/count_cut.png",
            "count_color": "figures/eda/count_color.png",
            "count_clarity": "figures/eda/count_clarity.png",
            "carat_vs_price_regplot": "figures/eda/carat_vs_price_regplot.png",
            "avg_price_by_cut": "figures/eda/avg_price_by_cut.png",
            "avg_price_by_color": "figures/eda/avg_price_by_color.png",
            "avg_price_by_clarity": "figures/eda/avg_price_by_clarity.png",
            "pairplot": "figures/eda/pairplot.png",
            "correlation_heatmap": "figures/eda/correlation_heatmap.png",
            "boxplots_numeric_features": "figures/eda/boxplots_numeric_features.png",
        },
    )
    save_text_file(report_text, report_path)

    logger.info("EDA pipeline completed successfully.")
    return {
        "processed_input_path": processed_input_path,
        "outliers_treated_path": outliers_treated_path,
        "skewness_treated_path": skewness_treated_path,
        "report_path": report_path,
        "outlier_summary_before": outlier_summary_before,
        "outlier_bounds_df": outlier_bounds_df,
        "skewness_before": skewness_before,
        "skewness_after": skewness_after,
        "selected_transformations": selected_transformations,
        "avg_price_by_cut": avg_price_by_cut,
        "avg_price_by_color": avg_price_by_color,
        "avg_price_by_clarity": avg_price_by_clarity,
        "corr_df": corr_df,
    }


if __name__ == "__main__":
    results = run_eda_pipeline()
    print("EDA pipeline completed successfully.")
    print("Outlier-treated dataset:", results["outliers_treated_path"])
    print("Skewness-treated dataset:", results["skewness_treated_path"])
    print("EDA report:", results["report_path"])