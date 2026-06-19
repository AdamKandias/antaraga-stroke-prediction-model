"""Loads the trained PPG -> vitals (BP + blood glucose) artifact, if it
exists. Until `model/train_ppg_vitals.py` has been run against real
ANTARAGA calibration data, this artifact does not exist on purpose -- see
`data/calibration/README.md`."""

from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import joblib
import numpy as np

from model.ppg_features import extract_pwa_features

ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "model" / "artifacts" / "ppg_vitals_model.joblib"


class VitalsFromPpgPrediction(TypedDict):
    systolic_bp_mmhg: float
    diastolic_bp_mmhg: float
    blood_glucose_mg_dl: float


def is_model_available() -> bool:
    return ARTIFACT_PATH.exists()


@lru_cache(maxsize=1)
def load_artifact() -> dict:
    if not ARTIFACT_PATH.exists():
        raise FileNotFoundError(
            f"PPG vitals model artifact not found at {ARTIFACT_PATH}. "
            "Run `python -m model.train_ppg_vitals` once real calibration "
            "data exists (see data/calibration/README.md)."
        )
    return joblib.load(ARTIFACT_PATH)


def predict_vitals_from_ppg(
    fs_hz: float,
    age_years: float,
    green: list[float] | None = None,
    red: list[float] | None = None,
    infrared: list[float] | None = None,
) -> VitalsFromPpgPrediction:
    artifact = load_artifact()
    feature_order = artifact["feature_order"]
    scaler = artifact["scaler"]
    model = artifact["model"]

    features = extract_pwa_features(fs=fs_hz, green=green, red=red, infrared=infrared)
    features["age_years"] = age_years

    row = np.array([[features.get(col, 0.0) for col in feature_order]])
    row_scaled = scaler.transform(row)
    prediction = model.predict(row_scaled)[0]

    target_columns = artifact["target_columns"]
    return VitalsFromPpgPrediction(**{col: float(val) for col, val in zip(target_columns, prediction)})
