import pandas as pd
from sqlalchemy import text
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.col_width", None)

from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Modify Column Datatypes
table_name4 = "stock_prices"
column_dtypes4 = {
    "date" : "date",
    "open" : "decimal(18, 6)",
    "high" : "decimal(18, 6)",
    "low" : "decimal(18, 6)",
    "close" : "decimal(18, 6)",
    "volume" : "bigint",
    "ticker" : "varchar(20)"
    }

with bridge.connect() as conn:
    for i, j in column_dtypes4.items():
        alter_sql4 = (f"""alter table {table_name4}
                        modify {i} {j};""")
        conn.execute(text(alter_sql4))

df = pd.read_sql("describe stock_prices", bridge)
print(df)