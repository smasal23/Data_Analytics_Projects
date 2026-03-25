from __future__ import annotations


def validate_user_input(payload: dict, configs: dict) -> dict:
    features_cfg = configs["features_config"]
    rules = features_cfg["validation_rules"]
    errors: list[str] = []

    # Required checks
    required_fields = ["carat", "cut", "color", "clarity", "depth", "table", "x", "y", "z"]
    for field in required_fields:
        if field not in payload or payload[field] in (None, ""):
            errors.append(f"Missing input: {field}")

    # Numeric checks
    if payload.get("carat", 0) <= 0:
        errors.append("Carat must be greater than zero.")

    for dim_col in rules["dimension_columns"]:
        if payload.get(dim_col, 0) <= 0:
            errors.append(f"{dim_col} must be greater than zero.")

    for col in rules["non_negative_columns"]:
        if col in payload and payload[col] < 0:
            errors.append(f"{col} cannot be negative.")

    # Allowed category checks
    allowed = rules["allowed_categories"]
    if payload.get("cut") not in allowed["cut"]:
        errors.append(f"Invalid cut value: {payload.get('cut')}")
    if payload.get("color") not in allowed["color"]:
        errors.append(f"Invalid color value: {payload.get('color')}")
    if payload.get("clarity") not in allowed["clarity"]:
        errors.append(f"Invalid clarity value: {payload.get('clarity')}")

    # Suspicious geometry checks
    x_val = float(payload.get("x", 0))
    y_val = float(payload.get("y", 0))
    z_val = float(payload.get("z", 0))

    if min(x_val, y_val, z_val) <= 0:
        errors.append("Invalid dimensions: x, y, and z must all be positive.")
    if z_val > max(x_val, y_val):
        errors.append("Invalid dimensions: z looks unusually larger than x/y.")
    if x_val > 0 and y_val > 0:
        ratio = max(x_val, y_val) / min(x_val, y_val)
        if ratio > 3:
            errors.append("Invalid dimensions: x and y are too imbalanced.")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }