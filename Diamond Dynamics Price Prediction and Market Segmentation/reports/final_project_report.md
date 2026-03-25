# Diamond Dynamics: Price Prediction and Market Segmentation  
## Final Project Report

## 1. Project Overview

This project builds a complete end-to-end machine learning workflow around the diamonds dataset with two connected objectives:

1. **Price Prediction** using regression
2. **Market Segmentation** using clustering

The implementation is modular and production-oriented. The codebase is split into reusable source modules for:

- data loading and cleaning
- validation and preprocessing
- EDA
- feature engineering and feature selection
- regression training and evaluation
- clustering training and evaluation
- inference utilities
- visualization helpers
- Streamlit deployment

---

## 2. Problem Statement

Diamond valuation depends on physical size, proportions, and quality-related attributes such as cut, color, and clarity. Businesses also need to group inventory into interpretable product segments for pricing strategy, inventory organization, and customer-facing positioning.

This project addresses both needs by building:

- a regression system to predict price
- a clustering system to segment diamonds into market groups

---

## 3. Dataset and Core Variables

The project is built around a diamonds dataset with:

### Target
- `price`

### Raw Numeric Features
- `carat`
- `depth`
- `table`
- `x`
- `y`
- `z`

### Raw Categorical Features
- `cut`
- `color`
- `clarity`

These are also the core fields used in inference through the Streamlit app.

---

## 4. Data Pipeline Implementation

The data layer is implemented through functions in `src/data/`.

### Main cleaning and validation functions
- `load_raw_dataset`
- `build_missing_summary`
- `build_dataset_summary`
- `detect_missing_and_invalid_values`
- `decide_columns_to_drop`
- `mark_invalid_xyz_as_missing`
- `remove_impossible_core_rows`
- `impute_missing_values`
- `clean_diamonds_dataset`

### Actual preprocessing rules used
From the implemented functions and configs:

- invalid `x`, `y`, `z` values less than or equal to zero are treated as missing
- impossible rows are removed based on strictly positive core fields
- numeric columns are imputed using median
- categorical columns are imputed using most frequent values
- regression downstream uses one-hot encoding
- clustering downstream uses ordinal encoding and scaling

This makes the cleaning layer reproducible and artifact-friendly.

---

## 5. Exploratory Data Analysis

The EDA layer is implemented across:

- `src/eda/univariate.py`
- `src/eda/bivariate.py`
- `src/eda/multivariate.py`
- `src/eda/eda_report.py`

### Key EDA functions
- `build_univariate_summary`
- `build_outlier_summary`
- `compute_skewness_table`
- `evaluate_skew_transforms`
- `build_price_category_summary`
- `build_carat_price_summary`
- `build_correlation_matrix`
- `build_eda_report`

### What the EDA phase contributes
- target and feature distribution understanding
- outlier diagnostics
- skewness review and transformation evaluation
- category-level price comparisons
- correlation structure analysis

This phase supports both modeling quality and project storytelling.

---

## 6. Feature Engineering

The feature engineering layer is implemented in `src/features/build_features.py`.

### Core functions
- `load_usd_inr_rate`
- `safe_divide`
- `create_carat_category`
- `add_engineered_features`
- `build_feature_documentation`
- `build_feature_engineering_report`

### Engineered features actually created
The implementation creates the following:

- `price_inr`
- `volume`
- `volume_proxy`
- `price_per_carat`
- `dimension_ratio`
- `carat_category`
- `length_width_ratio`
- `depth_pct_from_dimensions`
- `table_depth_interaction`
- `carat_squared`
- `table_to_depth_ratio`
- `face_area`

### Important modeling rules
The code and reports also show that:

- `price_inr` is reporting-only
- `price_per_carat` is analysis-only because it depends on the target
- clustering excludes leakage-style target-dependent features
- selected feature subsets are saved for regression and clustering separately

---

## 7. Feature Selection and Encoding

The feature selection layer is implemented in `src/features/feature_selection.py` and `src/features/encoding.py`.

### Main functions
- `compute_regression_feature_importance`
- `identify_high_correlation_pairs`
- `compute_vif_table`
- `select_regression_features`
- `select_clustering_features`
- `build_regression_preprocessor`
- `build_clustering_preprocessor`

### Purpose
This layer reduces redundancy, checks multicollinearity, and creates modeling-ready encoders for the two task types:

- regression: one-hot encoding
- clustering: ordinal encoding plus scaling

---

## 8. Regression Modeling

The regression training workflow is implemented across:

- `src/modeling/model_factory.py`
- `src/modeling/metrics.py`
- `src/modeling/evaluate_regression.py`
- `src/modeling/train_regression.py`

### Main modeling functions
- `infer_feature_types`
- `get_supported_regression_estimators`
- `build_model_pipeline`
- `evaluate_single_regression_model`
- `rank_regression_models`
- `create_regression_evaluation_outputs`
- `train_regression_models`

### Estimators supported by the implementation
The code builds and compares:

- `linear_regression`
- `decision_tree_regressor`
- `random_forest_regressor`
- `knn_regressor`
- optional `xgboost_regressor`

### Metric logic
The regression metrics layer computes:

- MAE
- MSE
- RMSE
- R²

The training flow also applies `log1p(price)` when configured, then inverts predictions for reporting.

### Final observed result
From the saved regression evaluation report, the best model is:

- `xgboost_regressor`

with the top-ranked regression performance among the trained candidates.

---

## 9. ANN Regression

The project also includes an ANN regression branch through:

- `src/modeling/train_ann.py`
- `src/modeling/evaluate_ann.py`

### Included ANN utilities
- seed setting
- PyTorch-based `DiamondANNRegressor`
- dataloader preparation
- ANN training flow
- artifact loading and result summarization

This extends the project beyond classical ML and shows experimentation with neural regression.

---

## 10. Clustering and Market Segmentation

The clustering workflow is implemented across:

- `src/modeling/train_clustering.py`
- `src/modeling/evaluate_clustering.py`

### Main clustering functions
- `prepare_clustering_input_dataset`
- `apply_optional_pca`
- `compute_internal_clustering_metrics`
- `run_elbow_search`
- `train_kmeans_candidates`
- `train_dbscan_candidates`
- `train_agglomerative_candidates`
- `compare_clustering_models`
- `select_best_model_bundle`
- `train_clustering_pipeline`
- `save_clustering_outputs`

### Cluster interpretation functions
- `build_cluster_summary`
- `build_cluster_name_mapping`
- `apply_cluster_name_mapping`

### Candidate model families used
- KMeans
- Agglomerative Clustering
- DBSCAN

### Final observed clustering result
From the saved project reports, the best selected clustering model is:

- `dbscan`

The workflow then builds profile summaries and assigns descriptive cluster names for business readability.

---

## 11. Inference Layer

The inference utilities are implemented in:

- `src/inference/input_schema.py`
- `src/inference/postprocess.py`
- `src/inference/predict_price.py`
- `src/inference/predict_cluster.py`

### Price inference
`predict_price_from_dict`:
- builds a single-row input frame
- adds runtime engineered features
- predicts using saved regression artifacts
- inverse-transforms the price if needed
- converts the prediction to INR
- maps the result into a price band

### Cluster inference
`predict_cluster_from_dict`:
- builds a single-row input frame
- adds runtime engineered features
- applies the saved clustering preprocessor
- predicts cluster label
- maps the cluster to a descriptive segment name

This inference layer is what makes the app deployment practical and reusable.

---

## 12. Streamlit Application

The app layer is implemented through:

- `streamlit_app/app.py`
- `streamlit_app/pages/1_Price_Prediction.py`
- `streamlit_app/pages/2_Market_Segmentation.py`
- `streamlit_app/components/*`
- `streamlit_app/utils/*`

### App behavior grounded in the actual code
- the home page hides duplicate sidebar navigation and uses custom styling
- the sidebar provides project info, navigation, feature counts, and usage tips
- the same validated input schema is used for both prediction pages
- the app loads artifacts dynamically through helper utilities
- validation checks dimensions, category values, and suspicious geometry before prediction

### Main app outputs
- predicted price in USD and INR
- price band label
- predicted cluster
- mapped cluster name
- optional engineered feature preview

---

## 13. Artifacts and Reports

The code saves multiple deliverables such as:

### Regression outputs
- trained pipelines
- best regression model
- preprocessing pipeline
- metrics table
- predictions table
- regression plots
- regression evaluation report

### Clustering outputs
- best clustering bundle
- cluster assignments
- cluster summary
- silhouette and inertia result tables
- elbow plot
- PCA plots
- clustering report
- model selection report
- PCA report

This artifact structure supports both debugging and portfolio presentation.

---

## 14. Visual Deliverables

The final project presentation should include these screenshots:

- `docs/screenshots/eda_distribution_price.png`
- `docs/screenshots/model_comparison_table.png`
- `docs/screenshots/cluster_pca_plot.png`
- `docs/screenshots/streamlit_home.png`
- `docs/screenshots/streamlit_price_prediction.png`
- `docs/screenshots/streamlit_cluster_prediction.png`

These visuals connect the notebook, reports, and README into a polished final layer.

---

## 15. Business Value

This project provides value in several ways:

- supports diamond price estimation
- supports product segmentation
- helps classify inventory into interpretable commercial groups
- demonstrates full ML lifecycle capability
- provides an interactive deployment layer for demonstration

It is not just a model training exercise; it is a full mini-product.

---

## 16. Limitations

Current limitations include:

- dependence on the given dataset distribution
- clustering interpretability being data-dependent
- no live serving or API layer yet
- no formal experiment tracking system
- no post-deployment drift monitoring

---

## 17. Future Enhancements

Recommended improvements:

- add SHAP explainability
- add batch CSV upload in Streamlit
- deploy publicly
- add MLflow or similar experiment tracking
- add monitoring for changing market data
- expose predictions through an API

---

## 18. Final Conclusion

This project successfully combines:

- structured preprocessing
- domain-aware feature engineering
- comparative regression modeling
- unsupervised segmentation
- descriptive cluster naming
- inference helpers
- Streamlit deployment
- final documentation

It is a strong end-to-end portfolio project that shows both technical implementation depth and practical presentation quality.