# Modeling Notes

## Purpose

This document records the real modeling logic implemented in the project codebase for both:

- diamond price prediction
- market segmentation

It is based on the current `src/modeling`, `src/features`, `src/inference`, and `streamlit_app` implementations.

---

## 1. Regression Modeling Notes

### Code locations
- `src/modeling/model_factory.py`
- `src/modeling/metrics.py`
- `src/modeling/evaluate_regression.py`
- `src/modeling/train_regression.py`

### Training flow
The regression workflow is built around these main steps:

1. prepare train and test splits
2. infer numeric and categorical columns dynamically
3. build a preprocessing + estimator pipeline
4. train multiple regression models
5. evaluate them on held-out test data
6. rank models by performance
7. save best model and outputs

### Important implementation details
- target column is `price`
- the training pipeline can use `log1p(price)` before fitting
- predictions are inverse-transformed for reporting when configured
- numeric and categorical preprocessing are combined in a single pipeline
- scaling is applied only where appropriate

### Supported regression estimators
The current code supports:

- `linear_regression`
- `decision_tree_regressor`
- `random_forest_regressor`
- `knn_regressor`
- `xgboost_regressor` when `xgboost` is installed

### Why this design works
The dataset mixes:
- continuous variables
- categorical quality grades
- nonlinear relationships
- engineered features

So a single plain linear baseline would be too limited. The comparative approach helps identify stronger nonlinear models.

---

## 2. Regression Metrics Used

### Implemented metrics
The project computes:

- `mae`
- `mse`
- `rmse`
- `r2`

### Why these matter
- **MAE** captures average absolute prediction error
- **MSE** penalizes larger mistakes more heavily
- **RMSE** makes the error scale easier to interpret
- **R²** measures explained variance

Together they provide a more complete evaluation picture than any single metric alone.

---

## 3. Preprocessing and Encoding Notes

### Regression preprocessing
The regression pipeline uses a dynamically built `ColumnTransformer`:

- numeric branch:
  - median imputation
  - optional standard scaling
- categorical branch:
  - most-frequent imputation
  - one-hot encoding with `handle_unknown="ignore"`

### Why dynamic inference is useful
Instead of hardcoding every feature transformation inside training, the code infers numeric and categorical roles from the actual training dataframe. That makes the workflow more reusable when selected feature sets change.

---

## 4. Feature Engineering Notes

### Implemented engineered features
The project builds:

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

### Important modeling exclusions
The code and reports make an important distinction:

- `price_inr` is reporting-only
- `price_per_carat` is EDA-only because it uses the target
- not every engineered feature is necessarily part of the final regression training input

This is good practice because engineered features should only be kept when they are useful and leakage-safe.

---

## 5. Feature Selection Notes

### Implemented analysis tools
- regression feature importance via tree-based importance
- high-correlation pair detection
- VIF computation
- correlation heatmap
- separate selectors for regression and clustering

### Why this matters
Feature engineering can improve signal, but it can also create:
- redundancy
- multicollinearity
- unstable model behavior

The feature selection stage helps reduce those risks.

---

## 6. Clustering Modeling Notes

### Code locations
- `src/modeling/train_clustering.py`
- `src/modeling/evaluate_clustering.py`

### Main clustering workflow
The clustering workflow:

1. prepares a clustering-specific input dataset
2. excludes inappropriate fields where necessary
3. preprocesses numeric and categorical inputs
4. runs multiple clustering candidate families
5. compares internal metrics
6. selects the best model bundle
7. creates cluster summaries
8. maps numeric clusters to descriptive names
9. saves artifacts and plots

### Candidate model families
The implemented clustering comparison includes:

- KMeans
- Agglomerative Clustering
- DBSCAN

### Why multiple clustering methods are used
Different clustering families capture different structure:

- KMeans works well for compact centroid-based groups
- Agglomerative is useful for hierarchical grouping
- DBSCAN is useful for irregular density-based grouping and noise handling

Using more than one makes the segmentation stage more defensible.

---

## 7. Clustering Evaluation Notes

### Implemented internal metrics
- silhouette score
- Davies-Bouldin score
- Calinski-Harabasz score
- inertia for KMeans
- elbow search
- optional PCA projection for visualization

### Selection logic
The comparison dataframe ranks candidate solutions and then the best bundle is selected. The code is careful about a key issue: it checks whether the chosen labels cover the full dataset length before using them as final assignments.

That is an important quality safeguard, especially when some candidate methods may be trained on sampled subsets.

---

## 8. Cluster Summary and Naming Notes

After fitting the selected clustering solution, the project builds:

- cluster size
- average and median carat
- average and median price
- average depth
- average table
- dominant cut
- dominant color
- dominant clarity
- category distributions

Then `build_cluster_name_mapping` converts raw cluster IDs into business-friendly labels such as:

- entry/value segment
- mid segment
- premium segment
- luxury segment

This makes the clustering results much easier to explain in the app and reports.

---

## 9. ANN Regression Notes

### Code locations
- `src/modeling/train_ann.py`
- `src/modeling/evaluate_ann.py`

### What is implemented
The project includes a PyTorch ANN regressor with:
- configurable hidden layers
- dropout
- batch normalization
- training loop with dataloaders
- saved training history and evaluation summary

This expands the project beyond traditional ML and shows experimentation with deep learning for tabular regression.

---

## 10. Inference Notes

### Price inference
`predict_price_from_dict`:
- builds the input row
- adds runtime engineered features
- predicts using the saved regression artifact
- inverse-transforms logged outputs if needed
- converts to INR
- maps the value to a price band

### Cluster inference
`predict_cluster_from_dict`:
- builds the input row
- adds runtime engineered features
- applies the saved preprocessor
- predicts the cluster label
- maps it to the saved cluster name

These functions are central because they make the training code deployable.

---

## 11. Deployment Alignment Notes

The Streamlit app does not reimplement model logic manually. Instead, it relies on:

- saved artifacts
- shared validation helpers
- inference functions
- common input-form handling

That is the right structure because deployment stays aligned with the actual model pipeline rather than drifting into a separate code path.

---

## 12. Final Modeling Takeaway

The modeling layer of this project is strong because it is:

- comparative rather than single-model
- modular rather than notebook-only
- inference-aware rather than training-only
- interpretable rather than raw-cluster-only
- deployment-ready rather than demo-limited

That makes the project suitable both as a learning project and as a portfolio project.