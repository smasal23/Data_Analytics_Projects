from src.utils.io import read_csv_file
from src.utils.paths import find_project_root, resolve_project_path
from src.modeling.train_clustering import train_clustering_pipeline, save_clustering_outputs


def main():
    root = find_project_root()

    processed_path = resolve_project_path(root, "data/processed/diamonds_processed.csv")
    df = read_csv_file(processed_path)

    results = train_clustering_pipeline(df = df, project_root = root)
    saved_paths = save_clustering_outputs(results)

    print("\nBest clustering model:")
    print(results["best_model_name"])

    print("\nTop comparison rows:")
    print(results["comparison_df"].head())

    print("\nSaved outputs:")
    for key, value in saved_paths.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()