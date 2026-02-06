import pandas as pd
from sqlalchemy import text
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)
from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Insert Metadata
df5 = pd.read_csv("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\crypto\\coin_list_meta.csv")
print(df5.head())
df5.drop("Unnamed: 0", axis = 1, inplace = True)
print(df5.head())
df5.to_sql(name = "coin_list_meta", con = bridge, if_exists = "replace", index = False)


# Modify Coin List
table_name = "coin_list"
# Had to increase column size in some cases as the records of that attribute were large in size.
column_dtypes = {
    "id": "VARCHAR(100)",
    "symbol": "VARCHAR(20)",
    "name": "VARCHAR(100)",
    "current_price": "DECIMAL(18,6)",
    "market_cap": "BIGINT",
    "market_cap_rank": "INT",
    "total_volume": "BIGINT",
    "circulating_supply": "DECIMAL(30,6)",
    "total_supply": "DECIMAL(30,6)",
    "ath": "DECIMAL(18,6)",
    "atl": "DECIMAL(18,6)",
    "date": "DATE"
}

with bridge.connect() as conn:
    #  ️Modify column datatypes
    for i, j in column_dtypes.items():
        alter_sql = f"""
        alter table {table_name}
        modify {i} {j};
        """
        conn.execute(text(alter_sql))
    # Add primary key
    conn.execute(text("""alter table coin_list
        add primary key (id)"""))


df = pd.read_sql("describe coin_list", bridge)
print(df)


# Modify Coin Prices
df2 = pd.read_sql("describe coin_prices", bridge)
print(df2)
with bridge.connect() as conn:
    rename_col = f"""alter table coin_prices
                  rename column price to price_usd;"""
    conn.execute(text(rename_col))
print(df2)

table_name2 = "coin_prices"
column_dtypes2 = {
    "coin_id" : "varchar(100)",
    "date" : "date",
    "price_usd" : "decimal(28, 6)"
}

with bridge.connect() as conn:
    for i, j in column_dtypes2.items():
        alter_sql2 = f"""
        modify {i} {j}"""
        conn.execute(text(alter_sql2))

df2 = pd.read_sql("describe coin_prices", bridge)
print(df2)

with bridge.connect() as con:
    con.execute(text(f"""alter table coin_prices
                    add constraint foreign key (coin_id)
                    references coin_list(id)
                    on delete cascade
                    on update cascade
                    """))

df2 = pd.read_sql("show create table coin_prices;", bridge)
print(df2)

df3 = pd.read_sql("select * from coin_list;", bridge)
print(df3.head())

df4 = pd.read_sql("select * from coin_prices;", bridge)
print(df4.head())


# Validate row Counts
