"""Ganti WiFi smartband dari mobile app - cloud-mediated, dengan rollback
otomatis di firmware. Lihat blok komentar WIFI_CFG_* di
Firmware/include/config.h untuk kontrak lengkap & alasan desainnya (device
yang MASIH tersambung ke WiFi lama polling endpoint check di bawah, mencoba
WiFi baru dengan timeout, dan otomatis kembali ke kredensial lama kalau
gagal - jadi tidak akan pernah "terkunci" offline hanya karena salah ketik
SSID/password dari app).

Alur:
  Mobile app                      Server                    ESP32
  ────────────────────────────    ──────────────────────    ──────────────
  POST /v1/wifi/request ────────▶ simpan sebagai "pending"
                                                     ─── GET /v1/wifi/check ──▶
                                                     ◀── {pending:true,...} ────
                                                     (coba konek; gagal -> rollback)
                                                     ─── POST /v1/wifi/result ─▶
                                   simpan last_result ◀────────────────────────
  GET  /v1/wifi/status ─────────▶  baca pending + last_result

Endpoint /request dan /status (dipakai mobile app, auth JWT + resolusi
profile->device) didefinisikan langsung di main.py, sama seperti endpoint
lain yang butuh _resolve_profile_for_request - modul ini cuma menyediakan
fungsi state (set_pending/get_status) yang dipanggilnya, plus APIRouter
untuk dua endpoint firmware-facing (auth device key, sama seperti ota.py).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from fastapi import APIRouter, Body, Header, HTTPException, Query
from pydantic import BaseModel

from api.config import DEVICE_INGEST_KEY
from api.logging_utils import logger

router = APIRouter(tags=["wifi"])

_STATE_FILE = Path(__file__).parent / "wifi_config_state.json"
_lock = Lock()


class WifiResultBody(BaseModel):
    """Body POST /v1/wifi/result -- ssid/message lewat body (bukan query)
    supaya pesan bebas spasi/koma tidak perlu di-escape di firmware."""

    ssid: str
    message: str = ""


def _load_state() -> dict:
    with _lock:
        try:
            return json.loads(_STATE_FILE.read_text()) if _STATE_FILE.exists() else {}
        except Exception:
            return {}


def _save_state(s: dict) -> None:
    with _lock:
        _STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))


def _verify_key(authorization: str) -> None:
    if authorization != f"Bearer {DEVICE_INGEST_KEY}":
        got = authorization[:20] + "…" if len(authorization) > 20 else authorization
        logger.warning("[WIFICFG] 403 - kunci ditolak: %r", got)
        raise HTTPException(status_code=403, detail="Invalid device key")


# ── dipakai LANGSUNG oleh main.py (endpoint mobile app, auth JWT) ──────

def set_pending(device_id: str, ssid: str, password: str) -> None:
    """Simpan permintaan ganti WiFi untuk device_id. Firmware akan
    mengambilnya di polling /check berikutnya."""
    state = _load_state()
    ds = state.setdefault(device_id, {})
    ds["pending"] = {"ssid": ssid, "password": password}
    # Permintaan baru menggantikan status hasil yang lama -- app harus
    # melihat "sedang mencoba" lagi, bukan hasil dari percobaan sebelumnya.
    ds.pop("last_result", None)
    _save_state(state)


def get_status(device_id: str) -> dict:
    """Status terkini untuk mobile app: ada permintaan yang masih
    menunggu firmware mencobanya, dan/atau hasil percobaan terakhir."""
    state = _load_state()
    ds = state.get(device_id, {})
    pending = ds.get("pending")
    return {
        "device_id": device_id,
        # Password TIDAK dikembalikan ke app lagi di endpoint status --
        # app sudah tahu apa yang dia kirim, tidak perlu dibaca-balik.
        "pending": {"ssid": pending["ssid"]} if pending else None,
        "last_result": ds.get("last_result"),
    }


# ── firmware-facing (auth: device key, sama seperti ota.py) ───────────

@router.get("/v1/wifi/check")
def wifi_check(
    device_id: str = Query(...),
    authorization: str = Header(default=""),
) -> dict:
    """Dipanggil firmware tiap WIFI_CFG_CHECK_INTERVAL_MS: ada permintaan
    ganti WiFi yang menunggu untuk device ini?"""
    _verify_key(authorization)
    state = _load_state()
    pending = state.get(device_id, {}).get("pending")
    if not pending:
        return {"pending": False}
    return {"pending": True, "ssid": pending["ssid"], "password": pending["password"]}


@router.post("/v1/wifi/result")
def wifi_result(
    device_id: str = Query(...),
    success: bool = Query(...),
    body: WifiResultBody = Body(...),
    authorization: str = Header(default=""),
) -> dict:
    """Dipanggil firmware setelah MENCOBA WiFi baru -- baik berhasil
    maupun gagal-dan-rollback ke WiFi lama -- supaya mobile app bisa
    menampilkan hasilnya alih-alih menunggu tanpa kejelasan."""
    _verify_key(authorization)
    state = _load_state()
    ds = state.setdefault(device_id, {})

    pending = ds.get("pending")
    # Hanya hapus "pending" kalau laporan ini memang untuk permintaan yang
    # SEDANG tersimpan. Kalau SSID-nya beda, berarti ada permintaan BARU
    # yang sudah menimpa sebelum laporan (yang basi) ini sampai -- jangan
    # sampai permintaan baru itu ikut terhapus oleh laporan lama.
    if pending and pending.get("ssid") == body.ssid:
        ds.pop("pending", None)

    ds["last_result"] = {
        "ssid": body.ssid,
        "success": success,
        "message": body.message,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    _save_state(state)
    logger.info(
        "[WIFICFG] %s: ganti ke %r -> %s (%s)",
        device_id, body.ssid, "OK" if success else "GAGAL", body.message,
    )
    return {"ok": True}
