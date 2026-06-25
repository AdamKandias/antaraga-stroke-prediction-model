"""Dev-mode hardware simulator.

When DEV_MODE=true, the API starts a background loop that periodically
behaves as if a real ANTARAGA smartband just finished a reading -- but only
for accounts that are actually "active" right now (a real Bearer token was
used within SIMULATOR_ACTIVE_WINDOW_SECONDS, see api/auth.py) AND that have
at least one profile ("parent") set up. There are no fixed demo users
anymore: register + fill in a profile, and the simulator picks you up
automatically while your session stays active; stop using the app and it
stops sending you data.

This only ever writes to *our own* prediction_logs/vital_readings tables,
since the simulator's job is to let you watch the model/ABCD2 logic and the
dashboard's vital cards react to "live" data, not to fabricate rows
anywhere else.
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone

from api import models_db
from api.config import SIMULATOR_ACTIVE_WINDOW_SECONDS, SIMULATOR_INTERVAL_SECONDS
from api.database import SessionLocal
from api.logging_utils import log_prediction, logger
from api.ml import predict_stroke_risk
from api.profile_utils import profile_to_features, record_vital_reading, resolve_active_profile


def _simulate_vitals() -> dict:
    return {
        "systolic_bp": max(90, round(random.gauss(135, 15))),
        "diastolic_bp": max(60, round(random.gauss(85, 10))),
        "avg_glucose_level": max(70.0, round(random.gauss(130, 35), 1)),
        "heart_rate_bpm": max(50, round(random.gauss(78, 10))),
        "spo2_percent": min(100, max(88, round(random.gauss(96, 2)))),
    }


def _active_candidates(db) -> list[tuple[models_db.User, models_db.Profile]]:
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=SIMULATOR_ACTIVE_WINDOW_SECONDS)
    active_users = (
        db.query(models_db.User)
        .filter(models_db.User.last_seen_at.isnot(None))
        .filter(models_db.User.last_seen_at >= cutoff)
        .all()
    )
    candidates = []
    for user in active_users:
        profile = resolve_active_profile(db, user.id)
        if profile is not None:
            candidates.append((user, profile))
    return candidates


async def _tick() -> None:
    db = SessionLocal()
    try:
        candidates = _active_candidates(db)
        if not candidates:
            logger.debug("[simulator] no active user with a profile yet -- skipping tick")
            return

        user, profile = random.choice(candidates)
        vitals = _simulate_vitals()
        features = profile_to_features(profile, vitals)
        result = predict_stroke_risk(features)

        record_vital_reading(
            db,
            profile.id,
            systolic_bp=vitals["systolic_bp"],
            blood_glucose_mg_dl=vitals["avg_glucose_level"],
            diastolic_bp=vitals["diastolic_bp"],
            heart_rate_bpm=vitals["heart_rate_bpm"],
            spo2_percent=vitals["spo2_percent"],
        )

        log_prediction(
            db,
            "stroke_risk",
            {"source": "hardware_simulator", **features, **vitals},
            dict(result),
            0.0,
            user_id=user.id,
            profile_id=profile.id,
        )
        logger.info(
            "[simulator] user=%s profile=%s(%s) risk=%s probability=%.3f",
            user.id,
            profile.id,
            profile.name,
            result["risk_level"],
            result["probability"],
        )
    finally:
        db.close()


async def run_simulator() -> None:
    logger.info(
        "Dev-mode hardware simulator started (interval=%ss, active_window=%ss)",
        SIMULATOR_INTERVAL_SECONDS,
        SIMULATOR_ACTIVE_WINDOW_SECONDS,
    )
    while True:
        await asyncio.sleep(SIMULATOR_INTERVAL_SECONDS)
        try:
            await _tick()
        except Exception:
            logger.exception("Simulator tick failed")
