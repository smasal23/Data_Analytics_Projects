from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import load_project_configs
from src.utils.paths import find_project_root

from streamlit_app.components.input_form import render_input_form
from streamlit_app.components.cluster_display import (
    render_cluster_result,
    render_cluster_profile_hint,
)
from streamlit_app.components.prediction_cards import (
    render_validation_errors,
    render_input_preview_table,
)
from streamlit_app.components.charts import render_sidebar_project_info
from streamlit_app.utils.validation import validate_user_input
from streamlit_app.utils.load_models import load_clustering_artifacts
from src.inference.predict_cluster import predict_cluster_from_dict


def load_css(project_root: Path):
    css_path = project_root / "streamlit_app" / "assets" / "custom_styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    root = find_project_root(PROJECT_ROOT)
    configs = load_project_configs(root)
    streamlit_cfg = configs["streamlit_config"]

    load_css(root)
    render_sidebar_project_info(configs)

    st.title("📊 Market Segmentation")
    st.caption("Assign the diamond to a learned market segment.")

    user_input = render_input_form(configs=configs, form_key="cluster_form")

    validation = validate_user_input(user_input, configs=configs)
    if not validation["is_valid"]:
        render_validation_errors(validation["errors"])

    if streamlit_cfg["display"].get("show_input_preview", True):
        render_input_preview_table(pd.DataFrame([user_input]))

    if st.button("Predict Cluster", type="primary", use_container_width=True):
        if not validation["is_valid"]:
            st.warning(streamlit_cfg["messages"]["invalid_input_warning"])
            st.stop()

        try:
            artifacts = load_clustering_artifacts(root, configs)
            result = predict_cluster_from_dict(
                payload=user_input,
                configs=configs,
                cluster_bundle=artifacts,
            )

            render_cluster_result(result, configs=configs)
            render_cluster_profile_hint(result)

        except Exception as exc:
            st.error(f"Cluster prediction failed: {exc}")


if __name__ == "__main__":
    main()