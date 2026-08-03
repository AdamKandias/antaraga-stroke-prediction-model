import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone

import os

import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from api import ingest_buffer, models_db, schemas
from api.auth import create_access_token, get_current_user_id, get_ingest_user_id
from api.config import DEV_MODE
from api.firmware import router as firmware_router
from api.ota import router as ota_router
from api.pwa_config import get_pwa_config, router as pwa_router
from api.database import Base, engine, get_db
from api.logging_utils import access_logger, log_prediction, logger
from api.ml import predict_stroke_risk
from api.ml_vitals import is_model_available, predict_vitals_from_ppg
from api.profile_utils import (
    age_from_birthday,
    compute_risk_flags,
    profile_to_features,
    record_vital_reading,
    resolve_active_profile,
)
from api.security import hash_password, verify_password
from api.simulator import run_simulator
from model.abcd2 import calculate_abcd2

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ANTARAGA API started (DEV_MODE=%s)", DEV_MODE)
    task = None
    if DEV_MODE:
        task = asyncio.create_task(run_simulator())
    yield
    if task is not None:
        task.cancel()


app = FastAPI(title="ANTARAGA API", version="0.4.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def access_log_middleware(request, call_next):
    t0 = time.time()
    response = await call_next(request)
    ms = (time.time() - t0) * 1000
    ip = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip() \
         or (request.client.host if request.client else "-")
    device_id = request.query_params.get("device_id", "")
    extra = f" device={device_id}" if device_id else ""
    access_logger.info(
        "%s \"%s %s\" %d %.0fms%s",
        ip, request.method, request.url.path, response.status_code, ms, extra,
    )
    return response

app.include_router(firmware_router)
app.include_router(ota_router)
app.include_router(pwa_router)


def _profile_to_response(profile: models_db.Profile) -> schemas.ProfileResponse:
    return schemas.ProfileResponse(
        id=profile.id,
        name=profile.name,
        gender=profile.gender,
        birthday=profile.birthday,
        weight_kg=profile.weight_kg,
        height_cm=profile.height_cm,
        status_merokok=profile.status_merokok,
        heart_disease=profile.heart_disease,
        is_working=profile.is_working,
        residence_type=profile.residence_type,
        has_diabetes=profile.has_diabetes,
        family_history_stroke=getattr(profile, "family_history_stroke", False),
    )


def _resolve_profile_for_request(
    db: Session, user_id: str, profile_id: str | None
) -> models_db.Profile:
    """Picks which "parent" a prediction/assessment request targets:
    `profile_id` if given (and it actually belongs to this user), else the
    account's active (last-viewed, else default/first-created) profile."""
    if profile_id:
        profile = db.get(models_db.Profile, profile_id)
        if profile is None or profile.user_id != user_id:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile

    profile = resolve_active_profile(db, user_id)
    if profile is None:
        raise HTTPException(
            status_code=400, detail="Isi profil dulu lewat POST /profiles sebelum prediksi"
        )
    return profile


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(_HOME_HTML, media_type="text/html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "dev_mode": DEV_MODE}


@app.post("/device/register-token", status_code=204)
def register_device_token(
    body: schemas.RegisterDeviceTokenRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> None:
    """Simpan FCM token device agar backend bisa kirim push notification."""
    user = db.query(models_db.User).filter(models_db.User.id == user_id).first()
    if user:
        user.fcm_token = body.fcm_token
        db.commit()


@app.post("/auth/register", response_model=schemas.AuthResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)) -> schemas.AuthResponse:
    filters = []
    if payload.email:
        filters.append(models_db.User.email == payload.email)
    if payload.phone:
        filters.append(models_db.User.phone == payload.phone)
    existing = db.query(models_db.User).filter(or_(*filters)).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email atau nomor HP sudah terdaftar")

    user = models_db.User(
        id=uuid.uuid4().hex,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        last_seen_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()

    token = create_access_token(user.id)
    return schemas.AuthResponse(access_token=token, user_id=user.id)


@app.post("/auth/login", response_model=schemas.AuthResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)) -> schemas.AuthResponse:
    user = (
        db.query(models_db.User)
        .filter(or_(models_db.User.email == payload.identifier, models_db.User.phone == payload.identifier))
        .first()
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email/HP atau password salah")

    user.last_seen_at = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(user.id)
    return schemas.AuthResponse(access_token=token, user_id=user.id)


@app.get("/auth/me", response_model=schemas.CurrentUserResponse)
def me(
    db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)
) -> schemas.CurrentUserResponse:
    user = db.get(models_db.User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.CurrentUserResponse(user_id=user.id, email=user.email, phone=user.phone)


@app.get("/profiles", response_model=list[schemas.ProfileResponse])
def list_profiles(
    db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)
) -> list[schemas.ProfileResponse]:
    profiles = (
        db.query(models_db.Profile)
        .filter(models_db.Profile.user_id == user_id)
        .order_by(models_db.Profile.created_at)
        .all()
    )
    return [_profile_to_response(p) for p in profiles]


@app.post("/profiles", response_model=schemas.ProfileResponse)
def create_profile(
    payload: schemas.ProfilePayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.ProfileResponse:
    profile = models_db.Profile(
        id=uuid.uuid4().hex,
        user_id=user_id,
        name=payload.name,
        gender=payload.gender.value,
        birthday=payload.birthday.date(),
        weight_kg=payload.weight_kg,
        height_cm=payload.height_cm,
        status_merokok=payload.status_merokok,
        heart_disease=payload.heart_disease,
        is_working=payload.is_working,
        residence_type=payload.residence_type.value,
        has_diabetes=payload.has_diabetes,
        family_history_stroke=payload.family_history_stroke,
    )
    db.add(profile)
    db.flush()

    # The first profile an account ever creates is its default "parent".
    # (No `user` row backs DEV_MODE's no-header fallback identity, hence the
    # None check -- that path just skips remembering a default.)
    user = db.get(models_db.User, user_id)
    if user is not None and user.last_viewed_profile_id is None:
        user.last_viewed_profile_id = profile.id

    db.commit()
    db.refresh(profile)
    return _profile_to_response(profile)


@app.get("/profiles/active", response_model=schemas.ProfileResponse)
def get_active_profile(
    db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)
) -> schemas.ProfileResponse:
    """The profile the app should open by default: last-viewed, else the
    first one ever created. 404 means the account has zero profiles yet —
    the app should show the profile-creation form (POST /profiles)."""
    profile = resolve_active_profile(db, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Belum ada profil orang tua/lansia")
    return _profile_to_response(profile)


@app.get("/profiles/{profile_id}", response_model=schemas.ProfileResponse)
def get_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.ProfileResponse:
    profile = db.get(models_db.Profile, profile_id)
    if profile is None or profile.user_id != user_id:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _profile_to_response(profile)


@app.put("/profiles/{profile_id}", response_model=schemas.ProfileResponse)
def update_profile(
    profile_id: str,
    payload: schemas.ProfilePayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.ProfileResponse:
    profile = db.get(models_db.Profile, profile_id)
    if profile is None or profile.user_id != user_id:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.name = payload.name
    profile.gender = payload.gender.value
    profile.birthday = payload.birthday.date()
    profile.weight_kg = payload.weight_kg
    profile.height_cm = payload.height_cm
    profile.status_merokok = payload.status_merokok
    profile.heart_disease = payload.heart_disease
    profile.is_working = payload.is_working
    profile.residence_type = payload.residence_type.value
    profile.has_diabetes = payload.has_diabetes
    profile.family_history_stroke = payload.family_history_stroke

    db.commit()
    db.refresh(profile)
    return _profile_to_response(profile)


@app.post("/profiles/{profile_id}/select", response_model=schemas.ProfileResponse)
def select_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.ProfileResponse:
    """Marks `profile_id` as this account's last-viewed parent -- call this
    when the app switches which parent it's showing."""
    profile = db.get(models_db.Profile, profile_id)
    if profile is None or profile.user_id != user_id:
        raise HTTPException(status_code=404, detail="Profile not found")

    user = db.get(models_db.User, user_id)
    if user is not None:
        user.last_viewed_profile_id = profile_id
        db.commit()
    return _profile_to_response(profile)


@app.post("/predict/stroke-risk", response_model=schemas.StrokeRiskResponse)
def predict_stroke_risk_endpoint(
    vital: schemas.VitalPayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.StrokeRiskResponse:
    start = time.perf_counter()

    profile = _resolve_profile_for_request(db, user_id, vital.profile_id)
    vital_dict = {
        "systolic_bp": vital.systolic_bp,
        "diastolic_bp": vital.diastolic_bp,
        "avg_glucose_level": vital.blood_glucose_mg_dl,
    }
    result = predict_stroke_risk(profile_to_features(profile, vital_dict))
    risk_flags = compute_risk_flags(profile)
    response = schemas.StrokeRiskResponse(**result, risk_flags=risk_flags)

    record_vital_reading(
        db,
        profile.id,
        systolic_bp=vital.systolic_bp,
        blood_glucose_mg_dl=vital.blood_glucose_mg_dl,
        diastolic_bp=vital.diastolic_bp,
        heart_rate_bpm=vital.heart_rate_bpm,
        spo2_percent=vital.spo2_percent,
    )

    latency_ms = (time.perf_counter() - start) * 1000
    log_prediction(
        db, "stroke_risk", vital.model_dump(), response.model_dump(), latency_ms,
        user_id=user_id, profile_id=profile.id,
    )
    return response


@app.get("/vitals/latest", response_model=schemas.LatestVitalResponse)
def get_latest_vital(
    profile_id: str | None = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.LatestVitalResponse:
    """Most recent vital-signs reading for the resolved profile, plus the
    risk assessment that was already computed for it -- purely a read, no
    new prediction is triggered (that only happens from a real
    /predict/stroke-risk call). 404 means no reading has ever arrived for
    this profile yet."""
    profile = _resolve_profile_for_request(db, user_id, profile_id)
    reading = (
        db.query(models_db.VitalReading)
        .filter(models_db.VitalReading.profile_id == profile.id)
        .order_by(desc(models_db.VitalReading.created_at))
        .first()
    )
    if reading is None:
        raise HTTPException(status_code=404, detail="Belum ada data vital untuk parent ini")

    log = (
        db.query(models_db.PredictionLog)
        .filter(models_db.PredictionLog.profile_id == profile.id)
        .filter(models_db.PredictionLog.endpoint == "stroke_risk")
        .order_by(desc(models_db.PredictionLog.created_at))
        .first()
    )
    risk = schemas.StrokeRiskResponse(**json.loads(log.response_payload)) if log else None

    return schemas.LatestVitalResponse(
        vital=schemas.VitalReadingResponse(
            systolic_bp=reading.systolic_bp,
            diastolic_bp=reading.diastolic_bp,
            heart_rate_bpm=reading.heart_rate_bpm,
            spo2_percent=reading.spo2_percent,
            blood_glucose_mg_dl=reading.blood_glucose_mg_dl,
            # All our DateTime columns are naive-but-conceptually-UTC
            # (datetime.utcnow() at insert time) -- attach the tz explicitly
            # so the JSON carries a UTC offset and the Flutter app's
            # DateTime.parse(...).toLocal() converts to the *device's*
            # timezone instead of silently treating UTC as if it were local.
            timestamp=reading.created_at.replace(tzinfo=timezone.utc),
        ),
        risk=risk,
    )


@app.get("/vitals/history", response_model=list[schemas.VitalReadingResponse])
def get_vital_history(
    date_: date | None = Query(None, alias="date"),
    profile_id: str | None = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> list[schemas.VitalReadingResponse]:
    """All vital-signs readings for the resolved profile on `date_` (server
    local date, defaults to today), oldest first. Empty list, not 404, if
    there's simply no data yet for that day."""
    profile = _resolve_profile_for_request(db, user_id, profile_id)
    day = date_ or datetime.now(timezone.utc).date()
    day_start = datetime.combine(day, datetime.min.time())
    day_end = day_start + timedelta(days=1)

    readings = (
        db.query(models_db.VitalReading)
        .filter(models_db.VitalReading.profile_id == profile.id)
        .filter(models_db.VitalReading.created_at >= day_start)
        .filter(models_db.VitalReading.created_at < day_end)
        .order_by(models_db.VitalReading.created_at)
        .all()
    )
    return [
        schemas.VitalReadingResponse(
            systolic_bp=r.systolic_bp,
            diastolic_bp=r.diastolic_bp,
            heart_rate_bpm=r.heart_rate_bpm,
            spo2_percent=r.spo2_percent,
            blood_glucose_mg_dl=r.blood_glucose_mg_dl,
            timestamp=r.created_at.replace(tzinfo=timezone.utc),
        )
        for r in readings
    ]


@app.post("/assessment/abcd2", response_model=schemas.Abcd2Response)
def assess_abcd2(
    payload: schemas.Abcd2Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.Abcd2Response:
    start = time.perf_counter()

    profile = _resolve_profile_for_request(db, user_id, payload.profile_id)

    result = calculate_abcd2(
        abcd2_age=payload.abcd2_age,
        abcd2_bp=payload.abcd2_bp,
        abcd2_clinical=payload.abcd2_clinical,
        abcd2_duration=payload.abcd2_duration,
        abcd2_diabetes=payload.abcd2_diabetes,
    )
    response = schemas.Abcd2Response(
        score=result.score,
        urgency=result.urgency.value,
        recommendation=result.recommendation,
        risk_2day_percent=result.risk_2day_percent,
        risk_7day_percent=result.risk_7day_percent,
        risk_90day_percent=result.risk_90day_percent,
    )

    latency_ms = (time.perf_counter() - start) * 1000
    log_prediction(
        db, "abcd2", payload.model_dump(), response.model_dump(), latency_ms,
        user_id=user_id, profile_id=profile.id,
    )
    return response


@app.post("/estimate/vitals-from-ppg", response_model=schemas.VitalsFromPpgResponse)
def estimate_vitals_from_ppg(
    payload: schemas.VitalsFromPpgRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.VitalsFromPpgResponse:
    if not is_model_available():
        raise HTTPException(
            status_code=503,
            detail=(
                "Model PPG->vitals belum dilatih. Pipeline-nya sudah siap, tapi "
                "menunggu data kalibrasi asli dari prototipe ANTARAGA (lihat "
                "data/calibration/README.md) -- bukan bug, ini status yang "
                "diharapkan sampai tahap Pengujian Alat selesai."
            ),
        )

    start = time.perf_counter()

    profile = _resolve_profile_for_request(db, user_id, payload.profile_id)

    result = predict_vitals_from_ppg(
        fs_hz=payload.fs_hz,
        age_years=age_from_birthday(profile.birthday),
        green=payload.green,
        red=payload.red,
        infrared=payload.infrared,
    )
    response = schemas.VitalsFromPpgResponse(**result)

    latency_ms = (time.perf_counter() - start) * 1000
    log_prediction(
        db,
        "vitals_from_ppg",
        {"fs_hz": payload.fs_hz, "n_channels": sum(c is not None for c in (payload.green, payload.red, payload.infrared))},
        response.model_dump(),
        latency_ms,
        user_id=user_id,
        profile_id=profile.id,
    )
    return response


@app.get("/v1/access-log")
def access_log(lines: int = 500) -> list[str]:
    """Baca N baris terakhir dari logs/access.log (fallback non-streaming)."""
    from api.logging_utils import LOG_DIR
    log_file = LOG_DIR / "access.log"
    if not log_file.exists():
        return []
    with log_file.open(errors="replace") as f:
        all_lines = f.readlines()
    return [l.rstrip() for l in reversed(all_lines) if l.strip()][:lines]


@app.get("/v1/access-log/stream")
async def access_log_stream():
    """SSE: kirim history access.log lalu tail untuk baris baru secara real-time.
    Klien menerima '__READY__' setelah history selesai, lalu baris baru tiap detik."""
    from api.logging_utils import LOG_DIR
    log_file = LOG_DIR / "access.log"

    async def _tail():
        pos = 0
        # History: 300 baris terakhir
        if log_file.exists():
            with log_file.open(errors="replace") as f:
                history = f.readlines()
                pos = f.tell()
            for line in history[-300:]:
                line = line.rstrip()
                if line:
                    yield f"data: {json.dumps(line)}\n\n"
        yield "data: __READY__\n\n"

        # Tail: poll tiap 1 detik untuk baris baru
        while True:
            await asyncio.sleep(1)
            if not log_file.exists():
                pos = 0
                continue
            try:
                size = log_file.stat().st_size
                if size < pos:
                    pos = 0   # file dirotasi tengah malam
                with log_file.open(errors="replace") as f:
                    f.seek(pos)
                    chunk = f.read()
                    pos = f.tell()
                for line in chunk.splitlines():
                    if line.strip():
                        yield f"data: {json.dumps(line.rstrip())}\n\n"
            except Exception:
                pos = 0

    return StreamingResponse(
        _tail(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/logs")
def list_logs(limit: int = 50, db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(models_db.PredictionLog)
        .order_by(desc(models_db.PredictionLog.created_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": row.id,
            "endpoint": row.endpoint,
            "user_id": row.user_id,
            "profile_id": row.profile_id,
            "request_payload": row.request_payload,
            "response_payload": row.response_payload,
            "risk_level": row.risk_level,
            "latency_ms": row.latency_ms,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


# ---------------------------------------------------------------------------
# /v1/ingest — menerima batch PPG dari firmware XIAO ESP32-S3
# ---------------------------------------------------------------------------

@app.post("/device/pair", response_model=schemas.DeviceStatusResponse)
def pair_device(
    body: schemas.PairDeviceRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.DeviceStatusResponse:
    """Hubungkan DEVICE_ID firmware ke akun ini. Masukkan nilai DEVICE_ID
    dari config.h, misal 'antaraga-001'. Setelah ini, data dari firmware
    tersebut otomatis masuk ke akun yang melakukan pairing."""
    key = body.device_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="device_key tidak boleh kosong")

    # Cek kalau device sudah di-pair ke akun lain
    existing = (
        db.query(models_db.User)
        .filter(models_db.User.device_key == key)
        .filter(models_db.User.id != user_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Perangkat ini sudah terhubung ke akun lain")

    user = db.query(models_db.User).filter(models_db.User.id == user_id).first()
    if user:
        user.device_key = key
        db.commit()
    return schemas.DeviceStatusResponse(paired=True, device_key=key)


@app.get("/device/status", response_model=schemas.DeviceStatusResponse)
def device_status(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.DeviceStatusResponse:
    """Cek apakah akun ini sudah terhubung ke perangkat."""
    user = db.query(models_db.User).filter(models_db.User.id == user_id).first()
    if user and user.device_key:
        return schemas.DeviceStatusResponse(paired=True, device_key=user.device_key)
    return schemas.DeviceStatusResponse(paired=False)


@app.post("/v1/ingest", response_model=schemas.IngestResponse)
def ingest_firmware_batch(
    batch: schemas.IngestBatch,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_ingest_user_id),
) -> schemas.IngestResponse:
    """Endpoint utama yang dipanggil firmware setiap BATCH_MS (default 500 ms).
    User diidentifikasi lewat device_key (batch.id) yang di-pair via mobile app.
    Pipeline: PPG → estimasi vital (MLP jika tersedia) → stroke risk (XGBoost)
    → simpan reading → FCM kalau HIGH."""
    start = time.perf_counter()

    # Cari user yang sudah pair device ini — prioritas utama
    paired_user = (
        db.query(models_db.User)
        .filter(models_db.User.device_key == batch.id)
        .first()
    )
    if paired_user:
        user_id = paired_user.id

    # Simpan ke buffer dulu (sebelum early-return) supaya dashboard bisa membaca
    ingest_buffer.store(batch.id, batch.model_dump())

    profile = resolve_active_profile(db, user_id)
    if profile is None:
        return schemas.IngestResponse(ok=True, seq=batch.seq)

    # --- Estimasi vital dari sinyal PPG --------------------------------
    vitals: dict = {}
    if is_model_available() and (batch.ppg or batch.red or batch.ir):
        try:
            vitals = predict_vitals_from_ppg(
                fs_hz=float(batch.fs_ppg or batch.fs_max or 200),
                age_years=age_from_birthday(profile.birthday),
                green=[float(v) for v in batch.ppg] if batch.ppg else None,
                red=[float(v) for v in batch.red] if batch.red else None,
                infrared=[float(v) for v in batch.ir] if batch.ir else None,
            )
        except Exception:
            pass  # model belum dilatih atau sinyal terlalu pendek

    if not vitals:
        # MLP belum tersedia: ambil vital terakhir yang sudah ada di DB
        last = (
            db.query(models_db.VitalReading)
            .filter(models_db.VitalReading.profile_id == profile.id)
            .order_by(desc(models_db.VitalReading.created_at))
            .first()
        )
        if last:
            vitals = {
                "systolic_bp_mmhg": last.systolic_bp,
                "diastolic_bp_mmhg": last.diastolic_bp,
                "blood_glucose_mg_dl": last.blood_glucose_mg_dl,
            }

    if not vitals:
        # Tidak ada data vital sama sekali → simpan batch metadata saja
        return schemas.IngestResponse(ok=True, seq=batch.seq)

    # --- Prediksi stroke risk -------------------------------------------
    features = profile_to_features(profile, {
        "systolic_bp": vitals.get("systolic_bp_mmhg", 120.0),
        "diastolic_bp": vitals.get("diastolic_bp_mmhg"),
        "avg_glucose_level": vitals.get("blood_glucose_mg_dl", 100.0),
    })
    result = predict_stroke_risk(features)

    # --- Simpan reading -------------------------------------------------
    record_vital_reading(
        db,
        profile.id,
        systolic_bp=vitals.get("systolic_bp_mmhg", 120.0),
        diastolic_bp=vitals.get("diastolic_bp_mmhg"),
        blood_glucose_mg_dl=vitals.get("blood_glucose_mg_dl", 100.0),
    )

    latency_ms = (time.perf_counter() - start) * 1000
    log_prediction(
        db, "stroke_risk",
        {"source": "firmware", "device_id": batch.id, "seq": batch.seq,
         "batt_pct": batch.batt_pct, "ppg_n": len(batch.ppg)},
        result, latency_ms,
        user_id=user_id, profile_id=profile.id,
    )

    # --- FCM kalau HIGH -------------------------------------------------
    if result["risk_level"] == "HIGH":
        from api.config import FCM_NOTIFICATION_COOLDOWN_SECONDS
        from api.fcm import send_high_risk_notification

        user = db.query(models_db.User).filter(models_db.User.id == user_id).first()
        if user and user.fcm_token:
            cooldown = timedelta(seconds=FCM_NOTIFICATION_COOLDOWN_SECONDS)
            now_utc = datetime.now(timezone.utc)
            last_notified = user.last_notified_at
            last_utc = last_notified.replace(tzinfo=timezone.utc) if last_notified else None
            if last_utc is None or (now_utc - last_utc) > cooldown:
                sent = send_high_risk_notification(user.fcm_token, profile.name)
                if sent:
                    user.last_notified_at = datetime.utcnow()
                    db.commit()

    return schemas.IngestResponse(ok=True, seq=batch.seq, risk_level=result["risk_level"])


# ---------------------------------------------------------------------------
# SQI helpers — filter batch berkualitas buruk sebelum analisis
# Flag bitmask sesuai Firmware/include/antaraga.h
# ---------------------------------------------------------------------------

_SQI_F_NO_FINGER = 0x01  # sensor tidak menempel
_SQI_F_SATURATED = 0x02  # ADC jenuh
_SQI_F_FLAT      = 0x04  # sinyal datar / tanpa denyut
_SQI_F_MOTION    = 0x08  # artefak gerak
_SQI_F_PPG_BAD   = 0x10  # kanal SON1303 buruk
_SQI_F_SHORT     = 0x20  # batch terlalu pendek

# Flag yang membuat data IR/RED tidak dapat dipakai untuk BPM dan analisis sinyal
_SQI_DISCARD = _SQI_F_NO_FINGER | _SQI_F_SATURATED | _SQI_F_FLAT | _SQI_F_MOTION

# Untuk kanal hijau (SON1303): MOTION dari IR tidak ikut — kanal hijau punya flag
# PPG_BAD sendiri. Gerakan ringan yang men-trigger tortuosity IR tidak harus
# memblokir green, karena bandpass 0.5–5 Hz sudah meredam sebagian besar artefak.
_SQI_DISCARD_GREEN = _SQI_F_NO_FINGER | _SQI_F_SATURATED | _SQI_F_FLAT | _SQI_F_PPG_BAD


def _filter_good_batches(batches: list[dict]) -> list[dict]:
    """Kembalikan batch tanpa flag kritis (IR/RED); jika semua buruk, kembalikan semua (fallback)."""
    good = [b for b in batches if not (b.get("sqi_flags", 0) & _SQI_DISCARD)]
    return good if good else batches


def _filter_good_batches_green(batches: list[dict]) -> list[dict]:
    """Filter khusus kanal hijau: abaikan MOTION dari IR, hanya buang PPG_BAD/FLAT/NO_FINGER."""
    good = [b for b in batches if not (b.get("sqi_flags", 0) & _SQI_DISCARD_GREEN)]
    return good if good else batches


def _sqi_summary(batches: list[dict]) -> dict:
    if not batches:
        return {}
    lat   = batches[-1]
    flags = lat.get("sqi_flags", 0)
    score = lat.get("sqi", 0)
    names = []
    if flags & 0x01: names.append("NO_FINGER")
    if flags & 0x02: names.append("SATURATED")
    if flags & 0x04: names.append("FLAT")
    if flags & 0x08: names.append("MOTION")
    if flags & 0x10: names.append("PPG_BAD")
    if flags & 0x20: names.append("SHORT")
    n_total   = len(batches)
    n_flagged = sum(1 for b in batches if b.get("sqi_flags", 0) & _SQI_DISCARD)
    return {
        "score":             score,
        "flags":             flags,
        "flag_names":        names,
        "ir_dc":             lat.get("ir_dc", 0),
        "ir_pi":             lat.get("ir_pi", 0),
        "ir_tort10":         lat.get("ir_tort10", 0),
        "n_total":           n_total,
        "n_flagged":         n_flagged,
        "pct_good":          round(100 * (n_total - n_flagged) / n_total) if n_total else 0,
        "analysis_filtered": n_flagged > 0,
    }


# ---------------------------------------------------------------------------
# /dashboard — web dashboard untuk monitoring hardware
# ---------------------------------------------------------------------------

_DASHBOARD_HTML = os.path.join(os.path.dirname(__file__), "static", "dashboard.html")
_HOME_HTML = os.path.join(os.path.dirname(__file__), "static", "index.html")


@app.get("/dashboard", include_in_schema=False)
def serve_dashboard() -> FileResponse:
    return FileResponse(_DASHBOARD_HTML, media_type="text/html")


@app.get("/v1/devices")
def list_devices() -> list[str]:
    """Daftar device yang sudah mengirim data sejak server terakhir dijalankan."""
    return ingest_buffer.list_devices()


@app.get("/v1/devices/{device_id}/check")
def check_device_exists(device_id: str, db: Session = Depends(get_db)) -> dict:
    """Cek apakah perangkat dengan device_id ini pernah mengirim data ke server.

    Dua sumber diperiksa:
    - Buffer in-memory: device mengirim data sejak server terakhir start.
    - Tabel users: device sudah pernah di-pair (data historis di DB).

    Mobile app memanggil ini sebelum /device/pair untuk memastikan device nyata.
    """
    in_buffer = device_id in ingest_buffer.list_devices()
    if in_buffer:
        return {"found": True}

    in_db = (
        db.query(models_db.User)
        .filter(models_db.User.device_key == device_id)
        .first()
    ) is not None
    return {"found": in_db}


@app.get("/v1/ingest/latest")
def ingest_latest_dashboard(
    device_id: str,
    window_s: float = Query(10.0, ge=1.0, le=60.0, description="Jendela waktu sinyal (detik, 1–60)"),
    db: Session = Depends(get_db),
) -> dict:
    """Kembalikan data terbaru dari device dalam 4 tahap pemrosesan:
    raw → PWA → MLP → XGBoost. Dipakai oleh /dashboard."""
    batches = ingest_buffer.get_window_s(device_id, window_s)
    if not batches:
        # Kembalikan 200 (bukan 404) agar log tidak penuh "error" untuk kondisi normal
        # (device belum kirim data / buffer habis masa).  Dashboard cek has_data: false.
        return {"has_data": False, "device_id": device_id}

    latest  = batches[-1]
    fs_ppg  = int(latest.get("fs_ppg", 200))
    fs_max  = int(latest.get("fs_max", 400))

    # Filter batch berkualitas buruk sebelum analisis
    good_batches = _filter_good_batches(batches)
    # Green pakai filter tersendiri: MOTION dari IR tidak mem-blokir kanal hijau
    good_green_batches = _filter_good_batches_green(batches)
    all_ppg = [float(v) for b in good_green_batches for v in b.get("ppg", [])]
    all_red = [float(v) for b in good_batches for v in b.get("red", [])]
    all_ir  = [float(v) for b in good_batches for v in b.get("ir", [])]

    # --- Stage 1: Raw (tampilkan single batch terbaru) ---
    ppg_raw = [float(v) for v in latest.get("ppg", [])]
    red_raw = [float(v) for v in latest.get("red", [])]
    ir_raw  = [float(v) for v in latest.get("ir", [])]
    stage_raw = {
        "ppg": ppg_raw, "red": red_raw, "ir": ir_raw,
        "fs_ppg": fs_ppg, "fs_max": fs_max,
        "n_ppg": len(ppg_raw), "n_max": len(red_raw),
        "t_unix_ms": latest.get("t_unix_ms", 0),
        "ovf": latest.get("ovf", 0),
    }

    # --- Stage 2: PWA (gunakan window penuh untuk akurasi BPM) ---
    stage_pwa = _compute_pwa(all_ppg, all_red, all_ir, fs_ppg, fs_max)

    # --- Stage 3: MLP ---
    stage_mlp = _compute_mlp(all_ppg, all_red, all_ir, fs_ppg)

    # --- Stage 4: XGBoost (ambil dari DB) ---
    stage_xgb = _compute_xgboost(device_id, db)

    # --- BPM Engine: port algoritma firmware (peak detection + median IBI) ---
    stage_bpm = _compute_bpm_engine(all_ppg, fs_ppg)

    # --- Analisis plotter: buang baseline + BPM autokorelasi (ketiga kanal) ---
    stage_analysis = _compute_ppg_analysis(all_ppg, all_red, all_ir, fs_ppg, fs_max)

    return {
        "device_id": device_id,
        "seq": latest.get("seq", 0),
        "received_at": latest.get("_received_at", ""),
        "batt_pct": latest.get("batt_pct", 0),
        "batt_mv": latest.get("batt_mv", 0),
        "sqi": _sqi_summary(batches),
        "raw": stage_raw,
        "pwa": stage_pwa,
        "mlp": stage_mlp,
        "xgboost": stage_xgb,
        "bpm_engine": stage_bpm,
        "analysis": stage_analysis,
    }


def _compute_pwa(ppg: list, red: list, ir: list, fs_ppg: int, fs_max: int) -> dict:
    from model.ppg_features import bandpass_filter, bpm_from_spectrum, extract_pwa_features

    cfg = get_pwa_config()

    result: dict = {
        "filtered_ppg": [], "peaks_ppg": [],
        "filtered_red": [], "peaks_red": [],
        "features": {}, "bpm": None, "note": None,
        "fs_ppg": fs_ppg, "fs_max": fs_max,
    }
    min_samples = int(fs_ppg * 2)  # 2 detik minimum

    def _process(signal: list, fs: int, key: str, invert: bool = False) -> None:
        if len(signal) < min_samples:
            return
        arr = np.array(signal, dtype=float)
        filt = bandpass_filter(
            arr, float(fs),
            low_hz=cfg["bandpass_low_hz"],
            high_hz=cfg["bandpass_high_hz"],
            order=int(cfg["filter_order"]),
        )
        result[f"filtered_{key}"] = [float(v) for v in filt]
        # For peak markers on the dashboard: detect on potentially inverted signal
        sig_for_peaks = -filt if invert else filt
        import numpy as _np
        from scipy.signal import find_peaks as _fp
        _min_dist = max(int(float(fs) * 60 / cfg["bpm_max"]), 1)
        _prom = float(_np.std(sig_for_peaks) * cfg["prominence_multiplier"])
        _pk, _ = _fp(sig_for_peaks, distance=_min_dist, prominence=_prom)
        result[f"peaks_{key}"] = [int(p) for p in _pk]
        # BPM via Welch spectrum (primary method — matches firmware scripts)
        if key == "ppg" and result["bpm"] is None:
            bpm = bpm_from_spectrum(filt, float(fs))
            if bpm is not None:
                result["bpm"] = round(bpm, 1)
        # Use RED/IR Welch BPM as fallback if green PPG unavailable
        if key in ("red", "ir") and result["bpm"] is None:
            bpm = bpm_from_spectrum(filt, float(fs))
            if bpm is not None:
                result["bpm"] = round(bpm, 1)

    if ppg: _process(ppg, fs_ppg, "ppg", invert=False)
    if red: _process(red, fs_max, "red", invert=True)
    if ir:  _process(ir,  fs_max, "ir",  invert=True)

    if len(ppg) < min_samples and len(red) < min_samples:
        result["note"] = (
            f"Window sinyal terlalu pendek ({len(ppg)}/{min_samples} sampel PPG). "
            "Tunggu beberapa detik — backend mengakumulasi data otomatis."
        )
    else:
        try:
            raw_feats = extract_pwa_features(
                fs=float(fs_ppg),
                green=ppg or None,
                red=red or None,
                infrared=ir or None,
            )
            # Konversi semua nilai ke Python native (numpy scalar tidak bisa di-serialize)
            result["features"] = {k: float(v) if isinstance(v, (int, float)) else v
                                  for k, v in raw_feats.items()}
        except Exception as exc:
            result["note"] = f"Ekstraksi fitur gagal: {exc}"

    return result


def _compute_ppg_analysis(
    ppg: list, red: list, ir: list, fs_ppg: int, fs_max: int
) -> dict:
    """Analisis tiga kanal: buang baseline + BPM autokorelasi + statistik.

    Menggabungkan analyze_channel() dan channel_stats() dari ppg_analysis.py,
    identik dengan algoritma di gui/plotter.py (ac_signal, bpm_autocorr,
    _tick_stats).  Setiap kanal mengembalikan:
      ac, bpm, conf, peaks        (dari analyze_channel)
      dc, ac_p2p, pi_permil, ref_pi_permil  (dari channel_stats)
    """
    try:
        from api.ppg_analysis import (
            analyze_channel, channel_stats, compute_linreg_vitals,
        )

        def _proc(sig: list, fs: float, ch: str) -> dict:
            if not sig:
                return _empty_ac()
            return {
                **analyze_channel(sig, fs),
                **channel_stats(sig, fs, ch),
            }

        fs_m = float(fs_max or 200)
        result = {
            "green":  _proc(ppg, float(fs_ppg or 200), "green"),
            "red":    _proc(red, fs_m, "red"),
            "ir":     _proc(ir,  fs_m, "ir"),
            "linreg": compute_linreg_vitals(ir, fs_m),
        }
        return result
    except Exception as exc:
        return {
            "green":  _empty_ac(str(exc)),
            "red":    _empty_ac(),
            "ir":     _empty_ac(),
            "linreg": {"available": False},
        }


def _empty_ac(note: str | None = None) -> dict:
    d: dict = {
        "ac": [], "bpm": None, "conf": 0.0, "peaks": [],
        "dc": None, "ac_p2p": None, "pi_permil": None, "ref_pi_permil": None,
    }
    if note:
        d["note"] = note
    return d


def _compute_bpm_engine(ppg: list, fs: int) -> dict:
    """Port algoritma bpm.cpp: peak detection + median IBI → BPM + HRV kasar."""
    if not ppg:
        return {"bpm": None, "conf": 0, "status": "TIDAK_ADA_DATA",
                "ibi_list": [], "ibi_med_ms": None, "sdnn_ms": None,
                "beats": 0, "rejects": 0, "peaks": [], "filtered": []}
    try:
        from api.bpm_engine import compute_bpm
        return compute_bpm(ppg, float(fs or 200))
    except Exception as exc:
        return {"bpm": None, "conf": 0, "status": f"ERROR: {exc}",
                "ibi_list": [], "ibi_med_ms": None, "sdnn_ms": None,
                "beats": 0, "rejects": 0, "peaks": [], "filtered": []}


def _compute_mlp(ppg: list, red: list, ir: list, fs_ppg: int) -> dict:
    from api.ml_vitals import is_model_available, predict_vitals_from_ppg
    from api.ml_calibration import (
        compute_risk_flags_from_vitals,
        is_calibration_model_available,
        predict_vitals,
    )
    from api.ppg_analysis import bpm_autocorr, channel_stats

    out: dict = {"available": False}

    # --- Old PPG-vitals model (systolic, diastolic, glucose) ---
    if is_model_available():
        try:
            result = predict_vitals_from_ppg(
                fs_hz=float(fs_ppg),
                age_years=60.0,
                green=ppg or None,
                red=red or None,
                infrared=ir or None,
            )
            out = {"available": True, **result}
        except Exception as exc:
            out = {"available": False, "message": str(exc)}
    else:
        out["message"] = "Model MLP belum dilatih — menunggu data kalibrasi dari hardware"

    # --- Calibration MLP (gula, kolesterol, asam_urat, sistolik, diastolik) ---
    if is_calibration_model_available() and ir and red:
        try:
            fs_m = float(fs_ppg)
            ir_stats  = channel_stats(ir,  fs_m, "ir")
            red_stats = channel_stats(red, fs_m, "red")
            bpm_val, _ = bpm_autocorr(ir, fs_m)
            calib_vitals = predict_vitals(
                ir_dc_mean  = ir_stats.get("dc") or 0.0,
                ir_ac_p2p   = ir_stats.get("ac_p2p") or 0.0,
                red_dc_mean = red_stats.get("dc") or 0.0,
                red_ac_p2p  = red_stats.get("ac_p2p") or 0.0,
                bpm         = bpm_val or 60.0,
            )
            out["calib_vitals"] = calib_vitals
            out["risk_flags"]   = compute_risk_flags_from_vitals(calib_vitals)
            out["available"]    = True
        except Exception:
            out.setdefault("risk_flags", [])
    else:
        out.setdefault("risk_flags", [])

    return out


def _compute_xgboost(device_id: str, db: Session) -> dict:
    user = (
        db.query(models_db.User)
        .filter(models_db.User.device_key == device_id)
        .first()
    )
    if not user:
        return {"available": False, "message": "Perangkat belum di-pair ke akun — pair dulu via mobile app"}

    log = (
        db.query(models_db.PredictionLog)
        .filter(models_db.PredictionLog.user_id == user.id)
        .filter(models_db.PredictionLog.endpoint == "stroke_risk")
        .order_by(desc(models_db.PredictionLog.created_at))
        .first()
    )
    if not log:
        return {"available": False, "message": "Belum ada prediksi risiko stroke — tunggu batch berikutnya"}

    resp = json.loads(log.response_payload)

    # Ambil risk_flags profil jika device sudah di-pair
    profile_flags: list = []
    if user:
        from api.profile_utils import compute_risk_flags, resolve_active_profile
        active = resolve_active_profile(db, user.id)
        if active:
            profile_flags = compute_risk_flags(active)

    stored_flags: list = resp.get("risk_flags", [])
    # Gabungkan: flags dari log (sudah tersimpan) + flags profil terbaru
    all_flags = list(dict.fromkeys(stored_flags + profile_flags))  # deduplicate, preserve order

    return {
        "available": True,
        "probability": resp.get("probability"),
        "risk_level": resp.get("risk_level"),
        "threshold": resp.get("threshold"),
        "model_name": resp.get("model_name"),
        "predicted_at": log.created_at.isoformat(),
        "risk_flags": all_flags,
    }


# ---------------------------------------------------------------------------
# /v1/calibrate — rekam sesi kalibrasi (sinyal PPG + nilai invasif)
# ---------------------------------------------------------------------------

@app.post("/v1/calibrate", status_code=201)
def calibrate_create(
    device_id: str,
    subject_id: str,
    age_years: float,
    gender: str,
    kondisi: str | None = None,
    gula_darah_mg_dl: float | None = None,
    kolesterol_mg_dl: float | None = None,
    asam_urat_mg_dl: float | None = None,
    sistolik_mmhg: float | None = None,
    diastolik_mmhg: float | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Rekam satu sesi kalibrasi.

    Sinyal PPG diambil otomatis dari buffer (window 10 detik terakhir) berdasarkan
    device_id.  Nilai invasif (ground truth) dimasukkan manual oleh peneliti.
    """
    batches = ingest_buffer.get_window_s(device_id, 10.0)
    if not batches:
        raise HTTPException(status_code=404, detail=f"Belum ada sinyal dari '{device_id}' — pastikan firmware sedang berjalan")

    latest = batches[-1]
    fs_max = float(latest.get("fs_max", 200))

    all_green = [float(v) for b in batches for v in b.get("ppg", [])]
    all_red   = [float(v) for b in batches for v in b.get("red", [])]
    all_ir    = [float(v) for b in batches for v in b.get("ir", [])]

    # Ekstrak fitur sinyal
    from api.ppg_analysis import channel_stats, bpm_autocorr
    ir_st  = channel_stats(all_ir,  fs_max, "ir")
    red_st = channel_stats(all_red, fs_max, "red")
    bpm_val, _ = bpm_autocorr(np.array(all_ir, dtype=float), fs_max) if all_ir else (None, 0.0)

    def _join(arr: list) -> str:
        return ";".join(str(round(v)) for v in arr)

    rec = models_db.CalibrationRecord(
        device_id    = device_id,
        subject_id   = subject_id.strip(),
        age_years    = age_years,
        gender       = gender.strip().upper(),
        kondisi      = (kondisi or "").strip() or None,
        fs_hz        = fs_max,
        green_raw    = _join(all_green) if all_green else None,
        red_raw      = _join(all_red)   if all_red   else None,
        infrared_raw = _join(all_ir)    if all_ir    else None,
        ir_dc_mean   = ir_st.get("dc"),
        ir_ac_p2p    = ir_st.get("ac_p2p"),
        red_dc_mean  = red_st.get("dc"),
        red_ac_p2p   = red_st.get("ac_p2p"),
        bpm          = bpm_val,
        gula_darah_mg_dl = gula_darah_mg_dl,
        kolesterol_mg_dl  = kolesterol_mg_dl,
        asam_urat_mg_dl   = asam_urat_mg_dl,
        sistolik_mmhg     = sistolik_mmhg,
        diastolik_mmhg    = diastolik_mmhg,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return _calib_to_dict(rec)


@app.get("/v1/calibrate")
def calibrate_list(
    device_id: str | None = None,
    limit: int = Query(200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Daftar rekaman kalibrasi, terbaru duluan."""
    q = db.query(models_db.CalibrationRecord).order_by(
        desc(models_db.CalibrationRecord.created_at)
    )
    if device_id:
        q = q.filter(models_db.CalibrationRecord.device_id == device_id)
    return [_calib_to_dict(r) for r in q.limit(limit).all()]


@app.patch("/v1/calibrate/{record_id}")
def calibrate_update(
    record_id: int,
    subject_id: str | None = None,
    age_years: float | None = None,
    gender: str | None = None,
    kondisi: str | None = None,
    gula_darah_mg_dl: float | None = None,
    kolesterol_mg_dl: float | None = None,
    asam_urat_mg_dl: float | None = None,
    sistolik_mmhg: float | None = None,
    diastolik_mmhg: float | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Perbarui nilai ground truth atau metadata satu rekaman kalibrasi."""
    rec = db.get(models_db.CalibrationRecord, record_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Record tidak ditemukan")
    if subject_id        is not None: rec.subject_id        = subject_id.strip()
    if age_years         is not None: rec.age_years         = age_years
    if gender            is not None: rec.gender            = gender.strip().upper()
    if kondisi           is not None: rec.kondisi           = kondisi.strip() or None
    if gula_darah_mg_dl  is not None: rec.gula_darah_mg_dl  = gula_darah_mg_dl
    if kolesterol_mg_dl  is not None: rec.kolesterol_mg_dl  = kolesterol_mg_dl
    if asam_urat_mg_dl   is not None: rec.asam_urat_mg_dl   = asam_urat_mg_dl
    if sistolik_mmhg     is not None: rec.sistolik_mmhg     = sistolik_mmhg
    if diastolik_mmhg    is not None: rec.diastolik_mmhg    = diastolik_mmhg
    db.commit()
    db.refresh(rec)
    return _calib_to_dict(rec)


@app.delete("/v1/calibrate/{record_id}", status_code=204)
def calibrate_delete(record_id: int, db: Session = Depends(get_db)) -> None:
    rec = db.get(models_db.CalibrationRecord, record_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Record tidak ditemukan")
    db.delete(rec)
    db.commit()


@app.get("/v1/calibrate/training-report")
def calibrate_training_report() -> dict:
    """Baca hasil pelatihan MLP terakhir dari artifacts (jika sudah dilatih)."""
    import pathlib
    metrics_path = pathlib.Path(__file__).resolve().parent.parent / "model" / "artifacts" / "mlp_calibration_metrics.json"
    if not metrics_path.exists():
        return {"available": False, "message": "Model belum dilatih — jalankan: python model/train_mlp_calibration.py"}
    import json as _json
    data = _json.loads(metrics_path.read_text())
    return {"available": True, "metrics": data}


@app.get("/v1/calibrate/export.csv")
def calibrate_export(
    device_id: str | None = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Export dataset kalibrasi sebagai CSV (kompatibel model/train_mlp_calibration.py)."""
    import csv, io
    q = db.query(models_db.CalibrationRecord).order_by(
        models_db.CalibrationRecord.created_at
    )
    if device_id:
        q = q.filter(models_db.CalibrationRecord.device_id == device_id)
    rows = q.all()

    buf = io.StringIO()
    headers = [
        "id", "device_id", "subject_id", "session_ts", "age_years", "gender", "kondisi",
        "fs_hz", "green_raw", "red_raw", "infrared_raw",
        "ir_dc_mean", "ir_ac_p2p", "red_dc_mean", "red_ac_p2p", "bpm",
        "gula_darah_mg_dl", "kolesterol_mg_dl", "asam_urat_mg_dl",
        "sistolik_mmhg", "diastolik_mmhg",
        # Alias kompatibel train_ppg_vitals.py
        "blood_glucose_mg_dl", "systolic_bp_mmhg", "diastolic_bp_mmhg",
    ]
    w = csv.DictWriter(buf, fieldnames=headers, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({
            "id": r.id,
            "device_id": r.device_id,
            "subject_id": r.subject_id,
            "session_ts": r.created_at.isoformat(),
            "age_years": r.age_years,
            "gender": r.gender,
            "kondisi": r.kondisi or "",
            "fs_hz": r.fs_hz,
            "green_raw": r.green_raw or "",
            "red_raw": r.red_raw or "",
            "infrared_raw": r.infrared_raw or "",
            "ir_dc_mean": r.ir_dc_mean or "",
            "ir_ac_p2p": r.ir_ac_p2p or "",
            "red_dc_mean": r.red_dc_mean or "",
            "red_ac_p2p": r.red_ac_p2p or "",
            "bpm": r.bpm or "",
            "gula_darah_mg_dl": r.gula_darah_mg_dl or "",
            "kolesterol_mg_dl": r.kolesterol_mg_dl or "",
            "asam_urat_mg_dl": r.asam_urat_mg_dl or "",
            "sistolik_mmhg": r.sistolik_mmhg or "",
            "diastolik_mmhg": r.diastolik_mmhg or "",
            # Alias
            "blood_glucose_mg_dl": r.gula_darah_mg_dl or "",
            "systolic_bp_mmhg": r.sistolik_mmhg or "",
            "diastolic_bp_mmhg": r.diastolik_mmhg or "",
        })

    buf.seek(0)
    filename = f"kalibrasi_{device_id or 'semua'}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.get("/v1/calibrate/summary")
def calibrate_summary(
    device_id: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Statistik ringkas dataset kalibrasi."""
    q = db.query(models_db.CalibrationRecord)
    if device_id:
        q = q.filter(models_db.CalibrationRecord.device_id == device_id)
    rows = q.all()
    n = len(rows)
    if n == 0:
        return {"total": 0}

    def _stats(vals):
        v = [x for x in vals if x is not None]
        if not v:
            return {"n": 0}
        arr = np.array(v)
        return {"n": len(v), "min": round(float(arr.min()), 1),
                "max": round(float(arr.max()), 1), "mean": round(float(arr.mean()), 1)}

    return {
        "total": n,
        "subjects": len({r.subject_id for r in rows}),
        "devices": list({r.device_id for r in rows}),
        "age":         _stats([r.age_years         for r in rows]),
        "gula_darah":  _stats([r.gula_darah_mg_dl  for r in rows]),
        "kolesterol":  _stats([r.kolesterol_mg_dl   for r in rows]),
        "asam_urat":   _stats([r.asam_urat_mg_dl    for r in rows]),
        "sistolik":    _stats([r.sistolik_mmhg       for r in rows]),
        "diastolik":   _stats([r.diastolik_mmhg      for r in rows]),
        "bpm":         _stats([r.bpm                for r in rows]),
    }


def _calib_to_dict(r: models_db.CalibrationRecord) -> dict:
    return {
        "id": r.id, "device_id": r.device_id,
        "subject_id": r.subject_id, "age_years": r.age_years,
        "gender": r.gender, "kondisi": r.kondisi,
        "session_ts": r.created_at.isoformat(),
        "ir_dc_mean": r.ir_dc_mean, "ir_ac_p2p": r.ir_ac_p2p,
        "red_dc_mean": r.red_dc_mean, "bpm": r.bpm,
        "gula_darah_mg_dl": r.gula_darah_mg_dl,
        "kolesterol_mg_dl":  r.kolesterol_mg_dl,
        "asam_urat_mg_dl":   r.asam_urat_mg_dl,
        "sistolik_mmhg":     r.sistolik_mmhg,
        "diastolik_mmhg":    r.diastolik_mmhg,
    }


# ---------------------------------------------------------------------------
# /v1/calibrate/generate-demo  — data sintetis realistis untuk uji pipeline
# ---------------------------------------------------------------------------

@app.post("/v1/calibrate/generate-demo")
def calibrate_generate_demo(
    n_rows: int = Query(250, ge=50, le=1000),
    db: Session = Depends(get_db),
) -> dict:
    """Generate data kalibrasi sintetis (multi-subjek, korelasi fisiologis realistis)
    dan masukkan ke calibration_records dengan device_id='demo-device'."""

    rng = np.random.default_rng(seed=int(time.time()) % (2**31))

    SUBJECTS = [
        {"id": f"S{i:03d}", "age": int(rng.integers(45, 82)),
         "gender": "L" if i <= 13 else "P",
         "dc_base": float(np.clip(rng.normal(145_000, 28_000), 80_000, 210_000))}
        for i in range(1, 21)
    ]
    KONDISI = ["sewaktu", "puasa", "2j_setelah_makan"]
    rows_each = max(1, n_rows // len(SUBJECTS))
    inserted = 0

    for s in SUBJECTS:
        age   = s["age"]
        gc    = 1.0 if s["gender"] == "L" else 0.0
        dc_b  = s["dc_base"]

        # Subject-level baseline vitals (individual variation)
        sis_b = 100.0 + age * 0.70 + gc * 5.0 + float(rng.normal(0, 8))
        dia_b =  60.0 + age * 0.30 + gc * 3.0 + float(rng.normal(0, 5))
        bpm_b =  80.0 - age * 0.18               + float(rng.normal(0, 5))

        for _ in range(rows_each):
            kondisi = str(rng.choice(KONDISI))

            sis = float(np.clip(rng.normal(sis_b, 10), 90, 180))
            dia = float(np.clip(rng.normal(dia_b,  7), 55, 110))
            if sis <= dia + 20:
                sis = dia + 20.0 + float(rng.uniform(5, 15))
            bpm = float(np.clip(rng.normal(bpm_b,  8), 48, 102))

            if kondisi == "puasa":
                gula = float(np.clip(rng.normal(85 + age * 0.30, 12), 70, 126))
            elif kondisi == "2j_setelah_makan":
                gula = float(np.clip(rng.normal(140 + age * 0.40, 25), 90, 280))
            else:
                gula = float(np.clip(rng.normal(105 + age * 0.35, 20), 70, 200))

            kol  = float(np.clip(rng.normal(160 + age * 0.80, 25) + (0 if gc else float(rng.uniform(0, 15))), 130, 290))
            au   = float(np.clip(rng.normal(6.0 if gc else 4.5, 1.2 if gc else 1.0), 2.0, 9.5))

            # PPG features: IR DC stable per subject; AC p2p driven by pulse pressure
            ir_dc  = float(np.clip(rng.normal(dc_b, dc_b * 0.03), dc_b * 0.85, dc_b * 1.15))
            pp     = sis - dia  # pulse pressure 30-70
            ac_r   = (pp / 40.0) * 0.018 + float(rng.normal(0, 0.003))
            ir_ac  = float(max(ir_dc * 0.005, ir_dc * max(ac_r, 0.003)))
            red_dc = float(np.clip(rng.normal(ir_dc * 0.73, ir_dc * 0.025), ir_dc * 0.60, ir_dc * 0.86))
            red_ac = float(max(ir_ac * 0.3, ir_ac * 0.87 + float(rng.normal(0, ir_ac * 0.05))))

            rec = models_db.CalibrationRecord(
                device_id        = "demo-device",
                subject_id       = s["id"],
                age_years        = float(age),
                gender           = s["gender"],
                kondisi          = kondisi,
                fs_hz            = 200.0,
                ir_dc_mean       = round(ir_dc, 1),
                ir_ac_p2p        = round(ir_ac, 1),
                red_dc_mean      = round(red_dc, 1),
                red_ac_p2p       = round(red_ac, 1),
                bpm              = round(bpm, 1),
                gula_darah_mg_dl = round(gula, 1),
                kolesterol_mg_dl  = round(kol,  1),
                asam_urat_mg_dl   = round(au,   2),
                sistolik_mmhg     = round(sis,  1),
                diastolik_mmhg    = round(dia,  1),
            )
            db.add(rec)
            inserted += 1

    db.commit()
    total = db.query(models_db.CalibrationRecord).count()
    return {"inserted": inserted, "total": total,
            "message": f"✓ {inserted} rekaman demo berhasil ditambahkan"}


@app.post("/v1/calibrate/clear-demo")
def calibrate_clear_demo(db: Session = Depends(get_db)) -> dict:
    """Hapus semua rekaman dengan device_id='demo-device'."""
    deleted = db.query(models_db.CalibrationRecord).filter(
        models_db.CalibrationRecord.device_id == "demo-device"
    ).delete(synchronize_session=False)
    db.commit()
    total = db.query(models_db.CalibrationRecord).count()
    return {"deleted": deleted, "total": total}


# ---------------------------------------------------------------------------
# /v1/calibrate/train  — latih MLP inline dari data di DB
# ---------------------------------------------------------------------------

@app.post("/v1/calibrate/train")
def calibrate_train(
    mode: str = Query("all", description="all | real | demo"),
    db: Session = Depends(get_db),
) -> dict:
    """Latih model MLP kalibrasi dari calibration_records di DB, simpan artifact.

    mode='real'  — hanya rekaman nyata (bukan demo-device)
    mode='demo'  — hanya rekaman demo (device_id = demo-device)
    mode='all'   — semua rekaman (default)
    """
    import pathlib as _pl, json as _json
    import joblib
    import pandas as pd
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import LeaveOneOut, cross_val_predict
    from sklearn.neural_network import MLPRegressor
    from sklearn.preprocessing import StandardScaler

    q = db.query(models_db.CalibrationRecord)
    if mode == "real":
        q = q.filter(models_db.CalibrationRecord.device_id != "demo-device")
    elif mode == "demo":
        q = q.filter(models_db.CalibrationRecord.device_id == "demo-device")
    rows = q.all()
    if not rows:
        label = {"real": "data asli", "demo": "demo data"}.get(mode, "kalibrasi")
        raise HTTPException(status_code=400, detail=f"Belum ada {label} di database")

    FEATURES_T = ["ir_dc_mean", "ir_ac_p2p", "red_dc_mean", "red_ac_p2p",
                  "bpm", "age_years", "gender_code"]
    TARGETS_T = {
        "gula_darah_mg_dl": "Gula Darah (mg/dL)",
        "kolesterol_mg_dl":  "Kolesterol (mg/dL)",
        "asam_urat_mg_dl":   "Asam Urat (mg/dL)",
        "sistolik_mmhg":     "Sistolik (mmHg)",
        "diastolik_mmhg":    "Diastolik (mmHg)",
    }
    MIN_ROWS_T = 10

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
    df = pd.DataFrame(records)
    df["gender_code"] = (df["gender"].str.upper() == "L").astype(float)
    for col in FEATURES_T:
        if col not in df.columns:
            df[col] = float("nan")
    df[FEATURES_T] = df[FEATURES_T].apply(pd.to_numeric, errors="coerce")

    if len(df) < MIN_ROWS_T:
        raise HTTPException(status_code=400,
                            detail=f"Data terlalu sedikit ({len(df)}/{MIN_ROWS_T} minimum)")

    n_subjects = df["subject_id"].nunique() if "subject_id" in df.columns else "?"
    trained_at = datetime.now(timezone.utc).isoformat()

    all_metrics: dict = {}
    all_models:  dict = {}

    for target_col, target_label in TARGETS_T.items():
        sub = df[df[target_col].notna()].copy()
        sub = sub[sub[FEATURES_T].notna().all(axis=1)]
        if len(sub) < MIN_ROWS_T:
            continue

        X = sub[FEATURES_T].values.astype(float)
        y = sub[target_col].values.astype(float)
        n = len(y)

        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)

        # lbfgs untuk dataset kecil (<30), adam+early_stopping untuk yang lebih besar
        if n < 30:
            _mlp_kwargs = dict(hidden_layer_sizes=(64, 32), activation="relu",
                               solver="lbfgs", alpha=0.01, max_iter=3000, random_state=42)
        else:
            _mlp_kwargs = dict(hidden_layer_sizes=(64, 32), activation="relu",
                               solver="adam", alpha=0.01, max_iter=500, random_state=42,
                               learning_rate_init=0.01, early_stopping=True,
                               n_iter_no_change=15, validation_fraction=0.1)

        cv_scheme = LeaveOneOut() if n < 30 else 5

        import warnings as _w
        with _w.catch_warnings():
            _w.simplefilter("ignore")
            y_cv = cross_val_predict(MLPRegressor(**_mlp_kwargs), Xs, y, cv=cv_scheme)
            mlp = MLPRegressor(**_mlp_kwargs)
            mlp.fit(Xs, y)

        mae  = float(mean_absolute_error(y, y_cv))
        rmse = float(np.sqrt(np.mean((y - y_cv) ** 2)))
        r2   = float(r2_score(y, y_cv))
        pct_err = float(np.mean(np.abs(y - y_cv) / np.maximum(np.abs(y), 1e-9)) * 100)
        acc  = round(100 - pct_err, 2)

        all_models[target_col] = {"scaler": scaler, "mlp": mlp, "features": FEATURES_T}
        all_metrics[target_col] = {
            "label": target_label, "n": n,
            "cv": "LOO" if n < 30 else "5-fold",
            "mae": round(mae, 2), "rmse": round(rmse, 2),
            "r2": round(r2, 4),
            "mean_pct_error": round(pct_err, 2),
            "accuracy_pct": acc,
            # Simpan prediksi CV agar laporan bisa plot scatter tanpa re-train
            "cv_y_true": [round(float(v), 2) for v in y],
            "cv_y_pred": [round(float(v), 2) for v in y_cv],
        }

    if not all_models:
        raise HTTPException(status_code=400,
                            detail="Tidak ada target yang cukup datanya untuk dilatih")

    artifact_dir = _pl.Path(__file__).resolve().parent.parent / "model" / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "mlp_calibration.joblib"
    metrics_path  = artifact_dir / "mlp_calibration_metrics.json"

    meta = {
        "_meta": {
            "trained_at": trained_at,
            "n_total": len(df),
            "n_subjects": n_subjects,
            "mode": mode,
        }
    }
    metrics_with_meta = {**meta, **all_metrics}
    joblib.dump(all_models, artifact_path)
    metrics_path.write_text(_json.dumps(metrics_with_meta, indent=2, ensure_ascii=False))

    # Invalidate lru_cache di ml_calibration.py agar prediksi berikutnya pakai model baru
    try:
        from api.ml_calibration import _load_artifact
        _load_artifact.cache_clear()
    except Exception:
        pass

    return {"success": True, "metrics": all_metrics,
            "models_trained": list(all_models.keys()),
            "n_total": len(df), "n_subjects": n_subjects, "mode": mode}


# ---------------------------------------------------------------------------
# /v1/calibrate/report.html  — laporan lengkap, dapat diunduh
# ---------------------------------------------------------------------------

@app.get("/v1/calibrate/report.html")
def calibrate_report_html() -> StreamingResponse:
    """Hasilkan laporan HTML lengkap (scatter plots, metrik, interpretasi) — siap diunduh."""
    import pathlib as _pl, json as _json, base64, io

    metrics_path = _pl.Path(__file__).resolve().parent.parent / "model" / "artifacts" / "mlp_calibration_metrics.json"
    if not metrics_path.exists():
        raise HTTPException(status_code=404,
                            detail="Model belum dilatih — klik 'Jalankan Training' dulu")

    full = _json.loads(metrics_path.read_text())
    meta = full.get("_meta", {})
    targets_data = {k: v for k, v in full.items() if k != "_meta"}

    LABELS = {
        "gula_darah_mg_dl": "Gula Darah",
        "kolesterol_mg_dl":  "Kolesterol",
        "asam_urat_mg_dl":   "Asam Urat",
        "sistolik_mmhg":     "Sistolik",
        "diastolik_mmhg":    "Diastolik",
    }
    UNITS = {
        "gula_darah_mg_dl": "mg/dL",
        "kolesterol_mg_dl":  "mg/dL",
        "asam_urat_mg_dl":   "mg/dL",
        "sistolik_mmhg":     "mmHg",
        "diastolik_mmhg":    "mmHg",
    }
    # Nilai MAE referensi klinis yang dianggap "baik"
    MAE_OK = {
        "gula_darah_mg_dl": 15.0,
        "kolesterol_mg_dl":  20.0,
        "asam_urat_mg_dl":   0.8,
        "sistolik_mmhg":     12.0,
        "diastolik_mmhg":    8.0,
    }

    def _acc_label(acc: float) -> tuple[str, str]:
        if acc >= 90:  return ("Sangat Baik", "#16a34a")
        if acc >= 80:  return ("Baik",        "#0ea5e9")
        if acc >= 70:  return ("Cukup",        "#d97706")
        return ("Perlu Data Lebih",            "#dc2626")

    def _r2_label(r2: float) -> str:
        if r2 >= 0.8:  return "Sangat kuat"
        if r2 >= 0.5:  return "Kuat"
        if r2 >= 0.0:  return "Sedang (lebih baik dari rata-rata)"
        return "Di bawah rata-rata — perlu data lebih banyak"

    # ── Scatter plots as base64 PNG ───────────────────────────────────────
    def _scatter_b64(key: str, data: dict) -> str | None:
        y_true = data.get("cv_y_true")
        y_pred = data.get("cv_y_pred")
        if not y_true or not y_pred:
            return None
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            yt = np.array(y_true); yp = np.array(y_pred)
            fig, ax = plt.subplots(figsize=(4.2, 4.2))
            ax.scatter(yt, yp, color="#3987e5", alpha=0.65, s=30, zorder=3)
            lo = min(yt.min(), yp.min()) * 0.93
            hi = max(yt.max(), yp.max()) * 1.07
            ax.plot([lo, hi], [lo, hi], "k--", lw=1, alpha=0.45)
            acc, mae, r2v = data["accuracy_pct"], data["mae"], data["r2"]
            lbl = LABELS.get(key, key)
            unit = UNITS.get(key, "")
            ax.set_xlabel(f"Referensi Invasif ({unit})", fontsize=9)
            ax.set_ylabel(f"Prediksi Sensor ({unit})", fontsize=9)
            ax.set_title(f"{lbl}\nAkurasi {acc}%  |  MAE {mae}  |  R² {r2v}", fontsize=8.5)
            ax.grid(True, alpha=0.25)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=130)
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode()
        except Exception:
            return None

    # ── Build rows & plots ────────────────────────────────────────────────
    table_rows = ""
    scatter_html = ""
    for key in ["gula_darah_mg_dl", "kolesterol_mg_dl", "asam_urat_mg_dl", "sistolik_mmhg", "diastolik_mmhg"]:
        if key not in targets_data:
            continue
        d = targets_data[key]
        lbl = LABELS.get(key, key)
        unit = UNITS.get(key, "")
        acc_text, acc_color = _acc_label(d["accuracy_pct"])
        r2_text = _r2_label(d["r2"])
        mae_ok = d["mae"] <= MAE_OK.get(key, 999)
        mae_color = "#16a34a" if mae_ok else "#d97706"

        table_rows += f"""
        <tr>
          <td><b>{lbl}</b><br><span style="color:#888;font-size:11px">{d['label']}</span></td>
          <td style="text-align:center"><b>{d['n']}</b></td>
          <td style="text-align:center">{d['cv']}</td>
          <td style="text-align:center;font-weight:700;color:{acc_color}">{d['accuracy_pct']}%<br>
            <span style="font-size:10px;font-weight:400">{acc_text}</span></td>
          <td style="text-align:center;color:{mae_color};font-weight:600">{d['mae']} {unit}</td>
          <td style="text-align:center">{d['rmse']} {unit}</td>
          <td style="text-align:center">{d['r2']}<br>
            <span style="font-size:10px;color:#888">{r2_text}</span></td>
          <td style="text-align:center">{d['mean_pct_error']}%</td>
        </tr>"""

        b64 = _scatter_b64(key, d)
        if b64:
            scatter_html += f"""
            <div class="scatter-card">
              <div class="scatter-title">{lbl}</div>
              <img src="data:image/png;base64,{b64}" alt="scatter {lbl}" style="width:100%;max-width:320px">
              <div class="scatter-meta">Akurasi <b style="color:{acc_color}">{d['accuracy_pct']}%</b>
                &nbsp;·&nbsp; MAE <b>{d['mae']} {unit}</b>
                &nbsp;·&nbsp; n={d['n']}
              </div>
            </div>"""

    trained_at_str = meta.get("trained_at", "—")
    try:
        from datetime import datetime as _dt
        trained_at_str = _dt.fromisoformat(trained_at_str).strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        pass

    mode_label = {"real": "Data Asli", "demo": "Data Demo", "all": "Semua Data"}.get(
        meta.get("mode", "all"), "Semua Data")

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Laporan Kalibrasi MLP — ANTARAGA</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Segoe UI',Arial,sans-serif; font-size:13px; color:#1a1a2e;
    background:#f8f9fb; padding:32px 24px; }}
  .cover {{ text-align:center; padding:40px 0 32px; border-bottom:2px solid #3987e5; margin-bottom:28px; }}
  .cover h1 {{ font-size:24px; color:#3987e5; font-weight:800; letter-spacing:-.3px; }}
  .cover .subtitle {{ color:#555; margin-top:6px; font-size:13px; }}
  .meta-grid {{ display:flex; gap:20px; flex-wrap:wrap; justify-content:center; margin-top:18px; }}
  .meta-chip {{ background:#e8f0fe; border-radius:20px; padding:5px 16px;
    font-size:12px; font-weight:600; color:#1a56db; }}
  h2 {{ font-size:16px; font-weight:700; color:#1a1a2e; margin:28px 0 12px;
    padding-bottom:6px; border-bottom:1px solid #dde3ed; }}
  h3 {{ font-size:13px; font-weight:700; margin:16px 0 8px; }}
  p {{ line-height:1.65; color:#444; margin-bottom:10px; }}
  table {{ width:100%; border-collapse:collapse; font-size:12px; margin-bottom:16px; }}
  th {{ background:#3987e5; color:#fff; padding:8px 10px; text-align:left; font-weight:600; }}
  td {{ padding:7px 10px; border-bottom:1px solid #e5e9f0; vertical-align:top; }}
  tr:nth-child(even) td {{ background:#f4f7fb; }}
  .scatter-grid {{ display:flex; flex-wrap:wrap; gap:20px; margin:16px 0; }}
  .scatter-card {{ background:#fff; border:1px solid #dde3ed; border-radius:10px;
    padding:14px; flex:1 1 280px; max-width:340px; text-align:center; }}
  .scatter-title {{ font-weight:700; font-size:13px; margin-bottom:8px; }}
  .scatter-meta {{ font-size:11px; color:#555; margin-top:8px; }}
  .legend-box {{ background:#fff; border:1px solid #dde3ed; border-radius:8px;
    padding:14px 18px; margin-bottom:14px; }}
  .legend-row {{ display:flex; gap:8px; align-items:flex-start; margin-bottom:7px; }}
  .badge {{ display:inline-block; padding:2px 10px; border-radius:12px; font-size:11px;
    font-weight:700; color:#fff; white-space:nowrap; }}
  .badge-green {{ background:#16a34a; }}
  .badge-blue  {{ background:#0ea5e9; }}
  .badge-amber {{ background:#d97706; }}
  .badge-red   {{ background:#dc2626; }}
  .footer {{ text-align:center; color:#999; font-size:11px; margin-top:40px;
    padding-top:16px; border-top:1px solid #dde3ed; }}
  @media print {{
    body {{ background:#fff; padding:16px; }}
    .scatter-card {{ break-inside:avoid; }}
  }}
</style>
</head>
<body>

<div class="cover">
  <div style="font-size:11px;font-weight:700;letter-spacing:.12em;color:#3987e5;text-transform:uppercase;margin-bottom:6px">
    ANTARAGA · Stroke Prediction Model</div>
  <h1>Laporan Kalibrasi Model MLP</h1>
  <div class="subtitle">Estimasi Non-Invasif Vital Sign melalui Sensor PPG</div>
  <div class="meta-grid">
    <span class="meta-chip">📅 Dilatih: {trained_at_str}</span>
    <span class="meta-chip">📊 Sumber: {mode_label}</span>
    <span class="meta-chip">👥 {meta.get('n_subjects', '?')} Subjek</span>
    <span class="meta-chip">📋 {meta.get('n_total', '?')} Rekaman Total</span>
  </div>
</div>

<h2>Apa yang Diukur Model Ini?</h2>
<p>Model MLP (Multi-Layer Perceptron) ANTARAGA menggunakan sinyal cahaya sensor PPG di pergelangan tangan untuk
memperkirakan 5 parameter vital secara non-invasif — tanpa tusuk jarum, tanpa alat laboratorium.
Model ini dilatih dari data kalibrasi berpasangan: sinyal sensor vs hasil alat medis standar.</p>
<p>Berikut adalah ringkasan seberapa akurat model saat ini berdasarkan <b>{meta.get('n_total', '?')} rekaman</b>
dari <b>{meta.get('n_subjects', '?')} subjek</b>, divalidasi dengan metode <i>cross-validation</i>.</p>

<h2>Ringkasan Akurasi per Parameter</h2>
<table>
  <thead><tr>
    <th>Parameter</th>
    <th style="text-align:center">Jumlah Data</th>
    <th style="text-align:center">Validasi</th>
    <th style="text-align:center">Akurasi (%)</th>
    <th style="text-align:center">MAE</th>
    <th style="text-align:center">RMSE</th>
    <th style="text-align:center">R² (Korelasi)</th>
    <th style="text-align:center">Rata-rata Error</th>
  </tr></thead>
  <tbody>{table_rows}</tbody>
</table>

<h2>Visualisasi Prediksi vs Referensi</h2>
<p>Setiap titik mewakili satu rekaman kalibrasi. Semakin dekat titik-titik ke garis diagonal putus-putus,
semakin akurat model. Garis diagonal = prediksi sempurna.</p>
<div class="scatter-grid">
{scatter_html if scatter_html else '<p style="color:#888">Tidak ada data visualisasi (data cv_data tidak tersimpan — latih ulang model).</p>'}
</div>

<h2>Cara Membaca Laporan Ini</h2>
<div class="legend-box">
  <h3>Akurasi (%)</h3>
  <p>Persentase ketepatan prediksi dibandingkan nilai referensi (alat medis). Semakin tinggi semakin baik.</p>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
    <span class="badge badge-green">≥ 90% — Sangat Baik</span>
    <span class="badge badge-blue">80–89% — Baik</span>
    <span class="badge badge-amber">70–79% — Cukup</span>
    <span class="badge badge-red">&lt; 70% — Perlu Data Lebih</span>
  </div>
</div>
<div class="legend-box">
  <div class="legend-row">
    <div style="min-width:90px;font-weight:700">MAE</div>
    <div><i>Mean Absolute Error</i> — rata-rata selisih absolut antara prediksi dan referensi dalam satuan asli
    (mis. mg/dL untuk gula darah). MAE 10 mg/dL berarti prediksi rata-rata meleset ±10 mg/dL.</div>
  </div>
  <div class="legend-row">
    <div style="min-width:90px;font-weight:700">RMSE</div>
    <div><i>Root Mean Squared Error</i> — serupa MAE namun menghukum kesalahan besar lebih berat.
    Berguna untuk melihat seberapa buruk outlier terparah.</div>
  </div>
  <div class="legend-row">
    <div style="min-width:90px;font-weight:700">R² (Korelasi)</div>
    <div>Seberapa kuat hubungan antara prediksi dan referensi. Nilai 1.0 = sempurna, 0.0 = model tidak lebih baik
    dari sekadar menerka rata-rata, &lt;0 = model lebih buruk dari rata-rata.</div>
  </div>
  <div class="legend-row">
    <div style="min-width:90px;font-weight:700">LOO / 5-fold</div>
    <div><i>Leave-One-Out</i> (untuk data kecil &lt;30) atau <i>5-fold Cross-Validation</i> (data ≥30):
    tiap rekaman diuji oleh model yang tidak melihat rekaman tersebut saat training — hasilnya lebih jujur
    dari sekadar memeriksa data training.</div>
  </div>
</div>

<h2>Konfigurasi Teknis Model</h2>
<table>
  <tr><th>Aspek</th><th>Detail</th></tr>
  <tr><td>Arsitektur</td><td>MLP 2 lapisan tersembunyi: 64 neuron → 32 neuron, aktivasi ReLU</td></tr>
  <tr><td>Solver</td><td>L-BFGS untuk &lt;30 data; Adam + Early Stopping untuk ≥30 data</td></tr>
  <tr><td>Regularisasi</td><td>L2 (alpha=0.01)</td></tr>
  <tr><td>Fitur Input (7)</td><td>ir_dc_mean, ir_ac_p2p, red_dc_mean, red_ac_p2p, bpm, age_years, gender_code</td></tr>
  <tr><td>Target Output (5)</td><td>Gula Darah, Kolesterol, Asam Urat, Sistolik, Diastolik</td></tr>
  <tr><td>Normalisasi</td><td>StandardScaler (per target)</td></tr>
  <tr><td>Model terpisah</td><td>Satu MLPRegressor per parameter vital (total 5 model)</td></tr>
</table>

<div class="footer">
  Laporan ini digenerate otomatis oleh sistem ANTARAGA · {datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")}
</div>

</body>
</html>"""

    return StreamingResponse(
        iter([html]),
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="laporan_kalibrasi_mlp.html"'},
    )


# ---------------------------------------------------------------------------
# /v1/calibrate/predict-test  — uji prediksi pada sampel acak dari DB
# ---------------------------------------------------------------------------

@app.post("/v1/calibrate/predict-test")
def calibrate_predict_test(
    n: int = Query(20, ge=5, le=200),
    db: Session = Depends(get_db),
) -> dict:
    """Ambil n rekaman acak dari DB (dengan ground truth), jalankan inferensi MLP,
    kembalikan perbandingan prediksi vs referensi per sampel dan per target."""
    from api.ml_calibration import is_calibration_model_available, predict_vitals

    if not is_calibration_model_available():
        raise HTTPException(status_code=400,
                            detail="Model belum dilatih — klik 'Jalankan Training' dulu")

    rows = (
        db.query(models_db.CalibrationRecord)
        .filter(
            models_db.CalibrationRecord.ir_dc_mean.isnot(None),
            models_db.CalibrationRecord.bpm.isnot(None),
        )
        .all()
    )
    if not rows:
        raise HTTPException(status_code=400, detail="Belum ada rekaman dengan fitur PPG lengkap")

    rng = np.random.default_rng()
    idx = rng.choice(len(rows), size=min(n, len(rows)), replace=False)
    sampled = [rows[int(i)] for i in idx]

    TARGETS_T = ["gula_darah_mg_dl", "kolesterol_mg_dl", "asam_urat_mg_dl",
                 "sistolik_mmhg", "diastolik_mmhg"]
    target_errs: dict[str, list[float]] = {t: [] for t in TARGETS_T}
    target_abs:  dict[str, list[float]] = {t: [] for t in TARGETS_T}

    results = []
    for rec in sampled:
        try:
            pred = predict_vitals(
                ir_dc_mean  = float(rec.ir_dc_mean),
                ir_ac_p2p   = float(rec.ir_ac_p2p or 0),
                red_dc_mean = float(rec.red_dc_mean or 0),
                red_ac_p2p  = float(rec.red_ac_p2p or 0),
                bpm         = float(rec.bpm),
                age_years   = float(rec.age_years),
                gender_code = 1.0 if rec.gender == "L" else 0.0,
            )
        except Exception:
            continue

        row: dict = {
            "id": rec.id, "subject_id": rec.subject_id,
            "age_years": rec.age_years, "gender": rec.gender,
            "predicted": {}, "actual": {}, "error_pct": {},
        }
        for t in TARGETS_T:
            actual_val = getattr(rec, t, None)
            pred_val   = pred.get(t)
            if actual_val is None or pred_val is None:
                continue
            a  = float(actual_val)
            p  = float(pred_val)
            ep = abs(a - p) / max(abs(a), 1e-9) * 100
            ae = abs(a - p)
            row["actual"][t]    = round(a,  1)
            row["predicted"][t] = round(p,  1)
            row["error_pct"][t] = round(ep, 1)
            target_errs[t].append(ep)
            target_abs[t].append(ae)
        results.append(row)

    LABELS = {
        "gula_darah_mg_dl": "Gula Darah", "kolesterol_mg_dl": "Kolesterol",
        "asam_urat_mg_dl": "Asam Urat",   "sistolik_mmhg": "Sistolik",
        "diastolik_mmhg": "Diastolik",
    }
    summary = {}
    for t in TARGETS_T:
        errs = target_errs[t]
        abs_e = target_abs[t]
        if not errs:
            continue
        summary[t] = {
            "label": LABELS[t],
            "n": len(errs),
            "mean_error_pct": round(float(np.mean(errs)), 1),
            "accuracy_pct":   round(100 - float(np.mean(errs)), 1),
            "mae": round(float(np.mean(abs_e)), 2),
        }

    return {"samples": results, "summary": summary, "n_tested": len(results)}


# ---------------------------------------------------------------------------
# /serial — monitor port serial firmware via WebSocket
# ---------------------------------------------------------------------------

@app.get("/serial/ports")
def list_serial_ports() -> list[dict]:
    """Daftar port serial yang tersambung di mesin ini. Buka di browser untuk
    cari tahu nama port sebelum sambungkan WebSocket."""
    try:
        import serial.tools.list_ports  # type: ignore
    except ImportError:
        raise HTTPException(status_code=503, detail="pyserial tidak terinstall")
    ports = serial.tools.list_ports.comports()
    return [{"port": p.device, "description": p.description, "hwid": p.hwid} for p in ports]


@app.websocket("/serial/ws")
async def serial_ws(
    websocket: WebSocket,
    port: str = Query(..., description="Nama port, mis. /dev/ttyUSB0 atau COM3"),
    baud: int = Query(115200),
) -> None:
    """Stream data serial secara real-time lewat WebSocket.

    Sambungkan via browser:
      ws://localhost:8000/serial/ws?port=/dev/ttyUSB0&baud=115200

    Setiap baris dari port serial dikirim sebagai satu pesan teks WebSocket.
    Kirim pesan teks apa pun dari client untuk meneruskannya ke port serial."""
    try:
        import serial  # type: ignore
    except ImportError:
        await websocket.close(code=1011, reason="pyserial tidak terinstall")
        return

    try:
        ser = serial.Serial(port, baudrate=baud, timeout=1)
    except serial.SerialException as exc:
        await websocket.close(code=1011, reason=str(exc))
        return

    await websocket.accept()
    loop = asyncio.get_event_loop()
    logger.info("[serial] klien WS tersambung ke %s @ %d baud", port, baud)

    try:
        while True:
            # Baca satu baris (blocking, dibungkus executor agar non-blocking)
            raw: bytes = await loop.run_in_executor(None, ser.readline)
            if raw:
                try:
                    line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                except Exception:
                    line = raw.hex()
                await websocket.send_text(line)

            # Cek apakah client mengirim data ke serial (non-blocking)
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                ser.write((msg + "\n").encode())
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.warning("[serial] error WS: %s", exc)
    finally:
        ser.close()
        logger.info("[serial] koneksi WS ke %s ditutup", port)
