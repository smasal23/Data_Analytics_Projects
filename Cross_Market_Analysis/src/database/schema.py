# Define schema
# schemas.py
# Pure schema definitions (design layer)

CRYPTOCURRENCIES_SCHEMA = {
    "table_name": "cryptocurrencies",
    "columns": {
        "id": "VARCHAR(50) PRIMARY KEY",   # CoinGecko coin id (bitcoin, ethereum)
        "symbol": "VARCHAR(10)",
        "name": "VARCHAR(100)",
        "current_price": "DECIMAL(18,6)",
        "market_cap": "BIGINT",
        "market_cap_rank": "INT",
        "total_volume": "BIGINT",
        "circulating_supply": "DECIMAL(20,6)",
        "total_supply": "DECIMAL(20,6)",
        "ath": "DECIMAL(18,6)",
        "atl": "DECIMAL(18,6)",
        "date": "DATE"
    }
}


CRYPTO_PRICES_SCHEMA = {
    "table_name": "crypto_prices",
    "columns": {
        "coin_id": "VARCHAR(50)",          # FK → cryptocurrencies.id
        "date" : "DATE",
        "price_usd" : "DECIMAL(18,6)"
    },
}


OIL_PRICES_SCHEMA = {
    "table_name": "oil_prices",
    "columns": {
        "date": "DATE PRIMARY KEY",
        "price_usd": "DECIMAL(18,6)"
    }
}


STOCK_PRICES_SCHEMA = {
    "table_name": "stock_prices",
    "columns": {
        "date": "DATE",
        "open": "DECIMAL(18,6)",
        "high": "DECIMAL(18,6)",
        "low": "DECIMAL(18,6)",
        "close": "DECIMAL(18,6)",
        "volume": "BIGINT",
        "ticker": "VARCHAR(20)"   # ^GSPC, ^IXIC, ^NSEI
    }
}


# Define FK
CRYPTO_PRICES_SCHEMA = {
    "table_name": "crypto_prices",
    "columns": {
        "coin_id": "VARCHAR(50)",          # FK → cryptocurrencies.id
        "date" : "DATE",
        "price_usd" : "DECIMAL(18,6)"
    },
        "foreign_keys": [
            ("coin_id", "cryptocurrencies", "id")
    ]
}

