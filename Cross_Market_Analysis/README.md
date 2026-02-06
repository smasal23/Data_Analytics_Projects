  💰🛢️📈Cross-Market Analysis: Crypto, Oil & Stocks with SQL and Streamlit

## Project Overview

    - Cryptocurrency in this digital age is ever-growing day-by-day to become a widely accepted mode of currency exchange.
    - This is an investment asset often compared to traditional ones like oil and stock indices.
    - The idea behind the project is to assess whether cryptocurrency can transfrom into a betting marketable asset, as an in-depth analysis using a SQL-powered crossmarket analytics platform is incorporated, comparing the following :
        - Top Cryptocurrencies(Bitcoin, Ethereum, etc)
        - Oil(WTI Benchmark)
        - Global Stock Indices(S&P 500, NASDAQ, NIFTY)
    - Ultimately leading to finding patterns, correlations and relative performance between these markets in the past few years.

## Project Objectives

    - Proper Learning of Data Collection using endpoint APIs.
    - Apprehension of integrating Collected Data into SQL tables.
    - Appropriating Schema & Relationships of Transformed Datasets into Relational SQL tables.
    - Inculcating Pythonic ways of creating and inserting automated SQL tables with query resolutions.
    - Building a fully functional Streamlit application UI showcasing Crypto Analysis, Oil and Stock Exploration and SQL-oriented analytics.

## Project In-Scope

    - Correlation of Cryptocurrencies with/or against Oil/Stock markets.
    - Comparison of Volatile Crypto with Traditional Assets.
    - Analytical Impact of events like Oil Spikes and Stock Crashes on Crypto Prices.
    - Broadened Understanding of Data Warehousing, SQL analytics and Financial Market Relationships in a single get-go.

## Project Out-Scope
    
    - Intraday data
    - Predictive modeling
    - Real-time streaming

## Data Sources

    - **Cryptocurrency**
        - Source: CoinGecko API
        - Data: Coin metadata and daily historical prices
        - Granularity: Daily
        - Coverage: Top cryptocurrencies by market cap

    - **Oil**
        - Source: GitHub Public Dataset (WTI Crude)
        - Data: Daily WTI crude oil prices (USD per barrel)
        - Coverage: Jan 2020 – Jan 2026

    - **Stock Markets**
        - Source: Yahoo Finance API
        - Data: Daily OHLCV index prices
        - Indices: S&P 500, NASDAQ, NIFTY
        - Coverage: Jan 2020 – Sept 2025

## Deliverables

    - SQL-Powered Analytics Solution.
    - Dynamic and Insightful Dashboard.
    - Concise and Clear Decision-Making.
    - Current Cryptocurrency Predicament.

## Known Limitations

    - CoinGecko free tier enforces strict API rate limits
    - Full pipeline execution may fail if rate limits are exceeded
    - Pre-extracted datasets are provided for demo and exploration purposes

## Success Criteria
    - Data successfully collected and stored for all three markets.
    - Relational SQL schema supports multi-market joins.
    - At least 30 cross-market analytical queries executed.
    - Streamlit dashboard enables date-based comparison and exploration.

## Tech Stack

    - Python
    - Pandas, SQLAlchemy
    - MySQL
    - Papermill
    - Streamlit
    - REST APIs (CoinGecko, Yahoo Finance)
