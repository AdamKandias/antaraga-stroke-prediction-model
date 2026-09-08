"""Logika inti pelatihan model estimasi vital dari data kalibrasi.

Satu sumber kebenaran, dipakai baik oleh endpoint HTTP
(`api/main.py::calibrate_train`, dipicu tombol dashboard) maupun skrip CLI
standalone (`model/train_mlp_calibration.py`, untuk dijalankan manual lewat
SSH/terminal kalau training lewat HTTP timeout). Jangan duplikasi logika ini
ke tempat lain - import dari sini.

Untuk tiap target vital, beberapa keluarga model (MLP, SVR, KNN, Random
Forest, XGBoost, dst.) dan beberapa set fitur dibandingkan lewat validasi
silang yang identik; algoritma dengan R2 tertinggi (bukan persentase akurasi,
yang bisa menyesatkan untuk target dengan variasi kecil) disimpan sebagai
model produksi - bisa berbeda-beda per parameter. Hyperparameter tiap model
ditentukan tetap di awal, tidak dicari-cari lalu dipilih setelah melihat
skor. Metodologi ini divalidasi di model/test_loso.ipynb sebelum diterapkan
ke sini.
"""

from __future__ import annotations

import json
import pathlib
import warnings

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import (
    ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor,
)
from sklearn.linear_model import BayesianRidge, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import (
    GroupKFold, LeaveOneGroupOut, LeaveOneOut, cross_val_predict,
)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

FEATURES_T = [
    "ir_dc_mean", "ir_ac_p2p", "red_dc_mean", "red_ac_p2p",
    "bpm", "age_years", "gender_code",
]
TARGETS_T = {
    "gula_darah_mg_dl": "Gula Darah (mg/dL)",
    "kolesterol_mg_dl":  "Kolesterol (mg/dL)",
    "asam_urat_mg_dl":   "Asam Urat (mg/dL)",
    "sistolik_mmhg":     "Sistolik (mmHg)",
    "diastolik_mmhg":    "Diastolik (mmHg)",
}
# 5 = batas bawah teknis (LOO butuh minimal 3, di bawah 5 tidak ada sisa
# untuk diuji sama sekali).  Metrik di bawah 30 subjek TIDAK bermakna -
# lihat field "reliability" pada tiap target.
MIN_ROWS_T = 5

ARTIFACT_DIR = pathlib.Path(__file__).resolve().parent.parent / "model" / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "mlp_calibration.joblib"
METRICS_PATH = ARTIFACT_DIR / "mlp_calibration_metrics.json"


def records_to_dataframe(records: list[dict]) -> pd.DataFrame:
    """records: list of dict dengan key subject_id, age_years, gender, dan
    seluruh kolom FEATURES_T/TARGETS_T. Dipakai dari query SQLAlchemy (lihat
    api/main.py atau model/train_mlp_calibration.py)."""
    df = pd.DataFrame(records)
    df["gender_code"] = (df["gender"].str.upper() == "L").astype(float)
    for col in FEATURES_T:
        if col not in df.columns:
            df[col] = float("nan")
    df[FEATURES_T] = df[FEATURES_T].apply(pd.to_numeric, errors="coerce")
    return df


# Set fitur kandidat untuk pencarian model terbaik per target. Ditentukan
# lebih dulu berdasarkan alasan fisiologis (bukan dicari-cari lalu dipilih
# setelah melihat skor) - persis metodologi yang divalidasi di
# model/test_loso.ipynb bagian 7. "Penuh" dipakai sebagai baseline utama;
# subset yang lebih kecil sengaja disertakan karena literatur data-kecil
# (N<30) menyarankan membatasi jumlah fitur prediktor.
def _fitur_kandidat(features_penuh: list[str]) -> dict[str, list[str]]:
    return {
        "Penuh (7 fitur)": features_penuh,
        "Inti (bpm, usia, gender)": ["bpm", "age_years", "gender_code"],
        "Serapan (IR/red DC, usia)": ["ir_dc_mean", "red_dc_mean", "age_years"],
        "Minimal (usia saja)": ["age_years"],
    }


def _mlp_kwargs_for(n: int) -> dict:
    # Kapasitas MLP diskalakan ke jumlah data.  MLP (64,32) = 2.625 parameter;
    # memaksakannya ke 5 baris hanya menghasilkan hafalan, bukan model.
    # max_iter dipangkas (5000→800, 3000→600): lbfgs pada data sekecil ini
    # konvergen jauh lebih awal; nilai besar sebelumnya hanya memperlambat
    # tanpa mengubah hasil (diverifikasi tidak mengubah R2 pemenang per
    # parameter) - versi awal menyebabkan 504 Gateway Timeout di VPS.
    if n < 10:
        return dict(hidden_layer_sizes=(4,), activation="relu",
                    solver="lbfgs", alpha=1.0, max_iter=800, random_state=42)
    if n < 30:
        return dict(hidden_layer_sizes=(16, 8), activation="relu",
                    solver="lbfgs", alpha=0.1, max_iter=600, random_state=42)
    return dict(hidden_layer_sizes=(64, 32), activation="relu",
                solver="adam", alpha=0.01, max_iter=500, random_state=42,
                learning_rate_init=0.01, early_stopping=True,
                n_iter_no_change=15, validation_fraction=0.1)


def _model_kandidat(mlp_kwargs: dict) -> dict:
    return {
        "MLP (adaptif)":       MLPRegressor(**mlp_kwargs),
        "Ridge":               Ridge(alpha=1.0),
        "LinearRegression":    LinearRegression(),
        "KNN (k=3)":           KNeighborsRegressor(n_neighbors=3, weights="distance"),
        "KNN (k=5)":           KNeighborsRegressor(n_neighbors=5, weights="distance"),
        "SVR (linear)":        SVR(kernel="linear", C=1.0, epsilon=0.1),
        "SVR (rbf)":           SVR(kernel="rbf", C=1.0, epsilon=0.1),
        # n_estimators dipangkas (100→20, 50→20): pada N sekecil ini, hutan
        # besar cuma menambah waktu tanpa menambah akurasi cross-validation
        # secara berarti (diverifikasi: hasil pemenang per parameter tidak
        # berubah). Pencarian menguji 4 set fitur x 12 model x 5 target = 240
        # kombinasi per training, jadi biaya per model dikali besar.
        "RandomForest":        RandomForestRegressor(n_estimators=20, max_depth=3, random_state=42),
        "ExtraTrees":          ExtraTreesRegressor(n_estimators=20, max_depth=3, random_state=42),
        "GradientBoosting":    GradientBoostingRegressor(n_estimators=20, max_depth=2,
                                                           learning_rate=0.1, random_state=42),
        "BayesianRidge":       BayesianRidge(),
        "XGBoost (reg. ketat)": xgb.XGBRegressor(
            n_estimators=20, max_depth=2, learning_rate=0.1,
            reg_lambda=5.0, subsample=0.8, colsample_bytree=0.8,
            random_state=42, verbosity=0, n_jobs=1,
        ),
    }


def train_one_target(sub: pd.DataFrame, target_col: str, target_label: str) -> tuple[dict, dict] | None:
    """Latih & pilih model terbaik untuk satu target vital.

    sub: baris df yang sudah difilter (target_col dan seluruh FEATURES_T lengkap).
    Return (model_entry, metrics_entry), atau None kalau datanya < MIN_ROWS_T.
    """
    if len(sub) < MIN_ROWS_T:
        return None

    y = sub[target_col].values.astype(float)
    n = len(y)
    groups = sub["subject_id"].values
    n_subj = int(sub["subject_id"].nunique())
    mlp_kwargs = _mlp_kwargs_for(n)

    # Skema CV: bila satu subjek punya >1 rekaman, kelompokkan per subjek.
    # Tanpa ini, rekaman orang yang sama masuk ke data latih DAN data uji -
    # metrik jadi optimistis palsu (leakage), model terlihat akurat padahal
    # menghafal.
    cv_groups = None
    if n_subj < n and n_subj >= 2:
        if n_subj >= 5:
            cv_scheme, cv_label = GroupKFold(n_splits=min(5, n_subj)), "GroupKFold/subjek"
        else:
            cv_scheme, cv_label = LeaveOneGroupOut(), "LOGO/subjek"
        cv_groups = groups
    elif n < 30:
        cv_scheme, cv_label = LeaveOneOut(), "LOO"
    else:
        cv_scheme, cv_label = 5, "5-fold"

    kandidat_terbaik = None  # (r2, nama_model, nama_fitur, fitur_kolom, y_cv)
    perbandingan: list[dict] = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for nama_fitur, fitur_kolom in _fitur_kandidat(FEATURES_T).items():
            X_combo = sub[fitur_kolom].values.astype(float)
            Xs_combo = StandardScaler().fit_transform(X_combo)
            for nama_model, model in _model_kandidat(mlp_kwargs).items():
                try:
                    y_cv_combo = cross_val_predict(model, Xs_combo, y,
                                                   cv=cv_scheme, groups=cv_groups)
                except Exception:
                    continue
                r2_combo = float(r2_score(y, y_cv_combo))
                pct_err_combo = float(np.mean(np.abs(y - y_cv_combo) / np.maximum(np.abs(y), 1e-9)) * 100)
                acc_combo = round(100 - pct_err_combo, 2)
                perbandingan.append({
                    "model": nama_model, "fitur": nama_fitur,
                    "r2": round(r2_combo, 4), "accuracy_pct": acc_combo,
                })
                if kandidat_terbaik is None or r2_combo > kandidat_terbaik[0]:
                    kandidat_terbaik = (r2_combo, nama_model, nama_fitur, fitur_kolom, y_cv_combo)

        if kandidat_terbaik is None:
            return None
        _, model_name, feature_set_name, fitur_terpilih, y_cv = kandidat_terbaik

        # Latih ulang model pemenang pada seluruh data sebagai artifact final.
        X_final = sub[fitur_terpilih].values.astype(float)
        scaler = StandardScaler()
        Xs_final = scaler.fit_transform(X_final)
        model_final = _model_kandidat(mlp_kwargs)[model_name]
        model_final.fit(Xs_final, y)

    perbandingan.sort(key=lambda r: r["r2"], reverse=True)

    mae = float(mean_absolute_error(y, y_cv))
    rmse = float(np.sqrt(np.mean((y - y_cv) ** 2)))
    r2 = float(r2_score(y, y_cv))
    pct_err = float(np.mean(np.abs(y - y_cv) / np.maximum(np.abs(y), 1e-9)) * 100)
    acc = round(100 - pct_err, 2)

    # Status keterandalan - dilaporkan apa adanya agar angka di atas tidak
    # dibaca sebagai validasi alat.
    if n_subj < 10:
        reliability = "TIDAK VALID"
        reliability_note = (
            f"Hanya {n_subj} subjek. Metrik di bawah ini hasil undian sampel, "
            "bukan ukuran akurasi alat. Butuh ≥30 subjek agar bermakna."
        )
    elif n_subj < 30:
        reliability = "LEMAH"
        reliability_note = (
            f"{n_subj} subjek - metrik masih sangat goyah. "
            "Target ≥30 subjek untuk angka yang bisa dipertanggungjawabkan."
        )
    else:
        reliability = "MEMADAI"
        reliability_note = f"{n_subj} subjek - metrik dapat dilaporkan."

    model_entry = {"scaler": scaler, "model": model_final, "features": fitur_terpilih}
    metrics_entry = {
        "label": target_label, "n": n, "n_subjects": n_subj,
        "reliability": reliability, "reliability_note": reliability_note,
        "cv": cv_label,
        "model_name": model_name, "feature_set_name": feature_set_name,
        "mae": round(mae, 2), "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "mean_pct_error": round(pct_err, 2),
        "accuracy_pct": acc,
        # 5 kombinasi model+fitur teratas (dari semua yang dicoba, diurutkan
        # R2) - ditampilkan apa adanya di laporan supaya pemilihan model
        # tetap transparan, bukan cuma menunjukkan yang menang.
        "perbandingan_model": perbandingan[:5],
        # Simpan prediksi CV agar laporan bisa plot scatter tanpa re-train
        "cv_y_true": [round(float(v), 2) for v in y],
        "cv_y_pred": [round(float(v), 2) for v in y_cv],
    }
    return model_entry, metrics_entry


def train_all(df: pd.DataFrame) -> tuple[dict, dict]:
    """df: hasil records_to_dataframe(). Return (all_models, all_metrics),
    key-nya kolom target (mis. 'sistolik_mmhg')."""
    all_models: dict = {}
    all_metrics: dict = {}
    for target_col, target_label in TARGETS_T.items():
        sub = df[df[target_col].notna()].copy()
        sub = sub[sub[FEATURES_T].notna().all(axis=1)]
        hasil = train_one_target(sub, target_col, target_label)
        if hasil is None:
            continue
        model_entry, metrics_entry = hasil
        all_models[target_col] = model_entry
        all_metrics[target_col] = metrics_entry
    return all_models, all_metrics


def save_artifacts(all_models: dict, all_metrics: dict, meta: dict) -> None:
    """Tulis artifact model (.joblib) dan metrik (.json) ke model/artifacts/.

    Server yang sedang berjalan mendeteksi perubahan file ini secara
    otomatis lewat pengecekan mtime di api/ml_calibration.py - tidak perlu
    restart proses, baik dipanggil dari endpoint HTTP maupun skrip CLI
    terpisah (model/train_mlp_calibration.py).
    """
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    metrics_with_meta = {"_meta": meta, **all_metrics}
    joblib.dump(all_models, ARTIFACT_PATH)
    METRICS_PATH.write_text(json.dumps(metrics_with_meta, indent=2, ensure_ascii=False))
