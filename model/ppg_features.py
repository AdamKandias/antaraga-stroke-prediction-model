"""Pulse Wave Analysis (PWA): turns a raw multi-wavelength PPG segment into
the morphology features the vitals-estimation MLP consumes.

This is deliberately a classic signal-processing pipeline (bandpass filter ->
pulse detection -> per-pulse morphology -> aggregate over the window), not a
learned feature extractor: it has no parameters that need training data, so
it can be built and unit-tested with synthetic signals today, ahead of having
any real calibration data from the ANTARAGA prototype.

Expected input: a few seconds (recommend >= 8s) of one or more PPG channels
(green from SON1303, red/infrared from MAX30102) sampled at a constant rate.
"""

from dataclasses import dataclass

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

MIN_HEART_RATE_BPM = 40
MAX_HEART_RATE_BPM = 180


@dataclass
class PulseEvent:
    onset_idx: int
    peak_idx: int
    amplitude: float
    crest_time_s: float
    pulse_width_50_s: float


def bandpass_filter(signal: np.ndarray, fs: float, low_hz: float = 0.5, high_hz: float = 8.0, order: int = 3) -> np.ndarray:
    """Keeps the cardiac pulse band, removes baseline drift and high-freq noise."""
    nyquist = fs / 2
    b, a = butter(order, [low_hz / nyquist, high_hz / nyquist], btype="band")
    return filtfilt(b, a, signal)


def detect_pulses(filtered: np.ndarray, fs: float) -> list[PulseEvent]:
    """Finds systolic peaks, then the pulse onset (the preceding local minimum)
    for each one, and computes basic per-pulse morphology features."""
    min_distance = int(fs * 60 / MAX_HEART_RATE_BPM)
    peaks, _ = find_peaks(filtered, distance=max(min_distance, 1))

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


def _channel_features(raw: np.ndarray, fs: float, prefix: str) -> dict:
    raw = np.asarray(raw, dtype=float)
    filtered = bandpass_filter(raw, fs)
    pulses = detect_pulses(filtered, fs)

    if len(pulses) < 2:
        # Not enough clean pulses in this window -- caller should treat the
        # whole reading as unreliable rather than trust noisy aggregates.
        return {f"{prefix}_n_pulses": len(pulses)}

    intervals_s = np.diff([p.peak_idx for p in pulses]) / fs
    heart_rate_bpm = 60.0 / np.mean(intervals_s)

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
    multi-wavelength fusion (SON1303 green + MAX30102 red/infrared)."""
    features: dict = {}

    channels = {"green": green, "red": red, "infrared": infrared}
    for name, signal in channels.items():
        if signal is not None and len(signal) > 0:
            features.update(_channel_features(np.array(signal), fs, name))

    if "green_amplitude_mean" in features and "red_amplitude_mean" in features:
        features["green_red_amplitude_ratio"] = (
            features["green_amplitude_mean"] / features["red_amplitude_mean"]
        )
    if "red_amplitude_mean" in features and "infrared_amplitude_mean" in features:
        features["red_infrared_amplitude_ratio"] = (
            features["red_amplitude_mean"] / features["infrared_amplitude_mean"]
        )

    return features
