import pandas as pd
import streamlit as st
from src.utils import get_engine
from datetime import date

bridge = get_engine()
print(bridge)
df1 = pd.read_csv("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\crypto\\coin_prices.csv")
df2 = pd.read_csv("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\oil\\oil_prices.csv")
df3 = pd.read_csv("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\Cross-Market Data\\cleaned\\stocks\\stock_prices.csv")


def page_intro():
    st.title(":blue[Asset Comparison and Exploration]")

    st.divider()

    st.markdown("""
          <div style="
            max-width: 900px;
            background: rgba(10,15,25,0.75);
            padding: 24px 28px;
            border-radius: 16px;
            color: cyan;
            font-size: 20px;
            font-weight: 600;
        ">
        
        <p> 
        Explore how major financial and commodity markets performed over a selected time period. By choosing a custom date range, 
        instantly view the average prices of key assets — including Bitcoin, Crude Oil, the S&P 500, and NIFTY.
        </p>
        
        <p>
        Alongside these summaries, a daily market snapshot table combines all four instruments into a single view, making it easier to compare
        market movements day-by-day across asset classes.
        </p>
        """,
        unsafe_allow_html = True)

    st.divider()

# Date Range Filter
def date_filter():
    st.markdown("Crypto * Oil * Stocks | SQL-powered analytics")

    col1, space, col2 = st.columns([1, 0.1, 1])

    with col1:
        start_date = st.date_input(
            label = "📅 Start Date",
            min_value = date(2020,1,1),
            max_value = date(2026,1,25)
            )

    with col2:
        end_date = st.date_input(
            label = "📅 End Date",
            min_value = date(2020, 1, 1),
            max_value = date(2026, 1, 25)
        )

    if start_date > end_date:
        st.error("Start Date must be before End Date.")

    st.session_state.start_date = start_date
    st.session_state.end_date = end_date

    st.divider()

# KPI cards
def KPIs():
    start_date = st.session_state.get("start_date")
    end_date = st.session_state.get("end_date")

    if not start_date or not end_date:
        st.info("Select a date range to view KPIs.")
        return

    # Convert dates
    for df in (df1, df2, df3):
        df["date"] = pd.to_datetime(df["date"])

    # Filter DF
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    filtered_df1 = df1[(df1["date"] >= start) &
                       (df1["date"] <= end)
                        ]
    filtered_df2 = df2[(df2["date"] >= start) &
                       (df2["date"] <= end)
                       ]
    filtered_df3 = df3[(df3["date"] >= start) &
                       (df3["date"] <= end)
                       ]

    # Calculate KPI averages
    btc_df = filtered_df1[filtered_df1["coin_id"] == "bitcoin"]
    avg_btc = btc_df["price"].mean()

    avg_oil = filtered_df2["price_usd"].mean()

    sp500_df = filtered_df3[filtered_df3["ticker"] == "^GSPC"]
    avg_sp500 = sp500_df["close"].mean()
    nifty_df = filtered_df3[filtered_df3["ticker"] == "^NSEI"]
    avg_nifty = nifty_df["close"].mean()

    # KPI Cards
    st.markdown("""
        <style>
        .kpi-badge {
                display: inline-block;
                padding: 10px 18px;
                border-radius: 999px;
                font-weight: 600;
                font-size: 15px;
                background: linear-gradient(135deg, #1f2937, #111827);
                color: #f9fafb;
                box-shadow: 0 4px 12px rgba(0,0,0,0.25);
                white-space: nowrap;
        }
        .kpi-title {
            font-size: 16px;
            opacity: 0.9;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 6px;
        }
        </style>
        """, unsafe_allow_html=True)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(
            f"""
            <div class="kpi-badge">
                <div class="kpi-title">₿ Bitcoin</div>
                <div class="kpi-value">${avg_btc:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi2:
        st.markdown(
            f"""
            <div class="kpi-badge">
                <div class="kpi-title">🛢️ Oil</div>
                <div class="kpi-value">${avg_oil:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi3:
        st.markdown(
            f"""
            <div class="kpi-badge">
                <div class="kpi-title">📈 S&P 500</div>
                <div class="kpi-value">{avg_sp500:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi4:
        st.markdown(
            f"""
            <div class="kpi-badge">
                <div class="kpi-title">🇮🇳 NIFTY 50</div>
                <div class="kpi-value">{avg_nifty:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()


# Snapshot Join Query
def daily_snapshot():
    start_date = st.session_state.get("start_date")
    end_date = st.session_state.get("end_date")

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    snapshot_df = pd.read_sql("""select c.date,
                    btc.price_usd as bitcoin_price,
                    oil.price_usd as oil_price,
                    sp.close as sp500,
                    nf.close as nifty
                    
                    from ( select distinct date from coin_prices) c
                    left join coin_prices btc
                    on c.date = btc.date
                        and btc.coin_id = 'bitcoin'
                        
                    left join oil_prices oil
                    on c.date = oil.date
                    
                    left join stock_prices sp
                    on c.date = sp.date
                        and sp.ticker = '^GSPC'
                    
                    left join stock_prices nf
                    on c.date = nf.date
                        and nf.ticker = '^NSEI'
                    
                    order by date desc;
                    """, bridge)


    snapshot_df['date'] = pd.to_datetime((snapshot_df["date"]))

    snapshot_df = snapshot_df[
                (snapshot_df["date"] >= start) &
                (snapshot_df["date"] <= end)
                ]

    snapshot_df["date"] = snapshot_df["date"].dt.date

    st.subheader("📉 Daily Market Snapshot")

    snapshot_df.rename(columns = {
                                "date": "📆 Date",
                                "bitcoin_price": "₿ Bitcoin ($)",
                                "oil_price": "🛢️ Oil ($)",
                                "sp500": "📈 S&P 500",
                                "nifty": "🇮🇳 NIFTY 50"
                                }, inplace=True)

    st.dataframe(snapshot_df, use_container_width = True)


# Table Rendering