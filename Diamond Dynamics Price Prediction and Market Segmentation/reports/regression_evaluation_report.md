# Regression Evaluation Report

## Best Model

- Selected model: `xgboost_regressor`

## Model Comparison

|      mae |              mse |      rmse |         r2 | model_name              |   rank |
|---------:|-----------------:|----------:|-----------:|:------------------------|-------:|
|  274.759 | 294178           |   542.382 |   0.981495 | xgboost_regressor       |      1 |
|  279.89  | 305725           |   552.924 |   0.980768 | random_forest_regressor |      2 |
|  358.366 | 468691           |   684.61  |   0.970517 | decision_tree_regressor |      3 |
|  405.324 | 602264           |   776.057 |   0.962114 | knn_regressor           |      4 |
| 1855.89  |      3.14373e+08 | 17730.6   | -18.7759   | linear_regression       |      5 |
