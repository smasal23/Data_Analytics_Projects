from __future__ import annotations

import pandas as pd
import streamlit as st


def render_validation_errors(errors: list[str]):
    if not errors:
        return
    st.error("Please fix the following issues:")
    for err in errors:
        st.markdown(f"- {err}")


def render_input_preview_table(df: pd.DataFrame):
    st.subheader("Input Preview")
    st.dataframe(df, use_container_width=True)


def render_price_prediction_card(result: dict, configs: dict):
    rounded_usd = result["predicted_price_usd"]
    rounded_inr = result["predicted_price_inr"]
    display_currency = configs["streamlit_config"]["prediction"].get("show_prediction_currency", "USD")

    c1, c2 = st.columns(2)
    with c1:
        st.metric(label=f"Predicted Price ({display_currency})", value=f"{rounded_usd:,.2f}")
    with c2:
        st.metric(label="Predicted Price (INR)", value=f"₹ {rounded_inr:,.2f}")

    if "price_band" in result:
        st.info(f"Estimated price band: **{result['price_band']}**")

    if "used_exchange_rate" in result:
        st.caption(f"USD→INR rate used: {result['used_exchange_rate']:.4f}")