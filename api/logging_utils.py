import json
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

from sqlalchemy.orm import Session

from api.models_db import PredictionLog

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── Logger utama (api.log, rotasi per ukuran) ─────────────────────────────────
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

# ── Access logger (access.log, rotasi tengah malam, simpan 1 hari) ────────────
# backupCount=1 → simpan 1 backup (kemarin); file 2 hari lalu langsung dihapus.
access_logger = logging.getLogger("antaraga.access")
access_logger.setLevel(logging.INFO)
access_logger.propagate = False   # jangan ikut masuk ke api.log

if not access_logger.handlers:
    _acc_handler = TimedRotatingFileHandler(
        LOG_DIR / "access.log",
        when="midnight",
        backupCount=1,
        encoding="utf-8",
        utc=False,
    )
    _acc_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    access_logger.addHandler(_acc_handler)

    _acc_console = logging.StreamHandler()
    _acc_console.setFormatter(logging.Formatter("%(asctime)s [ACCESS] %(message)s"))
    access_logger.addHandler(_acc_console)


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
