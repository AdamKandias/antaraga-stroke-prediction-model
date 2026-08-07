"""Inference wrapper untuk calibration MLP (mlp_calibration.joblib).

Model dilatih oleh model/train_mlp_calibration.py setelah data kalibrasi
terkumpul (minimal 10 sesi). Sebelum itu, is_calibration_model_available()
mengembalikan False dan semua fungsi di modul ini tidak tersedia.

Output per sesi:
    gula_darah_mg_dl, kolesterol_mg_dl, asam_urat_mg_dl,
    sistolik_mmhg, diastolik_mmhg
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

ARTIFACT_PATH = (
    Path(__file__).resolve().parent.parent
    / "model" / "artifacts" / "mlp_calibration.joblib"
)

FEATURES = [
    "ir_dc_mean", "ir_ac_p2p", "red_dc_mean", "red_ac_p2p",
    "bpm", "age_years", "gender_code",
]


def is_calibration_model_available() -> bool:
    return ARTIFACT_PATH.exists()


@lru_cache(maxsize=1)
def _load_artifact() -> dict:
    import joblib
    if not ARTIFACT_PATH.exists():
        raise FileNotFoundError(
            f"Calibration MLP not found at {ARTIFACT_PATH}. "
            "Run `python model/train_mlp_calibration.py` after collecting calibration data."
        )
    return joblib.load(ARTIFACT_PATH)


def predict_vitals(
    ir_dc_mean: float,
    ir_ac_p2p: float,
    red_dc_mean: float,
    red_ac_p2p: float,
    bpm: float,
    age_years: float = 60.0,
    gender_code: float = 0.5,  # 0=P, 1=L, 0.5=tidak diketahui
) -> dict[str, float]:
    """Prediksi vital sign dari fitur PPG menggunakan calibration MLP.

    Mengembalikan dict dengan key sesuai target yang berhasil dilatih,
    misalnya: gula_darah_mg_dl, kolesterol_mg_dl, asam_urat_mg_dl,
    sistolik_mmhg, diastolik_mmhg.
    Key yang modelnya belum dilatih (data tidak cukup) tidak muncul.
    """
    artifact = _load_artifact()
    X = np.array([[ir_dc_mean, ir_ac_p2p, red_dc_mean, red_ac_p2p,
                   bpm, age_years, gender_code]])

    results: dict[str, float] = {}
    for target_col, m in artifact.items():
        try:
            features = m["features"]
            scaler = m["scaler"]
            mlp = m["mlp"]
            # Susun ulang kolom sesuai urutan fitur model
            idx = [FEATURES.index(f) for f in features]
            X_ordered = X[:, idx]
            X_scaled = scaler.transform(X_ordered)
            results[target_col] = float(mlp.predict(X_scaled)[0])
        except Exception:
            continue

    return results


def compute_risk_flags_from_vitals(vitals: dict[str, float]) -> list[str]:
    """Flag risiko stroke berbasis nilai vital sign dari MLP kalibrasi."""
    flags: list[str] = []

    kolesterol = vitals.get("kolesterol_mg_dl")
    if kolesterol is not None:
        if kolesterol >= 240:
            flags.append(f"Kolesterol sangat tinggi ({kolesterol:.0f} mg/dL ≥240)")
        elif kolesterol >= 200:
            flags.append(f"Kolesterol batas tinggi ({kolesterol:.0f} mg/dL, 200–239)")

    asam_urat = vitals.get("asam_urat_mg_dl")
    if asam_urat is not None and asam_urat > 6.2:
        flags.append(f"Asam urat tinggi ({asam_urat:.1f} mg/dL >6,2)")

    sistolik = vitals.get("sistolik_mmhg")
    diastolik = vitals.get("diastolik_mmhg")
    if sistolik is not None and (sistolik >= 140 or (diastolik is not None and diastolik >= 90)):
        # Format diastolik disiapkan terpisah: menaruh kondisional di dalam
        # format-spec f-string ("{d:.0f if d else '?'}") bukan sintaks yang sah
        # dan melempar ValueError saat dijalankan.
        dia_txt = f"{diastolik:.0f}" if diastolik is not None else "?"
        flags.append(f"Tekanan darah tinggi ({sistolik:.0f}/{dia_txt} mmHg)")

    gula = vitals.get("gula_darah_mg_dl")
    if gula is not None and gula > 200:
        flags.append(f"Gula darah sangat tinggi ({gula:.0f} mg/dL >200)")

    return flags
