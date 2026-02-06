# To handle global configuration, navigation and shared resources.
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import streamlit as st
from streamlit_option_menu import option_menu
import base64
from pygments.styles.dracula import background
from src.utils import get_engine

bridge = get_engine()
print(bridge)

# Page Configuration
st.set_page_config(
    page_title = "Global Macro Monitor",
    page_icon = "🌐",
    layout = "wide",
    initial_sidebar_state = "expanded"
    )


# Sidebar - Global Navigation and Info
st.markdown("""
    <style>
    /* Hide default multipage sidebar */
    [data-testid = "stSidebarNav"] {
        display:none;
    }
    </style>
    """,
    unsafe_allow_html = True)

with st.sidebar:
    selected = option_menu(
        "NAVBAR",
        ["HOME", "MARKET OVERVIEW", "SQL RUNNER", "CRYPTO ANALYSIS"],
        icons = ["house", "bar-chart", "file-earmark-text", "currency-bitcoin"],
        menu_icon = "compass",
        default_index = 0
    )

st.sidebar.markdown("""
    🙌 **Credits**
    - 🖼️Project : Cross Market Analysis : Crypto, Oil and Stocks
    - 👨‍💻Developed By : Shubham Masal
    - 📊Data Source : CoinGecko, GitHub and Yahoo Finance
    - ⚙️Tech Stack : MySQL + Pandas + Matplotlib + Streamlit
    - 📧Contact : masalsam99@gmail.com""")

if selected == "MARKET OVERVIEW":
    from pages import market_overview
    market_overview.page_intro()
    market_overview.date_filter()
    market_overview.KPIs()
    market_overview.daily_snapshot()
elif selected == "SQL RUNNER":
    from pages import sql_runner
    sql_runner.page_intro()
    sql_runner.query_selection()
elif selected == "CRYPTO ANALYSIS":
    from pages.crypto_analysis import (
        page_intro,
        coin_selector,
        date_filter,
        fetch_data
    )

    page_intro()

    selected_coin = coin_selector()
    start_date, end_date = date_filter()

    fetch_data(
        bridge=bridge,
        selected_coin=selected_coin,
        start_date=start_date,
        end_date=end_date
    )

else:

# Title and Overview
    st.title("📊📉CROSS MARKET ANALYSIS 🧐")
    st.header("*MULTI-SECTOR :yellow[VOLATILITY] & :red[PERFORMANCE] OVERVIEW* ⚖️", divider = "gray")

    def set_bg(img_path):
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{data}");
            background-size: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    set_bg("F:\\onedrive\\Desktop\\DATA SCIENCE\\Project 1\\Cross-Market Analysis\\src\\streamlit_app\\Gemini_Generated_Image_84785c84785c8478.png")

    st.markdown("""
        <div style="
            max-width: 900px;
            background: rgba(10,15,25,0.75);
            padding: 24px 28px;
            border-radius: 16px;
            color: gold;
            font-size: 20px;
            font-weight: 600;
        ">

        <p>
        This Cross-Market Analysis platform unifies cryptocurrency, energy, and equity data
        through automated SQL pipelines and interactive dashboards to reveal how global
        markets move together.
        </p>

        <p>
        Cleaned and standardized time-series data powers real-time KPIs which will enable you to explore— such as:
        </p>

        <ul>
            <li>Individual market trends (Crypto / Oil / Stocks) - Returns</li> 
            <li>Price movements & indicators - Volatility</li>
            <li>Cross‑market relationships and correlations - Correlations</li>
        </ul>

        <p>
            By transforming fragmented market feeds into a single analytical view, the system supports:
        </p>

        <ul>
            <li>Smarter portfolio construction</li>
            <li>Risk monitoring</li>
            <li>Macro-driven decision-making</li>
        </ul>
        <p>
        <= Use the <b>sidebar</b> to navigate between markets.
        </p>
    
        </div>
        """,
        unsafe_allow_html=True
        )

    st.divider()


# Database Connection (GLOBAL)
    st.subheader("Database Status")

    try:
        engine = get_engine()
        with engine.connect():
            st.success("✅ Database Connected Successfully")
    except Exception as e:
        st.error("❌ Database Connection Failed")
        st.exception(e)


    st.divider()


# Instructions
    st.subheader("💡 How to Use This App")
    st.markdown("""
                <div style="
                max-width: 900px;
                background: rgba(10,15,25,0.75);
                padding: 24px 28px;
                border-radius: 16px;
                color: red;
                font-size: 20px;
                font-weight: 600;
            ">
        <ul>
        <li>1. Use the **Sidebar** to select a page.</li>
        <li>2. In the Market Overview, select between a range of dates to view averages and daily snapshots of the assets considered.</li>
        <li>3. In the SQL Runner, select any pre-defined analytical query to gather insights on the asset volatility.</li>
        <li>4. In the Crypto Analysis, select between a range of dates to visualize trends in the assets considered.</li>
        """,
        unsafe_allow_html = True
        )
