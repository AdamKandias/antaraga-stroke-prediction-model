"""
Port algoritma sinyal dari gui/plotter.py ANTARAGA.

Identik dengan plotter.py: ac_signal (= "buang baseline"), bpm_autocorr
(= BPM via autokorelasi FFT + periodisitas).  Dipakai oleh /v1/ingest/latest
untuk memproses ketiga kanal (hijau, merah, inframerah).

Referensi: Recorder3CH/gui/plotter.py — fungsi movavg, detrend, ac_signal,
bpm_autocorr.
"""
from __future__ import annotations

import numpy as np


# ── Primitif sinyal ────────────────────────────────────────────────────────

def movavg(x: np.ndarray, win: int) -> np.ndarray:
    """Rerata bergerak jendela terpangkas (bukan zero-padded).

    Identik dengan movavg() di plotter.py.  Jendela yang menyusut di tepi
    mencegah dua cacat yang terjadi bila di luar array dianggap nol:
      1. Baseline di tepi meluruh ke nol → sinyal tepi rusak.
      2. Plateau konstan berkorelasi sempurna → autokorelasi palsu.
    """
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    if n < 4:
        return np.full(n, x.mean() if n else 0.0)
    win = max(3, int(win) | 1)   # paksa ganjil
    h   = win // 2
    cs  = np.concatenate(([0.0], np.cumsum(x)))
    idx = np.arange(n)
    lo  = np.clip(idx - h,     0, n)
    hi  = np.clip(idx + h + 1, 0, n)
    return (cs[hi] - cs[lo]) / (hi - lo)


def detrend(x: np.ndarray, win: int) -> np.ndarray:
    return np.asarray(x, dtype=np.float64) - movavg(x, win)


def ac_signal(x: np.ndarray, fs: float) -> np.ndarray:
    """Komponen denyut: HP dua-tingkat + LP ringan (~5 Hz).

    Identik dengan ac_signal() di plotter.py.

    Kenapa dua tingkat HP: gelombang napas ~0.25 Hz ada di semua PPG nyata,
    dan satu tingkat rerata-bergerak hanya menekannya ke ~53%.  Sisa sebesar
    itu membuat autokorelasi meluruh monoton → BPM selalu salah (~220).
    Dua tingkat menekannya ke ~28% sementara denyut 43 bpm masih lolos
    dengan gain 1.23.

    LP window 17–18 sampel pada 200 Hz ≈ -3 dB di 5 Hz.
    """
    fs  = max(float(fs), 20.0)
    w_hp = fs * 2.5                                    # ~2.5 s
    y   = detrend(detrend(x, w_hp), w_hp)
    lp  = max(3, int(round(0.44 * fs / 5.0)))         # ~-3 dB di 5 Hz
    return movavg(y, lp)


# ── BPM via autokorelasi FFT ───────────────────────────────────────────────

def bpm_autocorr(
    x: np.ndarray,
    fs: float,
    bpm_min: float = 40.0,
    bpm_max: float = 180.0,
) -> tuple[float | None, float]:
    """Periode dominan via autokorelasi FFT.  Mengembalikan (bpm, conf).

    Identik dengan bpm_autocorr() di plotter.py.

    conf = puncak autokorelasi ternormalisasi (0–1).  conf < 0.30 berarti
    sinyal tidak cukup periodik dan angka BPM tidak bermakna.

    Rentang 40–180 membuang dua kesalahan oktaf: takik dikrotik (~200 bpm)
    dan modulasi napas/amplitudo (~35 bpm).
    """
    n = len(x)
    if n < int(fs * 4) or fs < 20:
        return None, 0.0

    y  = ac_signal(x, fs)
    y  = y - y.mean()
    r0 = float(np.dot(y, y)) / n
    if r0 <= 0:
        return None, 0.0

    nf = 1 << (2 * n - 1).bit_length()
    f  = np.fft.rfft(y, nf)
    ac = np.fft.irfft(f * np.conj(f), nf)[:n] / n

    lo = int(fs * 60.0 / bpm_max)
    hi = min(int(fs * 60.0 / bpm_min), n // 2)
    if hi - lo < 3:
        return None, 0.0
    seg = ac[lo:hi]

    # Wajib maksimum LOKAL — np.argmax selalu mengembalikan sesuatu, termasuk
    # kurva meluruh tanpa puncak, yang selalu jatuh di ujung = 220 bpm.
    inner = seg[1:-1]
    peak  = (inner > seg[:-2]) & (inner >= seg[2:])
    if not peak.any():
        return None, 0.0
    cand = np.flatnonzero(peak) + 1
    b    = int(cand[np.argmax(seg[cand])])

    # Interpolasi parabola: resolusi ~4 bpm per lag di 220 bpm tanpa ini.
    y0, y1, y2 = float(seg[b - 1]), float(seg[b]), float(seg[b + 1])
    den  = y0 - 2.0 * y1 + y2
    frac = 0.5 * (y0 - y2) / den if den < -1e-12 else 0.0
    frac = max(-0.5, min(0.5, frac))

    bpm  = 60.0 * fs / (lo + b + frac)
    conf = max(0.0, float(y1 / r0))
    return round(bpm, 1), round(conf, 3)


# ── Deteksi puncak untuk visualisasi ──────────────────────────────────────

def _find_peaks_ac(y: np.ndarray, fs: float, bpm_max: float = 180.0) -> list[int]:
    from scipy.signal import find_peaks
    if len(y) < int(fs * 2):
        return []
    min_dist = max(int(fs * 60.0 / bpm_max), 1)
    prom     = float(np.std(y)) * 0.5
    peaks, _ = find_peaks(y, distance=min_dist, prominence=prom)
    return [int(p) for p in peaks]


# ── Referensi perfusi (dari rekaman rekam_ppg_merah_v2_irred1.txt) ────────
_REF_PI: dict[str, float | None] = {
    "green": None,   # belum ada acuan rekaman optimal
    "red":   1.44,
    "ir":    3.03,
}


def channel_stats(
    raw: list | np.ndarray,
    fs: float,
    channel: str = "green",
) -> dict:
    """DC, AC p2p (1 detik terakhir), perfusi permil.

    Identik dengan blok perhitungan di _tick_stats() plotter.py:
      dc  = mean(y)
      ac  = max(y[-1s:]) - min(y[-1s:])
      pi  = 1000 * ac / dc
    """
    arr = np.asarray(raw, dtype=np.float64)
    n   = len(arr)
    if n == 0:
        return {
            "dc": None, "ac_p2p": None, "pi_permil": None,
            "ref_pi_permil": _REF_PI.get(channel),
        }
    dc   = float(arr.mean())
    n1s  = min(n, max(8, int(fs)))
    seg  = arr[-n1s:]
    ac   = float(seg.max() - seg.min())
    pi   = round(1000.0 * ac / dc, 2) if dc > 1 else 0.0
    return {
        "dc":            round(dc),
        "ac_p2p":        round(ac),
        "pi_permil":     pi,
        "ref_pi_permil": _REF_PI.get(channel),
    }


# ── API publik ─────────────────────────────────────────────────────────────

def analyze_channel(
    signal: list | np.ndarray,
    fs: float,
    bpm_min: float = 40.0,
    bpm_max: float = 180.0,
) -> dict:
    """Analisis satu kanal PPG: buang baseline + BPM autokorelasi + puncak.

    Mengembalikan:
      ac     – sinyal komponen AC (baseline dibuang, LP 5 Hz)
      bpm    – BPM dari autokorelasi (None jika sinyal terlalu pendek/tidak periodik)
      conf   – periodisitas 0–1  (< 0.30 = derau, tidak bermakna)
      peaks  – indeks puncak pada sinyal AC (untuk visualisasi)
    """
    arr = np.asarray(signal, dtype=np.float64)
    if len(arr) < int(fs * 4):
        return {"ac": [], "bpm": None, "conf": 0.0, "peaks": []}

    ac_arr = ac_signal(arr, fs)
    bpm, conf = bpm_autocorr(arr, fs, bpm_min, bpm_max)
    peaks     = _find_peaks_ac(ac_arr, fs, bpm_max)

    return {
        "ac":    [round(float(v), 4) for v in ac_arr],
        "bpm":   bpm,
        "conf":  conf,
        "peaks": peaks,
    }
