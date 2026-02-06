
import pymysql
import mysql
import pandas as pd
from sqlalchemy.dialects.mssql.information_schema import tables

pd.set_option("display.max_columns", None)
from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Create and Insert into Tables
df1 = pd.read_csv("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\crypto\\coin_list.csv")
print(df1.head())
print(df1.info())
df1.drop("Unnamed: 0", axis = 1, inplace = True)
print(df1.head())
df1.to_sql(name = "coin_list", con = bridge, if_exists = "replace", index = False)
print(df1.head())

df2 = pd.read_csv("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\crypto\\coin_prices.csv")
print(df2.head())
df2.drop("Unnamed: 0", axis = 1, inplace = True)
print(df2.head())
df2.to_sql(name = "coin_prices", con = bridge, if_exists = "replace", index = False)

df3 = pd.read_csv("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\oil\\oil_prices.csv")
print(df3.head())
df3.drop("Unnamed: 0", axis = 1, inplace = True)
print(df3.head())
df3.to_sql(name = "oil_prices", con = bridge, if_exists = "replace", index = False)

df4 = pd.read_csv("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\stocks\\stock_prices.csv")
print(df4.head())
df4.drop("Unnamed: 0", axis = 1, inplace = True)
print(df4.head())
df4.to_sql(name = 'stock_prices', con = bridge, if_exists = "replace", index = False)

df = pd.read_sql("show tables", bridge)
print(df)
# Index (date, ticker)