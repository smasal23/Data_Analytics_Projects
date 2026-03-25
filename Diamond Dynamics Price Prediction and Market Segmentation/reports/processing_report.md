# Preprocessing Report

    ## 1. Dataset Snapshot
    - Raw shape: `53940 rows × 10 columns`
    - Cleaned shape: `53940 rows × 10 columns`
    - Rows removed due to impossible core values (`carat <= 0` or `price <= 0`): `0`
    - Dropped unexpected columns: `None`
    
    ## 2. Missing Value Review
    | column   |   missing_count |   missing_pct |
|:---------|----------------:|--------------:|
| carat    |               0 |             0 |
| clarity  |               0 |             0 |
| color    |               0 |             0 |
| cut      |               0 |             0 |
| depth    |               0 |             0 |
| price    |               0 |             0 |
| table    |               0 |             0 |
| x        |               0 |             0 |
| y        |               0 |             0 |
| z        |               0 |             0 |
    
    ### Missing values after cleaning/imputation
    | column   |   missing_count |   missing_pct |
|:---------|----------------:|--------------:|
| carat    |               0 |             0 |
| clarity  |               0 |             0 |
| color    |               0 |             0 |
| cut      |               0 |             0 |
| depth    |               0 |             0 |
| price    |               0 |             0 |
| table    |               0 |             0 |
| x        |               0 |             0 |
| y        |               0 |             0 |
| z        |               0 |             0 |
    
    ## 3. Invalid x, y, z Review
    - Rule applied: `x`, `y`, `z` values of 0 or negative are treated as invalid and converted to null before imputation.
    
    | column   |   zero_count |   zero_pct |
|:---------|-------------:|-----------:|
| x        |            8 |     0.0148 |
| y        |            7 |     0.013  |
| z        |           20 |     0.0371 |
    
    ## 4. Impossible Numeric Values
    - Rule applied:
      - `carat <= 0` -> row removed
      - `price <= 0` -> row removed
      - invalid `x`, `y`, `z` -> set to null, then imputed
    
    | column   |   non_positive_count |   negative_count |
|:---------|---------------------:|-----------------:|
| carat    |                    0 |                0 |
| depth    |                    0 |                0 |
| table    |                    0 |                0 |
| x        |                    8 |                0 |
| y        |                    7 |                0 |
| z        |                   20 |                0 |
| price    |                    0 |                0 |
    
    ## 5. Column Separation
    - Numeric columns: `['carat', 'depth', 'table', 'x', 'y', 'z']`
    - Categorical columns: `['cut', 'color', 'clarity']`
    
    ## 6. Preprocessing Strategy
    - Numeric missing value strategy: `median`
    - Categorical missing value strategy: `most_frequent`
    - Categorical encoding for downstream modeling: `onehot` for regression; `ordinal` for clustering
    - Numeric scaling for downstream modeling: `standard` where required by model family
    
    ## 7. Dataset-level Imputation Values Used
    ```python
    {'carat': 0.7, 'depth': 61.8, 'table': 57.0, 'x': 5.7, 'y': 5.71, 'z': 3.53, 'cut': 'Ideal', 'color': 'G', 'clarity': 'SI1'}
    