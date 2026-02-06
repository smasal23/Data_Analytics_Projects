import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from src.utils import get_engine
from datetime import date

bridge = get_engine()
print(bridge)

# Page Set-up
def page_intro():
    st.title(":orange[Cryptocurrency Analysis]")

    st.caption(":orange[Daily Price Analysis for Top Currencies]")

    st.divider()

    st.markdown("""
    <div style = "
                max_width: 900px;
                background: rgba(10, 15, 25, 0.75);
                padding: 24px 28px;
                border-radius: 16px;
                color: #CC5500;
                font-size: 20px;
                font-weight: 600;
    ">
    
    <p>
    Focuses on analyzing the daily price behavior of leading cryptocurrencies over a selected time period. Cryptocurrencies are known for their
    high volatility, and understanding their price movements at a granular, day-by-day level is essential for identifying trends and market patterns.
    </p>
    
    <p>
    In this page, users can select one cryptocurrency from the top-ranked coins and apply a custom date range filter to explore its 
    historical performance. The analysis presents:
    - A daily price trend line chart, visualizing how the selected cryptocurrency’s price changes over time & A detailed daily price table, 
    showing exact price values for deeper inspection and verification.
    </p>
    
    <p>
    This view helps users observe short-term fluctuations, trend directions, and price stability, and serves as a foundational analysis 
    before comparing cryptocurrencies with traditional assets like oil and stock indices in later stages of the project.
    </p>
    """,
    unsafe_allow_html = True)

    st.divider()

# Coin Selector
def coin_selector():
    top_coins = pd.read_sql("""select distinct coin_id
                                from coin_prices
                                order by coin_id
                                limit 5;
                                """, bridge)

    selected_coin = st.selectbox("Select CryptoCurrency:", top_coins["coin_id"])

    return selected_coin

# Date Filter
def date_filter():
    col1, space, col2 = st.columns([1, 0.5, 1])

    with col1:
        start_date = st.date_input(label = "📅 Start Date",
                                   min_value = date(2020, 1, 1),
                                   max_value = date(2026, 1, 25))

    with col2:
        end_date = st.date_input(label = "📅 End Date",
                                 min_value = date(2020, 1, 1),
                                 max_value = date(2026, 1, 25))

    if start_date > end_date:
        st.error("⚠️ Start date must be before end date.")
        st.stop()

    return start_date, end_date

# Fetch data
def fetch_data(bridge, selected_coin, start_date, end_date):

    query = f"""select date, price_usd
                from coin_prices
                where coin_id = '{selected_coin}'
                    and date between '{start_date}' and '{end_date}'
                order by date;
                """

    df = pd.read_sql(query, bridge)

    if df.empty:
        st.warning("No data available for the selected period.")
        return

# Line Chart

    df["date"] = pd.to_datetime(df["date"]).dt.date

    st.subheader(f"📈 {selected_coin.upper()} Daily Price Trend")

    fig, ax = plt.subplots()
    ax.plot(df['date'], df['price_usd'])
    ax.set_xlabel("Date")
    ax.set_ylabel("Price(USD)")
    ax.set_title(f"{selected_coin.upper()} Price Trend")

    plt.xticks(rotation = 45)
    st.pyplot(fig)

# Daily Table

    st.subheader("📊 Daily Price Table")
    st.dataframe(df)