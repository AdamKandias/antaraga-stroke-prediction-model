from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class User(Base):
    """A family account that logs in and can monitor multiple elderly
    profiles ("parent"). Login is by email OR phone (at least one set) +
    password — no email verification, no third-party auth provider."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Updated on every authenticated request with a real Bearer token (not
    # the DEV_MODE no-header fallback) -- used to decide which users count
    # as "currently active" for the dev hardware simulator.
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Plain string, not a ForeignKey constraint: a Profile can be deleted
    # independently and that shouldn't be blocked by this pointer. Validity
    # is checked in application code (api/profile_utils.py).
    last_viewed_profile_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # FCM device token for push notifications. Registered by the mobile app
    # on launch (POST /device/register-token). Nullable because old accounts
    # may not have registered yet.
    fcm_token: Mapped[str | None] = mapped_column(String, nullable=True)

    # Throttle high-risk notifications: only send once per cooldown window.
    last_notified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # DEVICE_ID firmware yang di-pair ke akun ini (misal "antaraga-001").
    # Diisi lewat POST /device/pair dari mobile app.
    # Batch masuk ke /v1/ingest dicocokkan dengan field "id" di payload.
    device_key: Mapped[str | None] = mapped_column(String, nullable=True)

    profiles: Mapped[list["Profile"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Profile.created_at",
    )


class Profile(Base):
    """One elderly person ("parent") being monitored. A single account can
    have several of these; the first one ever created is the default."""

    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    gender: Mapped[str] = mapped_column(String, nullable=False)  # 'L' / 'P'
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    status_merokok: Mapped[str] = mapped_column(String, default="Unknown")
    heart_disease: Mapped[int] = mapped_column(Integer, default=0)
    is_working: Mapped[bool] = mapped_column(Boolean, default=True)
    residence_type: Mapped[str] = mapped_column(String, default="Urban")
    has_diabetes: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="profiles")


class VitalReading(Base):
    """One vital-signs reading for a profile -- from the real smartband
    (via /predict/stroke-risk) or the dev-mode simulator. Kept separate from
    PredictionLog (whose request_payload shape differs between callers) so
    the app has one clean, typed source for "latest vitals" and history
    charts."""

    __tablename__ = "vital_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    systolic_bp: Mapped[float] = mapped_column(Float, nullable=False)
    diastolic_bp: Mapped[float | None] = mapped_column(Float, nullable=True)
    heart_rate_bpm: Mapped[float | None] = mapped_column(Float, nullable=True)
    spo2_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    blood_glucose_mg_dl: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class CalibrationRecord(Base):
    """Satu sesi kalibrasi: sinyal PPG dari sensor + nilai invasif sebagai ground truth.

    Satu baris = satu subjek, satu waktu pengukuran.
    Dipakai untuk melatih MLP (model/train_mlp_calibration.py).
    """

    __tablename__ = "calibration_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # Identitas subjek (anonim)
    subject_id: Mapped[str] = mapped_column(String, nullable=False)   # mis. "S001"
    age_years: Mapped[float] = mapped_column(Float, nullable=False)
    gender: Mapped[str] = mapped_column(String, nullable=False)        # "L" / "P"
    kondisi: Mapped[str | None] = mapped_column(String, nullable=True) # "puasa" / "2j_makan"

    # Sinyal mentah — disimpan sebagai string nilai dipisah ";" (kompatibel train_ppg_vitals.py)
    fs_hz: Mapped[float] = mapped_column(Float, nullable=False)
    green_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    red_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    infrared_raw: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Fitur sinyal yang sudah dihitung (untuk tampilan cepat & training sederhana)
    ir_dc_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    ir_ac_p2p: Mapped[float | None] = mapped_column(Float, nullable=True)
    red_dc_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    red_ac_p2p: Mapped[float | None] = mapped_column(Float, nullable=True)
    bpm: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Ground truth dari alat invasif / medis standar
    gula_darah_mg_dl: Mapped[float | None] = mapped_column(Float, nullable=True)
    kolesterol_mg_dl: Mapped[float | None] = mapped_column(Float, nullable=True)
    asam_urat_mg_dl: Mapped[float | None] = mapped_column(Float, nullable=True)
    sistolik_mmhg: Mapped[float | None] = mapped_column(Float, nullable=True)
    diastolik_mmhg: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class PredictionLog(Base):
    """Every call to /predict/stroke-risk, /assessment/abcd2, or
    /estimate/vitals-from-ppg is recorded here, purely so the testing
    dashboard can show what the model/ABCD2 logic has been asked and what
    it answered.
    """

    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    profile_id: Mapped[str | None] = mapped_column(String, nullable=True)
    request_payload: Mapped[str] = mapped_column(Text, nullable=False)
    response_payload: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str | None] = mapped_column(String, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
