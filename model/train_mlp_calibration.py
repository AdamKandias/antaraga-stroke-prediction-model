#!/usr/bin/env python3
"""Latih model estimasi vital ANTARAGA secara manual, tanpa lewat HTTP.

Berguna kalau endpoint /v1/calibrate/train timeout di server - pencarian
model per parameter menguji puluhan kombinasi model x set fitur (MLP, SVR,
KNN, RandomForest, ExtraTrees, GradientBoosting, XGBoost, dst.), yang bisa
berat kalau dijalankan lewat request HTTP di VPS dengan sumber daya terbatas.

Skrip ini memakai logika training yang IDENTIK dengan endpoint tersebut
(satu sumber kebenaran, lihat api/vital_model_training.py - tidak ada
duplikasi logika yang bisa saling berbeda seiring waktu), dan menulis
artifact yang sama (model/artifacts/mlp_calibration.joblib). Server yang
sedang berjalan mendeteksi perubahan file ini otomatis lewat pengecekan
mtime (lihat api/ml_calibration.py) - begitu skrip ini selesai, model baru
langsung dipakai server tanpa perlu restart proses/container.

Cara pakai di server (lewat SSH, masuk ke container yang sedang berjalan):
    docker compose -f docker-compose.prod.yml exec antaraga-api \\
        python model/train_mlp_calibration.py --mode real

Atau di lingkungan lokal (DATABASE_URL dari .env dipakai otomatis):
    python model/train_mlp_calibration.py --mode real

Kalau database kosong, skrip mencoba fallback membaca
data/calibration/calibration_data.csv (format lama, kolom otomatis
disesuaikan).
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from api.vital_model_training import records_to_dataframe, save_artifacts, train_all


def load_from_db(mode: str) -> pd.DataFrame:
    from api import models_db
    from api.database import SessionLocal

    db = SessionLocal()
    try:
        q = db.query(models_db.CalibrationRecord)
        if mode == "real":
            q = q.filter(models_db.CalibrationRecord.device_id != "demo-device")
        elif mode == "demo":
            q = q.filter(models_db.CalibrationRecord.device_id == "demo-device")
        rows = q.all()
    finally:
        db.close()

    if not rows:
        return pd.DataFrame()

    records = [
        {
            "subject_id":       r.subject_id,
            "age_years":        r.age_years,
            "gender":           r.gender,
            "ir_dc_mean":       r.ir_dc_mean,
            "ir_ac_p2p":        r.ir_ac_p2p,
            "red_dc_mean":      r.red_dc_mean,
            "red_ac_p2p":       r.red_ac_p2p,
            "bpm":              r.bpm,
            "gula_darah_mg_dl": r.gula_darah_mg_dl,
            "kolesterol_mg_dl":  r.kolesterol_mg_dl,
            "asam_urat_mg_dl":   r.asam_urat_mg_dl,
            "sistolik_mmhg":     r.sistolik_mmhg,
            "diastolik_mmhg":    r.diastolik_mmhg,
        }
        for r in rows
    ]
    return records_to_dataframe(records)


def load_from_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    rename = {
        "blood_glucose_mg_dl": "gula_darah_mg_dl",
        "systolic_bp_mmhg":    "sistolik_mmhg",
        "diastolic_bp_mmhg":   "diastolik_mmhg",
    }
    df.rename(columns=rename, inplace=True)
    return records_to_dataframe(df.to_dict("records"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode", choices=["all", "real", "demo"], default="real",
        help="all=semua rekaman, real=hanya sensor asli (default, bukan demo-device), "
             "demo=hanya data sintetis",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("ANTARAGA - Pelatihan Model Estimasi Vital")
    print("=" * 60)

    df = load_from_db(args.mode)
    if df.empty:
        csv_path = ROOT / "data" / "calibration" / "calibration_data.csv"
        if csv_path.exists():
            print(f"DB kosong (mode={args.mode}) - baca dari {csv_path}")
            df = load_from_csv(csv_path)
        else:
            label = {"real": "data asli", "demo": "demo data"}.get(args.mode, "kalibrasi")
            print(f"\nBelum ada {label} di database, dan tidak ada CSV cadangan di {csv_path}.")
            sys.exit(1)

    n_subjects = df["subject_id"].nunique() if "subject_id" in df.columns else "?"
    print(f"\nDataset: {len(df)} baris, {n_subjects} subjek unik (mode={args.mode})")

    t0 = time.time()
    all_models, all_metrics = train_all(df)
    dt = time.time() - t0

    if not all_models:
        print("\nTidak ada target yang cukup datanya untuk dilatih (minimum 5 baris/target).")
        sys.exit(1)

    meta = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_total": len(df),
        "n_subjects": int(n_subjects) if isinstance(n_subjects, (int, float)) else n_subjects,
        "mode": args.mode,
    }
    save_artifacts(all_models, all_metrics, meta)

    print(f"\nSelesai dalam {dt:.1f} detik. {len(all_models)} model tersimpan:\n")
    print(f"{'Parameter':<22}{'Model':<22}{'Fitur':<30}{'R2':>8}  {'Akurasi':>8}")
    print("-" * 92)
    for m in all_metrics.values():
        print(f"{m['label']:<22}{m['model_name']:<22}{m['feature_set_name']:<30}"
              f"{m['r2']:>8.4f}  {m['accuracy_pct']:>7.2f}%  [{m['reliability']}]")

    print(
        "\nArtifact ditulis ke model/artifacts/mlp_calibration.joblib. Server yang sedang "
        "berjalan otomatis memakai model baru ini pada request berikutnya (tidak perlu restart)."
    )


if __name__ == "__main__":
    main()
