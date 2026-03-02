import pandas as pd
import requests
import os

# load_raw_data(path)
def download_csv(url, file_name, folder = "F:\\DATA SCIENCE\\Projects\\Global Literacy & Educational Trends\\data\\raw"):
    os.makedirs(folder, exist_ok = True)

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers = headers)
    response.raise_for_status()

    save_path = os.path.join(folder, f"{file_name}.csv")

    with open(save_path, "w", encoding = "utf-8") as f:
        f.write(response.text)

    print(f"Saved to {save_path}")


# merge and save datasets
def merge_and_save(df1: pd.DataFrame, df2: pd.DataFrame,
                   on_cols: list,
                   how: str = 'outer',
                   save_path: str = None):

    # Merge dataframes
    df_merged = pd.merge(df1, df2, on=on_cols, how=how)

    # Print info
    print(f"Merged dataframe shape: {df_merged.shape}")
    print(df_merged.head())

    # Save if path provided
    if save_path:
        df_merged.to_csv(save_path, index=False)
        print(f"Saved merged dataframe to: {save_path}")

    return df_merged
