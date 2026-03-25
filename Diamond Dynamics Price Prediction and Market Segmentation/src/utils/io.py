from pathlib import Path
import json
import pandas as pd


# Ensure a directory exists and return it as a Path object
def ensure_dir(path: str | Path):
    path = Path(path)
    path.mkdir(parents = True, exist_ok = True)
    return path


# Read a CSV file into a pandas DataFrame.
def read_csv_file(filepath: str | Path, **kwargs):
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    return pd.read_csv(filepath, **kwargs)


# Save Dataframe to CSV
def save_csv_file(df: pd.DataFrame, filepath: str | Path, index: bool = False):
    filepath = Path(filepath)
    ensure_dir(filepath.parent)
    df.to_csv(filepath, index = index)
    return filepath


# Load a JSON file and return its content
def load_json_file(filepath: str | Path):
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found: {filepath}")

    with open(filepath, "r", encoding = "utf-8") as f:
        return json.load(f)


# Save a dictionary to a JSON file
def save_json_file(data: dict, filepath: str | Path):
    filepath = Path(filepath)
    ensure_dir(filepath.parent)

    with open(filepath, "w", encoding = "utf-8") as f:
        json.dump(data, f, indent = 2, ensure_ascii = False, default = str)

    return filepath


# Save plain text content to a file
def save_text_file(text: str, filepath: str | Path):
    filepath = Path(filepath)
    ensure_dir(filepath.parent)

    with open(filepath, "w", encoding = "utf-8") as f:
        f.write(text)

    return filepath