"""Inference wrapper untuk model estimasi vital hasil kalibrasi (mlp_calibration.joblib).

Model per target dipilih otomatis dari beberapa keluarga model (MLP, SVR, KNN,
RandomForest, XGBoost, dst.) lewat pencarian model terbaik di
`api/main.py::calibrate_train` - bukan selalu MLP, meski nama file artifact
dipertahankan agar tidak mengubah alur deployment yang sudah berjalan.
Sebelum model pernah dilatih, is_calibration_model_available() mengembalikan
False dan semua fungsi di modul ini tidak tersedia.

Cache artifact dicek ulang berdasarkan mtime file (bukan lru_cache murni),
supaya training yang dijalankan dari proses lain - lewat skrip CLI
model/train_mlp_calibration.py di server, bukan cuma lewat endpoint HTTP di
proses yang sama - otomatis terdeteksi tanpa perlu restart server.

Output per sesi:
    gula_darah_mg_dl, kolesterol_mg_dl, asam_urat_mg_dl,
    sistolik_mmhg, diastolik_mmhg
"""

from __future__ import annotations

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

_cache: dict | None = None
_cache_mtime: float | None = None


def is_calibration_model_available() -> bool:
    return ARTIFACT_PATH.exists()


def _load_artifact() -> dict:
    global _cache, _cache_mtime
    if not ARTIFACT_PATH.exists():
        raise FileNotFoundError(
            f"Calibration model not found at {ARTIFACT_PATH}. "
            "Run `python model/train_mlp_calibration.py` after collecting calibration data."
        )
    mtime = ARTIFACT_PATH.stat().st_mtime
    if _cache is None or mtime != _cache_mtime:
        import joblib
        _cache = joblib.load(ARTIFACT_PATH)
        _cache_mtime = mtime
    return _cache


def predict_vitals(
    ir_dc_mean: float,
    ir_ac_p2p: float,
    red_dc_mean: float,
    red_ac_p2p: float,
    bpm: float,
    age_years: float = 60.0,
    gender_code: float = 0.5,  # 0=P, 1=L, 0.5=tidak diketahui
) -> dict[str, float]:
    """Prediksi vital sign dari fitur PPG menggunakan model kalibrasi estimasi vital.

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
            model = m["model"]
            # Susun ulang kolom sesuai urutan fitur model
            idx = [FEATURES.index(f) for f in features]
            X_ordered = X[:, idx]
            X_scaled = scaler.transform(X_ordered)
            results[target_col] = float(model.predict(X_scaled)[0])
        except Exception:
            continue

    return results


def compute_risk_flags_from_vitals(vitals: dict[str, float]) -> list[str]:
    """Flag risiko stroke berbasis nilai vital sign dari model kalibrasi estimasi vital."""
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
