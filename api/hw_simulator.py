"""Simulator perangkat keras ANTARAGA — menyuntikkan batch PPG sintetis
ke pipeline yang SAMA persis dengan yang dipakai firmware asli.

Tujuannya menguji alur ujung-ke-ujung tanpa perangkat fisik:

    simulator → POST /v1/ingest → MLP vital → XGBoost risiko
              → simpan reading → FCM → mobile app

Karena batch masuk lewat handler /v1/ingest yang asli, semua tahap hilir
berjalan apa adanya.  Tidak ada jalur khusus, tidak ada cabang "kalau demo".
Begitu perangkat asli tersambung, alurnya identik.

Dua hal yang sengaja dijaga realistis:

1. FASE BERSAMBUNG antar batch.  Fase kardiak disimpan sebagai state dan
   dilanjutkan di batch berikutnya.  Kalau tiap batch dimulai dari fase nol,
   akan muncul diskontinuitas 1 Hz di setiap sambungan — persis artefak yang
   membuat BPM kanal hijau terkunci di ~60 (lihat catatan ppg_analysis.py).

2. POLARITAS BENAR.  MAX30102 (merah/IR) mengeluarkan cacah mentah: saat
   sistol, darah menyerap lebih banyak cahaya sehingga cacah TURUN — sinyal
   terbalik.  SEN0203 (hijau) sudah AC-coupled di hardware dan tidak terbalik.
"""

from __future__ import annotations

import asyncio
import math
import time
from dataclasses import dataclass, field

import numpy as np

# ── Parameter sinyal (disetel menyerupai rekaman ANTARAGA nyata) ──────────
FS_PPG      = 200          # SEN0203 hijau
FS_MAX      = 400          # MAX30102 merah + IR
BATCH_MS    = 1000         # satu batch = 1 detik, sama seperti firmware

IR_DC       = 145_000.0    # cacah mentah IR (data asli: 125k–154k)
RED_DC       = 85_000.0    # cacah mentah merah (data asli: 43k–96k)
IR_PI_PERMIL = 1.10        # perfusi IR (data asli: 0,74–1,77‰)
RED_PI_PERMIL = 0.95

GREEN_MID   = 800.0        # SEN0203 12-bit, sudah AC-coupled
GREEN_AMP   = 620.0

RESP_HZ     = 0.25         # modulasi napas ~15×/menit


def _ppg_shape(phase: np.ndarray) -> np.ndarray:
    """Bentuk satu siklus PPG, fase 0–1.

    Puncak sistolik di ~0,15 lalu takik dikrotik + gundukan diastolik di ~0,52.
    Dijaga positif dan dinormalkan ke puncak 1,0.
    """
    systolic = np.exp(-(((phase - 0.15) / 0.085) ** 2))
    dicrotic = 0.32 * np.exp(-(((phase - 0.52) / 0.125) ** 2))
    w = systolic + dicrotic
    return w / 1.05


@dataclass
class SimState:
    device_id: str = "antaraga-demo"
    bpm: float     = 78.0
    running: bool  = False
    seq: int       = 0
    phase: float   = 0.0          # fase kardiak berjalan (0–1), DILANJUTKAN
    resp_phase: float = 0.0
    t0: float      = field(default_factory=time.time)
    batches_sent: int = 0
    last_error: str | None = None
    rng: np.random.Generator = field(
        default_factory=lambda: np.random.default_rng(12345)
    )


_state = SimState()
_task: asyncio.Task | None = None


def get_state() -> dict:
    return {
        "running":      _state.running,
        "device_id":    _state.device_id,
        "bpm":          round(_state.bpm, 1),
        "batches_sent": _state.batches_sent,
        "uptime_s":     round(time.time() - _state.t0, 1) if _state.running else 0.0,
        "last_error":   _state.last_error,
    }


def _make_channel(
    n: int, fs: int, phase0: float, bpm: float, resp0: float,
    dc: float, ac: float, inverted: bool, rng: np.random.Generator,
) -> tuple[list[int], float, float]:
    """Bangun satu kanal; kembalikan (sampel, fase_akhir, fase_napas_akhir)."""
    dt        = 1.0 / fs
    cyc_per_s = bpm / 60.0

    idx        = np.arange(n)
    phase      = (phase0 + idx * dt * cyc_per_s) % 1.0
    resp_phase = (resp0 + idx * dt * RESP_HZ) % 1.0

    wave = _ppg_shape(phase)
    # Modulasi napas ±8% pada amplitudo denyut
    wave = wave * (1.0 + 0.08 * np.sin(2 * math.pi * resp_phase))
    # Sedikit variasi antar-denyut supaya tidak terlihat sintetis sempurna
    wave = wave + rng.normal(0.0, 0.012, n)

    sig = dc - ac * wave if inverted else dc + ac * (wave - 0.5)
    sig = sig + rng.normal(0.0, max(ac * 0.02, 0.5), n)

    end_phase = (phase0 + n * dt * cyc_per_s) % 1.0
    end_resp  = (resp0  + n * dt * RESP_HZ)   % 1.0
    return [int(round(v)) for v in sig], end_phase, end_resp


def build_batch() -> dict:
    """Susun satu payload IngestBatch yang identik bentuknya dengan firmware."""
    s   = _state
    rng = s.rng

    # Detak berjalan pelan naik-turun seperti orang sungguhan (bukan konstan)
    s.bpm = float(np.clip(s.bpm + rng.normal(0, 0.6), 62.0, 96.0))

    n_ppg = int(FS_PPG * BATCH_MS / 1000)
    n_max = int(FS_MAX * BATCH_MS / 1000)

    ir_ac  = IR_DC  * IR_PI_PERMIL  / 1000.0
    red_ac = RED_DC * RED_PI_PERMIL / 1000.0

    # Ketiga kanal memakai fase awal yang SAMA (satu jantung, satu fase),
    # dan fase itu dilanjutkan ke batch berikutnya agar sambungannya mulus.
    ir,  ph_end, rs_end = _make_channel(n_max, FS_MAX, s.phase, s.bpm, s.resp_phase,
                                        IR_DC, ir_ac, True, rng)
    red, _, _           = _make_channel(n_max, FS_MAX, s.phase, s.bpm, s.resp_phase,
                                        RED_DC, red_ac, True, rng)
    grn, _, _           = _make_channel(n_ppg, FS_PPG, s.phase, s.bpm, s.resp_phase,
                                        GREEN_MID, GREEN_AMP, False, rng)

    s.phase, s.resp_phase = ph_end, rs_end
    s.seq += 1

    ir_arr = np.array(ir, dtype=float)
    ir_p2p = int(ir_arr.max() - ir_arr.min())
    gr_arr = np.array(grn, dtype=float)

    return {
        "id": s.device_id,
        "seq": s.seq,
        "t_ms": int((time.time() - s.t0) * 1000),
        "t_unix_ms": int(time.time() * 1000),
        "fs_ppg": FS_PPG,
        "fs_max": FS_MAX,
        "batt_mv": 3980,
        "batt_pct": 87,
        "ovf": 0,
        # SQI: sinyal sintetis ini memang bersih — laporkan apa adanya
        "sqi": 92,
        "sqi_flags": 0,
        "ir_dc": int(ir_arr.mean()),
        "ir_p2p": ir_p2p,
        "ir_pi": int(round(1000.0 * ir_p2p / max(ir_arr.mean(), 1.0))),
        "ir_jump": 0,
        "ir_jump_n": 0,
        "ir_tort10": 12,
        "ppg_dc": int(gr_arr.mean()),
        "ppg_p2p": int(gr_arr.max() - gr_arr.min()),
        "ppg_jump_n": 0,
        "ppg_tort10": 14,
        "clip_n": 0,
        "ppg": grn,
        "red": red,
        "ir": ir,
    }


async def _loop() -> None:
    """Kirim satu batch tiap BATCH_MS lewat handler /v1/ingest yang asli."""
    from api import models_db, schemas
    from api.database import SessionLocal
    from api.main import ingest_firmware_batch

    interval = BATCH_MS / 1000.0
    while _state.running:
        started = time.monotonic()
        db = SessionLocal()
        try:
            payload = build_batch()
            batch   = schemas.IngestBatch(**payload)

            # Pakai user yang paling terakhir aktif — perilaku yang sama dengan
            # DEVICE_INGEST_KEY pada firmware asli (lihat auth.get_ingest_user_id).
            user = db.query(models_db.User).order_by(
                models_db.User.last_seen_at.desc()
            ).first()

            # Handler asli: MLP → XGBoost → simpan reading → FCM
            ingest_firmware_batch(batch, db, user.id if user else "demo-user")
            _state.batches_sent += 1
            _state.last_error = None
        except Exception as exc:
            _state.last_error = f"{type(exc).__name__}: {exc}"
        finally:
            db.close()

        await asyncio.sleep(max(0.0, interval - (time.monotonic() - started)))


async def start(device_id: str | None = None, bpm: float | None = None) -> dict:
    global _task
    if _state.running:
        return {**get_state(), "message": "Simulator sudah berjalan"}

    if device_id:
        _state.device_id = device_id.strip()
    if bpm:
        _state.bpm = float(np.clip(bpm, 45.0, 150.0))

    _state.running      = True
    _state.t0           = time.time()
    _state.batches_sent = 0
    _state.last_error   = None
    _task = asyncio.create_task(_loop())
    return {**get_state(), "message": f"Simulator aktif sebagai \"{_state.device_id}\""}


async def stop() -> dict:
    global _task
    if not _state.running:
        return {**get_state(), "message": "Simulator memang tidak berjalan"}

    _state.running = False
    if _task is not None:
        _task.cancel()
        try:
            await _task
        except (asyncio.CancelledError, Exception):
            pass
        _task = None

    # Bersihkan state filter BPM agar tidak terbawa ke perangkat asli
    try:
        from api.bpm_filter import reset as _bpm_reset
        _bpm_reset(_state.device_id)
    except Exception:
        pass

    return {**get_state(), "message": "Simulator dihentikan"}
