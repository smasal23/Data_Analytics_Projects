from __future__ import annotations

import streamlit as st


def render_cluster_result(result: dict, configs: dict):
    st.success("Cluster prediction generated successfully.")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Cluster Number", str(result["cluster"]))
    with c2:
        st.metric("Cluster Name", result["cluster_name"])

    if result.get("model_name"):
        st.caption(f"Clustering model: {result['model_name']}")


def render_cluster_profile_hint(result: dict):
    if result.get("cluster_name"):
        st.info(
            f"This diamond is assigned to **{result['cluster_name']}**. "
            "Cluster names are mapped from the saved clustering artifact bundle."
        )