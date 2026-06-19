import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
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


def _age_from_birthday(birthday) -> float:
    today = datetime.now(timezone.utc).date()
    born = birthday if isinstance(birthday, type(today)) else birthday.date()
    years = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    return float(years)


def _derive_hypertension(systolic_bp: float, diastolic_bp: float | None) -> bool:
    if diastolic_bp is not None:
        return systolic_bp >= 140 or diastolic_bp >= 90
    return systolic_bp >= 140


def _profile_to_response(profile: models_db.Profile) -> schemas.ProfileResponse:
    return schemas.ProfileResponse(
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


@app.post("/profile", response_model=schemas.ProfileResponse)
def upsert_profile(
    payload: schemas.ProfilePayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.ProfileResponse:
    profile = db.get(models_db.Profile, user_id)
    if profile is None:
        profile = models_db.Profile(user_id=user_id)
        db.add(profile)

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


@app.get("/profile", response_model=schemas.ProfileResponse)
def get_profile(
    db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)
) -> schemas.ProfileResponse:
    profile = db.get(models_db.Profile, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not set yet")
    return _profile_to_response(profile)


@app.post("/predict/stroke-risk", response_model=schemas.StrokeRiskResponse)
def predict_stroke_risk_endpoint(
    vital: schemas.VitalPayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.StrokeRiskResponse:
    start = time.perf_counter()

    profile = db.get(models_db.Profile, user_id)
    if profile is None:
        raise HTTPException(status_code=400, detail="Isi profil dulu lewat POST /profile sebelum prediksi")

    bmi = profile.weight_kg / ((profile.height_cm / 100) ** 2)
    features = {
        "gender": "Male" if profile.gender == schemas.Gender.L.value else "Female",
        "age": _age_from_birthday(profile.birthday),
        "avg_glucose_level": vital.blood_glucose_mg_dl,
        "bmi": bmi,
        "hypertension": int(_derive_hypertension(vital.systolic_bp, vital.diastolic_bp)),
        "heart_disease": profile.heart_disease,
        "residence_type": profile.residence_type,
        "smoking_status": profile.status_merokok,
    }
    result = predict_stroke_risk(features)
    response = schemas.StrokeRiskResponse(**result)

    latency_ms = (time.perf_counter() - start) * 1000
    log_prediction(db, "stroke_risk", vital.model_dump(), response.model_dump(), latency_ms, user_id=user_id)
    return response


@app.post("/assessment/abcd2", response_model=schemas.Abcd2Response)
def assess_abcd2(
    payload: schemas.Abcd2Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> schemas.Abcd2Response:
    start = time.perf_counter()

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
    log_prediction(db, "abcd2", payload.model_dump(), response.model_dump(), latency_ms, user_id=user_id)
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
            "request_payload": row.request_payload,
            "response_payload": row.response_payload,
            "risk_level": row.risk_level,
            "latency_ms": row.latency_ms,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
