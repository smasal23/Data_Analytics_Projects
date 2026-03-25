from src.data.clean_data import clean_diamonds_dataset
from src.data.preprocess import summarize_preprocessing_strategy


def main():
    results = clean_diamonds_dataset()
    preprocessing_summary = summarize_preprocessing_strategy()

    print("\nData cleaning completed.")
    print(f"Processed dataset: {results['processed_output']}")
    print(f"Report: {results['report_output']}")
    print(f"Missing figure: {results['missing_fig_output']}")
    print(f"Invalid xyz figure: {results['invalid_xyz_fig_output']}")
    print("\nPreprocessing strategy summary:")
    print(preprocessing_summary)


if __name__ == "__main__":
    main()