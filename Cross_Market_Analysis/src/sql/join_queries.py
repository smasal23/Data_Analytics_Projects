from statistics import correlation

import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)

from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Join Queries

# 1. Compare Bitcoin vs Oil average price in 2025.
Q21 = pd.read_sql("""select avg(c.price_usd) as avg_btc_2025,
                        avg(o.price_usd) as avg_oil_2025
                        from coin_prices c inner join oil_prices o
                        on c.date = o.date
                        where c.coin_id = 'bitcoin'
                            and year(c.date) = 2025;
                        """, bridge)
# print(Q21)

# 2. Check if Bitcoin moves with S&P 500 (correlation idea).
Q22 = pd.read_sql("""select c.date,
                        c.price_usd as btc_price,
                        s.close as sp500_close
                        from coin_prices c inner join stock_prices s
                        on c.date = s.date
                        where c.coin_id = 'bitcoin'
                            and s.ticker = '^GSPC'
                        order by c.date;
                        """, bridge)
# print(Q22)

# 3. Compare Ethereum and NASDAQ daily prices for 2025.
Q23 = pd.read_sql("""select c.date,
                        c.price_usd as eth_price,
                        s.close as nasdaq_close
                        from coin_prices c inner join stock_prices s
                        on c.date = s.date
                        where c.coin_id = 'ethereum'
                            and year(c.date) = 2025
                            and s.ticker = '^IXIC'
                        order by c.date;
                        """, bridge)
# print(Q23)

# 4. Find days when oil price spiked and compare with Bitcoin price change.
Q24 = pd.read_sql("""select o.date,
                        o.price_usd as oil_price,
                        case
                            when o.price_usd > avg(o.price_usd) over()
                            then 'yes'
                            else 'no'
                        end as oil_spike,
                        c.price_usd as btc_price
                        from oil_prices o inner join coin_prices c
                        on o.date = c.date
                        where c.coin_id = 'bitcoin'
                        order by o.date;
                        """, bridge)
# print(Q24)

# 5. Compare top 3 coins daily price trend vs Nifty (^NSEI).
Q25 = pd.read_sql("""with coin_trend as (
                        select date, coin_id,
                        (price_usd - lag(price_usd) over (partition by coin_id order by date)) / lag(price_usd) over (partition by coin_id order by date) as coin_return
                        from coin_prices
                        where coin_id in ('bitcoin', 'ethereum', 'tether')
                        ),
                        nifty as (
                        select date,
                        (close - lag(close) over (order by date)) / lag(close) over (order by date) as nifty_return
                        from stock_prices
                        where ticker = '^NSEI'
                        )
                        select c.date, c.coin_id, c.coin_return, n.nifty_return
                        from coin_trend c inner join nifty n
                        on c.date = n.date
                        where c.coin_return is not null
                            and n.nifty_return is not null
                        order by c.date;
                        """, bridge)
# print(Q25)

# 6. Compare stock prices (^GSPC) with crude oil prices on the same dates
Q26 = pd.read_sql("""select s.date,
                        s.close as stock_gspc_prices, 
                        o.price_usd as crude_oil_prices
                        from stock_prices s inner join oil_prices o
                        on s.date = o.date
                        where s.ticker = '^GSPC'
                        order by s.date;
                        """, bridge)
# print(Q26)

# 7. Correlate Bitcoin closing price with crude oil closing price (same date)
Q27 = pd.read_sql("""select c.date,
                        c.price_usd as bitcoin_closing_price,
                        o.price_usd as crude_oil_closing_price
                        from coin_prices c inner join oil_prices o
                        on c.date = o.date
                        where c.coin_id = 'bitcoin'
                        order by c.date;
                        """, bridge)
# print(Q27)
corr_btc_oil = Q27[['bitcoin_closing_price', 'crude_oil_closing_price']].corr()
# print(corr_btc_oil)

# 8. Compare NASDAQ (^IXIC) with Ethereum price trends.
Q28 = pd.read_sql("""with eth as (
                        select date,
                            (price_usd - lag(price_usd) over (order by date)) / lag(price_usd) over (order by date) as eth_return
                        from coin_prices
                        where coin_id = 'ethereum'
                        ),
                        nasdaq as (
                        select date,
                            (close - lag(close) over (order by date)) / lag(close) over (order by date) as nasdaq_return
                        from stock_prices
                        where ticker = '^IXIC'
                        )
                        select e.date, e.eth_return, n.nasdaq_return
                        from eth e inner join nasdaq n
                        on e.date = n.date
                        where e.eth_return is not null
                            and n.nasdaq_return is not null
                        order by e.date;
                        """, bridge)
# print(Q28)

# 9. Join top 5 crypto coins with stock indices for 2025 # Had to modify to 2025 since historical prices of last 1 year was asked to collect.
Q29 = pd.read_sql("""select c.date, c.coin_id,
                        c.price_usd as crypto_price,
                        s.ticker as stock_indices,
                        s.close as index_close
                        from coin_prices c inner join stock_prices s
                        on c.date = s.date
                        where year(c.date) = 2025
                        order by c.date, c.coin_id, s.ticker;
                        """, bridge)
# print(Q29)

# 10. Multi-join: stock prices, oil prices, and Bitcoin prices for daily comparison
Q30 = pd.read_sql("""select s.date, s.ticker as stock_indices, s.close as stock_close,
                        o.price_usd as oil_price, c.coin_id,
                        c.price_usd as crypto_price
                        from stock_prices s left join oil_prices o
                            on s.date = o.date
                            left join coin_prices c
                            on s.date = c.date
                        where c.coin_id = 'bitcoin'
                        order by s.date, s.ticker;
                        """, bridge)
# print(Q30)