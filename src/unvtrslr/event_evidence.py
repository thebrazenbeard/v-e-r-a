from __future__ import annotations

from collections import defaultdict
from math import log
from typing import Iterable

import numpy as np

from .unit_registry import LocalUnitEvidence


def _median(
    values,
    default: float = 0.0,
) -> float:
    materialized = [
        float(value)
        for value in values
        if value is not None
        and np.isfinite(value)
    ]
    return (
        float(np.median(materialized))
        if materialized
        else float(default)
    )


def _event_descriptor(
    frames,
) -> tuple[float, ...]:
    frames = list(frames)
    if not frames:
        raise ValueError(
            "candidate event has no "
            "supporting acoustic frames"
        )

    f0 = np.asarray(
        [
            float(row.f0_hz)
            for row in frames
            if row.f0_hz is not None
            and row.f0_hz > 0
        ],
        dtype=float,
    )

    if f0.size:
        log_f0 = np.log2(f0)
        pitch_log2 = float(
            np.median(log_f0)
        )
        pitch_range_st = float(
            12.0
            * (
                np.max(log_f0)
                - np.min(log_f0)
            )
        )
    else:
        pitch_log2 = 0.0
        pitch_range_st = 0.0

    voiced_fraction = float(
        len(f0) / len(frames)
    )

    mfcc = np.asarray(
        [row.mfcc for row in frames],
        dtype=float,
    )
    mfcc_tail: list[float] = []

    for index in range(1, 5):
        mfcc_tail.append(
            float(
                np.median(
                    mfcc[:, index]
                )
            )
            if mfcc.shape[1] > index
            else 0.0
        )

    return (
        pitch_log2,
        pitch_range_st,
        voiced_fraction,
        _median(
            row.rms_db
            for row in frames
        ),
        log(
            max(
                _median(
                    (
                        row.spectral_centroid_hz
                        for row in frames
                    ),
                    1.0,
                ),
                1.0,
            )
        ),
        log(
            max(
                _median(
                    (
                        row.spectral_bandwidth_hz
                        for row in frames
                    ),
                    1.0,
                ),
                1.0,
            )
        ),
        _median(
            row.spectral_flatness
            for row in frames
        ),
        _median(
            row.spectral_slope_db_octave
            for row in frames
        ),
        _median(
            row.periodicity
            for row in frames
        ),
        _median(
            (
                row.h1_h2_db
                for row in frames
            ),
            0.0,
        ),
        *mfcc_tail,
    )


def evidence_from_event_frames(
    recording_id: str,
    source_id: str,
    frames: Iterable,
    event_result,
) -> tuple[
    LocalUnitEvidence,
    ...,
]:
    """Build raw-measurement descriptors for recording-local event units.

    PR #8's normalized event vectors remain untouched and continue to serve
    boundary/within-recording recurrence discovery. This adapter creates an
    additional raw acoustic view for cross-recording identity testing.
    """
    frame_rows = list(frames)
    grouped: dict[
        str,
        list[tuple[float, ...]],
    ] = defaultdict(list)

    events = list(
        event_result.events
    )

    for assignment in event_result.units:
        index = int(
            assignment.event_index
        )

        if (
            index < 0
            or index >= len(events)
        ):
            raise ValueError(
                "unit assignment "
                "event_index is out of range"
            )

        event = events[index]

        supporting = [
            row
            for row in frame_rows
            if float(event.start_s)
            <= float(row.time_s)
            < float(event.end_s)
        ]

        grouped[
            str(assignment.unit_id)
        ].append(
            _event_descriptor(
                supporting
            )
        )

    evidence: list[
        LocalUnitEvidence
    ] = []

    for local_unit_id in sorted(
        grouped
    ):
        matrix = np.asarray(
            grouped[local_unit_id],
            dtype=float,
        )

        evidence.append(
            LocalUnitEvidence(
                recording_id=(
                    recording_id
                ),
                source_id=source_id,
                local_unit_id=(
                    local_unit_id
                ),
                vector=tuple(
                    float(value)
                    for value in np.median(
                        matrix,
                        axis=0,
                    )
                ),
            )
        )

    return tuple(evidence)


def evidence_from_audio_event_result(
    recording_id: str,
    source_id: str,
    samples,
    sample_rate: int,
    event_result,
) -> tuple[
    LocalUnitEvidence,
    ...,
]:
    """Reuse PR #6 frame extraction on raw audio without replacing PR #8 data."""
    from .acoustics import (
        extract_frame_features,
    )

    frames = extract_frame_features(
        samples,
        sample_rate,
    )

    return evidence_from_event_frames(
        recording_id,
        source_id,
        frames,
        event_result,
    )
