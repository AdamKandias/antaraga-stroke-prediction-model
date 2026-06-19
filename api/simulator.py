"""Dev-mode hardware simulator.

When DEV_MODE=true, the API starts a background loop that periodically
behaves as if a real ANTARAGA smartband were sending readings for a couple
of fake users — so the prediction pipeline, logging, and dashboard can be
exercised end-to-end without real hardware or the Flutter app running.

This only ever writes to *our own* prediction_logs table (never to Supabase),
since the simulator's job is to let you watch the model/ABCD2 logic react to
"live" data, not to fabricate rows in the app's real database.
"""

import asyncio
import random

from api.config import SIMULATOR_INTERVAL_SECONDS
from api.database import SessionLocal
from api.logging_utils import log_prediction, logger
from api.ml import predict_stroke_risk

SIMULATED_USERS = [
    {"device_id": "smartband-demo-001", "user_id": "dev-user-budi", "gender": "Male", "age": 78, "bmi": 27.5},
    {"device_id": "smartband-demo-002", "user_id": "dev-user-siti", "gender": "Female", "age": 65, "bmi": 24.0},
]

_SMOKING_CHOICES = ["never smoked", "formerly smoked", "smokes", "Unknown"]


def _simulate_vitals() -> dict:
    return {
        "systolic_bp": max(90, round(random.gauss(135, 15))),
        "diastolic_bp": max(60, round(random.gauss(85, 10))),
        "avg_glucose_level": max(70.0, round(random.gauss(130, 35), 1)),
        "heart_rate_bpm": max(50, round(random.gauss(78, 10))),
        "spo2_percent": min(100, max(88, round(random.gauss(96, 2)))),
    }


async def _tick() -> None:
    user = random.choice(SIMULATED_USERS)
    vitals = _simulate_vitals()
    features = {
        "gender": user["gender"],
        "age": user["age"],
        "avg_glucose_level": vitals["avg_glucose_level"],
        "bmi": user["bmi"],
        "hypertension": int(vitals["systolic_bp"] >= 140 or vitals["diastolic_bp"] >= 90),
        "heart_disease": random.choice([0, 0, 0, 1]),
        "residence_type": random.choice(["Urban", "Rural"]),
        "smoking_status": random.choice(_SMOKING_CHOICES),
    }
    result = predict_stroke_risk(features)

    db = SessionLocal()
    try:
        log_prediction(
            db,
            "stroke_risk",
            {"source": "hardware_simulator", "device_id": user["device_id"], **features, **vitals},
            dict(result),
            0.0,
            user_id=user["user_id"],
        )
    finally:
        db.close()

    logger.info(
        "[simulator] device=%s user=%s risk=%s probability=%.3f",
        user["device_id"],
        user["user_id"],
        result["risk_level"],
        result["probability"],
    )


async def run_simulator() -> None:
    logger.info("Dev-mode hardware simulator started (interval=%ss)", SIMULATOR_INTERVAL_SECONDS)
    while True:
        await asyncio.sleep(SIMULATOR_INTERVAL_SECONDS)
        try:
            await _tick()
        except Exception:
            logger.exception("Simulator tick failed")
