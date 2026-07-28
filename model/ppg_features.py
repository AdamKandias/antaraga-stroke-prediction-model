"""Pulse Wave Analysis (PWA): turns a raw multi-wavelength PPG segment into
the morphology features the vitals-estimation MLP consumes.

This is deliberately a classic signal-processing pipeline (bandpass filter ->
pulse detection -> per-pulse morphology -> aggregate over the window), not a
learned feature extractor: it has no parameters that need training data, so
it can be built and unit-tested with synthetic signals today, ahead of having
any real calibration data from the ANTARAGA prototype.

Expected input: a few seconds (recommend >= 8s) of one or more PPG channels
(green from SON1303, red/infrared from MAX30102) sampled at a constant rate.

BPM estimation uses Welch spectral method (same approach as the firmware
reference scripts) rather than peak-counting — it is more robust on short
or noisy windows and has no hard BPM ceiling from the min-distance constraint.
"""

from dataclasses import dataclass

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks, welch

MIN_HEART_RATE_BPM = 40
MAX_HEART_RATE_BPM = 200

# HR frequency band: 40–200 BPM = 0.67–3.33 Hz
_HR_BAND_LO = 0.67
_HR_BAND_HI = 3.33


@dataclass
class PulseEvent:
    onset_idx: int
    peak_idx: int
    amplitude: float
    crest_time_s: float
    pulse_width_50_s: float


def bandpass_filter(signal: np.ndarray, fs: float, low_hz: float = 0.5, high_hz: float = 12.0, order: int = 4) -> np.ndarray:
    """Keeps the cardiac pulse band, removes baseline drift and high-freq noise.
    Cutoff 12 Hz (matches firmware reference scripts) preserves dicrotic notch."""
    nyquist = fs / 2
    high_hz = min(high_hz, nyquist * 0.95)  # guard against fs too low
    b, a = butter(order, [low_hz / nyquist, high_hz / nyquist], btype="band")
    return filtfilt(b, a, signal)


def bpm_from_spectrum(filtered: np.ndarray, fs: float) -> float | None:
    """Welch-based heart rate — mirrors firmware reference scripts (plot_ppg_*.py).

    Uses power spectral density instead of peak-counting so it is robust to
    noise and short windows.  Returns None when the signal is too short or the
    dominant frequency outside the physiological HR band."""
    min_samples = int(fs * 4)  # need >= 4 s for reliable spectral resolution
    if len(filtered) < min_samples:
        return None
    nperseg = min(len(filtered), int(fs * 8))
    freqs, psd = welch(filtered, fs=fs, nperseg=nperseg)
    band = (freqs >= _HR_BAND_LO) & (freqs <= _HR_BAND_HI)
    if not band.any():
        return None
    dominant_hz = freqs[band][np.argmax(psd[band])]
    return float(dominant_hz * 60.0)


def detect_pulses(filtered: np.ndarray, fs: float, invert: bool = False) -> list[PulseEvent]:
    """Finds systolic peaks, then the pulse onset (the preceding local minimum)
    for each one, and computes basic per-pulse morphology features.

    invert=True flips the signal before peak detection — required for reflective
    PPG channels (RED / IR from MAX30102) where systole causes a dip, not a peak.
    Prominence threshold (0.4 × std) matches the firmware reference scripts."""
    sig = -filtered if invert else filtered
    min_distance = int(fs * 60 / MAX_HEART_RATE_BPM)
    prominence = float(np.std(sig) * 0.4)
    peaks, _ = find_peaks(sig, distance=max(min_distance, 1), prominence=prominence)

    events: list[PulseEvent] = []
    for i, peak_idx in enumerate(peaks):
        window_start = peaks[i - 1] if i > 0 else max(0, peak_idx - int(fs * 60 / MIN_HEART_RATE_BPM))
        segment = filtered[window_start:peak_idx + 1]
        if segment.size < 2:
            continue
        onset_offset = int(np.argmin(segment))
        onset_idx = window_start + onset_offset

        baseline = filtered[onset_idx]
        amplitude = float(filtered[peak_idx] - baseline)
        if amplitude <= 0:
            continue

        crest_time_s = (peak_idx - onset_idx) / fs

        half_height = baseline + amplitude / 2
        pulse_width_50_s = _half_amplitude_width(filtered, onset_idx, peak_idx, half_height, fs)

        events.append(
            PulseEvent(
                onset_idx=onset_idx,
                peak_idx=peak_idx,
                amplitude=amplitude,
                crest_time_s=crest_time_s,
                pulse_width_50_s=pulse_width_50_s,
            )
        )
    return events


def _half_amplitude_width(filtered: np.ndarray, onset_idx: int, peak_idx: int, half_height: float, fs: float) -> float:
    """Width of the pulse at half its amplitude (rising edge to next descent
    below half_height, or end of signal if the pulse is cut off)."""
    rising = onset_idx
    while rising < peak_idx and filtered[rising] < half_height:
        rising += 1

    falling = peak_idx
    end = min(len(filtered) - 1, peak_idx + (peak_idx - onset_idx) * 2)
    while falling < end and filtered[falling] > half_height:
        falling += 1

    return (falling - rising) / fs


def _channel_features(raw: np.ndarray, fs: float, prefix: str, invert: bool = False) -> dict:
    raw = np.asarray(raw, dtype=float)
    filtered = bandpass_filter(raw, fs)
    pulses = detect_pulses(filtered, fs, invert=invert)

    # Primary BPM: Welch spectrum (robust, mirrors firmware approach).
    # Fall back to inter-peak interval only when spectral method fails.
    heart_rate_bpm = bpm_from_spectrum(filtered, fs)
    if heart_rate_bpm is None and len(pulses) >= 2:
        intervals_s = np.diff([p.peak_idx for p in pulses]) / fs
        heart_rate_bpm = 60.0 / float(np.mean(intervals_s))

    if len(pulses) < 2:
        result = {f"{prefix}_n_pulses": len(pulses)}
        if heart_rate_bpm is not None:
            result[f"{prefix}_heart_rate_bpm"] = float(heart_rate_bpm)
        return result

    amplitudes = np.array([p.amplitude for p in pulses])
    crest_times = np.array([p.crest_time_s for p in pulses])
    widths_50 = np.array([p.pulse_width_50_s for p in pulses])

    return {
        f"{prefix}_n_pulses": len(pulses),
        f"{prefix}_heart_rate_bpm": float(heart_rate_bpm),
        f"{prefix}_amplitude_mean": float(np.mean(amplitudes)),
        f"{prefix}_amplitude_std": float(np.std(amplitudes)),
        f"{prefix}_crest_time_mean_s": float(np.mean(crest_times)),
        f"{prefix}_pulse_width_50_mean_s": float(np.mean(widths_50)),
        f"{prefix}_dc_mean": float(np.mean(raw)),
    }


def extract_pwa_features(
    fs: float,
    green: list[float] | None = None,
    red: list[float] | None = None,
    infrared: list[float] | None = None,
) -> dict:
    """Combines per-channel morphology features with cross-channel ratios
    (same idea as SpO2's R-ratio) that take advantage of ANTARAGA's
    multi-wavelength fusion (SON1303 green + MAX30102 red/infrared).

    RED and IR from MAX30102 are reflective sensors where systole causes a
    dip (not a peak), so invert=True is passed for those channels."""
    features: dict = {}

    # SON1303 green: transmissive — peaks are real peaks, no inversion needed.
    # MAX30102 red/IR: reflective — systole = dip → must invert before peak detection.
    channel_config = [
        ("green", green, False),
        ("red", red, True),
        ("infrared", infrared, True),
    ]
    for name, signal, invert in channel_config:
        if signal is not None and len(signal) > 0:
            features.update(_channel_features(np.array(signal), fs, name, invert=invert))

    if "green_amplitude_mean" in features and "red_amplitude_mean" in features:
        features["green_red_amplitude_ratio"] = (
            features["green_amplitude_mean"] / features["red_amplitude_mean"]
        )
    if "red_amplitude_mean" in features and "infrared_amplitude_mean" in features:
        features["red_infrared_amplitude_ratio"] = (
            features["red_amplitude_mean"] / features["infrared_amplitude_mean"]
        )

    return features
