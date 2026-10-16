import math

import numpy as np

from unvtrslr.acoustics import acoustic_fingerprint, extract_frame_features
from unvtrslr.information import conditional_mutual_information, mutual_information

SR = 16000


def tone(freq=220.0, seconds=1.0, amp=0.5):
    t = np.arange(int(SR * seconds)) / SR
    return amp * np.sin(2 * np.pi * freq * t)


def chirp(f0, f1, seconds=1.0, amp=0.5):
    t = np.arange(int(SR * seconds)) / SR
    k = (f1 - f0) / seconds
    phase = 2 * np.pi * (f0 * t + 0.5 * k * t * t)
    return amp * np.sin(phase)


def harmonic_tone(f0=180.0, bright=False, seconds=1.0):
    t = np.arange(int(SR * seconds)) / SR
    if bright:
        return (
            0.25 * np.sin(2 * np.pi * f0 * t)
            + 0.30 * np.sin(2 * np.pi * 3 * f0 * t)
            + 0.25 * np.sin(2 * np.pi * 6 * f0 * t)
        )
    return (
        0.55 * np.sin(2 * np.pi * f0 * t)
        + 0.18 * np.sin(2 * np.pi * 2 * f0 * t)
        + 0.08 * np.sin(2 * np.pi * 3 * f0 * t)
    )


def test_f0_estimator_tracks_known_pitch():
    rows = extract_frame_features(tone(220.0), SR)
    f0 = np.array([r.f0_hz for r in rows if r.f0_hz is not None])
    assert len(f0) > 50
    assert abs(np.median(f0) - 220.0) < 3.0


def test_relative_pitch_is_speaker_scale_resistant_for_same_contour():
    low = acoustic_fingerprint(chirp(110.0, 220.0), SR)
    high = acoustic_fingerprint(chirp(220.0, 440.0), SR)
    a = low["channels"]["pitch_relative_semitones"]
    b = high["channels"]["pitch_relative_semitones"]
    assert a["slope"] > 0
    assert b["slope"] > 0
    assert abs(a["range"] - b["range"]) < 0.8


def test_pitch_contour_direction_is_preserved():
    rising = acoustic_fingerprint(chirp(140.0, 280.0), SR)
    falling = acoustic_fingerprint(chirp(280.0, 140.0), SR)
    assert rising["channels"]["pitch_relative_semitones"]["slope"] > 0
    assert falling["channels"]["pitch_relative_semitones"]["slope"] < 0


def test_timbre_changes_without_changing_fundamental():
    dark = acoustic_fingerprint(harmonic_tone(bright=False), SR)
    bright = acoustic_fingerprint(harmonic_tone(bright=True), SR)
    f0a = dark["channels"]["pitch_raw_hz"]["median"]
    f0b = bright["channels"]["pitch_raw_hz"]["median"]
    assert abs(f0a - f0b) < 4.0
    ca = dark["channels"]["spectral_centroid_hz"]["median"]
    cb = bright["channels"]["spectral_centroid_hz"]["median"]
    assert cb > ca * 1.5


def test_amplitude_scale_does_not_move_pitch_or_spectral_centroid_much():
    a = acoustic_fingerprint(tone(200, amp=0.2), SR)
    b = acoustic_fingerprint(tone(200, amp=0.8), SR)
    assert abs(a["channels"]["pitch_raw_hz"]["median"] - b["channels"]["pitch_raw_hz"]["median"]) < 2.0
    assert abs(a["channels"]["spectral_centroid_hz"]["median"] - b["channels"]["spectral_centroid_hz"]["median"]) < 10.0
    assert b["channels"]["intensity_db"]["median"] > a["channels"]["intensity_db"]["median"]


def test_mutual_information_finds_perfect_discrete_channel():
    x = ["low", "low", "high", "high"] * 8
    y = ["A", "A", "B", "B"] * 8
    assert math.isclose(mutual_information(x, y), 1.0, abs_tol=1e-9)


def test_conditional_mi_removes_speaker_only_correlation():
    x = ["low", "low", "high", "high"] * 8
    speaker = ["s1", "s1", "s2", "s2"] * 8
    meaning = ["A", "A", "B", "B"] * 8
    assert mutual_information(x, meaning) > 0.9
    assert math.isclose(conditional_mutual_information(x, meaning, speaker), 0.0, abs_tol=1e-9)


def test_constant_channel_has_zero_information():
    assert mutual_information(["same"] * 20, list("AABB" * 5)) == 0.0
