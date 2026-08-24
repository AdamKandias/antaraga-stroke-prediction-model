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


def _risk_level(
    probability: float, threshold: float, high_threshold: float | None = None
) -> str:
    """Tiga tingkat risiko dari dua ambang yang tugasnya berbeda.

      p <  threshold                    -> rendah  (tidak perlu tindak lanjut)
      threshold <= p < high_threshold   -> sedang  (perlu pemeriksaan lanjutan)
      p >= high_threshold               -> tinggi  (segera periksa)

    `threshold` adalah ambang deteksi yang sengaja dipasang rendah agar hampir
    tidak ada penderita yang terlewat.  `high_threshold` adalah titik F1 terbaik,
    tempat presisi dan recall paling seimbang.

    Keduanya WAJIB terpisah.  Sebelumnya batas "sedang" dihitung sebagai
    threshold * 0.5; begitu ambang deteksi diturunkan demi mengejar recall,
    batas itu ikut jatuh dan tidak seorang pun lagi mendapat label "rendah".
    Artefak lama yang belum punya high_threshold ditangani lewat fallback.
    """
    if high_threshold is None or high_threshold <= threshold:
        high_threshold = max(threshold, 0.5)      # perilaku lama, untuk artefak lama
    if probability >= high_threshold:
        return "high"
    if probability >= threshold:
        return "medium"
    return "low"


def _build_row(features: dict, artifact: dict) -> pd.DataFrame:
    feature_order = artifact["feature_order"]
    categorical_features = artifact["categorical_features"]
    category_values = artifact["category_values"]
    # Kolom yang tidak dikirim sama sekali diperlakukan sebagai nilai hilang,
    # bukan dilempar sebagai KeyError. Aplikasi mobile bisa mengirim muatan tak
    # lengkap (mis. pengguna melewatkan IMT), dan XGBoost sendiri sudah punya
    # penanganan bawaan untuk data hilang -- mempelajari arah percabangan terbaik
    # saat pelatihan. Membiarkan galat naik ke atas hanya membuat aplikasi rusak
    # di tangan pengguna tanpa alasan yang perlu.
    row = {col: features.get(col) for col in feature_order}
    frame = pd.DataFrame([row])[feature_order]

    # Kolom numerik dipastikan bertipe angka agar None menjadi NaN, bukan objek
    for col in feature_order:
        if col not in categorical_features:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")

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
    high_threshold = artifact.get("high_threshold")
    model = artifact["model"]

    frame = _build_row(features, artifact)
    probability = float(model.predict_proba(frame)[0, 1])

    return StrokeRiskPrediction(
        probability=probability,
        risk_level=_risk_level(probability, threshold, high_threshold),
        threshold=threshold,
        model_name=artifact["model_name"],
    )
