from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


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
