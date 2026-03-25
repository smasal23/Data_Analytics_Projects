# Feature Engineering Report0

    ## 1. Phase Summary
    - Input dataset shape: `53940 rows × 22 columns`
    - USD to INR exchange rate used: `nan`
    - Target column: `price`
    
    ## 2. Engineered Feature Documentation
    | feature   | feature_type   | formula   | reason   | use_for_regression   | use_for_clustering   | notes   |
|-----------|----------------|-----------|----------|----------------------|----------------------|---------|
    
    ## 3. Engineered Feature Summary
    |                           |   count |   unique | top   |   freq |        mean |          std |         min |         25% |         50% |        75% |         max |
|:--------------------------|--------:|---------:|:------|-------:|------------:|-------------:|------------:|------------:|------------:|-----------:|------------:|
| volume                    |   53940 |      nan | nan   |    nan |  129.911    |   78.2152    |   31.708    |   65.2045   |  114.853    |  170.847   |  3840.6     |
| price_per_carat           |   53940 |      nan | nan   |    nan | 4008.39     | 2012.67      | 1051.16     | 2477.94     | 3495.2      | 4949.6     | 17828.8     |
| dimension_ratio           |   53940 |      nan | nan   |    nan |    1.62064  |    0.0507329 |    0.161478 |    1.59936  |    1.61705  |    1.6382  |     6.21028 |
| carat_category            |   53940 |        5 | small |  18932 |  nan        |  nan         |  nan        |  nan        |  nan        |  nan       |   nan       |
| length_width_ratio        |   53940 |      nan | nan   |    nan |    0.999424 |    0.01168   |    0.137351 |    0.992625 |    0.995745 |    1.00694 |     1.61557 |
| depth_pct_from_dimensions |   53940 |      nan | nan   |    nan |   61.7559   |    2.84136   |   16.1023   |   61.0427   |   61.8412   |   62.5251  |   619.279   |
| table_depth_interaction   |   53940 |      nan | nan   |    nan | 3547        |  138.407     | 2322        | 3448.5      | 3533.6      | 3630.8     |  5767       |
| carat_squared             |   53940 |      nan | nan   |    nan |    0.86139  |    1.05651   |    0.04     |    0.16     |    0.49     |    1.0816  |    25.1001  |
| table_to_depth_ratio      |   53940 |      nan | nan   |    nan |    0.931254 |    0.04812   |    0.683625 |    0.898876 |    0.923825 |    0.95624 |     1.62116 |
| face_area                 |   53940 |      nan | nan   |    nan |   34.1192   |   13.4895    |   13.7264   |   22.278    |   32.5464   |   42.706   |   476.501   |
    
    ## 4. Modeling Rules
    - `price_per_carat` is retained for analysis only and excluded from regression/clustering inputs.
    - `price_inr` is retained for reporting only and excluded from regression/clustering inputs.
    - Clustering-ready dataset excludes `price` as requested for the deliverable.
    
    ## 5. Final Regression Features
    `['volume', 'carat', 'depth', 'table', 'clarity', 'color', 'cut']`
    
    ## 6. Final Clustering Features
    `['carat', 'depth', 'table', 'dimension_ratio', 'length_width_ratio', 'depth_pct_from_dimensions', 'table_depth_interaction', 'table_to_depth_ratio', 'cut', 'color', 'clarity']`
    
    ## 7. Saved Outputs
    - `data/processed/diamonds_feature_engineered.csv`
    - `data/processed/regression_model_input.csv`
    - `data/processed/clustering_model_input.csv`
    - `figures/feature_engineering/engineered_feature_distributions.png`
    - `figures/feature_engineering/feature_importance_baseline.png`
    - `figures/feature_engineering/correlation_selected_features.png`
    - `figures/feature_engineering/vif_summary_plot.png`
    