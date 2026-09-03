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
    import base64
    import json
    import os

    from api.config import FCM_SERVICE_ACCOUNT_PATH

    sumber = None
    isi_kunci = None

    # Jalur pertama: isi kunci ditanam langsung di variabel lingkungan sebagai
    # base64.  Dipakai di peladen, karena nilainya ikut .env.production yang
    # tidak tersentuh git pull maupun pembangunan ulang container.  Base64
    # dipakai supaya baris-baris private key tidak merusak berkas .env.
    b64 = os.getenv("FCM_SERVICE_ACCOUNT_B64", "").strip()
    if b64:
        try:
            isi_kunci = json.loads(base64.b64decode(b64))
            sumber = "variabel lingkungan FCM_SERVICE_ACCOUNT_B64"
        except Exception:
            logger.exception("[fcm] FCM_SERVICE_ACCOUNT_B64 ada tetapi tidak dapat dibaca")
            return None

    # Jalur kedua: berkas kunci di disk.  Dipakai saat mengembangkan di laptop.
    if isi_kunci is None:
        key_path = Path(FCM_SERVICE_ACCOUNT_PATH)
        # is_file(), bukan exists(): bind mount Docker yang berkasnya tidak ada
        # di host justru membuat DIREKTORI kosong di titik itu, dan exists()
        # akan menjawab True untuk sesuatu yang jelas bukan kunci.
        if not key_path.is_file():
            logger.warning(
                "[fcm] Kunci layanan tidak ditemukan di '%s' dan FCM_SERVICE_ACCOUNT_B64 "
                "juga kosong - notifikasi dinonaktifkan. Unduh dari Firebase Console, "
                "Project Settings, Service accounts.",
                key_path,
            )
            return None
        sumber = str(key_path)

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = (credentials.Certificate(isi_kunci) if isi_kunci is not None
                else credentials.Certificate(str(Path(FCM_SERVICE_ACCOUNT_PATH))))
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info(
            "[fcm] Firebase Admin SDK siap (proyek %s, kunci dari %s)",
            _firebase_app.project_id, sumber,
        )
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


def kirim_notifikasi_uji(
    fcm_token: str,
    profile_name: str,
    judul: str | None = None,
    isi: str | None = None,
) -> tuple[bool, str]:
    """Kirim notifikasi percobaan dari dashboard.

    Berbeda dari [send_high_risk_notification] yang hanya mengembalikan
    berhasil atau tidak, fungsi ini juga mengembalikan alasannya. Saat menguji
    dari dashboard, "gagal" tanpa keterangan tidak menolong siapa pun: token
    kedaluwarsa, kunci layanan yang belum terpasang, dan aplikasi yang belum
    pernah dibuka semuanya terlihat sama.

    Mengembalikan pasangan (berhasil, keterangan).
    """
    if not fcm_token:
        return False, ("Akun ini belum punya token notifikasi. Buka aplikasi "
                       "ANTARAGA dan masuk ke akun tersebut lebih dulu.")

    app = _get_app()
    if app is None:
        return False, ("Firebase belum dikonfigurasi di server. Berkas "
                       "serviceAccountKey.json tidak ditemukan atau tidak sah.")

    try:
        from firebase_admin import messaging

        message = messaging.Message(
            notification=messaging.Notification(
                title=judul or "Notifikasi Percobaan ANTARAGA",
                body=isi or (f"Ini notifikasi percobaan untuk {profile_name}. "
                             "Bila pesan ini sampai, jalur notifikasi sudah berjalan."),
            ),
            # Sengaja tidak memakai route "assessment_form" seperti peringatan
            # sungguhan, supaya menekan notifikasi percobaan tidak membuka
            # halaman penilaian dan meninggalkan catatan palsu.
            data={"route": "test"},
            token=fcm_token,
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    channel_id="antaraga_high_risk",
                    sound="default",
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(aps=messaging.Aps(sound="default")),
            ),
        )
        message_id = messaging.send(message)
        logger.info("[fcm] Notifikasi percobaan dikirim untuk profil '%s'", profile_name)
        return True, f"Terkirim ke Firebase (id {message_id.rsplit('/', 1)[-1]})"
    except Exception as exc:  # noqa: BLE001
        logger.exception("[fcm] Gagal kirim notifikasi percobaan '%s'", profile_name)
        nama = type(exc).__name__
        if "Unregistered" in nama or "NotFound" in nama:
            return False, ("Token notifikasi sudah tidak berlaku. Biasanya "
                           "karena aplikasi dihapus atau datanya dibersihkan. "
                           "Buka ulang aplikasi supaya token baru terdaftar.")
        if "InvalidArgument" in nama and "registration token" in str(exc):
            return False, ("Token notifikasi yang tersimpan tidak berbentuk token FCM "
                           "yang sah. Buka ulang aplikasi supaya token baru terdaftar.")
        if "SenderId" in nama or "ThirdPartyAuth" in nama:
            return False, ("Token ini milik proyek Firebase yang berbeda. "
                           "Pastikan google-services.json aplikasi sama dengan "
                           "kunci layanan di server.")
        return False, f"{nama}: {exc}"
