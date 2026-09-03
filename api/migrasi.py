"""Penyesuaian skema basis data yang berjalan sendiri saat server dinyalakan.

`Base.metadata.create_all()` hanya membuat tabel yang belum ada. Kolom baru
pada tabel yang sudah terlanjur berisi data tidak ikut dibuat, dan diam-diam
menghasilkan galat "no such column" saat dipakai. Modul ini menutup celah itu.

Sengaja tidak memakai Alembic: proyek ini hanya punya satu basis data SQLite
di satu peladen, sehingga menambah perkakas migrasi beserta berkas revisinya
justru lebih banyak yang harus dijaga daripada yang dihemat.

Aman dijalankan berulang kali. Tiap langkah memeriksa dulu apakah pekerjaannya
memang masih perlu dilakukan.
"""

from __future__ import annotations

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def _punya_kolom(engine: Engine, tabel: str, kolom: str) -> bool:
    inspector = inspect(engine)
    if tabel not in inspector.get_table_names():
        return True          # tabelnya belum ada, create_all yang akan mengurus
    return any(k["name"] == kolom for k in inspector.get_columns(tabel))


def _tambah_device_key_ke_profil(engine: Engine) -> None:
    """Pindahkan penyambungan gelang dari akun ke masing-masing orang tua.

    Sebelumnya `device_key` hanya ada di tabel users, sehingga satu akun hanya
    dapat menyambung satu gelang. Padahal satu keluarga bisa memantau lebih
    dari satu orang tua, dan tiap orang tua memakai gelangnya sendiri.

    Nilai lama dipindahkan ke profil yang paling masuk akal, yaitu profil yang
    terakhir dibuka akun tersebut, atau profil pertama yang pernah dibuat bila
    belum ada yang pernah dibuka. Kolom di tabel users dibiarkan apa adanya
    supaya versi lama aplikasi yang masih membacanya tidak ikut rusak.
    """
    if _punya_kolom(engine, "profiles", "device_key"):
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE profiles ADD COLUMN device_key VARCHAR"))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_profiles_device_key "
            "ON profiles (device_key)"
        ))
        logger.info("[migrasi] kolom profiles.device_key dibuat")

        baris = conn.execute(text(
            "SELECT id, device_key, last_viewed_profile_id FROM users "
            "WHERE device_key IS NOT NULL AND TRIM(device_key) <> ''"
        )).fetchall()

        dipindah = 0
        for user_id, device_key, terakhir_dibuka in baris:
            profil_id = None
            if terakhir_dibuka:
                cocok = conn.execute(text(
                    "SELECT id FROM profiles WHERE id = :pid AND user_id = :uid"
                ), {"pid": terakhir_dibuka, "uid": user_id}).fetchone()
                if cocok:
                    profil_id = cocok[0]
            if profil_id is None:
                pertama = conn.execute(text(
                    "SELECT id FROM profiles WHERE user_id = :uid "
                    "ORDER BY created_at LIMIT 1"
                ), {"uid": user_id}).fetchone()
                if pertama:
                    profil_id = pertama[0]
            if profil_id is None:
                continue      # akun belum punya profil sama sekali

            conn.execute(text(
                "UPDATE profiles SET device_key = :dk WHERE id = :pid"
            ), {"dk": device_key, "pid": profil_id})
            dipindah += 1

        if dipindah:
            logger.info(
                "[migrasi] %d penyambungan gelang dipindahkan dari akun ke profil",
                dipindah,
            )


def jalankan(engine: Engine) -> None:
    """Jalankan seluruh penyesuaian skema. Dipanggil sekali saat server mulai."""
    try:
        _tambah_device_key_ke_profil(engine)
    except Exception:
        # Server tetap dinyalakan. Kegagalan migrasi tidak boleh membuat
        # seluruh layanan mati, karena sebagian besar endpoint tidak
        # bergantung pada kolom yang baru ditambahkan.
        logger.exception("[migrasi] gagal menyesuaikan skema basis data")
