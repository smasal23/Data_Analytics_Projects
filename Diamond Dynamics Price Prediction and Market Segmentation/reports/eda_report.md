# EDA Report — Diamond Price Prediction and Market Segmentation

    ## 1. Dataset Overview
    - Shape: `53940 rows × 10 columns`
    - Columns: `['carat', 'cut', 'color', 'clarity', 'depth', 'table', 'price', 'x', 'y', 'z']`
    - Missing cells total: `0`

    ## 2. Univariate Summary
    | column   |   count |   missing_count |      mean |   median |      std |      min |       q1 |       q3 |     max |    skewness |
|:---------|--------:|----------------:|----------:|---------:|---------:|---------:|---------:|---------:|--------:|------------:|
| price    |   53940 |               0 |  7.19001  |  7.20808 | 0.846809 |  5.46459 |  6.40715 |  7.88426 |  8.5553 |  0.00805396 |
| carat    |   53940 |               0 |  0.792558 |  0.7     | 0.457089 |  0.2     |  0.4     |  1.04    |  2      |  0.899893   |
| depth    |   53940 |               0 | 61.7494   | 61.8     | 1.43262  | 43       | 61       | 62.5     | 79      | -0.082294   |
| table    |   53940 |               0 | 57.4572   | 57       | 2.23449  | 43       | 56       | 59       | 95      |  0.796896   |
| x        |   53940 |               0 |  5.73184  |  5.7     | 1.11902  |  3.73    |  4.71    |  6.54    |  9.285  |  0.394179   |
| y        |   53940 |               0 |  5.73379  |  5.71    | 1.11113  |  3.68    |  4.72    |  6.54    |  9.27   |  0.389861   |
| z        |   53940 |               0 |  3.53936  |  3.53    | 0.691047 |  1.215   |  2.91    |  4.04    |  5.735  |  0.387198   |

    ## 3. Carat vs Price Summary
    | metric                          |        value |
|:--------------------------------|-------------:|
| pearson_correlation_carat_price |     0.921607 |
| carat_mean                      |     0.792558 |
| price_mean                      |     7.19001  |
| sample_size                     | 53940        |

    ## 4. Average Price by Cut
    | cut       |   count |   mean_price |   median_price |   min_price |   max_price |
|:----------|--------:|-------------:|---------------:|------------:|------------:|
| Fair      |    1610 |       7.4568 |         7.4748 |      5.4941 |      8.5553 |
| Premium   |   13791 |       7.3251 |         7.4492 |      5.4646 |      8.5553 |
| Good      |    4906 |       7.2402 |         7.4125 |      5.4673 |      8.5553 |
| Very Good |   12082 |       7.2002 |         7.2918 |      5.4915 |      8.5553 |
| Ideal     |   21551 |       7.0665 |         6.9656 |      5.4646 |      8.5553 |

    ## 5. Average Price by Color
    | color   |   count |   mean_price |   median_price |   min_price |   max_price |
|:--------|--------:|-------------:|---------------:|------------:|------------:|
| J       |    2808 |       7.4886 |         7.6908 |      5.4888 |      8.5553 |
| I       |    5422 |       7.3783 |         7.5834 |      5.4862 |      8.5553 |
| H       |    8304 |       7.2987 |         7.5196 |      5.4941 |      8.5553 |
| G       |   11292 |       7.1924 |         7.1494 |      5.5379 |      8.5553 |
| F       |    9542 |       7.1721 |         7.1873 |      5.5072 |      8.5553 |
| D       |    6775 |       7.0511 |         6.9788 |      5.5454 |      8.5553 |
| E       |    9797 |       7.0189 |         6.9311 |      5.4646 |      8.5553 |

    ## 6. Average Price by Clarity
    | clarity   |   count |   mean_price |   median_price |   min_price |   max_price |
|:----------|--------:|-------------:|---------------:|------------:|------------:|
| SI2       |    9194 |       7.5068 |         7.6578 |      5.4646 |      8.5553 |
| I1        |     741 |       7.408  |         7.4907 |      5.515  |      8.5553 |
| SI1       |   13065 |       7.2439 |         7.3461 |      5.4646 |      8.5553 |
| VS2       |   12258 |       7.169  |         7.0743 |      5.4862 |      8.5553 |
| VS1       |    8171 |       7.1376 |         7.0535 |      5.4673 |      8.5553 |
| VVS2      |    5066 |       6.976  |         6.6871 |      5.4915 |      8.5553 |
| IF        |    1790 |       6.8651 |         6.5188 |      5.5748 |      8.5553 |
| VVS1      |    3655 |       6.7999 |         6.5292 |      5.4915 |      8.5553 |

    ## 7. Correlation Matrix
    |       |   price |   carat |   depth |   table |       x |       y |      z |
|:------|--------:|--------:|--------:|--------:|--------:|--------:|-------:|
| price |  1      |  0.9216 |  0.0022 |  0.1589 |  0.9555 |  0.9561 | 0.9516 |
| carat |  0.9216 |  1      |  0.0267 |  0.1844 |  0.9831 |  0.9822 | 0.981  |
| depth |  0.0022 |  0.0267 |  1      | -0.2958 | -0.0252 | -0.0284 | 0.0962 |
| table |  0.1589 |  0.1844 | -0.2958 |  1      |  0.1961 |  0.1898 | 0.1558 |
| x     |  0.9555 |  0.9831 | -0.0252 |  0.1961 |  1      |  0.9985 | 0.9906 |
| y     |  0.9561 |  0.9822 | -0.0284 |  0.1898 |  0.9985 |  1      | 0.9903 |
| z     |  0.9516 |  0.981  |  0.0962 |  0.1558 |  0.9906 |  0.9903 | 1      |

    ## 8. Key Visuals
    [Distribution of Price](figures/eda/dist_price.png)

[Distribution of Carat](figures/eda/dist_carat.png)

[Distribution of X](figures/eda/dist_x.png)

[Distribution of Y](figures/eda/dist_y.png)

[Distribution of Z](figures/eda/dist_z.png)

[Countplot of Cut](figures/eda/count_cut.png)

[Countplot of Color](figures/eda/count_color.png)

[Countplot of Clarity](figures/eda/count_clarity.png)

[Carat vs Price Regression Plot](figures/eda/carat_vs_price_regplot.png)

[Average Price by Cut](figures/eda/avg_price_by_cut.png)

[Average Price by Color](figures/eda/avg_price_by_color.png)

[Average Price by Clarity](figures/eda/avg_price_by_clarity.png)

[Pairplot](figures/eda/pairplot.png)

[Correlation Heatmap](figures/eda/correlation_heatmap.png)

[Numeric Feature Boxplots](figures/eda/boxplots_numeric_features.png)

    ## 9. EDA Observations
    1. Price remains positively associated with carat, indicating carat is a dominant predictor of diamond value.
2. The dimensional variables x, y, and z move closely with carat, suggesting strong multicollinearity among physical size variables.
3. Cut, color, and clarity show meaningful price differences, confirming that categorical quality grades carry predictive signal.
4. After outlier clipping and skewness treatment, the major numeric distributions are more stable for downstream regression modeling.
5. The numeric variables are not purely normal even after treatment, so tree-based models will likely remain strong candidates alongside transformed linear baselines.
    