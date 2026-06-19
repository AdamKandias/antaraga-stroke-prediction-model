"""Loads the trained stroke-risk artifact and exposes a prediction helper."""

from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import joblib
import numpy as np
import pandas as pd

ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "model" / "artifacts" / "stroke_risk_model.joblib"


class StrokeRiskPrediction(TypedDict):
    probability: float
    risk_level: str
    threshold: float
    model_name: str


@lru_cache(maxsize=1)
def load_artifact() -> dict:
    if not ARTIFACT_PATH.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {ARTIFACT_PATH}. Run `python model/train.py` first."
        )
    return joblib.load(ARTIFACT_PATH)


def _risk_level(probability: float, threshold: float) -> str:
    if probability >= threshold:
        return "high"
    if probability >= threshold * 0.5:
        return "medium"
    return "low"


def _build_row(features: dict, artifact: dict) -> pd.DataFrame:
    feature_order = artifact["feature_order"]
    categorical_features = artifact["categorical_features"]
    category_values = artifact["category_values"]
    row = {col: features[col] for col in feature_order}
    frame = pd.DataFrame([row])[feature_order]

    if artifact["encoding"] == "native_categorical":
        for col in categorical_features:
            frame[col] = pd.Categorical(frame[col], categories=category_values[col])
    else:  # ordinal_codes (XGBoost fallback path)
        for col in categorical_features:
            categories = category_values[col]
            frame[col] = pd.Categorical(frame[col], categories=categories).codes.astype("float64")
            frame[col] = frame[col].replace(-1, np.nan)

    return frame


def predict_stroke_risk(features: dict) -> StrokeRiskPrediction:
    artifact = load_artifact()
    threshold = artifact["threshold"]
    model = artifact["model"]

    frame = _build_row(features, artifact)
    probability = float(model.predict_proba(frame)[0, 1])

    return StrokeRiskPrediction(
        probability=probability,
        risk_level=_risk_level(probability, threshold),
        threshold=threshold,
        model_name=artifact["model_name"],
    )
