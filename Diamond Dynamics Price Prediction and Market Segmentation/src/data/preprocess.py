# Imports

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from src.utils.config import load_project_configs
from src.utils.paths import find_project_root


def load_preprocessing_context(project_root: str | Path | None = None):
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    return {
        "project_root": root,
        "main_config": configs["main_config"],
        "features_config": configs["features_config"],
        "regression_config": configs["regression_config"],
        "clustering_config": configs["clustering_config"]
    }


def get_feature_lists(project_root: str | Path | None = None):
    ctx = load_preprocessing_context(project_root)
    features_cfg = ctx["features_config"]

    return {
        "target_col": features_cfg["schema"]["target"],
        "numeric_cols": features_cfg["schema"]["numeric_features"],
        "categorical_cols": features_cfg["schema"]["categorical_features"],
        "ordinal_mappings": features_cfg["ordinal_mappings"],
    }


def build_numeric_pipeline(
    imputation_strategy: str = "median",
    scaling: bool = True,
):
    steps = [
        ("imputer", SimpleImputer(strategy=imputation_strategy)),
    ]

    if scaling:
        steps.append(("scaler", StandardScaler()))

    return Pipeline(steps=steps)


def build_categorical_onehot_pipeline(
    imputation_strategy: str = "most_frequent",
    handle_unknown: str = "ignore",
    drop_first: bool = False,
):
    encoder = OneHotEncoder(
        handle_unknown=handle_unknown,
        sparse_output=False,
        drop="first" if drop_first else None,
    )

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy=imputation_strategy)),
            ("encoder", encoder),
        ]
    )


def build_categorical_ordinal_pipeline(
    categories: list[list[str]],
    imputation_strategy: str = "most_frequent",
):
    encoder = OrdinalEncoder(
        categories=categories,
        handle_unknown="use_encoded_value",
        unknown_value=-1,
    )

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy=imputation_strategy)),
            ("encoder", encoder),
        ]
    )


def build_regression_preprocessor(project_root: str | Path | None = None):
    ctx = load_preprocessing_context(project_root)
    features_cfg = ctx["features_config"]
    regression_cfg = ctx["regression_config"]

    numeric_cols = features_cfg["schema"]["numeric_features"]
    categorical_cols = features_cfg["schema"]["categorical_features"]

    numeric_imputation = regression_cfg["preprocessing"]["numeric_imputation"]
    categorical_imputation = regression_cfg["preprocessing"]["categorical_imputation"]
    handle_unknown = regression_cfg["preprocessing"]["handle_unknown_categories"]
    drop_first = regression_cfg["preprocessing"]["drop_first"]
    scaling_for_linear_models = regression_cfg["preprocessing"]["scaling_for_linear_models"]

    numeric_pipeline = build_numeric_pipeline(
        imputation_strategy=numeric_imputation,
        scaling=scaling_for_linear_models,
    )

    categorical_pipeline = build_categorical_onehot_pipeline(
        imputation_strategy=categorical_imputation,
        handle_unknown=handle_unknown,
        drop_first=drop_first,
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_clustering_preprocessor(project_root: str | Path | None = None):
    ctx = load_preprocessing_context(project_root)
    features_cfg = ctx["features_config"]
    clustering_cfg = ctx["clustering_config"]

    numeric_cols = clustering_cfg["clustering"]["input_features"]["numeric"]
    categorical_cols = clustering_cfg["clustering"]["input_features"]["ordinal_encoded"]

    ordinal_mappings = features_cfg["ordinal_mappings"]
    ordinal_categories = [
        list(ordinal_mappings[col].keys())
        for col in categorical_cols
    ]

    numeric_pipeline = build_numeric_pipeline(
        imputation_strategy=clustering_cfg["preprocessing"]["numeric_imputation"],
        scaling=(clustering_cfg["preprocessing"]["scaling"] == "standard"),
    )

    categorical_pipeline = build_categorical_ordinal_pipeline(
        categories=ordinal_categories,
        imputation_strategy=clustering_cfg["preprocessing"]["categorical_imputation"],
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def summarize_preprocessing_strategy(project_root: str | Path | None = None):
    ctx = load_preprocessing_context(project_root)

    features_cfg = ctx["features_config"]
    regression_cfg = ctx["regression_config"]
    clustering_cfg = ctx["clustering_config"]

    return {
        "numeric_columns": features_cfg["schema"]["numeric_features"],
        "categorical_columns": features_cfg["schema"]["categorical_features"],
        "dataset_level_cleaning_strategy": {
            "numeric_missing": features_cfg["preprocessing"]["missing_value_strategy"]["numeric"],
            "categorical_missing": features_cfg["preprocessing"]["missing_value_strategy"]["categorical"],
            "invalid_xyz": "set 0/negative x,y,z to NaN, then impute",
            "impossible_core_rows": "remove rows where carat <= 0 or price <= 0",
        },
        "regression_pipeline_strategy": {
            "numeric_imputation": regression_cfg["preprocessing"]["numeric_imputation"],
            "categorical_imputation": regression_cfg["preprocessing"]["categorical_imputation"],
            "categorical_encoding": regression_cfg["preprocessing"]["categorical_encoding"],
            "handle_unknown_categories": regression_cfg["preprocessing"]["handle_unknown_categories"],
            "scaling_for_linear_models": regression_cfg["preprocessing"]["scaling_for_linear_models"],
        },
        "clustering_pipeline_strategy": {
            "numeric_imputation": clustering_cfg["preprocessing"]["numeric_imputation"],
            "categorical_imputation": clustering_cfg["preprocessing"]["categorical_imputation"],
            "categorical_encoding": clustering_cfg["preprocessing"]["encoding"],
            "scaling": clustering_cfg["preprocessing"]["scaling"],
        },
    }


def split_numeric_and_categorical(df: pd.DataFrame, project_root: str | Path | None = None):
    feature_lists = get_feature_lists(project_root)
    numeric_df = df[feature_lists["numeric_cols"]].copy()
    categorical_df = df[feature_lists["categorical_cols"]].copy()
    return numeric_df, categorical_df