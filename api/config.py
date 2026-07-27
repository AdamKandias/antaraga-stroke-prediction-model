"""Centralized environment configuration. Loaded once from `.env`."""

import os

from dotenv import load_dotenv

load_dotenv()

DEV_MODE = os.getenv("DEV_MODE", "false").strip().lower() == "true"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./antaraga.db")

# Secret used to sign/verify our own access tokens (api/security.py).
# Set a long random value in .env for anything beyond local development —
# anyone with this secret can mint valid tokens for any user.
JWT_SECRET = os.getenv("JWT_SECRET", "dev-insecure-secret-change-me")

JWT_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "30"))

SIMULATOR_INTERVAL_SECONDS = int(os.getenv("SIMULATOR_INTERVAL_SECONDS", "20"))

# A user counts as "currently active" for the simulator if they've made an
# authenticated request (real Bearer token, see api/auth.py) within this
# many seconds. Keeps the simulator from forever feeding someone who logged
# in once and closed the app.
SIMULATOR_ACTIVE_WINDOW_SECONDS = int(os.getenv("SIMULATOR_ACTIVE_WINDOW_SECONDS", "1800"))

# Path ke service account JSON dari Firebase Console (Project Settings →
# Service accounts → Generate new private key). Wajib diisi agar push
# notification bisa dikirim; kalau kosong/tidak ada, FCM dinonaktifkan.
FCM_SERVICE_ACCOUNT_PATH = os.getenv("FCM_SERVICE_ACCOUNT_PATH", "api/serviceAccountKey.json")

# Jeda minimum (detik) antar notifikasi HIGH-risk per user supaya tidak spam.
FCM_NOTIFICATION_COOLDOWN_SECONDS = int(os.getenv("FCM_NOTIFICATION_COOLDOWN_SECONDS", "300"))

# Kunci statis untuk perangkat keras (firmware). Dikirim sebagai
# "Authorization: Bearer <DEVICE_INGEST_KEY>" dari config.h CLOUD_API_KEY.
# Berbeda dari JWT (yang expire) — kunci ini permanen sampai diubah manual.
# Ganti ke nilai random sebelum production!
DEVICE_INGEST_KEY = os.getenv("DEVICE_INGEST_KEY", "antaraga-hw-2026-01")
