from __future__ import annotations

import numpy as np

from streamlit_app.utils.constants import PRICE_BANDS


def inverse_log_if_needed(value: float, use_log_target: bool, inverse_for_reporting: bool) -> float:
    if use_log_target and inverse_for_reporting:
        return float(np.expm1(value))
    return float(value)


def map_price_band(price_inr: float) -> str:
    for low, high, label in PRICE_BANDS:
        if low <= price_inr < high:
            return label
    return "Unknown"