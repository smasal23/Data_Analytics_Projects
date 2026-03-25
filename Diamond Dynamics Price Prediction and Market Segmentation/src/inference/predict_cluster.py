from __future__ import annotations

from streamlit_app.utils.preprocess_input import build_input_dataframe, add_runtime_engineered_features


def predict_cluster_from_dict(
    payload: dict,
    configs: dict,
    cluster_bundle: dict,
    usd_inr_rate: float | None = None,
) -> dict:
    df = build_input_dataframe(payload)

    project_root = None
    if usd_inr_rate is None:
        engineered_df, usd_inr_rate = add_runtime_engineered_features(df, project_root)
    else:
        engineered_df = df.copy()

    bundle = cluster_bundle["cluster_bundle"]
    model = bundle["model"]
    preprocessor = bundle["preprocessor"]
    feature_cols = bundle["feature_cols"]
    name_mapping = bundle.get("cluster_name_mapping", {})
    model_name = bundle.get("model_name", "clustering_model")

    X = engineered_df[feature_cols].copy()
    X_processed = preprocessor.transform(X)

    if hasattr(model, "predict"):
        cluster = int(model.predict(X_processed)[0])
    elif hasattr(model, "fit_predict"):
        cluster = int(model.fit_predict(X_processed)[0])
    else:
        raise AttributeError("Cluster model does not support predict or fit_predict.")

    cluster_name = name_mapping.get(cluster, f"Segment {cluster}")

    return {
        "cluster": cluster,
        "cluster_name": cluster_name,
        "model_name": model_name,
    }