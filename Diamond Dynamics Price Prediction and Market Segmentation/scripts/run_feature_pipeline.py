from __future__ import annotations

from pathlib import Path
import joblib
import pandas as pd

from src.utils.config import load_project_configs
from src.utils.paths import find_project_root, resolve_project_path
from src.utils.io import save_csv_file, save_text_file, ensure_dir
from src.utils.logger import get_logger

from src.features.build_features import (
    load_feature_input_dataset,
    load_usd_inr_rate,
    add_engineered_features,
    plot_engineered_feature_distributions,
    build_feature_engineering_report,
)
from src.features.feature_selection import (
    select_regression_features,
    select_clustering_features,
    plot_feature_importance,
    plot_correlation_heatmap_for_selected,
    plot_vif_summary,
)
from src.features.encoding import (
    build_regression_preprocessor,
    build_clustering_preprocessor,
    transform_with_preprocessor,
)
from src.features.scaling import fit_numeric_scaler


def run_feature_pipeline(project_root: str | Path | None = None) -> dict:
    logger = get_logger("scripts.run_feature_pipeline")
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    features_cfg = configs["features_config"]
    main_cfg = configs["main_config"]
    random_state = main_cfg["project"]["random_state"]

    processed_dir = resolve_project_path(root, "data/processed")
    figures_dir = resolve_project_path(root, "figures/feature_engineering")
    artifacts_dir = resolve_project_path(root, "artifacts/preprocessing")
    reports_dir = resolve_project_path(root, "reports")

    for path in [processed_dir, figures_dir, artifacts_dir, reports_dir]:
        ensure_dir(path)

    logger.info("Loading cleaned processed dataset...")
    df = load_feature_input_dataset(root)

    logger.info("Loading USD-INR rate...")
    usd_inr_rate = load_usd_inr_rate(root)

    logger.info("Creating engineered features...")
    df_fe, feature_doc_df = add_engineered_features(df=df, usd_inr_rate=usd_inr_rate)

    raw_numeric_cols = features_cfg["schema"]["numeric_features"]
    raw_categorical_cols = features_cfg["schema"]["categorical_features"]

    engineered_numeric_cols = [
        "volume",
        "volume_proxy",
        "dimension_ratio",
        "length_width_ratio",
        "depth_pct_from_dimensions",
        "table_depth_interaction",
        "carat_squared",
        "table_to_depth_ratio",
        "face_area",
    ]
    engineered_categorical_cols = ["carat_category"]

    logger.info("Saving engineered master dataset...")
    feature_engineered_path = resolve_project_path(root, "data/processed/diamonds_feature_engineered.csv")
    save_csv_file(df_fe, feature_engineered_path, index=False)

    logger.info("Plotting engineered feature distributions...")
    engineered_fig_path = resolve_project_path(root, "figures/feature_engineering/engineered_feature_distributions.png")
    plot_engineered_feature_distributions(df_fe, engineered_fig_path)

    logger.info("Running regression feature selection...")
    regression_selection = select_regression_features(
        df=df_fe,
        raw_numeric_cols=raw_numeric_cols,
        raw_categorical_cols=raw_categorical_cols,
        engineered_numeric_cols=engineered_numeric_cols,
        engineered_categorical_cols=engineered_categorical_cols,
        target_col="price",
        importance_threshold=0.01,
        corr_threshold=0.90,
        vif_threshold=10.0,
        random_state=random_state,
    )

    logger.info("Running clustering feature selection...")
    clustering_selection = select_clustering_features(
        df=df_fe,
        raw_numeric_cols=raw_numeric_cols,
        raw_categorical_cols=raw_categorical_cols,
        engineered_numeric_cols=engineered_numeric_cols,
        engineered_categorical_cols=engineered_categorical_cols,
        corr_threshold=0.90,
    )

    logger.info("Saving feature selection figures...")
    plot_feature_importance(
        regression_selection["importance_df"],
        resolve_project_path(root, "figures/feature_engineering/feature_importance_baseline.png"),
    )

    selected_corr_cols = regression_selection["selected_numeric_features"]
    if len(selected_corr_cols) >= 2:
        plot_correlation_heatmap_for_selected(
            df_fe,
            selected_corr_cols,
            resolve_project_path(root, "figures/feature_engineering/correlation_selected_features.png"),
        )

    plot_vif_summary(
        regression_selection["vif_df"],
        resolve_project_path(root, "figures/feature_engineering/vif_summary_plot.png"),
    )

    regression_features = regression_selection["selected_features"]
    regression_dataset = df_fe[regression_features + ["price"]].copy()

    clustering_features = clustering_selection["selected_features"]
    clustering_dataset = df_fe[clustering_features].copy()

    # Force no target leakage in clustering deliverable.
    clustering_dataset = clustering_dataset.drop(columns=["price"], errors="ignore")

    logger.info("Saving modeling datasets...")
    regression_dataset_path = resolve_project_path(root, "data/processed/regression_model_input.csv")
    clustering_dataset_path = resolve_project_path(root, "data/processed/clustering_model_input.csv")

    save_csv_file(regression_dataset, regression_dataset_path, index=False)
    save_csv_file(clustering_dataset, clustering_dataset_path, index=False)

    regression_numeric = [col for col in regression_dataset.columns if col != "price" and regression_dataset[col].dtype != "object"]
    regression_categorical = [col for col in regression_dataset.columns if col != "price" and regression_dataset[col].dtype == "object"]

    clustering_numeric = [col for col in clustering_dataset.columns if clustering_dataset[col].dtype != "object"]
    clustering_categorical = [col for col in clustering_dataset.columns if clustering_dataset[col].dtype == "object"]

    logger.info("Building preprocessors...")
    regression_preprocessor = build_regression_preprocessor(
        numeric_cols=regression_numeric,
        categorical_cols=regression_categorical,
        project_root=root,
    )
    clustering_preprocessor = build_clustering_preprocessor(
        numeric_cols=clustering_numeric,
        categorical_cols=clustering_categorical,
        project_root=root,
    )

    logger.info("Fitting preprocessors...")
    regression_X = regression_dataset.drop(columns=["price"])
    regression_transformed_df = transform_with_preprocessor(regression_X, regression_preprocessor, fit=True)
    clustering_transformed_df = transform_with_preprocessor(clustering_dataset, clustering_preprocessor, fit=True)

    logger.info("Saving preprocessors and components...")
    numeric_imputer = regression_preprocessor.named_transformers_["num"].named_steps["imputer"]
    categorical_encoder = clustering_preprocessor.named_transformers_["cat"].named_steps["encoder"]

    joblib.dump(numeric_imputer, resolve_project_path(root, "artifacts/preprocessing/numeric_imputer.pkl"))
    joblib.dump(categorical_encoder, resolve_project_path(root, "artifacts/preprocessing/categorical_encoder.pkl"))
    joblib.dump(regression_preprocessor, resolve_project_path(root, "artifacts/preprocessing/regression_preprocessor.pkl"))
    joblib.dump(clustering_preprocessor, resolve_project_path(root, "artifacts/preprocessing/clustering_preprocessor.pkl"))

    scaler_regression = fit_numeric_scaler(regression_dataset, regression_numeric)
    scaler_clustering = fit_numeric_scaler(clustering_dataset, clustering_numeric)

    joblib.dump(scaler_regression, resolve_project_path(root, "artifacts/preprocessing/scaler_regression.pkl"))
    joblib.dump(scaler_clustering, resolve_project_path(root, "artifacts/preprocessing/scaler_clustering.pkl"))

    logger.info("Writing markdown report...")
    report_text = build_feature_engineering_report(
        df=df_fe,
        feature_doc_df=feature_doc_df,
        usd_inr_rate=usd_inr_rate,
        selected_regression_features=regression_features,
        selected_clustering_features=clustering_dataset.columns.tolist(),
    )
    report_path = resolve_project_path(root, "reports/feature_engineering_report.md")
    save_text_file(report_text, report_path)

    logger.info("Feature pipeline completed.")
    return {
        "feature_engineered_path": feature_engineered_path,
        "regression_dataset_path": regression_dataset_path,
        "clustering_dataset_path": clustering_dataset_path,
        "report_path": report_path,
        "regression_transformed_shape": regression_transformed_df.shape,
        "clustering_transformed_shape": clustering_transformed_df.shape,
        "regression_features": regression_features,
        "clustering_features": clustering_dataset.columns.tolist(),
        "usd_inr_rate": usd_inr_rate,
    }


if __name__ == "__main__":
    results = run_feature_pipeline()
    print("Feature engineering pipeline completed successfully.")
    print("Feature engineered dataset:", results["feature_engineered_path"])
    print("Regression dataset:", results["regression_dataset_path"])
    print("Clustering dataset:", results["clustering_dataset_path"])
    print("Report:", results["report_path"])
    print("Regression transformed shape:", results["regression_transformed_shape"])
    print("Clustering transformed shape:", results["clustering_transformed_shape"])