"""Penyaring lonjakan BPM + penahan nilai terakhir yang baik (last known good).

Masalah yang diselesaikan: pembacaan stabil di ~80 bpm tiba-tiba melompat ke 40
selama beberapa detik lalu kembali ke 80.  Lompatan seperti itu bukan perubahan
fisiologis — detak jantung tidak bisa berubah 50% dalam satu detik.  Penyebab
tersering adalah *octave error*: detektor puncak melewatkan satu dari dua denyut
(→ setengah), atau mengunci takik dikrotik sebagai denyut (→ dua kali lipat).

Empat lapis, berurutan:
  1. Gerbang confidence  — conf < 0,30 dibuang (ambang yang sudah dipakai
     bpm_autocorr sendiri sebagai batas "tidak bermakna").
  2. Koreksi oktaf       — nilai yang ≈ setengah / ≈ dua kali nilai terakhir
     dikalikan / dibagi 2 dan dipakai, bukan dibuang.
  3. Batas laju          — sisanya yang menyimpang >20% dari nilai terakhir
     ditolak; yang ditampilkan tetap nilai terakhir yang baik.
  4. Median bergulir     — meredam riak kecil pada nilai yang sudah diterima.
     Median, bukan rata-rata, karena rata-rata masih tertarik outlier.

Penahanan dibatasi HOLD_MAX_S detik.  Lewat itu nilai dilepas menjadi None,
supaya layar tidak memajang angka basi saat jari sudah lepas dari sensor.

Pemulihan: bila RESYNC_N pembacaan berturut-turut sama-sama ditolak TAPI saling
konsisten, filter menganggap detak jantung memang berpindah level dan mengunci
ke nilai baru.  Tanpa ini, perubahan nyata (mis. setelah naik tangga) akan
tertahan selamanya.
"""

from __future__ import annotations

import time
from statistics import median
from threading import Lock

# ── Konstanta ─────────────────────────────────────────────────────────────
MIN_CONF      = 0.30   # ambang periodisitas; sama dengan bpm_autocorr
MAX_JUMP_PCT  = 20.0   # simpangan maksimum terhadap nilai terakhir (%)
HOLD_MAX_S    = 15.0   # lama maksimum menahan nilai lama (detik)
RESYNC_N      = 8      # pembacaan konsisten berturut-turut untuk pindah level
MEDIAN_WIN    = 5      # panjang jendela median
BPM_MIN       = 40.0
BPM_MAX       = 180.0
OCTAVE_TOL    = 0.18   # toleransi relatif saat menguji rasio 2× / ½×


class BpmFilter:
    """Filter BPM untuk SATU perangkat.  Simpan state antar pembacaan."""

    def __init__(self) -> None:
        self.last_good: float | None = None
        self.last_good_ts: float     = 0.0
        self.accepted: list[float]   = []
        self._pending: list[float]   = []

    # ── internal ──────────────────────────────────────────────────────────
    @staticmethod
    def _dev_pct(a: float, b: float) -> float:
        return abs(a - b) / b * 100.0 if b else float("inf")

    def _octave_fix(self, bpm: float) -> float | None:
        """Kembalikan nilai terkoreksi bila bpm adalah kelipatan/pembagi 2."""
        ref = self.last_good
        if ref is None:
            return None
        for cand in (bpm * 2.0, bpm / 2.0):
            if BPM_MIN <= cand <= BPM_MAX and self._dev_pct(cand, ref) <= MAX_JUMP_PCT * (1 + OCTAVE_TOL):
                return cand
        return None

    def _commit(self, value: float, now: float) -> None:
        self.last_good    = value
        self.last_good_ts = now
        self._pending.clear()
        self.accepted.append(value)
        if len(self.accepted) > MEDIAN_WIN:
            self.accepted.pop(0)

    # ── API ───────────────────────────────────────────────────────────────
    def update(
        self,
        bpm: float | None,
        conf: float = 1.0,
        now: float | None = None,
    ) -> dict:
        """Masukkan satu pembacaan mentah, dapatkan nilai yang layak tampil.

        Mengembalikan dict:
          bpm      – nilai untuk ditampilkan (None bila tidak ada yang layak)
          held     – True bila ini nilai lama yang ditahan, bukan pembacaan baru
          status   – OK | OKTAF_DIKOREKSI | DITAHAN_LONJAKAN | DITAHAN_DERAU
                     | DITAHAN_KOSONG | KEDALUWARSA | MENUNGGU
          raw      – nilai mentah yang masuk (untuk diagnostik)
        """
        now = time.monotonic() if now is None else now

        def hold(status: str) -> dict:
            """Tahan nilai terakhir, kecuali sudah kedaluwarsa."""
            if self.last_good is None:
                return {"bpm": None, "held": False, "status": "MENUNGGU", "raw": bpm}
            if now - self.last_good_ts > HOLD_MAX_S:
                self.last_good = None
                self.accepted.clear()
                self._pending.clear()
                return {"bpm": None, "held": False, "status": "KEDALUWARSA", "raw": bpm}
            return {"bpm": round(self.last_good, 1), "held": True, "status": status, "raw": bpm}

        # 1 — tidak ada angka sama sekali
        if bpm is None or not (BPM_MIN <= float(bpm) <= BPM_MAX):
            return hold("DITAHAN_KOSONG")

        bpm = float(bpm)

        # 2 — sinyal tidak cukup periodik
        if conf < MIN_CONF:
            return hold("DITAHAN_DERAU")

        # 3 — pembacaan pertama: tidak ada acuan, terima apa adanya
        if self.last_good is None:
            self._commit(bpm, now)
            return {"bpm": round(bpm, 1), "held": False, "status": "OK", "raw": bpm}

        # 4 — masih dalam batas laju fisiologis
        if self._dev_pct(bpm, self.last_good) <= MAX_JUMP_PCT:
            self._commit(bpm, now)
            smoothed = median(self.accepted)
            return {"bpm": round(smoothed, 1), "held": False, "status": "OK", "raw": bpm}

        # 5 — lompatan: coba dulu sebagai kesalahan oktaf
        fixed = self._octave_fix(bpm)
        if fixed is not None:
            self._commit(fixed, now)
            smoothed = median(self.accepted)
            return {"bpm": round(smoothed, 1), "held": False,
                    "status": "OKTAF_DIKOREKSI", "raw": bpm}

        # 6 — lompatan nyata: tahan, tapi catat untuk kemungkinan resync
        self._pending.append(bpm)
        if len(self._pending) >= RESYNC_N:
            ref = self._pending[-1]
            if all(self._dev_pct(v, ref) <= MAX_JUMP_PCT for v in self._pending[-RESYNC_N:]):
                # Konsisten sekian kali berturut-turut → memang pindah level
                self.accepted.clear()
                self._commit(ref, now)
                return {"bpm": round(ref, 1), "held": False, "status": "OK", "raw": bpm}
            self._pending = self._pending[-RESYNC_N:]

        return hold("DITAHAN_LONJAKAN")


# ── Registry per-device ───────────────────────────────────────────────────
_filters: dict[str, BpmFilter] = {}
_lock = Lock()


def get_filter(device_id: str) -> BpmFilter:
    with _lock:
        f = _filters.get(device_id)
        if f is None:
            f = BpmFilter()
            _filters[device_id] = f
        return f


def filter_bpm(
    device_id: str,
    bpm: float | None,
    conf: float = 1.0,
) -> dict:
    """Jalan pintas: saring satu pembacaan untuk device tertentu."""
    return get_filter(device_id).update(bpm, conf)


def reset(device_id: str | None = None) -> None:
    with _lock:
        if device_id is None:
            _filters.clear()
        else:
            _filters.pop(device_id, None)
