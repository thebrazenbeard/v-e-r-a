from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import math

import numpy as np
from scipy.fft import dct
from scipy.signal import get_window

_EPS = 1e-12


@dataclass(frozen=True)
class FrameFeatures:
    time_s: float
    rms_db: float
    f0_hz: float | None
    periodicity: float
    spectral_centroid_hz: float
    spectral_bandwidth_hz: float
    spectral_flatness: float
    spectral_rolloff_hz: float
    spectral_slope_db_octave: float
    h1_h2_db: float | None
    mfcc: tuple[float, ...]


def _mono(samples: np.ndarray | Iterable[float]) -> np.ndarray:
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 2:
        x = x.mean(axis=1)
    if x.ndim != 1:
        raise ValueError("samples must be mono or shape (n_samples, n_channels)")
    if x.size == 0:
        raise ValueError("samples must not be empty")
    x = np.nan_to_num(x, copy=False)
    peak = float(np.max(np.abs(x)))
    if peak > 1.0:
        x = x / peak
    return x


def _frames(x: np.ndarray, frame_size: int, hop: int) -> np.ndarray:
    if x.size < frame_size:
        x = np.pad(x, (0, frame_size - x.size))
    n = 1 + max(0, (x.size - frame_size) // hop)
    return np.stack([x[i * hop : i * hop + frame_size] for i in range(n)])


def _estimate_f0(frame: np.ndarray, sr: int, fmin: float, fmax: float) -> tuple[float | None, float]:
    centered = frame - frame.mean()
    energy = float(np.dot(centered, centered))
    if energy < 1e-9:
        return None, 0.0
    corr = np.correlate(centered, centered, mode="full")[len(centered) - 1 :]
    corr /= max(float(corr[0]), _EPS)
    min_lag = max(1, int(sr / fmax))
    max_lag = min(len(corr) - 1, int(sr / fmin))
    if max_lag <= min_lag:
        return None, 0.0
    segment = corr[min_lag : max_lag + 1]
    rel = int(np.argmax(segment))
    lag = min_lag + rel
    periodicity = float(segment[rel])
    if periodicity < 0.25:
        return None, max(0.0, periodicity)
    if 1 <= lag < len(corr) - 1:
        a, b, c = corr[lag - 1], corr[lag], corr[lag + 1]
        denom = a - 2 * b + c
        if abs(denom) > _EPS:
            lag = lag + 0.5 * (a - c) / denom
    return float(sr / lag), periodicity


def _mel(freq_hz):
    return 2595.0 * np.log10(1.0 + np.asarray(freq_hz) / 700.0)


def _inv_mel(mel):
    return 700.0 * (10.0 ** (np.asarray(mel) / 2595.0) - 1.0)


def _mfcc(power: np.ndarray, freqs: np.ndarray, sr: int, n_mels: int = 26, n_coeffs: int = 13) -> tuple[float, ...]:
    mel_points = np.linspace(float(_mel(20.0)), float(_mel(sr / 2.0)), n_mels + 2)
    hz_points = _inv_mel(mel_points)
    energies = []
    for left_hz, center_hz, right_hz in zip(hz_points[:-2], hz_points[1:-1], hz_points[2:]):
        up = (freqs - left_hz) / max(center_hz - left_hz, _EPS)
        down = (right_hz - freqs) / max(right_hz - center_hz, _EPS)
        weights = np.maximum(0.0, np.minimum(up, down))
        energies.append(float(np.sum(power * weights)))
    log_e = np.log(np.maximum(np.asarray(energies), _EPS))
    return tuple(float(v) for v in dct(log_e, type=2, norm="ortho")[:n_coeffs])


def _spectral_slope(freqs: np.ndarray, mag: np.ndarray) -> float:
    mask = (freqs >= 80.0) & (mag > _EPS)
    if np.count_nonzero(mask) < 4:
        return 0.0
    x = np.log2(freqs[mask])
    y = 20.0 * np.log10(mag[mask])
    slope, _ = np.polyfit(x, y, 1)
    return float(slope)


def _harmonic_amplitude(freqs: np.ndarray, mag: np.ndarray, target: float) -> float:
    if target <= 0 or target > freqs[-1]:
        return 0.0
    idx = int(np.argmin(np.abs(freqs - target)))
    return float(np.max(mag[max(0, idx - 1) : min(len(mag), idx + 2)]))


def extract_frame_features(
    samples: np.ndarray | Iterable[float],
    sample_rate: int,
    *,
    frame_ms: float = 40.0,
    hop_ms: float = 10.0,
    fmin: float = 60.0,
    fmax: float = 500.0,
) -> list[FrameFeatures]:
    """Extract interpretable acoustic channels without assuming linguistic units."""
    if sample_rate < 2000:
        raise ValueError("sample_rate is too low for speech-like acoustic analysis")
    x = _mono(samples)
    frame_size = max(64, int(round(sample_rate * frame_ms / 1000.0)))
    hop = max(1, int(round(sample_rate * hop_ms / 1000.0)))
    window = get_window("hann", frame_size, fftbins=True)
    rows: list[FrameFeatures] = []

    for i, frame in enumerate(_frames(x, frame_size, hop)):
        f0, periodicity = _estimate_f0(frame, sample_rate, fmin, fmax)
        rms = math.sqrt(float(np.mean(frame * frame)) + _EPS)
        rms_db = 20.0 * math.log10(max(rms, _EPS))
        spectrum = np.fft.rfft((frame - frame.mean()) * window)
        mag = np.abs(spectrum) + _EPS
        power = mag * mag
        freqs = np.fft.rfftfreq(frame_size, d=1.0 / sample_rate)
        total = float(np.sum(power))
        centroid = float(np.sum(freqs * power) / max(total, _EPS))
        bandwidth = float(np.sqrt(np.sum(((freqs - centroid) ** 2) * power) / max(total, _EPS)))
        flatness = float(np.exp(np.mean(np.log(power + _EPS))) / max(np.mean(power), _EPS))
        cdf = np.cumsum(power)
        roll_idx = int(np.searchsorted(cdf, 0.85 * cdf[-1]))
        rolloff = float(freqs[min(roll_idx, len(freqs) - 1)])
        slope = _spectral_slope(freqs, mag)
        h1_h2 = None
        if f0 is not None:
            h1 = _harmonic_amplitude(freqs, mag, f0)
            h2 = _harmonic_amplitude(freqs, mag, 2.0 * f0)
            if h1 > _EPS and h2 > _EPS:
                h1_h2 = float(20.0 * np.log10(h1 / h2))
        rows.append(
            FrameFeatures(
                time_s=(i * hop + frame_size / 2) / sample_rate,
                rms_db=rms_db,
                f0_hz=f0,
                periodicity=float(periodicity),
                spectral_centroid_hz=centroid,
                spectral_bandwidth_hz=bandwidth,
                spectral_flatness=flatness,
                spectral_rolloff_hz=rolloff,
                spectral_slope_db_octave=slope,
                h1_h2_db=h1_h2,
                mfcc=_mfcc(power, freqs, sample_rate),
            )
        )
    return rows


def _summary(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"median": None, "iqr": None, "mean": None, "std": None}
    a = np.asarray(values, dtype=np.float64)
    q25, q75 = np.quantile(a, [0.25, 0.75])
    return {
        "median": float(np.median(a)),
        "iqr": float(q75 - q25),
        "mean": float(np.mean(a)),
        "std": float(np.std(a)),
    }


def _trajectory_stats(values: np.ndarray) -> dict[str, float | None]:
    if values.size < 2:
        return {"slope": None, "curvature": None, "range": None}
    t = np.linspace(-1.0, 1.0, values.size)
    curvature = float(np.polyfit(t, values, 2)[0]) if values.size >= 3 else None
    return {
        "slope": float(np.polyfit(t, values, 1)[0]),
        "curvature": curvature,
        "range": float(np.max(values) - np.min(values)),
    }


def acoustic_fingerprint(samples: np.ndarray | Iterable[float], sample_rate: int) -> dict:
    """Return a source-relative multidimensional acoustic fingerprint."""
    rows = extract_frame_features(samples, sample_rate)
    f0 = np.asarray([r.f0_hz for r in rows if r.f0_hz is not None], dtype=np.float64)
    f0_semitones = np.asarray([], dtype=np.float64)
    if f0.size:
        anchor = float(np.median(f0))
        f0_semitones = 12.0 * np.log2(f0 / anchor)

    rms = [r.rms_db for r in rows]
    centroid = [r.spectral_centroid_hz for r in rows]
    bandwidth = [r.spectral_bandwidth_hz for r in rows]
    flatness = [r.spectral_flatness for r in rows]
    rolloff = [r.spectral_rolloff_hz for r in rows]
    slope = [r.spectral_slope_db_octave for r in rows]
    h1h2 = [r.h1_h2_db for r in rows if r.h1_h2_db is not None]
    periodicity = [r.periodicity for r in rows]
    mfcc_matrix = np.asarray([r.mfcc for r in rows], dtype=np.float64)
    mfcc_summary = []
    if mfcc_matrix.size:
        for i in range(mfcc_matrix.shape[1]):
            mfcc_summary.append({"index": i, **_summary(mfcc_matrix[:, i].tolist())})

    envelope = 10.0 ** (np.asarray(rms) / 20.0)
    envelope = envelope - np.mean(envelope)
    peak_mod_hz = None
    if envelope.size >= 8:
        mod_freqs = np.fft.rfftfreq(envelope.size, d=0.010)
        mod_power = np.abs(np.fft.rfft(envelope)) ** 2
        band = (mod_freqs >= 0.5) & (mod_freqs <= 12.0)
        if np.any(band):
            band_freqs = mod_freqs[band]
            band_power = mod_power[band]
            peak_mod_hz = float(band_freqs[int(np.argmax(band_power))])

    return {
        "schema": "UNVTRSLR_ACOUSTIC_FINGERPRINT_V1",
        "claim_ceiling": "ACOUSTIC_STRUCTURE_ONLY_NO_SEMANTIC_QUALIFICATION",
        "frame_count": len(rows),
        "voiced_frame_fraction": float(len(f0) / max(len(rows), 1)),
        "channels": {
            "pitch_raw_hz": _summary(f0.tolist()),
            "pitch_relative_semitones": {**_summary(f0_semitones.tolist()), **_trajectory_stats(f0_semitones)},
            "intensity_db": {**_summary(rms), **_trajectory_stats(np.asarray(rms))},
            "periodicity": _summary(periodicity),
            "spectral_centroid_hz": _summary(centroid),
            "spectral_bandwidth_hz": _summary(bandwidth),
            "spectral_flatness": _summary(flatness),
            "spectral_rolloff_hz": _summary(rolloff),
            "spectral_slope_db_octave": _summary(slope),
            "h1_h2_db": _summary(h1h2),
            "mfcc": mfcc_summary,
            "envelope_modulation_peak_hz": peak_mod_hz,
        },
    }
