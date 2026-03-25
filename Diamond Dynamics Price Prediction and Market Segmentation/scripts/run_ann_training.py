from src.modeling.train_ann import train_ann_regression_model


def main():
    results = train_ann_regression_model()

    print("\nPyTorch ANN training completed.")
    print("Saved model:", results["model_path"])
    print("Metrics:", results["metrics"])


if __name__ == "__main__":
    main()