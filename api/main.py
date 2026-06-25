import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from api import models_db, schemas
from api.auth import create_access_token, get_current_user_id
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
            timestamp=reading.created_at,
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
            timestamp=r.created_at,
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
