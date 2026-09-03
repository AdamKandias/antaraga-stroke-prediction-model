"""Training script for the PPG -> vitals (BP + blood glucose) MLP.

This is the "pipeline now, model later" piece: the feature extraction
(`model/ppg_features.py`) has no learned parameters and is ready today, but
this script refuses to produce a model until real calibration data from the
ANTARAGA prototype exists (see `data/calibration/README.md`). There is no
synthetic or borrowed-journal data fallback here on purpose - training on
data that isn't from ANTARAGA's own hardware/population would produce a
model that looks accurate on paper but has no real predictive validity for
an actual user's wrist. The 30-row reference dataset from Gusti et al.
(2025) lives in `data/external_reference/` for sanity-checking only, not as
a training source (see that folder's README for the full reasoning).

Run with: python model/train_ppg_vitals.py
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import LeaveOneOut, KFold, cross_val_predict
from sklearn.metrics import mean_absolute_error
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from model.ppg_features import extract_pwa_features

ROOT = Path(__file__).resolve().parent.parent
CALIBRATION_PATH = ROOT / "data" / "calibration" / "calibration_data.csv"
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "ppg_vitals_model.joblib"
METRICS_PATH = ARTIFACT_DIR / "ppg_vitals_metrics.json"

TARGET_COLUMNS = ["systolic_bp_mmhg", "diastolic_bp_mmhg", "blood_glucose_mg_dl"]
MIN_ROWS_TO_TRAIN = 20


def _parse_signal(cell: str) -> list[float]:
    return [float(v) for v in str(cell).split(";") if v.strip()]


def _row_to_features(row: pd.Series) -> dict:
    features = extract_pwa_features(
        fs=float(row["fs_hz"]),
        green=_parse_signal(row["green_raw"]) if pd.notna(row.get("green_raw")) else None,
        red=_parse_signal(row["red_raw"]) if pd.notna(row.get("red_raw")) else None,
        infrared=_parse_signal(row["infrared_raw"]) if pd.notna(row.get("infrared_raw")) else None,
    )
    features["age_years"] = float(row["age_years"])
    return features


def build_feature_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    rows = [_row_to_features(row) for _, row in df.iterrows()]
    feature_df = pd.DataFrame(rows)
    feature_order = sorted(feature_df.columns)
    feature_df = feature_df[feature_order].fillna(0.0)
    return feature_df, feature_order


def main() -> None:
    if not CALIBRATION_PATH.exists():
        sys.exit(
            f"No calibration data found at {CALIBRATION_PATH}.\n\n"
            "This model is intentionally NOT trained on synthetic data or on the "
            "Gusti et al. (2025) journal reference (different hardware/population, "
            "see data/external_reference/README.md). Collect real PPG + ground-truth "
            "vitals from the ANTARAGA prototype during the 'Pengujian Alat' phase, "
            "format it per data/calibration/README.md, save it as that file, then "
            "re-run this script."
        )

    df = pd.read_csv(CALIBRATION_PATH)
    missing_targets = [c for c in TARGET_COLUMNS if c not in df.columns]
    if missing_targets:
        sys.exit(f"calibration_data.csv is missing required target column(s): {missing_targets}")

    X, feature_order = build_feature_matrix(df)
    y = df[TARGET_COLUMNS]

    n = len(df)
    if n < MIN_ROWS_TO_TRAIN:
        print(
            f"WARNING: only {n} calibration rows available (recommend >= {MIN_ROWS_TO_TRAIN}). "
            "Training anyway, but treat any metric below as a rough indication, not a "
            "validated accuracy figure -- do not report it as a final result."
        )

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = MLPRegressor(
        hidden_layer_sizes=(16, 8),
        activation="tanh",
        alpha=0.01,
        max_iter=5000,
        random_state=42,
    )

    cv = LeaveOneOut() if n < 50 else KFold(n_splits=5, shuffle=True, random_state=42)
    oof_pred = cross_val_predict(model, X_scaled, y, cv=cv)
    mae_per_target = {
        target: float(mean_absolute_error(y[target], oof_pred[:, i]))
        for i, target in enumerate(TARGET_COLUMNS)
    }

    model.fit(X_scaled, y)

    metrics = {
        "n_samples": n,
        "cv_strategy": "LeaveOneOut" if n < 50 else "KFold(5)",
        "mae_per_target_cv": mae_per_target,
        "feature_order": feature_order,
        "note": (
            "Cross-validated MAE on ANTARAGA's own calibration data only. "
            "Not comparable to Gusti et al. (2025)'s reported accuracy "
            "(different hardware, population, and target set)."
        ),
    }
    print(json.dumps(metrics, indent=2))

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "scaler": scaler,
            "feature_order": feature_order,
            "target_columns": TARGET_COLUMNS,
            "metrics": metrics,
        },
        ARTIFACT_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(f"\nSaved model artifact to {ARTIFACT_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    main()
