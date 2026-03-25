from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inference.predict_price import predict_price_from_dict


class DummyPipeline:
    def predict(self, X):
        return [8.0]  # logged prediction


def test_predict_price_from_dict_logged_output():
    configs = {
        "streamlit_config": {
            "prediction": {
                "round_prediction_to": 2,
            }
        },
        "regression_config": {
            "regression": {
                "use_log_target": True,
                "inverse_transform_predictions_for_reporting": True,
            }
        },
    }

    payload = {
        "carat": 1.0,
        "cut": "Ideal",
        "color": "G",
        "clarity": "VS2",
        "depth": 61.5,
        "table": 57.0,
        "x": 6.4,
        "y": 6.3,
        "z": 4.0,
    }

    model_bundle = {
        "model_bundle": DummyPipeline(),
    }

    result = predict_price_from_dict(payload, configs, model_bundle, usd_inr_rate=80.0)

    assert "predicted_price_usd" in result
    assert "predicted_price_inr" in result
    assert result["predicted_price_usd"] > 0
    assert result["predicted_price_inr"] > result["predicted_price_usd"]