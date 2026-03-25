from __future__ import annotations

from pathlib import Path
from typing import Any

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import make_scorer
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover
    XGBRegressor = None

from src.utils.config import load_project_configs
from src.utils.paths import find_project_root


# Infer numeric and categorical predictor columns from the actual modeling dataframe.
def infer_feature_types(df, target_col: str = "price"):
    feature_df = df.drop(columns = [target_col], errors = "ignore").copy()

    numeric_cols = [col for col in feature_df.columns if feature_df[col].dtype != "object"]
    categorical_cols = [col for col in feature_df.columns if feature_df[col].dtype == "object"]

    return numeric_cols, categorical_cols


# Build a preprocessing object from the actual train dataframe columns.
def build_dynamic_regression_preprocessor(
    numeric_cols: list[str],
    categorical_cols: list[str],
    scale_numeric: bool = True,
    numeric_imputation: str = "median",
    categorical_imputation: str = "most_frequent",
    handle_unknown: str = "ignore",
    drop_first: bool = False,
):
    numeric_steps = [("imputer", SimpleImputer(strategy = numeric_imputation))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    numeric_pipeline = Pipeline(steps = numeric_steps)

    categorical_pipeline = Pipeline(
        steps = [
            ("imputer", SimpleImputer(strategy = categorical_imputation)),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown = handle_unknown,
                    sparse_output = False,
                    drop = "first" if drop_first else None,
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


def get_model_registry(project_root: str | Path | None = None):
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)
    return configs["model_registry"]


def get_regression_config(project_root: str | Path | None = None):
    root = find_project_root(project_root) if project_root else find_project_root()
    configs = load_project_configs(root)
    return configs["regression_config"]


# Return the project-requested regression estimators.
def get_supported_regression_estimators(
    random_state: int = 42,
) -> dict[str, Any]:
    """

    """
    estimators: dict[str, Any] = {
        "linear_regression": LinearRegression(),
        "decision_tree_regressor": DecisionTreeRegressor(
            random_state = random_state,
            max_depth = 12,
            min_samples_split = 5,
            min_samples_leaf = 2,
        ),
        "random_forest_regressor": RandomForestRegressor(
            n_estimators = 300,
            random_state = random_state,
            n_jobs = -1,
            max_depth = None,
            min_samples_split = 2,
            min_samples_leaf = 1,
        ),
        "knn_regressor": KNeighborsRegressor(
            n_neighbors = 7,
            weights = "distance",
            p = 2,
        ),
    }

    if XGBRegressor is not None:
        estimators["xgboost_regressor"] = XGBRegressor(
            n_estimators = 400,
            learning_rate = 0.05,
            max_depth = 6,
            subsample = 0.9,
            colsample_bytree = 0.9,
            objective = "reg:squarederror",
            random_state = random_state,
            n_jobs = -1,
        )

    return estimators


# Build preprocessing + estimator pipeline.
def build_model_pipeline(
    model_name: str,
    estimator,
    numeric_cols: list[str],
    categorical_cols: list[str],
    project_root: str | Path | None = None,
):
    regression_cfg = get_regression_config(project_root)
    preprocessing_cfg = regression_cfg["preprocessing"]

    scale_numeric = model_name in {"linear_regression", "knn_regressor"}

    preprocessor = build_dynamic_regression_preprocessor(
        numeric_cols = numeric_cols,
        categorical_cols = categorical_cols,
        scale_numeric = scale_numeric,
        numeric_imputation = preprocessing_cfg["numeric_imputation"],
        categorical_imputation = preprocessing_cfg["categorical_imputation"],
        handle_unknown = preprocessing_cfg["handle_unknown_categories"],
        drop_first = preprocessing_cfg["drop_first"],
    )

    return Pipeline(
        steps = [
            ("preprocessor", preprocessor),
            ("model", estimator),
        ]
    )


# Mark models that support built-in feature importance extraction.
def get_tree_feature_importance_support(model_name: str) -> bool:
    return model_name in {
        "decision_tree_regressor",
        "random_forest_regressor",
        "xgboost_regressor",
    }