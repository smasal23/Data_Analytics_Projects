# Project Paths

from pathlib import Path
# Resolve converts relative path to absolute one and Parents is list of folder upwards.
Base_DIR = Path(__file__).resolve().parents[2]
# Associated Directories
Data_DIR = Base_DIR / "data"

Raw_Data_DIR = Data_DIR / "raw"
Cleaned_Data_DIR = Data_DIR / "cleaned"
Processed_Data_DIR = Data_DIR / "processed"

Database_DIR = Data_DIR / "database"
Logs_DIR = Data_DIR / "logs"


# Global Data Config - defines the “time universe” of your analysis.
global_start_date = "01/01/2020"
global_end_date = "24/01/2026"

Asset_Date_Ranges = {"crypto" : {"start" : "01/01/2025", "end" : "31/01/2026"},
                     "oil" : {"start" : "01/01/2020", "end" : "24/01/2026"},
                     "stock" : {"start" : "01/01/2020", "end" : "30/09/2025"}
                     }


# API Config - isolates external dependency risk.
    # Crypto
Coingecko_Base_URL = "https://api.coingecko.com/api/v3"

Coingecko_Market_Endpoint = "/coins/markets?page=1&sparkline=False"
Coingecko_VS_Currency = "usd"
Coingecko_Per_Page = "250"
Coingecko_Order = "market_cap_desc"

Coingecko_Price_Endpoint = "/coins/{coin_id}/market_chart"
Coingecko_Price_Interval = "daily"
Coingecko_Price_Days = 365

# Asset Definitions - turns a script into a configurable platform.
    # Crypto
Top_N_Coins = 5
    # Stocks
SP_Tickers = {"S&P 500" : "^GSPC", "NASDAQ" : "^IXIC", "NIFTY 50" : "^NSEI"}
    # Oil
Oil_Data_Source = "WTI"
WTI_URL = "https://raw.githubusercontent.com/datasets/oil-prices/main/data/wti-daily.csv"


# Database Config
DB_Name = "cross_market.db"
DB_Path = Database_DIR / DB_Name


# Column Standards - turns multi-source chaos into a single reusable pipeline.
#                  - ensures consistency, joinability, and correctness across multi-source data pipelines, analytics, and dashboards.
    # Crypto Metadata
Crypto_Metadata_Columns = ["id", "symbol", "name", "market_cap", "market_cap_rank"]
    # Price Data
Price_Columns = ["coin_id", "date", "price_usd"]


# Streamlit Dashboard Config
APP_Title = "Cross Market Analysis"
Default_Theme = "Dark"

Default_Start_Date = "2021-01-01"
Default_End_Date = "2024-12-31"