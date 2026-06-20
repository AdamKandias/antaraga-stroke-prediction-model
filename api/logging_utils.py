import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from sqlalchemy.orm import Session

from api.models_db import PredictionLog

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("antaraga")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    file_handler = RotatingFileHandler(LOG_DIR / "api.log", maxBytes=2_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def log_prediction(
    db: Session,
    endpoint: str,
    request_payload: dict,
    response_payload: dict,
    latency_ms: float,
    user_id: str | None = None,
    profile_id: str | None = None,
) -> None:
    risk_level = response_payload.get("risk_level") or response_payload.get("urgency")
    entry = PredictionLog(
        endpoint=endpoint,
        user_id=user_id,
        profile_id=profile_id,
        request_payload=json.dumps(request_payload, default=str),
        response_payload=json.dumps(response_payload, default=str),
        risk_level=risk_level,
        latency_ms=latency_ms,
    )
    db.add(entry)
    db.commit()

    logger.info(
        "endpoint=%s user_id=%s latency_ms=%.2f risk_level=%s",
        endpoint,
        user_id,
        latency_ms,
        risk_level,
    )
