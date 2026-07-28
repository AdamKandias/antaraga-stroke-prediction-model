import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/pwa", tags=["pwa"])

_CONFIG_FILE = Path(__file__).parent / "pwa_config.json"

DEFAULTS: dict = {
    "bandpass_low_hz": 0.5,
    "bandpass_high_hz": 12.0,
    "filter_order": 4,
    "bpm_min": 40,
    "bpm_max": 200,
    "prominence_multiplier": 0.4,
}


def get_pwa_config() -> dict:
    if _CONFIG_FILE.exists():
        try:
            saved = json.loads(_CONFIG_FILE.read_text())
            return {**DEFAULTS, **{k: v for k, v in saved.items() if k in DEFAULTS}}
        except Exception:
            pass
    return DEFAULTS.copy()


def save_pwa_config(config: dict) -> None:
    merged = {**DEFAULTS, **{k: v for k, v in config.items() if k in DEFAULTS}}
    _CONFIG_FILE.write_text(json.dumps(merged, indent=2))


@router.get("/config")
def get_config() -> dict:
    return {"config": get_pwa_config(), "defaults": DEFAULTS}


@router.put("/config")
def update_config(body: dict) -> dict:
    save_pwa_config(body)
    return {"ok": True}
