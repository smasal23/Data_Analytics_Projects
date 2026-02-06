import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Cryptocurrencies
df = pd.read_sql("select * from coin_list;", bridge)
# print(df.head())
# Since the SQL tables are unordered sets, created a sorted view first
# df = pd.read_sql("create or replace view coin_list_sorted as select * from coin_list order by market_cap_rank asc;", bridge)
# Q = pd.read_sql("select * from coin_list_sorted", bridge)
# print(Q.head())

# 1. Find the top 3 cryptocurrencies by market cap.
Q1 = pd.read_sql("""select name, symbol, market_cap, market_cap_rank 
                    from coin_list_sorted 
                    order by market_cap desc 
                    limit 3;""", bridge)
# print(Q1)

# 2. List all coins where circulating supply exceeds 90% of total supply.
Q2 = pd.read_sql("""select name, symbol, circulating_supply, total_supply
                        from coin_list_sorted
                        where circulating_supply > 0.9 * total_supply;
                    """, bridge)
# print(Q2)

# 3. Get coins that are within 10% of their all-time-high (ATH).
Q3 = pd.read_sql("""select name, symbol, current_price, ath
                    from coin_list_sorted
                    where current_price >= 0.9 * ath;
                """, bridge)
# print(Q3)

# 4. Find the average market cap rank of coins with volume above $1B.
Q4 = pd.read_sql("""select name, symbol, market_cap_rank, total_volume,
                            ( select avg(market_cap_rank)
                            from coin_list_sorted
                            where total_volume > 1000000000
                            ) as avg_market_cap_rank
                        from coin_list_sorted
                        where total_volume > 1000000000;
                        """, bridge)
# print(Q4)

# 5. Get the most recently updated coin.
Q5 = pd.read_sql("""select name, symbol, date
                        from coin_list_sorted
                        order by date desc
                        limit 1;
                    """, bridge)
# print(Q5)
