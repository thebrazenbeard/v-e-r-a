from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .acoustics import FrameFeatures, extract_frame_features


_EPS = 1e-9


@dataclass(frozen=True)
class CandidateEvent:
    start_s: float
    end_s: float
    vector: tuple[float, ...]
    boundary_score_before: float | None


@dataclass(frozen=True)
class UnitAssignment:
    event_index: int
    unit_id: str
    distance_to_prototype: float


@dataclass(frozen=True)
class EventDiscoveryResult:
    schema: str
    claim_ceiling: str
    events: tuple[CandidateEvent, ...]
    units: tuple[UnitAssignment, ...]
    boundary_scores: tuple[float, ...]


def _robust_scale(matrix: np.ndarray) -> np.ndarray:
    median = np.median(matrix, axis=0)
    mad = np.median(np.abs(matrix - median), axis=0)
    scale = 1.4826 * mad
    # Never let near-constant numerical/phase variation become a giant novelty
    # signal. Floors are expressed in the native feature coordinates below and
    # act as an explicit minimum effect size, not as learned semantic weights.
    floors = np.asarray([
        0.75,  # source-relative pitch, semitones
        1.5,   # RMS dB
        0.08,  # log spectral centroid
        0.08,  # log spectral bandwidth
        0.02,  # spectral flatness
        2.0,   # spectral slope dB/octave
        0.05,  # periodicity
        2.0, 2.0, 2.0, 2.0,  # MFCC 1..4
    ], dtype=float)
    scale = np.maximum(scale, floors)
    return (matrix - median) / scale


def _frame_matrix(rows: list[FrameFeatures]) -> np.ndarray:
    voiced = np.asarray([r.f0_hz for r in rows if r.f0_hz is not None], dtype=float)
    f0_anchor = float(np.median(voiced)) if voiced.size else 1.0

    raw = []
    for r in rows:
        pitch = 0.0 if r.f0_hz is None else 12.0 * np.log2(max(r.f0_hz, _EPS) / f0_anchor)
        raw.append(
            [
                pitch,
                r.rms_db,
                np.log(max(r.spectral_centroid_hz, 1.0)),
                np.log(max(r.spectral_bandwidth_hz, 1.0)),
                r.spectral_flatness,
                r.spectral_slope_db_octave,
                r.periodicity,
                *r.mfcc[1:5],
            ]
        )
    return _robust_scale(np.asarray(raw, dtype=float))


def _novelty(matrix: np.ndarray, radius: int) -> np.ndarray:
    n = len(matrix)
    scores = np.zeros(n, dtype=float)
    if n < 2 * radius + 1:
        return scores
    denom = np.sqrt(matrix.shape[1])
    for i in range(radius, n - radius):
        left = np.median(matrix[i - radius : i], axis=0)
        right = np.median(matrix[i : i + radius], axis=0)
        scores[i] = float(np.linalg.norm(right - left) / max(denom, _EPS))
    return scores


def _pick_boundaries(scores: np.ndarray, threshold: float, min_gap_frames: int) -> list[int]:
    if len(scores) < 3:
        return []
    candidates = [
        i
        for i in range(1, len(scores) - 1)
        if scores[i] >= threshold and scores[i] >= scores[i - 1] and scores[i] >= scores[i + 1]
    ]
    chosen: list[int] = []
    for i in sorted(candidates, key=lambda j: (-scores[j], j)):
        if all(abs(i - j) >= min_gap_frames for j in chosen):
            chosen.append(i)
    return sorted(chosen)


def discover_events_from_frames(
    rows: Iterable[FrameFeatures],
    *,
    hop_s: float = 0.010,
    context_radius_frames: int = 4,
    novelty_threshold: float = 1.15,
    min_event_s: float = 0.12,
    cluster_distance: float = 1.35,
) -> EventDiscoveryResult:
    materialized = list(rows)
    if not materialized:
        raise ValueError("at least one frame is required")
    if context_radius_frames < 1:
        raise ValueError("context_radius_frames must be >= 1")

    matrix = _frame_matrix(materialized)
    scores = _novelty(matrix, context_radius_frames)
    min_gap = max(1, int(round(min_event_s / hop_s)))
    boundaries = _pick_boundaries(scores, novelty_threshold, min_gap)

    cuts = [0, *boundaries, len(materialized)]
    events: list[CandidateEvent] = []
    for event_index, (a, b) in enumerate(zip(cuts[:-1], cuts[1:])):
        if b <= a:
            continue
        vector = tuple(float(v) for v in np.median(matrix[a:b], axis=0))
        score_before = None if event_index == 0 else float(scores[a])
        events.append(
            CandidateEvent(
                start_s=float(a * hop_s),
                end_s=float(b * hop_s),
                vector=vector,
                boundary_score_before=score_before,
            )
        )

    assignments = _cluster_events(events, threshold=cluster_distance)
    return EventDiscoveryResult(
        schema="UNVTRSLR_CANDIDATE_EVENT_DISCOVERY_V1",
        claim_ceiling="ACOUSTIC_EVENT_HYPOTHESES_ONLY_NO_LINGUISTIC_SEGMENTATION",
        events=tuple(events),
        units=tuple(assignments),
        boundary_scores=tuple(float(v) for v in scores),
    )


def _cluster_events(events: list[CandidateEvent], *, threshold: float) -> list[UnitAssignment]:
    prototypes: list[np.ndarray] = []
    counts: list[int] = []
    assignments: list[UnitAssignment] = []

    for index, event in enumerate(events):
        vector = np.asarray(event.vector, dtype=float)
        if not prototypes:
            prototypes.append(vector.copy())
            counts.append(1)
            assignments.append(UnitAssignment(index, "u0", 0.0))
            continue

        distances = np.asarray(
            [np.linalg.norm(vector - p) / np.sqrt(len(vector)) for p in prototypes],
            dtype=float,
        )
        best = int(np.argmin(distances))
        distance = float(distances[best])
        if distance > threshold:
            best = len(prototypes)
            prototypes.append(vector.copy())
            counts.append(1)
            distance = 0.0
        else:
            count = counts[best]
            prototypes[best] = (prototypes[best] * count + vector) / (count + 1)
            counts[best] = count + 1
        assignments.append(UnitAssignment(index, f"u{best}", distance))

    return assignments


def discover_candidate_units(
    samples: np.ndarray | Iterable[float],
    sample_rate: int,
    **kwargs,
) -> EventDiscoveryResult:
    rows = extract_frame_features(samples, sample_rate)
    return discover_events_from_frames(rows, **kwargs)
