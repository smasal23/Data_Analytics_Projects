import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Stock Prices Queries
df = pd.read_sql("select * from stock_prices", bridge)
print(df.head())

# 1. Get all stock prices for a given ticker.
Q16 = pd.read_sql("""select ticker, date, open, high, low, close, volume 
                        from stock_prices
                        order by ticker asc, date asc;""", bridge)
# print(Q16.head())

# 2. Find the highest closing price for NASDAQ (^IXIC).
Q17 = pd.read_sql("""select ticker, date, close
                        from stock_prices
                        where ticker = '^IXIC'
                        order by close desc
                        limit 1;""", bridge)
# print(Q17)

# 3. List top 5 days with highest price difference (high - low) for S&P 500 (^GSPC).
Q18 = pd.read_sql("""select ticker, date, high, low,
                    (high - low) as price_diff
                    from stock_prices
                    where ticker = '^GSPC'
                    order by price_diff desc, date desc
                    limit 5;""", bridge)
# print(Q18)

# 4. Get monthly average closing price for each ticker.
Q19 = pd.read_sql("""select ticker,
                        year(date) as year,
                        month(date) as month,
                        avg(close) as monthly_avg
                        from stock_prices
                        group by ticker, year(date), month(date)
                        order by ticker, year, month;
                        """, bridge)
# print(Q19)

# 5. Get average trading volume of NSEI in 2024
Q20 = pd.read_sql("""select ticker, 
                        year(date) as year,
                        avg(volume) as avg_trading_vol
                        from stock_prices
                        where ticker = '^NSEI'
                            and year(date) = 2024
                        group by ticker, year;
                        """, bridge)
# print(Q20)