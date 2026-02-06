import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Crypto Prices Queries
df = pd.read_sql("select * from coin_prices", bridge)
# print(df.head())

# 1. Find the highest daily price of Bitcoin in the last 365 days.
Q6 = pd.read_sql("""select coin_id, date, price_usd
                        from coin_prices
                        where coin_id = "bitcoin"
                        and date >= curdate() - interval 365 day
                        and price_usd = ( 
                            select max(price_usd)
                            from coin_prices
                            where coin_id = "bitcoin"
                            and date >= curdate() - interval 365 day);
                """, bridge)
# print(Q6)

# 2. Calculate the average daily price of Ethereum in the past 1 year.
Q7 = pd.read_sql("""select coin_id, date, price_usd,
                            (select avg(price_usd)
                            from coin_prices
                            where coin_id = "ethereum" 
                            and date >= curdate() - interval 365 day
                            ) as avg_eth_price
                        from coin_prices 
                        where coin_id = "ethereum"
                        and date >= curdate() - interval 365 day;
                    """, bridge)
# print(Q7)

# 3. Show the daily price trend of Bitcoin in January 2025.
Q8 = pd.read_sql("""select date, price_usd
                        from coin_prices
                        where coin_id = "bitcoin"
                        and date between '2025-01-01' and '2025-01-31'
                        order by date asc;
                        """, bridge)
# print(Q8)

# 4. Find the coin with the highest average price over 1 year.
Q9 = pd.read_sql("""select coin_id,
                    avg(price_usd) as avg_price_1y
                    from coin_prices
                    where date >= curdate() - interval 365 day
                    group by coin_id
                    order by avg_price_1y desc
                    limit 1;
                    """, bridge)
# print(Q9)

# 5. Get the % change in Bitcoin’s price between Jan 2025 and Dec 2025.
Q10 = pd.read_sql("""select
                        ((max(price_usd) - min(price_usd)) / min(price_usd)) * 100
                        as percent_change
                        from coin_prices
                        where coin_id = 'bitcoin'
                        and date between '2025-01-01' and '2025-12-31';
                        """, bridge)
# print(Q10)