"""Firebase Cloud Messaging helper.

Lazily initialises the Firebase Admin SDK on first use. If the service
account key file is missing or invalid, FCM is silently disabled and
send_high_risk_notification() always returns False -- the rest of the app
keeps working normally without push notifications.

Setup (satu kali):
  1. Firebase Console → Project Settings → Service accounts
  2. "Generate new private key" → simpan sebagai api/serviceAccountKey.json
  3. Isi FCM_SERVICE_ACCOUNT_PATH di .env kalau path-nya beda
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_firebase_app = None
_init_attempted = False


def _get_app():
    global _firebase_app, _init_attempted
    if _init_attempted:
        return _firebase_app

    _init_attempted = True
    from api.config import FCM_SERVICE_ACCOUNT_PATH

    key_path = Path(FCM_SERVICE_ACCOUNT_PATH)
    if not key_path.exists():
        logger.warning(
            "[fcm] Service account key tidak ditemukan di '%s' — push notification dinonaktifkan. "
            "Download dari Firebase Console → Project Settings → Service accounts.",
            key_path,
        )
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate(str(key_path))
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("[fcm] Firebase Admin SDK berhasil diinisialisasi (project: %s)", key_path)
    except Exception:
        logger.exception("[fcm] Gagal inisialisasi Firebase Admin SDK")
        _firebase_app = None

    return _firebase_app


def send_high_risk_notification(fcm_token: str, profile_name: str) -> bool:
    """Kirim push notification ke device user saat risiko stroke HIGH.

    Returns True jika berhasil dikirim, False jika gagal atau FCM tidak
    dikonfigurasi (service account key tidak ada).
    """
    if not fcm_token:
        return False

    app = _get_app()
    if app is None:
        return False

    try:
        from firebase_admin import messaging

        message = messaging.Message(
            notification=messaging.Notification(
                title="⚠️ Risiko Stroke Tinggi Terdeteksi",
                body=f"Risiko stroke {profile_name} terdeteksi tinggi. "
                "Segera lakukan Penilaian ABCD2.",
            ),
            data={"route": "assessment_form"},
            token=fcm_token,
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    channel_id="antaraga_high_risk",
                    sound="default",
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default"),
                ),
            ),
        )
        messaging.send(message)
        logger.info("[fcm] Notifikasi HIGH-risk dikirim ke profil '%s'", profile_name)
        return True
    except Exception:
        logger.exception("[fcm] Gagal kirim notifikasi FCM ke profil '%s'", profile_name)
        return False
