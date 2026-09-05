"""Centralized environment configuration. Loaded once from `.env`."""

import os

from dotenv import load_dotenv

load_dotenv()

DEV_MODE = os.getenv("DEV_MODE", "false").strip().lower() == "true"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./antaraga.db")

# Secret used to sign/verify our own access tokens (api/security.py).
# Set a long random value in .env for anything beyond local development -
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

# Akun operator untuk dashboard web (/dashboard). Satu akun untuk tim riset,
# terpisah dari tabel users milik aplikasi mobile.
# WAJIB diganti lewat .env sebelum dipasang di server yang bisa diakses publik -
# nilai default di bawah ada di repo, jadi siapa pun yang melihat kode ini tahu
# password-nya.
DASHBOARD_EMAIL = os.getenv("DASHBOARD_EMAIL", "antaraga@gmail.com")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "password")

# Kunci penanda tangan cookie sesi dashboard. Ikut JWT_SECRET kalau tidak
# diisi sendiri; mengganti nilainya membuat semua sesi lama otomatis logout.
# "or JWT_SECRET", bukan default getenv: baris kosong di .env (DASHBOARD_
# SESSION_SECRET=) menghasilkan string kosong, dan itu berarti cookie
# ditandatangani dengan kunci kosong - siapa pun bisa memalsukannya.
DASHBOARD_SESSION_SECRET = os.getenv("DASHBOARD_SESSION_SECRET", "").strip() or JWT_SECRET

DASHBOARD_SESSION_DAYS = int(os.getenv("DASHBOARD_SESSION_DAYS", "7"))

# Jeda minimum (detik) antar notifikasi HIGH-risk per user supaya tidak spam.
FCM_NOTIFICATION_COOLDOWN_SECONDS = int(os.getenv("FCM_NOTIFICATION_COOLDOWN_SECONDS", "300"))

# Jeda terpisah untuk notifikasi risiko SEDANG, sengaja jauh lebih panjang
# daripada jeda Tinggi. Sedang bukan keadaan darurat -- mengingatkan tiap
# lima menit seperti Tinggi hanya akan membuat keluarga terbiasa mengabaikan
# notifikasi ANTARAGA sama sekali. Bawaan satu jam.
FCM_MEDIUM_NOTIFICATION_COOLDOWN_SECONDS = int(
    os.getenv("FCM_MEDIUM_NOTIFICATION_COOLDOWN_SECONDS", "3600")
)

# Kunci statis untuk perangkat keras (firmware). Dikirim sebagai
# "Authorization: Bearer <DEVICE_INGEST_KEY>" dari config.h CLOUD_API_KEY.
# Berbeda dari JWT (yang expire) - kunci ini permanen sampai diubah manual.
# Ganti ke nilai random sebelum production!
DEVICE_INGEST_KEY = os.getenv("DEVICE_INGEST_KEY", "antaraga-hw-2026-01")
