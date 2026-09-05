#!/usr/bin/env python3
"""
Pelatihan MLP dari dataset kalibrasi ANTARAGA (DB atau CSV).

Jalankan setelah mengumpulkan minimal 20 sesi kalibrasi:
  python model/train_mlp_calibration.py

Output:
  model/artifacts/mlp_calibration.joblib   - model terlatih
  model/artifacts/mlp_calibration_metrics.json
  reports/kalibrasi/scatter_*.png          - scatter plot untuk proposal
  reports/kalibrasi/training_report.txt    - ringkasan teks

Setiap parameter vital dilatih sebagai model MLPRegressor terpisah.
Fitur input: [ir_dc_mean, ir_ac_p2p, red_dc_mean, red_ac_p2p, bpm, age_years, gender_code]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut, cross_val_predict
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT_DIR = ROOT / "model" / "artifacts"
REPORT_DIR   = ROOT / "reports" / "kalibrasi"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = {
    "gula_darah_mg_dl":  "Gula Darah (mg/dL)",
    "kolesterol_mg_dl":  "Kolesterol (mg/dL)",
    "asam_urat_mg_dl":   "Asam Urat (mg/dL)",
    "sistolik_mmhg":     "Sistolik (mmHg)",
    "diastolik_mmhg":    "Diastolik (mmHg)",
}

FEATURES = [
    "ir_dc_mean", "ir_ac_p2p", "red_dc_mean", "red_ac_p2p",
    "bpm", "age_years", "gender_code",
]

MIN_ROWS = 10   # minimum untuk mulai training (idealnya ≥20)


# ── Muat data ─────────────────────────────────────────────────────────────

def load_from_db() -> pd.DataFrame:
    sys.path.insert(0, str(ROOT))
    from api.database import SessionLocal
    from api import models_db

    db = SessionLocal()
    try:
        rows = db.query(models_db.CalibrationRecord).all()
    finally:
        db.close()

    if not rows:
        return pd.DataFrame()

    records = []
    for r in rows:
        records.append({
            "subject_id":      r.subject_id,
            "age_years":       r.age_years,
            "gender":          r.gender,
            "kondisi":         r.kondisi,
            "ir_dc_mean":      r.ir_dc_mean,
            "ir_ac_p2p":       r.ir_ac_p2p,
            "red_dc_mean":     r.red_dc_mean,
            "red_ac_p2p":      r.red_ac_p2p,
            "bpm":             r.bpm,
            "gula_darah_mg_dl": r.gula_darah_mg_dl,
            "kolesterol_mg_dl":  r.kolesterol_mg_dl,
            "asam_urat_mg_dl":   r.asam_urat_mg_dl,
            "sistolik_mmhg":     r.sistolik_mmhg,
            "diastolik_mmhg":    r.diastolik_mmhg,
        })
    return pd.DataFrame(records)


def load_from_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalisasi kolom agar cocok dengan format DB
    rename = {
        "blood_glucose_mg_dl": "gula_darah_mg_dl",
        "systolic_bp_mmhg":    "sistolik_mmhg",
        "diastolic_bp_mmhg":   "diastolik_mmhg",
    }
    df.rename(columns=rename, inplace=True)
    return df


# ── Siapkan fitur ──────────────────────────────────────────────────────────

def prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["gender_code"] = (df["gender"].str.upper() == "L").astype(float)
    for col in FEATURES:
        if col not in df.columns:
            df[col] = np.nan
    df[FEATURES] = df[FEATURES].apply(pd.to_numeric, errors="coerce")
    return df


# ── Train satu target ──────────────────────────────────────────────────────

def train_one(
    X: np.ndarray, y: np.ndarray, groups: np.ndarray,
) -> tuple[StandardScaler, MLPRegressor, dict]:
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    # lbfgs lebih stabil untuk dataset kecil (<200 baris)
    mlp = MLPRegressor(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="lbfgs",
        alpha=0.01,
        max_iter=2000,
        random_state=42,
    )

    # Validasi WAJIB dikelompokkan per subjek, bukan per baris. Satu orang
    # yang direkam di beberapa sesi kalibrasi menghasilkan beberapa baris --
    # kalau baris-baris itu boleh terpisah antara latih dan uji, model bisa
    # "mengenali" orangnya dari sesi lain alih-alih benar-benar menebak dari
    # sinyal optik. LeaveOneOut() biasa tidak tahu soal ini dan akan
    # melaporkan akurasi yang bohong. Dibuktikan di
    # model/mlp_rancangan_15agustus.ipynb: LOO per baris R²=0,720 vs
    # GroupKFold per subjek R²=-4,737 pada data yang sama persis.
    n = len(y)
    n_subjek = len(np.unique(groups))
    cv = LeaveOneGroupOut() if n_subjek < 15 else GroupKFold(n_splits=5)
    y_pred_cv = cross_val_predict(
        MLPRegressor(hidden_layer_sizes=(64, 32), activation="relu",
                     solver="lbfgs", alpha=0.01, max_iter=2000, random_state=42),
        Xs, y, cv=cv, groups=groups,
    )

    mlp.fit(Xs, y)

    mae  = float(mean_absolute_error(y, y_pred_cv))
    rmse = float(np.sqrt(np.mean((y - y_pred_cv) ** 2)))
    r2   = float(r2_score(y, y_pred_cv))
    mean_pct_err = float(np.mean(np.abs(y - y_pred_cv) / np.abs(y + 1e-9)) * 100)
    acc  = round(100 - mean_pct_err, 2)

    metrics = {
        "n": n,
        "n_subjek": n_subjek,
        "cv": "LOSO (per subjek)" if n_subjek < 15 else "GroupKFold-5 (per subjek)",
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "mean_pct_error": round(mean_pct_err, 2),
        "accuracy_pct": acc,
    }
    return scaler, mlp, metrics, y_pred_cv


# ── Scatter plot ───────────────────────────────────────────────────────────

def make_scatter(y_true, y_pred, label: str, out: Path, metrics: dict):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"  [skip] matplotlib tidak tersedia - scatter {label} tidak dibuat")
        return

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(y_true, y_pred, color="#3987e5", alpha=0.75, s=50, zorder=3)

    lo = min(y_true.min(), y_pred.min()) * 0.95
    hi = max(y_true.max(), y_pred.max()) * 1.05
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1, alpha=0.5, label="Ideal")

    ax.set_xlabel(f"Referensi Invasif - {label}", fontsize=10)
    ax.set_ylabel(f"Prediksi Sensor - {label}", fontsize=10)
    ax.set_title(
        f"{label}\n"
        f"R²={metrics['r2']}  MAE={metrics['mae']}  Akurasi={metrics['accuracy_pct']}%",
        fontsize=9,
    )
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Scatter → {out}")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("ANTARAGA - Pelatihan MLP Kalibrasi Vital Sign")
    print("=" * 60)

    # Coba dari DB dulu, fallback ke CSV
    df = load_from_db()
    if df.empty:
        csv_path = ROOT / "data" / "calibration" / "calibration_data.csv"
        if csv_path.exists():
            print(f"DB kosong - baca dari {csv_path}")
            df = load_from_csv(csv_path)
        else:
            print("\n❌  Belum ada data kalibrasi.")
            print("    Rekam minimal", MIN_ROWS, "sesi via dashboard tab 'Kalibrasi',")
            print("    atau letakkan CSV di data/calibration/calibration_data.csv")
            sys.exit(1)

    df = prepare(df)
    print(f"\nDataset: {len(df)} baris, {df['subject_id'].nunique() if 'subject_id' in df.columns else '?'} subjek unik")

    if len(df) < MIN_ROWS:
        print(f"\n⚠️  Data terlalu sedikit ({len(df)}/{MIN_ROWS} baris minimum).")
        print("   Tambah lebih banyak rekaman kalibrasi sebelum melatih model.")
        sys.exit(1)

    # Statistik dataset
    print("\nStatistik fitur sinyal:")
    for col in ["ir_dc_mean", "bpm", "age_years"]:
        if col in df.columns and df[col].notna().any():
            s = df[col].dropna()
            print(f"  {col:15s}: n={len(s):3d}  mean={s.mean():.1f}  min={s.min():.1f}  max={s.max():.1f}")

    # Pelatihan per target
    all_metrics: dict = {}
    all_models: dict  = {}
    report_lines = ["ANTARAGA - Hasil Pelatihan MLP Kalibrasi\n" + "=" * 50]

    for target_col, target_label in TARGETS.items():
        sub = df[df[target_col].notna()].copy()
        mask_feat = sub[FEATURES].notna().all(axis=1)
        sub = sub[mask_feat]

        print(f"\n{'─'*50}")
        print(f"Target: {target_label}  ({len(sub)} baris tersedia)")

        if len(sub) < MIN_ROWS:
            print(f"  ⚠  Lewati - data tidak cukup ({len(sub)}/{MIN_ROWS})")
            report_lines.append(f"\n{target_label}: TIDAK CUKUP DATA ({len(sub)} baris)")
            continue

        X = sub[FEATURES].values.astype(float)
        y = sub[target_col].values.astype(float)
        groups = sub["subject_id"].values

        n_subjek = len(np.unique(groups))
        if n_subjek < MIN_SUBJEK:
            print(f"  ⚠  Lewati - subjek unik tidak cukup ({n_subjek}/{MIN_SUBJEK}). "
                  f"Baris boleh banyak, tapi kalau berasal dari sedikit orang saja, "
                  f"validasinya tidak berarti apa-apa.")
            report_lines.append(
                f"\n{target_label}: TIDAK CUKUP SUBJEK ({n_subjek} subjek, {len(sub)} baris)"
            )
            continue

        scaler, mlp, metrics, y_pred_cv = train_one(X, y, groups)

        print(f"  CV={metrics['cv']}  n={metrics['n']} baris dari {metrics['n_subjek']} subjek")
        print(f"  R²    = {metrics['r2']}")
        print(f"  MAE   = {metrics['mae']}")
        print(f"  RMSE  = {metrics['rmse']}")
        print(f"  Error = {metrics['mean_pct_error']}%  →  Akurasi {metrics['accuracy_pct']}%")

        all_models[target_col] = {"scaler": scaler, "mlp": mlp, "features": FEATURES}
        all_metrics[target_col] = {**metrics, "label": target_label}

        scatter_path = REPORT_DIR / f"scatter_{target_col}.png"
        make_scatter(y, y_pred_cv, target_label, scatter_path, metrics)

        report_lines.append(
            f"\n{target_label}\n"
            f"  N = {metrics['n']} baris ({metrics['n_subjek']} subjek unik)  CV = {metrics['cv']}\n"
            f"  R²       = {metrics['r2']}\n"
            f"  MAE      = {metrics['mae']}\n"
            f"  RMSE     = {metrics['rmse']}\n"
            f"  %Error   = {metrics['mean_pct_error']}%\n"
            f"  Akurasi  = {metrics['accuracy_pct']}%"
        )

    if not all_models:
        print("\n❌  Tidak ada target yang bisa dilatih (semua data tidak cukup).")
        sys.exit(1)

    # Simpan model dan metrik
    artifact_path = ARTIFACT_DIR / "mlp_calibration.joblib"
    metrics_path  = ARTIFACT_DIR / "mlp_calibration_metrics.json"
    report_path   = REPORT_DIR / "training_report.txt"

    joblib.dump(all_models, artifact_path)
    metrics_path.write_text(json.dumps(all_metrics, indent=2, ensure_ascii=False))
    report_path.write_text("\n".join(report_lines))

    print("\n" + "=" * 60)
    print(f"✅  Model tersimpan  → {artifact_path}")
    print(f"    Metrik           → {metrics_path}")
    print(f"    Laporan          → {report_path}")
    print(f"    Scatter plots    → {REPORT_DIR}/scatter_*.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
