"""Internal testing dashboard for the ANTARAGA model + API.

Run with: streamlit run dashboard/app.py

Three tabs:
- Coba Prediksi: manually try the stroke-risk model and the ABCD2 scorer.
- Metrics Model: training/evaluation metrics from the last `model/train.py` run.
- Log Riwayat: every prediction served by the API (or made from this
  dashboard), for debugging what the model has been asked and answered.

This talks to the model and the log database directly (not over HTTP), so it
works even if the FastAPI process isn't running.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.database import Base, SessionLocal, engine  # noqa: E402
from api.logging_utils import log_prediction  # noqa: E402
from api.ml import load_artifact, predict_stroke_risk  # noqa: E402
from api.models_db import PredictionLog  # noqa: E402
from model.abcd2 import calculate_abcd2  # noqa: E402

Base.metadata.create_all(bind=engine)

METRICS_PATH = Path(__file__).resolve().parent.parent / "model" / "artifacts" / "metrics.json"

st.set_page_config(page_title="ANTARAGA — Model Dashboard", layout="wide")
st.title("ANTARAGA — Dashboard Model & API")

tab_predict, tab_metrics, tab_logs = st.tabs(["Coba Prediksi", "Metrics Model", "Log Riwayat"])


with tab_predict:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Prediksi Risiko Stroke")
        with st.form("stroke_risk_form"):
            gender = st.selectbox("Gender", ["L", "P"])
            birthday = st.date_input("Tanggal lahir", value=datetime(1955, 1, 1))
            weight_kg = st.number_input("Berat badan (kg)", min_value=1.0, value=65.0)
            height_cm = st.number_input("Tinggi badan (cm)", min_value=1.0, value=160.0)
            status_merokok = st.selectbox(
                "Status merokok", ["never smoked", "formerly smoked", "smokes", "Unknown"]
            )
            heart_disease = st.checkbox("Riwayat penyakit jantung")
            residence_type = st.selectbox("Tempat tinggal", ["Urban", "Rural"])
            st.markdown("**Vital terbaru**")
            systolic_bp = st.number_input("Sistolik (mmHg)", min_value=0.0, value=130.0)
            diastolic_bp = st.number_input("Diastolik (mmHg)", min_value=0.0, value=85.0)
            blood_glucose = st.number_input("Gula darah (mg/dL)", min_value=0.0, value=110.0)
            submitted = st.form_submit_button("Prediksi")

        if submitted:
            age = (datetime.now().date() - birthday).days / 365.25
            bmi = weight_kg / ((height_cm / 100) ** 2)
            hypertension = int(systolic_bp >= 140 or diastolic_bp >= 90)
            features = {
                "gender": "Male" if gender == "L" else "Female",
                "age": age,
                "avg_glucose_level": blood_glucose,
                "bmi": bmi,
                "hypertension": hypertension,
                "heart_disease": int(heart_disease),
                "residence_type": residence_type,
                "smoking_status": status_merokok,
            }
            result = predict_stroke_risk(features)

            db = SessionLocal()
            try:
                log_prediction(
                    db,
                    "stroke_risk",
                    {"source": "dashboard", **features},
                    dict(result),
                    0.0,
                    user_id="dashboard-test",
                )
            finally:
                db.close()

            level_color = {"low": "green", "medium": "orange", "high": "red"}[result["risk_level"]]
            st.metric("Probabilitas risiko stroke", f"{result['probability']:.1%}")
            st.markdown(f"Tingkat risiko: **:{level_color}[{result['risk_level'].upper()}]**")
            st.caption(f"Model: {result['model_name']} · threshold={result['threshold']:.3f} · BMI dihitung={bmi:.1f}")

    with col2:
        st.subheader("Asesmen ABCD2")
        with st.form("abcd2_form"):
            abcd2_age = st.checkbox("Usia >= 60 tahun")
            abcd2_bp = st.checkbox("Tekanan darah elevasi (sistolik>=140 atau diastolik>=90)")
            abcd2_clinical = st.selectbox(
                "Fitur klinis",
                options=[0, 1, 2],
                format_func=lambda v: {
                    0: "0 - Tidak ada gejala fokal",
                    1: "1 - Gangguan bicara tanpa kelemahan",
                    2: "2 - Kelemahan unilateral",
                }[v],
            )
            abcd2_duration = st.selectbox(
                "Durasi gejala",
                options=[0, 1, 2],
                format_func=lambda v: {0: "0 - <10 menit", 1: "1 - 10-59 menit", 2: "2 - >=60 menit"}[v],
            )
            abcd2_diabetes = st.checkbox("Diabetes melitus")
            submitted_abcd2 = st.form_submit_button("Hitung Skor")

        if submitted_abcd2:
            result = calculate_abcd2(
                abcd2_age=abcd2_age,
                abcd2_bp=abcd2_bp,
                abcd2_clinical=abcd2_clinical,
                abcd2_duration=abcd2_duration,
                abcd2_diabetes=abcd2_diabetes,
            )
            payload = {
                "abcd2_age": abcd2_age,
                "abcd2_bp": abcd2_bp,
                "abcd2_clinical": abcd2_clinical,
                "abcd2_duration": abcd2_duration,
                "abcd2_diabetes": abcd2_diabetes,
            }
            response = {
                "score": result.score,
                "urgency": result.urgency.value,
                "recommendation": result.recommendation,
                "risk_2day_percent": result.risk_2day_percent,
                "risk_7day_percent": result.risk_7day_percent,
                "risk_90day_percent": result.risk_90day_percent,
            }
            db = SessionLocal()
            try:
                log_prediction(db, "abcd2", {"source": "dashboard", **payload}, response, 0.0, user_id="dashboard-test")
            finally:
                db.close()

            urgency_color = {"low": "green", "moderate": "orange", "high": "red"}[result.urgency.value]
            st.metric("Skor ABCD2", f"{result.score} / 7")
            st.markdown(f"Urgensi: **:{urgency_color}[{result.urgency.value.upper()}]**")
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Risiko 2 hari", f"{result.risk_2day_percent:.1f}%")
            rc2.metric("Risiko 7 hari", f"{result.risk_7day_percent:.1f}%")
            rc3.metric("Risiko 90 hari", f"{result.risk_90day_percent:.1f}%")
            st.info(result.recommendation)


with tab_metrics:
    if not METRICS_PATH.exists():
        st.warning("Belum ada model terlatih. Jalankan `python model/train.py` dulu.")
    else:
        metrics = json.loads(METRICS_PATH.read_text())
        artifact = load_artifact()

        st.subheader(f"Model terpilih: {metrics['model_name']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Test AUC", f"{metrics['test_auc']:.3f}")
        c2.metric("Test F1", f"{metrics['test_f1']:.3f}")
        c3.metric("Test Precision", f"{metrics['test_precision']:.3f}")
        c4.metric("Test Recall", f"{metrics['test_recall']:.3f}")

        c5, c6, c7 = st.columns(3)
        c5.metric("CV Average Precision", f"{metrics['cv_average_precision']:.3f}")
        c6.metric("Threshold", f"{metrics['threshold']:.3f}")
        c7.metric("Positive rate (data)", f"{metrics['positive_rate']:.1%}")

        st.markdown("**Confusion Matrix (test set, baris=aktual, kolom=prediksi)**")
        cm = metrics["test_confusion_matrix"]
        st.dataframe(
            pd.DataFrame(cm, index=["Actual: No Stroke", "Actual: Stroke"], columns=["Pred: No Stroke", "Pred: Stroke"])
        )

        st.markdown("**Hyperparameter terpilih**")
        st.json(metrics["best_params"])

        model = artifact["model"]
        importances = getattr(model, "feature_importances_", None)
        if importances is not None:
            st.markdown("**Feature importance**")
            fi_df = pd.DataFrame(
                {"feature": artifact["feature_order"], "importance": importances}
            ).sort_values("importance", ascending=False)
            st.bar_chart(fi_df.set_index("feature"))

        st.caption(
            f"Data latih: {metrics['n_train']} baris · Data test: {metrics['n_test']} baris · "
            "Fitur: " + ", ".join(artifact["feature_order"])
        )


with tab_logs:
    st.subheader("Riwayat Prediksi")
    db = SessionLocal()
    try:
        endpoint_filter = st.selectbox("Filter endpoint", ["Semua", "stroke_risk", "abcd2"])
        limit = st.slider("Jumlah baris", min_value=10, max_value=500, value=100, step=10)

        query = db.query(PredictionLog).order_by(PredictionLog.created_at.desc())
        if endpoint_filter != "Semua":
            query = query.filter(PredictionLog.endpoint == endpoint_filter)
        rows = query.limit(limit).all()
    finally:
        db.close()

    if not rows:
        st.info("Belum ada riwayat prediksi. Coba tab 'Coba Prediksi' atau panggil API-nya dulu.")
    else:
        df = pd.DataFrame(
            [
                {
                    "id": r.id,
                    "waktu": r.created_at,
                    "endpoint": r.endpoint,
                    "user_id": r.user_id,
                    "risk_level": r.risk_level,
                    "latency_ms": round(r.latency_ms, 2),
                    "request": r.request_payload,
                    "response": r.response_payload,
                }
                for r in rows
            ]
        )
        st.dataframe(df, use_container_width=True)
