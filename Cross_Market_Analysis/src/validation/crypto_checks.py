from src.config.settings import (Top_N_Coins)
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

df = pd.read_pickle("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\raw\\crypto\\processed_df.pkl")
df_meta = pd.read_pickle("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\raw\\crypto\\processed_df_meta.pkl")

# Validate missing values
print(df.isnull().sum())
print(df_meta.isnull().sum())
# Handle Missing values with mean for total_supply
df['total_supply'].mean()
df['total_supply'] = df['total_supply'].fillna(345994970375285.75)
print(df.isnull().sum())


# Save Cleaned Data(Markets)
print(sum(df.duplicated()))
print(df.head())
print(df_meta.head())
df.to_csv('F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\crypto\\coin_list.csv')

df_meta.to_csv('F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\crypto\\coin_list_meta.csv')


# Identify top 3 coins
def get_top_coins(df_meta, Top_N_Coins):
    # Ensure market_cap_rank is numeric, coerce will convert non-numeric values to NaN.
    df_meta['market_cap_rank'] = pd.to_numeric(df_meta['market_cap_rank'], errors = 'coerce')
    # Assign low priority to NaN values, so they don't interfere and the data length remains intact.
    df_meta['market_cap_rank'] = df_meta['market_cap_rank'].fillna(float('inf'))
    top_coins = df_meta['id'].head(Top_N_Coins)
    return top_coins.tolist()

print(get_top_coins(df_meta, Top_N_Coins))


# Validate 365-day coverage for crypto historical prices
df_prices = pd.read_pickle("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\raw\\crypto\\processed_df_prices.pkl")
# Drop true duplicates as same coin same date while keeping the first.
df_prices = df_prices.drop_duplicates(subset = ['coin_id', 'date'], keep = 'first')
duplicates_per_coin = df_prices.duplicated(subset = ['coin_id', 'date']).sum()
print(duplicates_per_coin)
print(df_prices.head())


# Save Cleaned Data(Prices)
df_prices.to_csv("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\crypto\\coin_prices.csv")


