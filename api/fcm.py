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
# Dari mana kunci akhirnya terbaca. Dicatat saat inisialisasi, bukan ditebak
# ulang belakangan: bila nilai env rusak lalu jatuh ke berkas, menebak dari
# ada tidaknya env akan melaporkan sumber yang keliru.
_sumber_kunci: str | None = None


def _get_app():
    global _firebase_app, _init_attempted, _sumber_kunci
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
            # Nilainya rusak, misalnya JSON mentah yang tertempel apa adanya
            # sehingga terbaca sepotong.  Jangan menyerah di sini: berkas kunci
            # di disk mungkin justru baik-baik saja, dan mematikan notifikasi
            # gara-gara satu baris .env yang salah ketik itu berlebihan.
            logger.warning(
                "[fcm] FCM_SERVICE_ACCOUNT_B64 terisi tetapi tidak dapat dibaca "
                "(isinya harus base64 dari berkas kunci, bukan JSON mentah). "
                "Beralih ke berkas kunci."
            )
            isi_kunci = None

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
        _sumber_kunci = sumber
        logger.info(
            "[fcm] Firebase Admin SDK siap (proyek %s, kunci dari %s)",
            _firebase_app.project_id, sumber,
        )
    except Exception:
        logger.exception("[fcm] Gagal inisialisasi Firebase Admin SDK")
        _firebase_app = None

    return _firebase_app


def _klasifikasi_galat(exc: Exception) -> tuple[str, bool]:
    """Terjemahkan galat Firebase menjadi (keterangan, token_mati).

    `token_mati` berarti token yang tersimpan sudah tidak mungkin dipakai lagi,
    berapa kali pun dicoba. Pemanggil wajib membuang token itu dari basis data,
    kalau tidak server akan terus mengirim ke alamat yang sudah tidak ada
    sampai pengguna kebetulan membuka aplikasinya lagi.
    """
    nama = type(exc).__name__
    if "Unregistered" in nama or "NotFound" in nama:
        return ("Token notifikasi sudah tidak berlaku. Biasanya karena aplikasi "
                "dihapus atau datanya dibersihkan.", True)
    if "InvalidArgument" in nama and "registration token" in str(exc):
        return ("Token notifikasi yang tersimpan tidak berbentuk token FCM yang sah.", True)
    if "SenderId" in nama or "ThirdPartyAuth" in nama:
        return ("Token ini milik proyek Firebase yang berbeda. Pastikan "
                "google-services.json aplikasi sama dengan kunci layanan di server.", True)
    # Sisanya dianggap gangguan sementara: jaringan, kuota, layanan sedang
    # bermasalah. Token tidak boleh dibuang karena besok mungkin berhasil.
    return (f"{nama}: {exc}", False)


# Templat pesan per tingkat risiko. "tinggi" dan "sedang" sama-sama dikirim
# otomatis oleh sistem (lihat ingest_firmware_batch di api/main.py, yang
# mengecek risk_level in ("high", "medium")) -- "tinggi" lewat
# send_high_risk_notification, "sedang" lewat kirim_notifikasi_uji dengan
# skenario="sedang" supaya teksnya satu sumber dengan pratinjau dashboard.
# "rendah" murni pratinjau, tidak pernah dikirim otomatis.
#
# `dikirim_otomatis` di sini sekadar metadata untuk ditampilkan dashboard
# (lewat GET /v1/notify/scenarios) -- bukan yang menentukan pengiriman
# sungguhan. Kalau nilainya diubah tanpa mengubah pengecekan risk_level di
# ingest_firmware_batch, dashboard akan menampilkan keterangan yang salah.
TEMPLAT_NOTIFIKASI: dict[str, dict] = {
    "tinggi": {
        "judul": "⚠️ Risiko Stroke Tinggi Terdeteksi",
        "isi": lambda nama: f"Risiko stroke {nama} terdeteksi tinggi. Segera lakukan assesmen ABCD2 dan memeriksakan diri ke tenaga kesehatan dalam waktu dekat.",
        "route": "assessment_form",
        "dikirim_otomatis": True,
    },
    "sedang": {
        "judul": "Perlu Pemeriksaan Lanjutan",
        "isi": lambda nama: (
            f"Tanda vital {nama} menunjukkan risiko sedang. Disarankan "
            "memeriksakan diri ke tenaga kesehatan dalam waktu dekat."
        ),
        "route": "assessment_form",
        "dikirim_otomatis": True,
    },
    "rendah": {
        "judul": "Pemantauan Berjalan Normal",
        "isi": lambda nama: (
            f"Tanda vital {nama} saat ini berada dalam rentang normal. "
            "Pemantauan tetap berjalan seperti biasa dan tetap jaga kesehatan."
        ),
        "route": "dashboard",
        "dikirim_otomatis": False,
    },
}


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

        templat = TEMPLAT_NOTIFIKASI["tinggi"]
        message = messaging.Message(
            notification=messaging.Notification(
                title=templat["judul"],
                body=templat["isi"](profile_name),
            ),
            data={"route": templat["route"]},
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
    except Exception as exc:  # noqa: BLE001
        keterangan, token_mati = _klasifikasi_galat(exc)
        logger.warning(
            "[fcm] Gagal kirim notifikasi ke profil '%s': %s", profile_name, keterangan,
        )
        # Ditandai lewat atribut fungsi supaya tanda tangan lamanya tetap utuh
        # bagi pemanggil yang hanya peduli berhasil atau tidak.
        send_high_risk_notification.token_mati = token_mati
        return False


def kirim_notifikasi_uji(
    fcm_token: str,
    profile_name: str,
    judul: str | None = None,
    isi: str | None = None,
    skenario: str = "tinggi",
) -> tuple[bool, str, bool]:
    """Kirim notifikasi percobaan dari dashboard.

    [skenario] memilih templat tingkat risiko yang dipratinjaukan --
    "tinggi", "sedang", atau "rendah" (lihat TEMPLAT_NOTIFIKASI). Hanya
    "tinggi" yang benar-benar dikirim otomatis oleh sistem sekarang; dua
    lainnya murni pratinjau, untuk melihat bunyi pesannya sebelum dipakai
    sungguhan. `judul`/`isi` yang diisi manual selalu menimpa templat.

    Berbeda dari [send_high_risk_notification] yang hanya mengembalikan
    berhasil atau tidak, fungsi ini juga mengembalikan alasannya. Saat menguji
    dari dashboard, "gagal" tanpa keterangan tidak menolong siapa pun: token
    kedaluwarsa, kunci layanan yang belum terpasang, dan aplikasi yang belum
    pernah dibuka semuanya terlihat sama.

    Mengembalikan (berhasil, keterangan, token_mati). `token_mati` menandai
    token yang tidak akan pernah bisa dipakai lagi, sehingga pemanggil dapat
    membuangnya dari basis data.
    """
    if not fcm_token:
        return False, ("Akun ini belum punya token notifikasi. Buka aplikasi "
                       "ANTARAGA dan masuk ke akun tersebut lebih dulu."), False

    app = _get_app()
    if app is None:
        return False, ("Firebase belum dikonfigurasi di server. Berkas "
                       "serviceAccountKey.json tidak ditemukan atau tidak sah."), False

    templat = TEMPLAT_NOTIFIKASI.get(skenario, TEMPLAT_NOTIFIKASI["tinggi"])

    try:
        from firebase_admin import messaging

        message = messaging.Message(
            notification=messaging.Notification(
                title=judul or templat["judul"],
                body=isi or templat["isi"](profile_name),
            ),
            # Route ikut templat, KECUALI dipertahankan sebagai "test" pada
            # data tambahan supaya aplikasi tetap tahu ini pesan percobaan
            # (berguna kalau nanti perlu dibedakan dari peringatan asli di
            # sisi aplikasi), sementara route navigasinya tetap realistis.
            data={"route": templat["route"], "percobaan": "1"},
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
        return True, f"Terkirim ke Firebase (id {message_id.rsplit('/', 1)[-1]})", False
    except Exception as exc:  # noqa: BLE001
        logger.warning("[fcm] Gagal kirim notifikasi percobaan '%s'", profile_name)
        keterangan, token_mati = _klasifikasi_galat(exc)
        if token_mati:
            keterangan += " Token akan dibuang dari server; buka ulang aplikasi supaya token baru terdaftar."
        return False, keterangan, token_mati


def status() -> dict:
    """Keadaan jalur notifikasi, untuk diperiksa tanpa mengirim apa pun.

    Inisialisasi Firebase sengaja ditunda sampai pengiriman pertama, sehingga
    log tidak memuat apa pun sampai ada yang benar-benar dikirim.  Fungsi ini
    memaksa inisialisasinya lalu melaporkan hasilnya, supaya pemasangan kunci
    di peladen dapat dipastikan lewat satu panggilan.
    """
    import os
    from pathlib import Path

    from api.config import FCM_SERVICE_ACCOUNT_PATH

    berkas = Path(FCM_SERVICE_ACCOUNT_PATH)
    b64 = os.getenv("FCM_SERVICE_ACCOUNT_B64", "").strip()
    app = _get_app()

    if app is not None:
        sumber = _sumber_kunci or str(berkas)
        pesan = "Jalur notifikasi siap."
    elif b64:
        sumber = "variabel lingkungan (gagal dibaca)"
        pesan = ("FCM_SERVICE_ACCOUNT_B64 terisi tetapi tidak dapat dibaca, dan "
                 "tidak ada berkas kunci sebagai cadangan. Isinya harus base64 "
                 "dari berkas kunci, bukan JSON mentah. Kosongkan barisnya lalu "
                 "pakai berkas kunci saja bila ragu.")
    elif berkas.is_file():
        sumber = str(berkas)
        pesan = "Berkas kunci ada tetapi ditolak Firebase. Periksa isinya."
    else:
        sumber = None
        pesan = (f"Kunci tidak ditemukan. Berkas '{berkas}' tidak ada, dan "
                 "FCM_SERVICE_ACCOUNT_B64 kosong.")

    return {
        "siap": app is not None,
        "project_id": getattr(app, "project_id", None),
        "sumber_kunci": sumber,
        "berkas_ada": berkas.is_file(),
        "env_terisi": bool(b64),
        "pesan": pesan,
    }
