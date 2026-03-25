from __future__ import annotations

import streamlit as st


def render_sidebar_project_info(configs: dict):
    main_cfg = configs["main_config"]
    features_cfg = configs["features_config"]

    project_name = main_cfg["project"].get("display_name", "Diamond Dynamics")
    version = main_cfg["project"].get("version", "1.0.0")
    author = main_cfg["project"].get("author", "Shubham Masal")

    numeric_features = features_cfg["schema"].get("numeric_features", [])
    categorical_features = features_cfg["schema"].get("categorical_features", [])
    target_col = features_cfg["schema"].get("target_column", "price")

    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-header-card">
                <div class="sidebar-badge">ML Deployment</div>
                <h2>{project_name}</h2>
                <p>Interactive prediction and segmentation dashboard for diamonds.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Navigation")
        st.page_link("app.py", label="Home", icon="🏠")
        st.page_link("pages/1_Price_Prediction.py", label="Price Prediction", icon="💰")
        st.page_link("pages/2_Market_Segmentation.py", label="Market Segmentation", icon="📊")

        st.markdown("---")
        st.markdown("### Project Summary")
        st.markdown(
            f"""
            - **Version:** {version}
            - **Author:** {author}
            - **Target:** {target_col}
            - **Numeric Inputs:** {len(numeric_features)}
            - **Categorical Inputs:** {len(categorical_features)}
            """
        )

        st.markdown("---")
        st.markdown("### Input Features")
        st.caption("Numeric")
        for col in numeric_features:
            st.markdown(f"- {col}")

        st.caption("Categorical")
        for col in categorical_features:
            st.markdown(f"- {col}")

        st.markdown("---")
        st.markdown("### What this app does")
        st.markdown(
            """
            - predicts diamond price
            - converts prediction to INR
            - assigns market segment
            - validates user inputs
            - surfaces model-ready results
            """
        )

        st.markdown("---")
        st.markdown("### Tips")
        st.caption(
            "Use realistic values for carat and dimensions. Invalid geometry such as zero or highly imbalanced dimensions may fail validation."
        )


def render_quick_stats(features_cfg: dict, main_cfg: dict):
    numeric_features = features_cfg["schema"].get("numeric_features", [])
    categorical_features = features_cfg["schema"].get("categorical_features", [])
    target_col = features_cfg["schema"].get("target_column", "price")
    project_name = main_cfg["project"].get("display_name", "Diamond Dynamics")

    st.subheader("Project Snapshot")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Project", project_name)
    with c2:
        st.metric("Numeric Inputs", len(numeric_features))
    with c3:
        st.metric("Categorical Inputs", len(categorical_features))
    with c4:
        st.metric("Main Target", target_col)


def render_home_feature_cards():
    st.subheader("Core Capabilities")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h4>💎 Smart Inputs</h4>
                <p>Accepts raw gem attributes including carat, cut, color, clarity, and physical dimensions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h4>📈 Price Estimation</h4>
                <p>Uses the trained regression artifact to estimate value and display the converted INR output.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h4>🧩 Segment Discovery</h4>
                <p>Maps each diamond to a market segment using the saved clustering workflow and cluster-name mapping.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_how_it_works():
    st.subheader("How It Works")

    st.markdown(
        """
        <div class="info-card">
            <ol>
                <li>User enters raw diamond specifications</li>
                <li>Inputs are validated for completeness and geometry sanity</li>
                <li>The saved ML artifacts are loaded</li>
                <li>Regression predicts price and clustering predicts segment</li>
                <li>Results are shown in an easy-to-read UI</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_price_explanation(result: dict):
    st.subheader("Prediction Insight")
    st.write(
        "The predicted price is generated using the saved regression model pipeline, "
        "then converted to INR using the configured exchange-rate logic."
    )

    if result.get("engineered_preview"):
        st.markdown("#### Engineered Feature Preview")
        st.json(result["engineered_preview"])