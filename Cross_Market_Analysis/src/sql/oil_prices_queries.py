import pandas as pd
pd.set_option("display.max_rows", None)

from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Oil Prices Queries
df = pd.read_sql("select * from oil_prices;", bridge)
print(df)

# 1. Find the highest oil price in the last 5 years.
Q11 = pd.read_sql("""select date, price_usd
                    from oil_prices
                    where date between curdate() - interval 1825 day and curdate()
                    and price_usd = (
                        select max(price_usd)
                        from oil_prices
                        where date between curdate() - interval 1825 day and curdate());
                        """, bridge)
# print(Q11)

# 2. Get the average oil price per year.
Q12 = pd.read_sql("""select year(date) as year, avg(price_usd) as avg_price_1y
                    from oil_prices
                    group by year(date)
                    order by year desc;""", bridge)
# print(Q12)

# 3. Show oil prices during COVID crash (March–April 2020).
Q13 = pd.read_sql("""select * from oil_prices
                        where date between "2020-03-01" and "2020-04-30";
                        """, bridge)
# print(Q13)

# 4. Find the lowest price of oil in the last 6 years.
Q14 = pd.read_sql("""select date, price_usd
                        from oil_prices
                        where price_usd = (
                            select min(price_usd)
                            from oil_prices);
                        """, bridge)
# print(Q14)

# 5. Calculate the volatility of oil prices (max-min difference per year).
Q15 = pd.read_sql("""select year(date) as year,
                        max(price_usd) as max_price_usd,
                        min(price_usd) as min_price_usd,
                        max(price_usd) - min(price_usd) as volatility
                    from oil_prices
                    group by year(date)
                    order by year asc;
                    """, bridge)
# print(Q15)