from pathlib import Path

from src.utils.io import read_csv_file
from src.utils.paths import find_project_root, resolve_project_path


def main():
    root = find_project_root()
    comparison_path = resolve_project_path(root, "artifacts/comparison/model_comparison_table.csv")

    df = read_csv_file(comparison_path)

    print("\nModel comparison table:")
    print(df)

    print("\nBest model:")
    print(df.iloc[0].to_dict())


if __name__ == "__main__":
    main()