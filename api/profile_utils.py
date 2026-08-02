"""Shared helpers for resolving/using a user's Profile ("parent").

Lives in its own module (not api/main.py) so api/simulator.py can reuse the
exact same active-profile resolution and feature-building logic without a
circular import with main.py.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from api import models_db


def age_from_birthday(birthday) -> float:
    today = datetime.now(timezone.utc).date()
    born = birthday if isinstance(birthday, type(today)) else birthday.date()
    years = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    return float(years)


def derive_hypertension(systolic_bp: float, diastolic_bp: float | None) -> bool:
    if diastolic_bp is not None:
        return systolic_bp >= 140 or diastolic_bp >= 90
    return systolic_bp >= 140


def resolve_active_profile(db: Session, user_id: str) -> models_db.Profile | None:
    """The profile the app should show/predict for by default: the user's
    last-viewed profile if it still exists and still belongs to them,
    otherwise the first profile ever created (the default "parent")."""
    # No `user` row backs DEV_MODE's no-header fallback identity
    # (api.auth.DEV_USER_ID) -- fall straight through to the
    # first-created-profile lookup below for that case.
    user = db.get(models_db.User, user_id)
    if user is not None and user.last_viewed_profile_id:
        profile = db.get(models_db.Profile, user.last_viewed_profile_id)
        if profile is not None and profile.user_id == user_id:
            return profile

    return (
        db.query(models_db.Profile)
        .filter(models_db.Profile.user_id == user_id)
        .order_by(models_db.Profile.created_at)
        .first()
    )


def record_vital_reading(
    db: Session,
    profile_id: str,
    systolic_bp: float,
    blood_glucose_mg_dl: float,
    diastolic_bp: float | None = None,
    heart_rate_bpm: float | None = None,
    spo2_percent: float | None = None,
) -> models_db.VitalReading:
    """Stores one vital-signs reading for a profile, regardless of whether it
    came from a real /predict/stroke-risk call or the dev-mode simulator --
    this is what GET /vitals/latest and /vitals/history read back."""
    reading = models_db.VitalReading(
        profile_id=profile_id,
        systolic_bp=systolic_bp,
        diastolic_bp=diastolic_bp,
        heart_rate_bpm=heart_rate_bpm,
        spo2_percent=spo2_percent,
        blood_glucose_mg_dl=blood_glucose_mg_dl,
    )
    db.add(reading)
    db.commit()
    return reading


def profile_to_features(profile: models_db.Profile, vital: dict) -> dict:
    """Builds the exact feature dict api/ml.py::predict_stroke_risk expects,
    combining the profile's static data with a fresh vital reading."""
    bmi = profile.weight_kg / ((profile.height_cm / 100) ** 2)
    return {
        "gender": "Male" if profile.gender == "L" else "Female",
        "age": age_from_birthday(profile.birthday),
        "avg_glucose_level": vital["avg_glucose_level"],
        "bmi": bmi,
        "hypertension": int(derive_hypertension(vital["systolic_bp"], vital.get("diastolic_bp"))),
        "heart_disease": profile.heart_disease,
        "is_working": int(profile.is_working),
        "residence_type": profile.residence_type,
        "smoking_status": profile.status_merokok,
    }


def compute_risk_flags(
    profile: models_db.Profile,
    kolesterol: float | None = None,
    asam_urat: float | None = None,
) -> list[str]:
    """Faktor risiko stroke berbasis profil dan hasil MLP kalibrasi.
    Digunakan sebagai peringatan tambahan di luar skor XGBoost."""
    flags: list[str] = []

    if getattr(profile, "family_history_stroke", False):
        flags.append("Riwayat keluarga stroke")

    if profile.has_diabetes:
        flags.append("Riwayat diabetes melitus")

    if kolesterol is not None:
        if kolesterol >= 240:
            flags.append(f"Kolesterol sangat tinggi ({kolesterol:.0f} mg/dL ≥240)")
        elif kolesterol >= 200:
            flags.append(f"Kolesterol batas tinggi ({kolesterol:.0f} mg/dL, 200–239)")

    if asam_urat is not None and asam_urat > 6.2:
        flags.append(f"Asam urat tinggi ({asam_urat:.1f} mg/dL >6,2)")

    return flags
