import streamlit as st
from src.sql.cryptocurrency_queries import (Q1, Q2, Q3, Q4, Q5)
from src.sql.crypto_prices_queries import (Q6, Q7, Q8, Q9, Q10)
from src.sql.oil_prices_queries import (Q11, Q12, Q13, Q14, Q15)
from src.sql.stock_prices_queries import (Q16, Q17, Q18, Q19, Q20)
from src.sql.join_queries import (Q21, Q22, Q23, Q24, Q25, Q26, Q27, Q28, Q29, Q30)
from src.utils import get_engine

bridge = get_engine()
print(bridge)

def page_intro():
    st.title(":green[Analytical Take Using SQL]")
    st.caption(":green[Predefined analytical SQL queries]")

    st.divider()

    st.markdown("""
          <div style="
            max-width: 900px;
            background: rgba(10,15,25,0.75);
            padding: 24px 28px;
            border-radius: 16px;
            color: forestgreen;
            font-size: 20px;
            font-weight: 600;
        ">

        <p> 
        A unified, SQL-powered view of global financial markets in one place. Using structured queries and carefully aligned date joins, 
        the view brings together Crypto, Crude Oil and Stock Prices into a single dataframe snapshot.
        </p>

        <p>
        The goal is simple: Remove data silos and Analyze how crypto, commodities, and equity indices move side by side on the same 
        trading day. By normalizing dates and resolving mismatches across sources, this view ensures consistency and comparability 
        across markets.
        </p>
        
         <p>
        Whether you’re exploring correlations, validating trends, or just getting a quick market pulse, 
        this runner acts as a reliable foundation for deeper analysis and visualizations built on top of SQL-backed data.
        </p>
        """,
        unsafe_allow_html=True)

# Query Dropdown
def query_selection():
    Query_Map = {
                "Top 3 Cryptocurrencies by Market Cap": {
                    "description": "Shows top 3 cryptos by latest market cap",
                    "function": lambda: Q1
                },
                "Coins with Circulating Supply Exceeding 90% of Total Supply": {
                    "description": "Lists all coins where circulating supply exceeds 90% of total supply.",
                    "function": lambda: Q2
                },
                "Coins within 10% of their ATH": {
                    "description": "Get coins that are within 10% of their all-time-high (ATH).",
                    "function": lambda: Q3
                },
                "Average Market Cap Rank of Coins with Volume above $1B": {
                    "description": "Find the average market cap rank of coins with volume above $1B.",
                    "function": lambda: Q4
                },
                "Most Recently Updated Coin": {
                    "description": "Get the most recently updated coin",
                    "function": lambda: Q5
                },
                "Highest Daily Price of Bitcoin in the Last 365 Days": {
                    "description": "Finds the highest daily price of Bitcoin in the last 365 days.",
                    "function": lambda: Q6
                },
                "Average Daily Price of Ethereum in the Past 1 Year": {
                    "description": "Calculates the average daily price of Ethereum in the past 1 year.",
                    "function": lambda: Q7
                },
                "Daily Price Trend of Bitcoin in January 2025": {
                    "description": "Show the daily price trend of Bitcoin in January 2025",
                    "function": lambda: Q8
                },
                "Coin with the Highest Average Price over 1 Year": {
                    "description": "Find the coin with the highest average price over 1 year.",
                    "function": lambda: Q9
                },
                "% Change in Bitcoin’s Price Between Jan 2025 and Dec 2025": {
                    "description": "Get the % change in Bitcoin’s price between Jan 2025 and Dec 2025.",
                    "function": lambda: Q10
                },
                "Highest Oil Price in the last 5 Years": {
                    "description": "Find the highest oil price in the last 5 years",
                    "function": lambda: Q11
                },
                "Average Oil Price per Year": {
                    "description": "Get the average oil price per year.",
                    "function": lambda: Q12
                },
                "Oil Prices During COVID Crash (March–April 2020)": {
                    "description": "Show oil prices during COVID crash (March–April 2020).",
                    "function": lambda: Q13
                },
                "Lowest Price of Oil in the Last 6 Years": {
                    "description": "Find the lowest price of oil in the last 6 years.",
                    "function": lambda: Q14
                },
                "Volatility of Oil Prices (max-min difference per year)": {
                    "description": "Calculate the volatility of oil prices (max-min difference per year).",
                    "function": lambda: Q15
                },
                "All Stock Prices for a Given Ticker": {
                    "description": "Get all stock prices for a given ticker.",
                    "function": lambda: Q16
                },
                "Highest Closing Price for NASDAQ": {
                    "description": "Find the highest closing price for NASDAQ (^IXIC).",
                    "function": lambda: Q17
                },
                "Top 5 Days with Highest Price Difference (high - low) for S&P 500": {
                    "description": "List top 5 days with highest price difference (high - low) for S&P 500 (^GSPC).",
                    "function": lambda: Q18
                },
                "Monthly Average Closing Price For Each Ticker.": {
                    "description": "Get monthly average closing price for each ticker.",
                    "function": lambda: Q19
                },
                "Average Trading Volume of NSEI in 2024": {
                    "description": "Get average trading volume of NSEI in 2024.",
                    "function": lambda: Q20
                },
                "Bitcoin vs Oil Average Price in 2025": {
                    "description": "Compare Bitcoin vs Oil average price in 2025.",
                    "function": lambda: Q21
                },
                "Bitcoin Movement with S&P 500": {
                    "description": "Check if Bitcoin moves with S&P 500 (correlation idea).",
                    "function": lambda: Q22
                },
                "Ethereum vs NASDAQ Daily Prices for 2025": {
                    "description": "Compare Ethereum and NASDAQ daily prices for 2025.",
                    "function": lambda: Q23
                },
                "Oil Price Spiked and Compared with Bitcoin Price Change": {
                    "description": "Find days when oil price spiked and compare with Bitcoin price change.",
                    "function": lambda: Q24
                },
                "Top 3 Coins Daily Price Trend vs Nifty": {
                    "description": "Compare top 3 coins daily price trend vs Nifty (^NSEI).",
                    "function": lambda: Q25
                },
                "Stock Prices with Crude Oil Prices on Same Dates": {
                    "description": "Compare stock prices (^GSPC) with crude oil prices on the same dates.",
                    "function": lambda: Q26
                },
                "Correlate Bitcoin Closing Price with Crude Oil Closing Price": {
                    "description": "Correlate Bitcoin closing price with crude oil closing price (same date).",
                    "function": lambda: Q27
                },
                "NASDAQ vs Ethereum price trends": {
                    "description": "Compare NASDAQ (^IXIC) with Ethereum price trends.",
                    "function": lambda: Q28
                },
                "Top 5 Crypto Coins with Stock Indices for 2025": {
                    "description": "Join top 5 crypto coins with stock indices for 2025.",
                    "function": lambda: Q29
                },
                "Multi-join: stock prices, oil prices, and Bitcoin prices": {
                    "description": "Multi-join: stock prices, oil prices, and Bitcoin prices for daily comparison.",
                    "function": lambda: Q30
                }
    }
    selected_query = st.selectbox("📌 Select a Query", list(Query_Map.keys()))

    result_df = None

# Execute Button

    if st.button("▶ Run Query"):
        with st.spinner("Executing Query..."):
            result_df = Query_Map[selected_query]["function"]()

# Results Table

    if result_df is not None and not result_df.empty:
        st.success("Query executed successfully.")
        st.dataframe(result_df, use_container_width = True)
    else:
        st.warning("No data returned for this query.")


    st.markdown("""
        <div style = "
                    max_width: 900px;
                    background: rgba(10, 15, 25, 0.75)
                    padding: 24px 28px;
                    border-radius: 16px;
                    color: pink;
                    font-size: 20px;
                    font-weight: 600;
        ">
        
        <p> 
        These Queries are executed directly on to the SQL database.
        </p>
        
        """, unsafe_allow_html = True)