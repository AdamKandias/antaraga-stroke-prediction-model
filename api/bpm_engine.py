"""
Port Python dari algoritma BPM firmware ANTARAGA (Firmware/src/bpm.cpp).

Masukan : deretan sampel ADC SON1303 mentah pada laju tetap fs Hz.
Keluaran: dict berisi bpm, conf, status, ibi_list, sdnn_ms, peaks, dll.

Filter: sosfilt KAUSAL dengan semai DC (zi * sig[0]), identik perilakunya
dengan firmware - tidak ada transien awal, tidak ada artefak edge.
sosfiltfilt (zero-phase) SENGAJA dihindari karena transiennya membuat
env_hi melonjak di awal dan menyebabkan banyak puncak terlewat.

Semua konstanta numerik identik dengan Firmware/include/config.h.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.signal import butter, sosfilt, sosfilt_zi

# ── Konstanta (cermin config.h) ───────────────────────────────────────────
_HP_HZ            = 0.5
_LP_HZ            = 5.0
_DC_HZ            = 0.1
_THR_HI           = 0.60
_THR_LO           = 0.40
_ENV_DECAY_S      = 0.6
_BPM_MIN          = 30.0
_BPM_MAX          = 220.0
_REFRACT_MS       = 260.0
_EXC_MAX_MS       = 600.0
_IBI_DEV_PCT      = 30.0
_IBI_HIST         = 8
_MIN_BEATS        = 4
_MISSED_TOL_PCT   = 20.0
_MISSED_FIX       = True
_RESYNC_REJECTS   = 4
_AC_MIN_LSB       = 15.0
_PI_MIN_PERMIL    = 3.0
_PI_GOOD_LO       = 10.0
_PI_GOOD_HI       = 400.0
_PI_MAX_PERMIL    = 800.0
_STAB_GOOD_PERMIL = 50.0
_STAB_MAX_PERMIL  = 250.0
_CLIP_MAX_N       = 2
_MIN_CONF         = 50
_SAT_LEVEL        = 4090
_FLOOR_LEVEL      = 5


def _band_score(v: float, fv: float, lo: float, hi: float, cv: float) -> int:
    if v <= fv or v >= cv:
        return 0
    if lo <= v <= hi:
        return 100
    if v < lo:
        return int(100.0 * (v - fv) / (lo - fv))
    return int(100.0 * (cv - v) / (cv - hi))


def _decay_score(v: float, good: float, max_v: float) -> int:
    if v <= good:
        return 100
    if v >= max_v:
        return 0
    return int(100.0 - 100.0 * (v - good) / (max_v - good))


def compute_bpm(raw: list, fs: float = 200.0) -> dict:
    """
    Hitung BPM dari sampel ADC SON1303 mentah menggunakan algoritma firmware.

    Mengembalikan:
      bpm         – BPM dari median IBI (float atau None)
      conf        – skor keyakinan 0–100 (minimum 4 sub-skor)
      status      – "LOCKED" / "NOISY" / "SEARCHING" / "TERLALU_PENDEK"
      ibi_list    – daftar IBI yang diterima (ms), berguna untuk HRV
      ibi_med_ms  – median IBI (ms)
      sdnn_ms     – SDNN: simpangan baku riwayat IBI (HRV kasar)
      beats       – jumlah denyut yang diterima
      rejects     – jumlah interval yang ditolak gerbang IBI
      peaks       – indeks sampel puncak (relatif terhadap `raw`)
      filtered    – sinyal setelah band-pass (untuk debug/chart)
    """
    _empty: dict = {
        "bpm": None, "conf": 0, "status": "TERLALU_PENDEK",
        "ibi_list": [], "ibi_med_ms": None, "sdnn_ms": None,
        "beats": 0, "rejects": 0, "peaks": [], "filtered": [],
    }
    n = len(raw)
    if n < int(fs * 1.5):   # butuh minimal 1.5 detik
        return _empty

    sig = np.asarray(raw, dtype=float)
    ms  = 1000.0 / fs

    # ── 1. Band-pass Butterworth 0.5–5 Hz (kausal, semai DC) ─────────────
    # Pakai sosfilt kausal (bukan sosfiltfilt) dengan inisialisasi zi * sig[0]:
    # filter dianggap sudah memproses DC = sig[0] selamanya → keluaran mulai
    # dari nol tanpa transien. Ini persis perilaku firmware (causal, real-time).
    # sosfiltfilt SENGAJA dihindari: transiennya melonjak env_hi sehingga
    # thr_hi menjadi terlalu tinggi dan banyak puncak terlewat.
    sos_hp = butter(2, _HP_HZ / (fs / 2), btype="high", output="sos")
    sos_lp = butter(2, _LP_HZ / (fs / 2), btype="low",  output="sos")
    hp, _  = sosfilt(sos_hp, sig, zi=sosfilt_zi(sos_hp) * sig[0])
    filt, _ = sosfilt(sos_lp, hp,  zi=sosfilt_zi(sos_lp) * hp[0])

    # ── Baseline DC (one-pole, identik dengan firmware) ───────────────────
    alpha  = 1.0 - math.exp(-2.0 * math.pi * _DC_HZ / fs)
    dc_val = float(sig[0])
    dc_arr = np.empty(n)
    for i, x in enumerate(sig.tolist()):
        dc_val += alpha * (x - dc_val)
        dc_arr[i] = dc_val

    # ── 2. Pelacak amplitudo (serangan seketika, peluruhan lambat) ────────
    # Inisialisasi dari 1 detik pertama: analog dengan settle period firmware.
    # Tanpa ini, env_lo = 0 (belum lihat nilai negatif) → thr_lo terlalu tinggi
    # → eksursi pertama dianggap terlalu panjang dan dibuang.
    env_decay = _ENV_DECAY_S / fs
    warmup_n  = min(int(fs), n)
    env_hi    = float(np.max(filt[:warmup_n]))
    env_lo    = float(np.min(filt[:warmup_n]))

    # ── 3+4. Eksursi berhisteresis + maks lokal + interpolasi parabola ───
    refract_n = int(_REFRACT_MS * fs / 1000.0)
    exc_max_n = int(_EXC_MAX_MS * fs / 1000.0)

    in_exc     = False
    exc_start  = 0
    have_max   = False
    max_val = max_prev = max_next = 0.0
    max_idx    = 0
    s1 = s2    = float(filt[0])

    have_prev   = False
    prev_idx    = 0
    prev_frac   = 0.0
    last_peak_n = -refract_n   # supaya blanking tidak aktif di awal

    # ── 5. Gerbang interval IBI ───────────────────────────────────────────
    ibi_min_ms = 60000.0 / _BPM_MAX
    ibi_max_ms = 60000.0 / _BPM_MIN

    ibi_buf      : list[float] = []
    reject_run   = 0
    accepted_ibi : list[float] = []
    disp_peaks   : list[int]   = []
    beat_count   = 0
    reject_count = 0

    for i, s in enumerate(filt.tolist()):
        # update pelacak amplitudo
        # env_lo hanya diperbarui di LUAR eksursi (fase diastolik):
        # selama sistol, sinyal selalu di atas env_lo sehingga env_lo merayap naik
        # dan menggelembungkan thr_hi - puncak berikutnya jadi tak terjangkau.
        # Firmware tidak punya masalah ini karena beroperasi menerus (menit/jam)
        # dan env_lo selalu pulih saat diastol panjang antar batch.
        amp_p = env_hi - env_lo
        if s > env_hi:   env_hi  = s
        else:            env_hi -= amp_p * env_decay
        if not in_exc:   # env_lo hanya update saat diastol
            if s < env_lo: env_lo  = s
            else:          env_lo += amp_p * env_decay
        if env_hi < env_lo:
            mid = 0.5 * (env_hi + env_lo)
            env_hi = env_lo = mid

        amp    = env_hi - env_lo
        thr_hi = env_lo + _THR_HI * amp
        thr_lo = env_lo + _THR_LO * amp

        if not in_exc:
            blanked = (i - last_peak_n) < refract_n
            if amp >= _AC_MIN_LSB and s >= thr_hi and not blanked:
                in_exc    = True
                exc_start = i
                have_max  = False
                max_val   = 0.0
        else:
            # uji maks lokal pada s2 (sampel i-1)
            if i >= 2 and s2 > s1 and s2 >= s and (not have_max or s2 > max_val):
                max_val  = s2
                max_idx  = i - 1
                max_prev = s1
                max_next = s
                have_max = True

            too_long = (i - exc_start) > exc_max_n
            if s < thr_lo or too_long:
                if have_max and not too_long:
                    # interpolasi parabola tiga titik
                    frac = 0.0
                    den  = max_prev - 2.0 * max_val + max_next
                    if den < -1e-6:
                        frac = 0.5 * (max_prev - max_next) / den
                        frac = max(-0.5, min(0.5, frac))

                    last_peak_n = max_idx

                    if not have_prev:
                        # puncak pertama: jadi acuan, belum ada IBI
                        have_prev = True
                        prev_idx  = max_idx
                        prev_frac = frac
                        beat_count += 1
                        disp_peaks.append(max_idx)
                    else:
                        ibi = (float(max_idx - prev_idx) + (frac - prev_frac)) * ms
                        ok  = False

                        if ibi_min_ms <= ibi <= ibi_max_ms:
                            if len(ibi_buf) < 3:
                                ibi_buf.append(ibi)
                                ok = True
                            else:
                                hist = ibi_buf[-_IBI_HIST:]
                                med  = float(np.median(hist))
                                tol  = med * (_IBI_DEV_PCT / 100.0)
                                if abs(ibi - med) <= tol:
                                    ibi_buf.append(ibi)
                                    ok = True
                                elif _MISSED_FIX:
                                    half = ibi * 0.5
                                    if abs(half - med) <= med * (_MISSED_TOL_PCT / 100.0):
                                        ibi_buf.extend([half, half])
                                        ok = True

                        if ok:
                            accepted_ibi.append(ibi)
                            beat_count += 1
                            reject_run  = 0
                            disp_peaks.append(max_idx)
                        else:
                            reject_count += 1
                            reject_run   += 1
                            if reject_run >= _RESYNC_REJECTS:
                                ibi_buf.clear()
                                reject_run = 0

                        prev_idx  = max_idx
                        prev_frac = frac

                in_exc = False

        s1 = s2
        s2 = s

    # ── 6. BPM + statistik ────────────────────────────────────────────────
    recent = ibi_buf[-_IBI_HIST:]

    if len(recent) >= _MIN_BEATS:
        med_ibi = float(np.median(recent))
        bpm     = round(60000.0 / med_ibi, 1)
        sdnn    = float(np.std(recent, ddof=0))
        mad     = float(np.mean(np.abs(np.array(recent) - med_ibi)))
        stab_pm = (mad / med_ibi * 1000.0) if med_ibi > 0 else 1000.0
    else:
        med_ibi = bpm = sdnn = None
        stab_pm = 1000.0

    # ── Skor keyakinan = minimum 4 sub-skor ──────────────────────────────
    dc_mean   = float(np.mean(dc_arr))
    amp_final = env_hi - env_lo
    pi_pm     = (amp_final * 1000.0 / dc_mean) if dc_mean > 1.0 else 0.0
    clip_n    = int(np.sum((sig >= _SAT_LEVEL) | (sig <= _FLOOR_LEVEL)))

    s_fill = int(len(recent) * 100 / _IBI_HIST)
    s_stab = _decay_score(stab_pm, _STAB_GOOD_PERMIL, _STAB_MAX_PERMIL) if recent else 0
    s_perf = _band_score(pi_pm, _PI_MIN_PERMIL, _PI_GOOD_LO, _PI_GOOD_HI, _PI_MAX_PERMIL)
    s_clip = 100 if clip_n == 0 else (50 if clip_n <= _CLIP_MAX_N else 0)
    conf   = min(s_fill, s_stab, s_perf, s_clip)

    if bpm is None:
        status = "SEARCHING"
    elif conf < _MIN_CONF:
        status = "NOISY"
    else:
        status = "LOCKED"

    return {
        "bpm":        bpm,
        "conf":        conf,
        "status":      status,
        "ibi_list":    [round(v, 1) for v in accepted_ibi],
        "ibi_med_ms":  round(med_ibi, 1) if med_ibi is not None else None,
        "sdnn_ms":     round(sdnn, 2)    if sdnn    is not None else None,
        "beats":       beat_count,
        "rejects":     reject_count,
        "peaks":       disp_peaks,
        "filtered":    [round(float(v), 2) for v in filt],
    }
