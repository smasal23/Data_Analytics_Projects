from pathlib import Path
import pandas as pd
import pytest

from src.data.load_data import load_csv_data
from src.data.validate_data import (
    check_target_present,
    get_missing_required_columns,
    get_unexpected_columns,
    count_duplicates,
    build_missing_summary,
    build_column_summary,
    build_dataset_summary,
)


# Test that a CSV file is loaded correctly.
def test_load_csv_data_success(tmp_path: Path):
    sample_file = tmp_path / "sample.csv"

    df_sample = pd.DataFrame({
        "carat": [0.5, 1.0],
        "price": [1000, 5000],
    })
    df_sample.to_csv(sample_file, index=False)

    df_loaded = load_csv_data(sample_file)

    assert isinstance(df_loaded, pd.DataFrame)
    assert df_loaded.shape == (2, 2)
    assert list(df_loaded.columns) == ["carat", "price"]


# Test that loading a non-existent file raises FileNotFoundError.
def test_load_csv_data_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_csv_data("non_existent_file.csv")


# Test target column presence detection.
def test_check_target_present():
    df = pd.DataFrame({
        "carat": [0.5, 1.0],
        "price": [1000, 5000],
    })

    assert check_target_present(df, "price") is True
    assert check_target_present(df, "target") is False


# Test missing required column detection.
def test_get_missing_required_columns():
    df = pd.DataFrame({
        "carat": [0.5],
        "price": [1000],
    })

    required_columns = ["carat", "cut", "price"]

    missing = get_missing_required_columns(df, required_columns)

    assert missing == ["cut"]


# Test unexpected column detection.
def test_get_unexpected_columns():
    df = pd.DataFrame({
        "carat": [0.5],
        "price": [1000],
        "extra_col": [1],
    })

    expected_columns = ["carat", "price"]

    unexpected = get_unexpected_columns(df, expected_columns)

    assert unexpected == ["extra_col"]


# Test duplicate row counting.
def test_count_duplicates():
    df = pd.DataFrame({
        "carat": [0.5, 0.5],
        "price": [1000, 1000],
    })

    assert count_duplicates(df) == 1


# Test missing summary structure.
def test_build_missing_summary():
    df = pd.DataFrame({
        "carat": [0.5, None],
        "price": [1000, 5000],
    })

    summary = build_missing_summary(df)

    assert isinstance(summary, pd.DataFrame)
    assert set(summary.columns) == {"column", "missing_count", "missing_pct"}
    assert summary.loc[summary["column"] == "carat", "missing_count"].iloc[0] == 1


# Test column summary structure.
def test_build_column_summary():
    df = pd.DataFrame({
        "carat": [0.5, 1.0],
        "price": [1000, 5000],
    })

    summary = build_column_summary(df)

    assert isinstance(summary, pd.DataFrame)
    assert "column" in summary.columns
    assert "dtype" in summary.columns
    assert "n_unique" in summary.columns
    assert summary.shape[0] == 2


# Test dataset summary dictionary creation.
def test_build_dataset_summary():
    df = pd.DataFrame({
        "carat": [0.5, 1.0],
        "price": [1000, 5000],
    })

    summary = build_dataset_summary(
        df=df,
        target_col="price",
        required_columns=["carat", "price"],
        expected_columns=["carat", "price"],
    )

    assert isinstance(summary, dict)
    assert summary["target_present"] is True
    assert summary["missing_required_columns"] == []
    assert summary["unexpected_columns"] == []
    assert summary["shape"]["rows"] == 2