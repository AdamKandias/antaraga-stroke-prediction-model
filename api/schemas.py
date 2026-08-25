from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator, field_serializer


class Gender(str, Enum):
    L = "L"
    P = "P"


class ResidenceType(str, Enum):
    URBAN = "Urban"
    RURAL = "Rural"


# Maps every value the Flutter app is known to send for smoking status,
# including the legacy Bahasa variants noted in lib/models/user_profile.dart's
# fromJson(), onto the categories the model was trained on.
_SMOKING_STATUS_ALIASES = {
    "formerly smoked": "formerly smoked",
    "never smoked": "never smoked",
    "smokes": "smokes",
    "merokok": "smokes",
    "pernah_merokok": "formerly smoked",
    "tidak_pernah_merokok": "never smoked",
}


class RegisterRequest(BaseModel):
    email: str | None = None
    phone: str | None = Field(None, min_length=6)
    password: str = Field(..., min_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is not None and "@" not in value:
            raise ValueError("email tidak valid")
        return value

    @model_validator(mode="after")
    def require_identifier(self):
        if not self.email and not self.phone:
            raise ValueError("email atau phone wajib diisi salah satu")
        return self


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Email atau nomor HP")
    password: str


class AuthResponse(BaseModel):
    access_token: str
    user_id: str


class CurrentUserResponse(BaseModel):
    user_id: str
    email: str | None
    phone: str | None


class ProfilePayload(BaseModel):
    """Mirrors UserProfile.toJson() in the Flutter app (minus `id`, which is
    always the authenticated user)."""

    name: str
    gender: Gender
    birthday: datetime
    weight_kg: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    status_merokok: str = "Unknown"
    heart_disease: int = Field(0, ge=0, le=1)
    is_working: bool = True
    residence_type: ResidenceType
    has_diabetes: bool = False
    family_history_stroke: bool = False

    @field_validator("status_merokok")
    @classmethod
    def normalize_smoking_status(cls, value: str) -> str:
        return _SMOKING_STATUS_ALIASES.get(value, "Unknown")


class ProfileResponse(ProfilePayload):
    id: str


class VitalPayload(BaseModel):
    """Mirrors VitalData.toJson() in the Flutter app. Only the fields the
    risk model needs are required; heart_rate_bpm/spo2_percent are accepted
    but unused by /predict/stroke-risk.

    `profile_id` is optional: omit it to target the account's active
    (last-viewed, else default) parent profile. Pass it explicitly once the
    app supports monitoring more than one parent at a time."""

    systolic_bp: float = Field(..., ge=0)
    diastolic_bp: float | None = Field(None, ge=0)
    blood_glucose_mg_dl: float = Field(..., ge=0)
    heart_rate_bpm: float | None = None
    spo2_percent: float | None = None
    profile_id: str | None = None


class StrokeRiskResponse(BaseModel):
    probability: float
    risk_level: str
    threshold: float
    model_name: str
    risk_flags: list[str] = []


class VitalReadingResponse(BaseModel):
    """Mirrors VitalData.fromJson() in the Flutter app -- same field names
    (including `timestamp`, not `recorded_at`) so the client can parse this
    directly with no field-renaming glue code."""

    systolic_bp: float
    diastolic_bp: float | None
    heart_rate_bpm: float | None
    spo2_percent: float | None
    blood_glucose_mg_dl: float
    timestamp: datetime

    @field_serializer("timestamp")
    def _ts_utc(self, v: datetime, _info) -> str:
        """Sertakan penanda zona UTC saat serialisasi.

        Kolom waktu disimpan sebagai UTC tanpa penanda zona. Tanpa akhiran
        "+00:00", aplikasi mobile menganggapnya waktu setempat sehingga jam
        yang tampil mundur 7 jam bagi pengguna WIB.
        """
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.isoformat()


class LatestVitalResponse(BaseModel):
    """What the dashboard polls: the latest vital reading plus whatever risk
    assessment was computed for it (same call that wrote the reading also
    wrote a StrokeRiskResponse -- this just reads it back, no new prediction
    triggered). `risk` is null only if a reading exists but somehow no
    matching prediction was ever logged for it."""

    vital: VitalReadingResponse
    risk: StrokeRiskResponse | None = None


class Abcd2Request(BaseModel):
    """Mirrors AssessmentResult.toJson() in the Flutter app — the app already
    resolves each component to its point value before sending it."""

    abcd2_age: bool
    abcd2_bp: bool
    abcd2_clinical: int = Field(..., ge=0, le=2)
    abcd2_duration: int = Field(..., ge=0, le=2)
    abcd2_diabetes: bool
    profile_id: str | None = None


class Abcd2Response(BaseModel):
    score: int
    urgency: str
    recommendation: str
    risk_2day_percent: float
    risk_7day_percent: float
    risk_90day_percent: float


class VitalsFromPpgRequest(BaseModel):
    """Raw multi-wavelength PPG segment from the smartband (>= 8s recommended)
    plus the user's age. At least one channel must be provided."""

    fs_hz: float = Field(..., gt=0)
    green: list[float] | None = None
    red: list[float] | None = None
    infrared: list[float] | None = None
    profile_id: str | None = None

    @model_validator(mode="after")
    def require_one_channel(self):
        if not self.green and not self.red and not self.infrared:
            raise ValueError("isi minimal salah satu channel: green, red, atau infrared")
        return self


class VitalsFromPpgResponse(BaseModel):
    systolic_bp_mmhg: float
    diastolic_bp_mmhg: float
    blood_glucose_mg_dl: float


class RegisterDeviceTokenRequest(BaseModel):
    """Body untuk POST /device/register-token."""
    fcm_token: str


class IngestBatch(BaseModel):
    """Payload dari firmware XIAO ESP32-S3 ke POST /v1/ingest."""
    id: str
    seq: int
    t_ms: int
    t_unix_ms: int
    fs_ppg: int
    fs_max: int
    batt_mv: int = 0
    batt_pct: int = 0
    ovf: int = 0
    # SQI metadata — dikirim firmware sejak v0.x; opsional agar payload lama tetap valid
    sqi: int = 0           # skor 0–100 (MINIMUM sub-skor; 0 jika ada flag aktif)
    sqi_flags: int = 0     # bitmask: 0x01=NO_FINGER 0x02=SAT 0x04=FLAT 0x08=MOTION 0x10=PPG_BAD 0x20=SHORT
    ir_dc: int = 0
    ir_p2p: int = 0
    ir_pi: int = 0         # perfusi IR dalam per-mil (p2p/DC × 1000)
    ir_jump: int = 0
    ir_jump_n: int = 0
    ir_tort10: int = 0     # tortuositas × 10
    ppg_dc: int = 0
    ppg_p2p: int = 0
    ppg_jump_n: int = 0
    ppg_tort10: int = 0
    clip_n: int = 0
    ppg: list[int] = []
    red: list[int] = []
    ir: list[int] = []


class IngestResponse(BaseModel):
    ok: bool
    seq: int
    risk_level: str | None = None


class PairDeviceRequest(BaseModel):
    device_key: str


class DeviceStatusResponse(BaseModel):
    paired: bool
    device_key: str | None = None
