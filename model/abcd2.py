"""ABCD2 score: short-term stroke risk stratification after a TIA-like episode.

Pure rule-based scoring (Spampinato et al., 2022, cited in the proposal),
deliberately kept separate from the ML risk model: it only activates when
ANTARAGA's threshold/anomaly trigger fires.

The Flutter app's assessment form already resolves each component to its
point value before sending it (age >= 60, BP elevated, clinical feature
0-2, duration 0-2, diabetes) - see `AssessmentResult` in
lib/models/assessment.dart - so this module just sums and categorizes
rather than re-deriving the components from raw inputs.

Risk-by-category percentages below are the original ABCD2 validation cohort
figures (Johnston et al., 2007 - the same source physio-pedia's Stroke:
Assessment page tabulates), used here only to give the family a concrete,
literature-backed number alongside the urgency label.
"""

from enum import Enum
from typing import NamedTuple


class UrgencyLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class Abcd2Result(NamedTuple):
    score: int
    urgency: UrgencyLevel
    recommendation: str
    risk_2day_percent: float
    risk_7day_percent: float
    risk_90day_percent: float


_RECOMMENDATIONS = {
    UrgencyLevel.HIGH: (
        "Risiko tinggi (skor 6-7). Segera bawa lansia ke IGD/layanan "
        "kesehatan terdekat untuk evaluasi medis darurat."
    ),
    UrgencyLevel.MODERATE: (
        "Risiko sedang (skor 4-5). Disarankan segera berkonsultasi ke "
        "fasilitas kesehatan dalam waktu dekat untuk evaluasi lebih lanjut."
    ),
    UrgencyLevel.LOW: (
        "Risiko rendah (skor 0-3). Tetap lakukan pemantauan rutin dan "
        "evaluasi berkala jika gejala serupa muncul kembali."
    ),
}

# 2-day / 7-day / 90-day subsequent-stroke risk per ABCD2 category,
# from the original validation cohort.
_RISK_PERCENT = {
    UrgencyLevel.LOW: (1.0, 1.2, 3.1),
    UrgencyLevel.MODERATE: (4.1, 5.9, 9.8),
    UrgencyLevel.HIGH: (8.1, 11.7, 17.8),
}


def calculate_abcd2(
    abcd2_age: bool,
    abcd2_bp: bool,
    abcd2_clinical: int,
    abcd2_duration: int,
    abcd2_diabetes: bool,
) -> Abcd2Result:
    if not 0 <= abcd2_clinical <= 2:
        raise ValueError("abcd2_clinical must be 0, 1, or 2")
    if not 0 <= abcd2_duration <= 2:
        raise ValueError("abcd2_duration must be 0, 1, or 2")

    score = (
        int(abcd2_age)
        + int(abcd2_bp)
        + abcd2_clinical
        + abcd2_duration
        + int(abcd2_diabetes)
    )

    if score >= 6:
        urgency = UrgencyLevel.HIGH
    elif score >= 4:
        urgency = UrgencyLevel.MODERATE
    else:
        urgency = UrgencyLevel.LOW

    risk_2day, risk_7day, risk_90day = _RISK_PERCENT[urgency]

    return Abcd2Result(
        score=score,
        urgency=urgency,
        recommendation=_RECOMMENDATIONS[urgency],
        risk_2day_percent=risk_2day,
        risk_7day_percent=risk_7day,
        risk_90day_percent=risk_90day,
    )
