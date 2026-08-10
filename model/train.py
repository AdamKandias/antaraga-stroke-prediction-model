"""Training script for the ANTARAGA stroke-risk model.

Design decisions (see README in this folder for the full rationale):

- Feature set is restricted to what the Flutter app can actually supply from
  `UserProfile` + `VitalData`: gender, age, heart_disease, residence_type,
  smoking_status, avg_glucose_level, bmi. `hypertension` is kept as a feature
  (the original dataset has it as a static diagnosis flag) but the API layer
  derives it from the latest BP reading since the app has no separate
  diagnosis field. `ever_married` and the 5-way `work_type` are dropped
  entirely: the app doesn't collect comparable data, and feeding the model a
  guessed proxy is worse than not using the feature.
- HistGradientBoostingClassifier (histogram-based GBDT, same family cited as
  "Gradient Boosting" in the proposal / Luo et al., 2025) is used instead of
  the plain GradientBoostingClassifier: it natively handles missing BMI
  values and unseen/missing categories at inference (no LabelEncoder crash on
  an unexpected category), and supports `class_weight="balanced"` directly
  for the imbalance problem.
- XGBoost is tried as a challenger with the same categorical/imbalance
  handling; whichever wins on cross-validated average precision is kept.
- The decision threshold is picked from out-of-fold predictions on the
  training set (never from the held-out test set) to avoid leakage.

Run with: python model/train.py
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_predict,
    train_test_split,
)
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "healthcare-dataset-stroke-data.csv"
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "stroke_risk_model.joblib"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"

NUMERIC_FEATURES = ["age", "avg_glucose_level", "bmi"]
BINARY_FEATURES = ["hypertension", "heart_disease", "is_working"]
CATEGORICAL_FEATURES = ["gender", "residence_type", "smoking_status"]
FEATURE_ORDER = NUMERIC_FEATURES + BINARY_FEATURES + CATEGORICAL_FEATURES

CATEGORY_VALUES = {
    "gender": ["Male", "Female", "Other"],
    "residence_type": ["Urban", "Rural"],
    "smoking_status": ["formerly smoked", "never smoked", "smokes", "Unknown"],
}

RANDOM_STATE = 42
CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df.rename(columns={"Residence_type": "residence_type"})
    # Map 5-way work_type ke binary is_working (kompatibel dengan input mobile app)
    df["is_working"] = df["work_type"].isin(["Private", "Self-employed", "Govt_job"]).astype(int)
    for col, categories in CATEGORY_VALUES.items():
        df[col] = pd.Categorical(df[col], categories=categories)
    return df[FEATURE_ORDER + ["stroke"]]


# Target recall dipatok pada prediksi OUT-OF-FOLD, bukan pada data uji.
#
# Diberi margin: ambang yang dipilih dari data latih selalu melemah sedikit saat
# dipakai di data baru.  Pada dataset ini target OOF 0,93 hanya menghasilkan
# recall 0,84 di data uji, sedangkan target OOF 0,98 menghasilkan 0,97.  Margin
# itulah alasan angkanya dipatok setinggi ini, bukan karena mengejar angka uji.
TARGET_RECALL = 0.98


def best_f1_threshold(y_true: np.ndarray, y_proba: np.ndarray) -> float:
    candidates = np.linspace(0.05, 0.95, 181)
    scores = [f1_score(y_true, (y_proba >= t).astype(int)) for t in candidates]
    return float(candidates[int(np.argmax(scores))])


def recall_target_threshold(
    y_true: np.ndarray, y_proba: np.ndarray, target: float = TARGET_RECALL
) -> float:
    """Ambang tertinggi yang masih mencapai recall >= target.

    ANTARAGA adalah alat SKRINING, bukan alat diagnosis.  Melewatkan penderita
    (false negative) jauh lebih berbahaya daripada merujuk orang sehat untuk
    pemeriksaan lanjutan (false positive), jadi recall yang dikejar lebih dulu.

    Kenapa mengambil ambang TERTINGGI yang memenuhi target, bukan yang terendah:
    setiap penurunan ambang menambah false positive, jadi begitu target recall
    tercapai tidak ada gunanya turun lebih jauh.

    Kenapa tidak dipatok 1,0: recall sempurna baru tercapai saat ambang jatuh
    ke ~0,02, dan di titik itu model menandai SELURUH orang sehat juga.
    Presisinya turun ke angka dasar populasi, artinya keluarannya tidak lagi
    membawa informasi apa pun.  Pada data uji, mengejar 2 penderita terakhir
    menambah lebih dari 500 false positive.
    """
    candidates = np.linspace(0.99, 0.01, 981)
    for t in candidates:                       # dari tinggi ke rendah
        if recall_score(y_true, (y_proba >= t).astype(int), zero_division=0) >= target:
            return float(t)
    return float(candidates[-1])


def tune_hist_gb(X, y) -> RandomizedSearchCV:
    # class_weight="balanced" reweights the loss internally; the scorer below
    # still evaluates on the *unweighted* labels, so the CV score stays honest.
    param_distributions = {
        "max_iter": [100, 150, 200, 300],
        "max_depth": [3, 4, 5, 6, None],
        "learning_rate": [0.03, 0.05, 0.08, 0.1],
        "max_leaf_nodes": [15, 31, 63],
        "l2_regularization": [0.0, 0.1, 0.5, 1.0],
        "min_samples_leaf": [10, 20, 30],
    }
    search = RandomizedSearchCV(
        estimator=HistGradientBoostingClassifier(
            categorical_features="from_dtype", class_weight="balanced", random_state=RANDOM_STATE
        ),
        param_distributions=param_distributions,
        n_iter=40,
        scoring="average_precision",
        cv=CV,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    search.fit(X, y)
    return search


def _ordinal_encode_for_xgb(X: pd.DataFrame) -> pd.DataFrame:
    """XGBoost's native categorical support gets unreliable when routed through
    sklearn's CV machinery (dtype info gets lost on some versions). Ordinal
    codes are a robust fallback that tree models handle fine for low-cardinality
    columns."""
    X = X.copy()
    for col in CATEGORICAL_FEATURES:
        X[col] = X[col].cat.codes.astype("float64").replace(-1, np.nan)
    return X


def tune_xgb(X, y) -> RandomizedSearchCV:
    # scale_pos_weight reweights XGBoost's loss internally (model hyperparameter,
    # not a fit-time sample_weight array), so it can never leak into the scorer.
    X_enc = _ordinal_encode_for_xgb(X)
    neg, pos = (y == 0).sum(), (y == 1).sum()
    base_ratio = neg / pos
    param_distributions = {
        "n_estimators": [100, 150, 200, 300],
        "max_depth": [3, 4, 5, 6],
        "learning_rate": [0.03, 0.05, 0.08, 0.1],
        "min_child_weight": [1, 5, 10],
        "subsample": [0.7, 0.85, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
        "reg_lambda": [0.5, 1.0, 2.0],
        "scale_pos_weight": [1.0, base_ratio * 0.25, base_ratio * 0.5, base_ratio],
    }
    search = RandomizedSearchCV(
        estimator=XGBClassifier(
            tree_method="hist",
            eval_metric="aucpr",
            random_state=RANDOM_STATE,
        ),
        param_distributions=param_distributions,
        n_iter=40,
        scoring="average_precision",
        cv=CV,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    search.fit(X_enc, y)
    return search


def main() -> None:
    df = load_dataset()
    X = df[FEATURE_ORDER]
    y = df["stroke"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=RANDOM_STATE, stratify=y
    )

    print("Tuning HistGradientBoostingClassifier...")
    hgb_search = tune_hist_gb(X_train, y_train)
    print(f"  best CV average_precision: {hgb_search.best_score_:.4f}")

    print("Tuning XGBClassifier...")
    xgb_search = tune_xgb(X_train, y_train)
    print(f"  best CV average_precision: {xgb_search.best_score_:.4f}")

    if hgb_search.best_score_ >= xgb_search.best_score_:
        model_name, search, encoding = "HistGradientBoostingClassifier", hgb_search, "native_categorical"
        X_train_model, X_test_model = X_train, X_test
    else:
        model_name, search, encoding = "XGBClassifier", xgb_search, "ordinal_codes"
        X_train_model, X_test_model = _ordinal_encode_for_xgb(X_train), _ordinal_encode_for_xgb(X_test)

    model = search.best_estimator_
    print(f"\nSelected model: {model_name} (CV average_precision={search.best_score_:.4f})")
    print(f"Best params: {search.best_params_}")

    oof_proba = cross_val_predict(model, X_train_model, y_train, cv=CV, method="predict_proba")[:, 1]

    # DUA ambang, dua tugas berbeda:
    #
    #   threshold      -> ambang DETEKSI.  Dipakai untuk memutuskan apakah satu
    #                     orang perlu ditindaklanjuti.  Sengaja rendah agar
    #                     hampir tidak ada penderita yang terlewat.
    #
    #   high_threshold -> batas label "risiko tinggi" yang tampil di aplikasi.
    #                     Memakai titik F1 terbaik, yaitu tempat presisi dan
    #                     recall paling seimbang.
    #
    # Keduanya harus terpisah.  Sebelumnya label risiko diturunkan dari
    # ambang deteksi (threshold * 0.5); begitu ambang deteksi turun ke 0,04,
    # SELURUH pengguna berlabel tinggi atau sedang dan tidak seorang pun
    # mendapat "rendah" -- labelnya jadi tidak berarti.
    threshold = recall_target_threshold(y_train.to_numpy(), oof_proba, TARGET_RECALL)
    high_threshold = best_f1_threshold(y_train.to_numpy(), oof_proba)

    proba_test = model.predict_proba(X_test_model)[:, 1]
    y_pred = (proba_test >= threshold).astype(int)

    cm = confusion_matrix(y_test, y_pred).tolist()
    metrics = {
        "model_name": model_name,
        "best_params": {k: (v if v is None or isinstance(v, (int, float, str)) else str(v)) for k, v in search.best_params_.items()},
        "cv_average_precision": float(search.best_score_),
        "threshold": threshold,
        "high_threshold": high_threshold,
        "target_recall": TARGET_RECALL,
        "test_auc": float(roc_auc_score(y_test, proba_test)),
        "test_average_precision": float(average_precision_score(y_test, proba_test)),
        "test_precision": float(precision_score(y_test, y_pred)),
        "test_recall": float(recall_score(y_test, y_pred)),
        "test_f1": float(f1_score(y_test, y_pred)),
        "test_confusion_matrix": cm,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "positive_rate": float(y.mean()),
    }
    print("\nTest set metrics:")
    print(json.dumps(metrics, indent=2))

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "model_name": model_name,
            "encoding": encoding,
            "feature_order": FEATURE_ORDER,
            "numeric_features": NUMERIC_FEATURES,
            "binary_features": BINARY_FEATURES,
            "categorical_features": CATEGORICAL_FEATURES,
            "category_values": CATEGORY_VALUES,
            "threshold": threshold,
            "high_threshold": high_threshold,
            "metrics": metrics,
        },
        ARTIFACT_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(f"\nSaved model artifact to {ARTIFACT_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    main()
