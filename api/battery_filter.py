"""Penghalus baterai -- EMA mV berbasis waktu + histeresis pada persen yang
ditampilkan, supaya angka tidak melompat 2-4% walau bacaan ADC mentahnya goyang.

Kenapa masih goyang padahal firmware sudah meng-EMA (BATT_EMA_ALPHA=0,2 tiap
2 detik, lihat config.h): rentang LiPo yang dipetakan ke 0-100% cuma 800 mV
(3,4-4,2 V), jadi 1% == 8 mV saja -- noise ADC ESP32 yang berpuluh mV langsung
jadi beberapa persen. EMA firmware itu juga masih cukup reaktif (konstanta
waktu efektif ~8 s). Dua lapis tambahan di sini, dilakukan di server supaya
bisa disetel tanpa flash ulang:

  1. EMA KEDUA pada mV, lebih lambat (TAU_S), dan BERBASIS WAKTU -- bukan
     per-panggilan seperti bpm_filter.py. Endpoint ini DIPOLL (dashboard web
     & mobile app), bukan dipanggil sekali per batch baru dari firmware; EMA
     per-panggilan biasa akan "menguap" ke nilai mentah kalau terus diberi
     makan bacaan yang sama tiap kali dipoll. Dengan decay berbasis waktu,
     memoll ulang dalam rentang sangat pendek praktis tidak menggerakkan EMA;
     yang menentukan seberapa jauh ia bergerak adalah waktu yang BENAR-BENAR
     berlalu antar pembacaan baru.

  2. Histeresis pada persen -- band Schmitt-trigger di sekitar persen yang
     SEDANG ditampilkan. Persen hanya pindah kalau mV terhalus sudah melewati
     setengah-step (4 mV) PLUS margin dari titik tengah persen saat ini,
     supaya tidak bolak-balik persis di garis batas dua persen.
"""

from __future__ import annotations

import math
import time
from threading import Lock

TAU_S = 25.0  # konstanta waktu EMA (detik) -- jauh lebih lambat dari EMA
# firmware (~8 s efektif pada alpha 0,2 / 2 s)
BATT_MIN_MV = 3400.0
BATT_MAX_MV = 4200.0
STEP_MV = (BATT_MAX_MV - BATT_MIN_MV) / 100.0  # mV per 1%
HYSTERESIS_MV = 6.0  # margin ekstra di atas setengah-step sebelum persen pindah


def _mv_to_pct(mv: float) -> int:
    pct = (mv - BATT_MIN_MV) / (BATT_MAX_MV - BATT_MIN_MV) * 100.0
    return max(0, min(100, round(pct)))


class BatteryFilter:
    """Filter baterai untuk SATU device. Simpan state antar pembacaan."""

    def __init__(self) -> None:
        self.ema_mv: float | None = None
        self.last_ts: float | None = None
        self.displayed_pct: int | None = None

    def update(self, raw_mv: float | None, now: float | None = None) -> dict:
        now = time.monotonic() if now is None else now

        if not raw_mv or raw_mv <= 0:
            # Tidak ada bacaan baru -- tahan nilai terakhir, kalau ada.
            if self.ema_mv is None:
                return {"batt_pct": 0, "batt_mv": 0}
            return {"batt_pct": self.displayed_pct, "batt_mv": round(self.ema_mv)}

        raw_mv = float(raw_mv)

        if self.ema_mv is None:
            self.ema_mv = raw_mv
            self.last_ts = now
            self.displayed_pct = _mv_to_pct(raw_mv)
            return {"batt_pct": self.displayed_pct, "batt_mv": round(self.ema_mv)}

        dt = max(0.0, now - self.last_ts)
        self.last_ts = now
        alpha = 1.0 - math.exp(-dt / TAU_S)
        self.ema_mv += alpha * (raw_mv - self.ema_mv)

        candidate_pct = _mv_to_pct(self.ema_mv)
        if candidate_pct != self.displayed_pct:
            anchor_mv = BATT_MIN_MV + self.displayed_pct / 100.0 * (BATT_MAX_MV - BATT_MIN_MV)
            if abs(self.ema_mv - anchor_mv) >= STEP_MV / 2 + HYSTERESIS_MV:
                self.displayed_pct = candidate_pct

        return {"batt_pct": self.displayed_pct, "batt_mv": round(self.ema_mv)}


# ── Registry per-device ───────────────────────────────────────────────────
_filters: dict[str, BatteryFilter] = {}
_lock = Lock()


def get_filter(device_id: str) -> BatteryFilter:
    with _lock:
        f = _filters.get(device_id)
        if f is None:
            f = BatteryFilter()
            _filters[device_id] = f
        return f


def filter_battery(device_id: str, raw_mv: float | None) -> dict:
    """Jalan pintas: saring satu pembacaan baterai untuk device tertentu.

    Dipanggil dari /v1/ingest/latest (dashboard web) DAN /vitals/latest
    (mobile app) dengan device_id yang sama -- sengaja berbagi satu registry
    supaya kedua sisi menampilkan angka yang konsisten, bukan dua hasil
    smoothing yang berbeda untuk perangkat yang sama.
    """
    return get_filter(device_id).update(raw_mv)


def reset(device_id: str | None = None) -> None:
    with _lock:
        if device_id is None:
            _filters.clear()
        else:
            _filters.pop(device_id, None)
