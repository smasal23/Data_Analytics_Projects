from __future__ import annotations

import numpy as np

from streamlit_app.utils.preprocess_input import build_input_dataframe, add_runtime_engineered_features
from src.inference.postprocess import inverse_log_if_needed, map_price_band


def predict_price_from_dict(
    payload: dict,
    configs: dict,
    model_bundle: dict,
    usd_inr_rate: float | None = None,
) -> dict:
    df = build_input_dataframe(payload)

    project_root = None
    if usd_inr_rate is None:
        engineered_df, usd_inr_rate = add_runtime_engineered_features(df, project_root)
    else:
        engineered_df = df.copy()

    pipeline = model_bundle["model_bundle"]
    y_pred = pipeline.predict(engineered_df)[0]

    reg_cfg = configs["regression_config"]["regression"]
    streamlit_pred_cfg = configs["streamlit_config"]["prediction"]

    predicted_usd = inverse_log_if_needed(
        y_pred,
        use_log_target=reg_cfg.get("use_log_target", False),
        inverse_for_reporting=reg_cfg.get("inverse_transform_predictions_for_reporting", False),
    )

    predicted_inr = float(predicted_usd) * float(usd_inr_rate)
    round_digits = int(streamlit_pred_cfg.get("round_prediction_to", 2))

    engineered_preview = {}
    for col in ["volume", "volume_proxy", "length_width_ratio", "depth_pct_from_dimensions", "carat_squared"]:
        if col in engineered_df.columns:
            engineered_preview[col] = float(engineered_df.iloc[0][col])

    return {
        "predicted_price_usd": round(float(predicted_usd), round_digits),
        "predicted_price_inr": round(float(predicted_inr), round_digits),
        "used_exchange_rate": float(usd_inr_rate),
        "price_band": map_price_band(predicted_inr),
        "engineered_preview": engineered_preview,
    }