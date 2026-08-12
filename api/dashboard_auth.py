"""Login sesi untuk dashboard web (/dashboard).

Terpisah dari api/auth.py yang melayani mobile app: di sana klien memegang
Bearer JWT, sedangkan dashboard dibuka lewat browser sehingga butuh cookie
yang ikut terkirim otomatis pada navigasi biasa, unduhan CSV, tab laporan
PDF, dan koneksi EventSource.

Kredensialnya satu akun operator dari environment (bukan tabel users) —
dashboard ini alat internal tim riset, bukan akun keluarga yang dipakai
aplikasi mobile.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import time
from collections import defaultdict

from api.config import (
    DASHBOARD_EMAIL,
    DASHBOARD_PASSWORD,
    DASHBOARD_SESSION_DAYS,
    DASHBOARD_SESSION_SECRET,
)

COOKIE_NAME = "antaraga_dash"
LOGIN_PATH = "/login"


# ── Token sesi: "<payload-b64>.<hmac-b64>" ────────────────────────────────
# Ditandatangani, bukan dienkripsi — isinya memang cuma email dan waktu
# kedaluwarsa. Yang dijaga adalah keasliannya, supaya cookie tidak bisa
# dikarang sendiri oleh pengunjung.

def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64d(txt: str) -> bytes:
    return base64.urlsafe_b64decode(txt + "=" * (-len(txt) % 4))


def _sign(payload: bytes) -> str:
    return _b64e(hmac.new(DASHBOARD_SESSION_SECRET.encode(), payload, hashlib.sha256).digest())


def create_session(email: str) -> str:
    exp = int(time.time()) + DASHBOARD_SESSION_DAYS * 86400
    payload = f"{email}|{exp}".encode()
    return f"{_b64e(payload)}.{_sign(payload)}"


def verify_session(token: str | None) -> str | None:
    """Kembalikan email bila token sah dan belum kedaluwarsa, selain itu None."""
    if not token or "." not in token:
        return None
    body, sig = token.rsplit(".", 1)
    try:
        payload = _b64d(body)
    except Exception:
        return None
    if not hmac.compare_digest(sig, _sign(payload)):
        return None
    try:
        email, exp = payload.decode().rsplit("|", 1)
        if int(exp) < int(time.time()):
            return None
    except Exception:
        return None
    return email


def check_credentials(email: str, password: str) -> bool:
    """Bandingkan dengan waktu tetap supaya tidak bocor lewat timing."""
    ok_email = hmac.compare_digest(email.strip().lower(), DASHBOARD_EMAIL.strip().lower())
    ok_pass = hmac.compare_digest(password, DASHBOARD_PASSWORD)
    return ok_email and ok_pass


# ── Rem percobaan login ───────────────────────────────────────────────────
# Password dashboard cuma satu dan pendek, jadi tanpa rem ini seorang
# penebak otomatis bisa mencoba ribuan kombinasi per menit.

_MAX_GAGAL = 8
_JENDELA_S = 300.0
_gagal: dict[str, list[float]] = defaultdict(list)


def _bersihkan(ip: str) -> list[float]:
    batas = time.time() - _JENDELA_S
    _gagal[ip] = [t for t in _gagal[ip] if t > batas]
    return _gagal[ip]


def is_throttled(ip: str) -> bool:
    return len(_bersihkan(ip)) >= _MAX_GAGAL


def record_failure(ip: str) -> None:
    _bersihkan(ip).append(time.time())


def reset_failures(ip: str) -> None:
    _gagal.pop(ip, None)


# ── Cakupan yang wajib login ──────────────────────────────────────────────
# Hanya jalur yang memang dipakai dashboard dari browser. Jalur perangkat
# keras sengaja dibiarkan terbuka: firmware ESP32 mengirim Bearer
# DEVICE_INGEST_KEY dan tidak bisa menyimpan cookie sesi, jadi menutupnya
# akan memutus ingest dan OTA di lapangan.
#
#   terbuka: POST /v1/ingest, /v1/ota/check, /v1/ota/firmware, /v1/ota/ack
#            (perangkat), serta endpoint mobile app yang sudah pakai JWT.

_DILINDUNGI: tuple[str, ...] = (
    "/dashboard",
    "/stream",
    "/serial",
    "/v1/access",
    "/v1/devices",
    "/v1/sim",
    "/v1/calibrate",
    "/v1/ingest/latest",
    "/v1/ota/bins",
    "/v1/ota/deploy",
    "/v1/ota/device-status",
    "/firmware",
    "/pwa",
)


def needs_session(path: str) -> bool:
    """True bila path ini cuma boleh diakses operator yang sudah login.

    Pencocokan per segmen, bukan awalan mentah: "/v1/ingest/latest" ikut
    terlindungi tanpa ikut menyeret "/v1/ingest" milik firmware.
    """
    return any(path == p or path.startswith(p + "/") for p in _DILINDUNGI)
