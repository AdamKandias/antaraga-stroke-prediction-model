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
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from api import ingest_buffer, models_db, schemas
from api.auth import create_access_token, get_current_user_id, get_ingest_user_id
from api.config import DEV_MODE
from api.database import Base, engine, get_db
from api.logging_utils import log_prediction, logger
from api.ml import predict_stroke_risk
from api.ml_vitals import is_model_available, predict_vitals_from_ppg
from api.profile_utils import (
    age_from_birthday,
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
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


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
    response = schemas.StrokeRiskResponse(**result)

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
# /dashboard — web dashboard untuk monitoring hardware
# ---------------------------------------------------------------------------

_DASHBOARD_HTML = os.path.join(os.path.dirname(__file__), "static", "dashboard.html")


@app.get("/dashboard", include_in_schema=False)
def serve_dashboard() -> FileResponse:
    return FileResponse(_DASHBOARD_HTML, media_type="text/html")


@app.get("/v1/devices")
def list_devices() -> list[str]:
    """Daftar device yang sudah mengirim data sejak server terakhir dijalankan."""
    return ingest_buffer.list_devices()


@app.get("/v1/ingest/latest")
def ingest_latest_dashboard(device_id: str, db: Session = Depends(get_db)) -> dict:
    """Kembalikan data terbaru dari device dalam 4 tahap pemrosesan:
    raw → PWA → MLP → XGBoost. Dipakai oleh /dashboard."""
    batches = ingest_buffer.get_window(device_id)
    if not batches:
        raise HTTPException(status_code=404, detail=f"Belum ada data dari device '{device_id}'")

    latest  = batches[-1]
    # Concatenate window untuk sinyal yang lebih panjang (PWA/MLP butuh ≥ 2 detik)
    all_ppg = [float(v) for b in batches for v in b.get("ppg", [])]
    all_red = [float(v) for b in batches for v in b.get("red", [])]
    all_ir  = [float(v) for b in batches for v in b.get("ir", [])]
    fs_ppg  = int(latest.get("fs_ppg", 200))
    fs_max  = int(latest.get("fs_max", 400))

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

    return {
        "device_id": device_id,
        "seq": latest.get("seq", 0),
        "received_at": latest.get("_received_at", ""),
        "batt_pct": latest.get("batt_pct", 0),
        "batt_mv": latest.get("batt_mv", 0),
        "raw": stage_raw,
        "pwa": stage_pwa,
        "mlp": stage_mlp,
        "xgboost": stage_xgb,
    }


def _compute_pwa(ppg: list, red: list, ir: list, fs_ppg: int, fs_max: int) -> dict:
    from model.ppg_features import bandpass_filter, detect_pulses, extract_pwa_features

    result: dict = {
        "filtered_ppg": [], "peaks_ppg": [],
        "filtered_red": [], "peaks_red": [],
        "features": {}, "bpm": None, "note": None,
        "fs_ppg": fs_ppg, "fs_max": fs_max,
    }
    min_samples = int(fs_ppg * 2)  # 2 detik minimum

    def _process(signal: list, fs: int, key: str) -> None:
        if len(signal) < min_samples:
            return
        arr = np.array(signal, dtype=float)
        filt = bandpass_filter(arr, float(fs))
        result[f"filtered_{key}"] = [float(v) for v in filt]   # np.float64 → float
        pulses = detect_pulses(filt, float(fs))
        result[f"peaks_{key}"] = [int(p.peak_idx) for p in pulses]  # np.int64 → int
        if len(pulses) >= 2 and key == "ppg":
            intervals = np.diff([p.peak_idx for p in pulses]) / float(fs)
            result["bpm"] = round(float(60.0 / float(np.mean(intervals))), 1)

    if ppg: _process(ppg, fs_ppg, "ppg")
    if red: _process(red, fs_max, "red")

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


def _compute_mlp(ppg: list, red: list, ir: list, fs_ppg: int) -> dict:
    from api.ml_vitals import is_model_available, predict_vitals_from_ppg

    if not is_model_available():
        return {
            "available": False,
            "message": "Model MLP belum dilatih — menunggu data kalibrasi dari hardware",
        }
    try:
        result = predict_vitals_from_ppg(
            fs_hz=float(fs_ppg),
            age_years=60.0,
            green=ppg or None,
            red=red or None,
            infrared=ir or None,
        )
        return {"available": True, **result}
    except Exception as exc:
        return {"available": False, "message": str(exc)}


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
    return {
        "available": True,
        "probability": resp.get("probability"),
        "risk_level": resp.get("risk_level"),
        "threshold": resp.get("threshold"),
        "model_name": resp.get("model_name"),
        "predicted_at": log.created_at.isoformat(),
    }


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
