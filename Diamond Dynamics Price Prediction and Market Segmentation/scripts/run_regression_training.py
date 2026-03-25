from src.modeling.train_regression import train_regression_models


def main():
    results = train_regression_models()

    print("\nRegression training completed.")
    print(f"Best model: {results['best_model_name']}")
    print("\nMetrics table:")
    print(results["metrics_df"])


if __name__ == "__main__":
    main()