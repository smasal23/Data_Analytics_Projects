import pandas as pd
from sqlalchemy import text
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)

from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Modify Column Dtypes
table_name3 = "oil_prices"
column_dtypes3 = {
    "date" : "date",
    "price_usd" : "decimal(18, 6)"
    }

with bridge.connect() as conn:
    for i, j in column_dtypes3.items():
        alter_sql3 = f"""alter table {table_name3}
                        modify {i} {j};
                    """
        conn.execute(text(alter_sql3))

df2 = pd.read_sql("describe oil_prices", bridge)
print(df2)


# Verify PK
df3 = pd.read_sql("alter table oil_prices add constraint primary key (date);", bridge)
df3 = pd.read_sql("describe oil_prices", bridge)
print(df3)


# Validate row Counts