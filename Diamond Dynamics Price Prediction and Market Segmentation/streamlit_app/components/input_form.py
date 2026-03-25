from __future__ import annotations

import streamlit as st


def render_input_form(configs: dict, form_key: str = "diamond_form", include_submit: bool = False):
    streamlit_cfg = configs["streamlit_config"]
    numeric_cfg = streamlit_cfg["input_form"]["numeric_inputs"]
    categorical_cfg = streamlit_cfg["input_form"]["categorical_inputs"]

    st.subheader("Diamond Input Form")

    col1, col2, col3 = st.columns(3)

    with col1:
        carat = st.number_input(
            "Carat",
            min_value=float(numeric_cfg["carat"]["min"]),
            max_value=float(numeric_cfg["carat"]["max"]),
            value=float(numeric_cfg["carat"]["default"]),
            step=float(numeric_cfg["carat"]["step"]),
            key=f"{form_key}_carat",
        )
        depth = st.number_input(
            "Depth",
            min_value=float(numeric_cfg["depth"]["min"]),
            max_value=float(numeric_cfg["depth"]["max"]),
            value=float(numeric_cfg["depth"]["default"]),
            step=float(numeric_cfg["depth"]["step"]),
            key=f"{form_key}_depth",
        )
        table = st.number_input(
            "Table",
            min_value=float(numeric_cfg["table"]["min"]),
            max_value=float(numeric_cfg["table"]["max"]),
            value=float(numeric_cfg["table"]["default"]),
            step=float(numeric_cfg["table"]["step"]),
            key=f"{form_key}_table",
        )

    with col2:
        x_val = st.number_input(
            "x (length)",
            min_value=float(numeric_cfg["x"]["min"]),
            max_value=float(numeric_cfg["x"]["max"]),
            value=float(numeric_cfg["x"]["default"]),
            step=float(numeric_cfg["x"]["step"]),
            key=f"{form_key}_x",
        )
        y_val = st.number_input(
            "y (width)",
            min_value=float(numeric_cfg["y"]["min"]),
            max_value=float(numeric_cfg["y"]["max"]),
            value=float(numeric_cfg["y"]["default"]),
            step=float(numeric_cfg["y"]["step"]),
            key=f"{form_key}_y",
        )
        z_val = st.number_input(
            "z (depth dimension)",
            min_value=float(numeric_cfg["z"]["min"]),
            max_value=float(numeric_cfg["z"]["max"]),
            value=float(numeric_cfg["z"]["default"]),
            step=float(numeric_cfg["z"]["step"]),
            key=f"{form_key}_z",
        )

    with col3:
        cut = st.selectbox(
            "Cut",
            options=categorical_cfg["cut"]["options"],
            index=categorical_cfg["cut"]["options"].index(categorical_cfg["cut"]["default"]),
            key=f"{form_key}_cut",
        )
        color = st.selectbox(
            "Color",
            options=categorical_cfg["color"]["options"],
            index=categorical_cfg["color"]["options"].index(categorical_cfg["color"]["default"]),
            key=f"{form_key}_color",
        )
        clarity = st.selectbox(
            "Clarity",
            options=categorical_cfg["clarity"]["options"],
            index=categorical_cfg["clarity"]["options"].index(categorical_cfg["clarity"]["default"]),
            key=f"{form_key}_clarity",
        )

    payload = {
        "carat": float(carat),
        "cut": str(cut),
        "color": str(color),
        "clarity": str(clarity),
        "depth": float(depth),
        "table": float(table),
        "x": float(x_val),
        "y": float(y_val),
        "z": float(z_val),
    }

    return payload