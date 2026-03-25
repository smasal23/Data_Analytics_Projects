from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from src.utils.config import load_project_configs
from src.utils.paths import find_project_root


#
def load_encoding_context(project_root: str | Path | None = None):
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)

    return {
        "project_root": root,
        "features_config": configs["features_config"],
        "regression_config": configs["regression_config"],
        "clustering_config": configs["clustering_config"],
    }


def get_ordinal_category_orders(project_root: str | Path | None = None):
    ctx = load_encoding_context(project_root)
    ordinal_mappings = ctx["features_config"]["ordinal_mappings"]

    return {
        feature: list(mapping.keys())
        for feature, mapping in ordinal_mappings.items()
    }


def build_regression_preprocessor(
    numeric_cols: list[str],
    categorical_cols: list[str],
    project_root: str | Path | None = None,
):
    ctx = load_encoding_context(project_root)
    regression_cfg = ctx["regression_config"]

    numeric_pipeline = Pipeline(
        steps = [
            ("imputer", SimpleImputer(strategy = regression_cfg["preprocessing"]["numeric_imputation"])),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps = [
            ("imputer", SimpleImputer(strategy = regression_cfg["preprocessing"]["categorical_imputation"])),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown = regression_cfg["preprocessing"]["handle_unknown_categories"],
                    sparse_output = False,
                    drop = "first" if regression_cfg["preprocessing"]["drop_first"] else None,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers = [
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ],
        remainder = "drop",
        verbose_feature_names_out=False,
    )


def build_clustering_preprocessor(
    numeric_cols: list[str],
    categorical_cols: list[str],
    project_root: str | Path | None = None,
):
    ordinal_orders = get_ordinal_category_orders(project_root)

    categories = [ordinal_orders[col] for col in categorical_cols]

    numeric_pipeline = Pipeline(
        steps = [
            ("imputer", SimpleImputer(strategy = "median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps = [
            ("imputer", SimpleImputer(strategy = "most_frequent")),
            (
                "encoder",
                OrdinalEncoder(
                    categories = categories,
                    handle_unknown = "use_encoded_value",
                    unknown_value = -1,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers = [
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ],
        remainder = "drop",
        verbose_feature_names_out = False,
    )


def transform_with_preprocessor(
    df: pd.DataFrame,
    preprocessor: ColumnTransformer,
    fit: bool = True,
):
    transformed = preprocessor.fit_transform(df) if fit else preprocessor.transform(df)

    feature_names = list(preprocessor.get_feature_names_out())
    transformed_df = pd.DataFrame(transformed, columns = feature_names, index = df.index)
    return transformed_df