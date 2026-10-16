from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from hashlib import sha256
from math import sqrt
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class LocalUnitEvidence:
    recording_id: str
    source_id: str
    local_unit_id: str
    vector: tuple[float, ...]


@dataclass(frozen=True)
class GlobalUnitAssignment:
    recording_id: str
    source_id: str
    local_unit_id: str
    global_unit_id: str | None
    distance_to_centroid: float | None
    source_coverage: int
    status: str


@dataclass(frozen=True)
class UnitRegistryResult:
    schema: str
    claim_ceiling: str
    assignments: tuple[GlobalUnitAssignment, ...]
    eligible_source_count: int
    excluded_source_count: int

    def to_dict(self) -> dict:
        return asdict(self)


def evidence_from_event_result(
    recording_id: str,
    source_id: str,
    result,
) -> tuple[LocalUnitEvidence, ...]:
    """Aggregate recording-local recurrence IDs into one vector per local unit.

    Local IDs from event discovery are evidence keys only. They are not assumed
    to have any identity outside the recording that produced them.
    """
    events = list(result.events)
    assignments = list(result.units)
    grouped: dict[str, list[np.ndarray]] = defaultdict(list)

    for assignment in assignments:
        index = int(assignment.event_index)
        if index < 0 or index >= len(events):
            raise ValueError("unit assignment event_index is out of range")
        grouped[str(assignment.unit_id)].append(
            np.asarray(events[index].vector, dtype=float)
        )

    rows: list[LocalUnitEvidence] = []
    for local_unit_id in sorted(grouped):
        matrix = np.vstack(grouped[local_unit_id])
        rows.append(
            LocalUnitEvidence(
                recording_id=recording_id,
                source_id=source_id,
                local_unit_id=local_unit_id,
                vector=tuple(
                    float(v) for v in np.median(matrix, axis=0)
                ),
            )
        )
    return tuple(rows)


def _aggregate(
    evidence: Sequence[LocalUnitEvidence],
) -> list[LocalUnitEvidence]:
    grouped: dict[
        tuple[str, str, str], list[np.ndarray]
    ] = defaultdict(list)

    for row in evidence:
        grouped[
            (row.recording_id, row.source_id, row.local_unit_id)
        ].append(np.asarray(row.vector, dtype=float))

    result: list[LocalUnitEvidence] = []
    for (
        recording_id,
        source_id,
        local_unit_id,
    ), vectors in grouped.items():
        matrix = np.vstack(vectors)
        result.append(
            LocalUnitEvidence(
                recording_id=recording_id,
                source_id=source_id,
                local_unit_id=local_unit_id,
                vector=tuple(
                    float(v) for v in np.median(matrix, axis=0)
                ),
            )
        )

    result.sort(
        key=lambda r: (
            r.source_id,
            r.recording_id,
            r.local_unit_id,
        )
    )
    return result


def _normalize_by_source(
    evidence: Sequence[LocalUnitEvidence],
    *,
    min_units_per_source: int,
    scale_floor: float,
) -> tuple[
    dict[tuple[str, str, str], np.ndarray],
    set[str],
    set[str],
]:
    by_source: dict[str, list[LocalUnitEvidence]] = defaultdict(list)
    for row in evidence:
        by_source[row.source_id].append(row)

    normalized: dict[
        tuple[str, str, str], np.ndarray
    ] = {}
    eligible: set[str] = set()

    for source_id, rows in by_source.items():
        unique_units = {
            (r.recording_id, r.local_unit_id)
            for r in rows
        }
        if len(unique_units) < min_units_per_source:
            continue

        matrix = np.vstack([r.vector for r in rows])
        median = np.median(matrix, axis=0)
        mad = (
            1.4826
            * np.median(
                np.abs(matrix - median),
                axis=0,
            )
        )
        spread = np.ptp(matrix, axis=0)
        scale = np.maximum(
            mad,
            np.maximum(
                spread / 4.0,
                scale_floor,
            ),
        )

        eligible.add(source_id)
        for row in rows:
            key = (
                row.recording_id,
                row.source_id,
                row.local_unit_id,
            )
            normalized[key] = (
                np.asarray(row.vector, dtype=float)
                - median
            ) / scale

    return (
        normalized,
        eligible,
        set(by_source) - eligible,
    )


def _complete_link_clusters(
    keys: Sequence[tuple[str, str, str]],
    vectors: np.ndarray,
    threshold: float,
) -> list[list[int]]:
    clusters: list[list[int]] = [
        [i] for i in range(len(keys))
    ]
    dimensions = vectors.shape[1]

    def max_distance(
        left: list[int],
        right: list[int],
    ) -> float:
        return max(
            float(
                np.linalg.norm(
                    vectors[i] - vectors[j]
                )
                / sqrt(dimensions)
            )
            for i in left
            for j in right
        )

    while True:
        candidates: list[
            tuple[tuple, int, int]
        ] = []

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                distance = max_distance(
                    clusters[i],
                    clusters[j],
                )
                if distance <= threshold:
                    signature = (
                        distance,
                        tuple(
                            keys[k]
                            for k in clusters[i]
                        ),
                        tuple(
                            keys[k]
                            for k in clusters[j]
                        ),
                    )
                    candidates.append(
                        (signature, i, j)
                    )

        if not candidates:
            break

        _, i, j = min(
            candidates,
            key=lambda item: item[0],
        )
        merged = sorted(
            clusters[i] + clusters[j],
            key=lambda k: keys[k],
        )
        clusters = [
            cluster
            for index, cluster in enumerate(clusters)
            if index not in (i, j)
        ]
        clusters.append(merged)
        clusters.sort(
            key=lambda cluster: tuple(
                keys[k] for k in cluster
            )
        )

    return clusters


def _stable_registry_id(
    member_keys: Sequence[
        tuple[str, str, str]
    ],
) -> str:
    payload = "\n".join(
        "|".join(parts)
        for parts in sorted(member_keys)
    ).encode("utf-8")
    return (
        "g_"
        + sha256(payload).hexdigest()[:10]
    )


def build_unit_registry(
    evidence: Iterable[LocalUnitEvidence],
    *,
    min_sources: int = 2,
    min_units_per_source: int = 2,
    cluster_distance: float = 0.65,
    scale_floor: float = 0.25,
) -> UnitRegistryResult:
    """Promote local acoustic recurrence only when it survives source contrast.

    This routine performs deterministic complete-link clustering in a
    source-normalized feature space. It intentionally refuses to treat a
    recording-local ID as globally meaningful merely because the string matches.
    """
    rows = _aggregate(list(evidence))
    if not rows:
        raise ValueError(
            "at least one local unit is required"
        )

    dimensions = {
        len(row.vector) for row in rows
    }
    if (
        len(dimensions) != 1
        or next(iter(dimensions)) == 0
    ):
        raise ValueError(
            "all local unit vectors must have "
            "the same non-zero dimension"
        )
    if min_sources < 2:
        raise ValueError(
            "min_sources must be >= 2 for "
            "cross-source promotion"
        )
    if min_units_per_source < 2:
        raise ValueError(
            "min_units_per_source must be >= 2"
        )
    if (
        cluster_distance <= 0
        or scale_floor <= 0
    ):
        raise ValueError(
            "cluster_distance and scale_floor "
            "must be > 0"
        )

    (
        normalized,
        eligible_sources,
        excluded_sources,
    ) = _normalize_by_source(
        rows,
        min_units_per_source=min_units_per_source,
        scale_floor=scale_floor,
    )

    eligible_rows = [
        row
        for row in rows
        if row.source_id in eligible_sources
    ]
    dimension = next(iter(dimensions))

    if eligible_rows:
        keys = [
            (
                row.source_id,
                row.recording_id,
                row.local_unit_id,
            )
            for row in eligible_rows
        ]
        vectors = np.vstack(
            [
                normalized[
                    (
                        row.recording_id,
                        row.source_id,
                        row.local_unit_id,
                    )
                ]
                for row in eligible_rows
            ]
        )
        clusters = _complete_link_clusters(
            keys,
            vectors,
            cluster_distance,
        )
    else:
        keys = []
        vectors = np.empty(
            (0, dimension),
            dtype=float,
        )
        clusters = []

    cluster_by_index: dict[
        int,
        tuple[list[int], int, np.ndarray],
    ] = {}
    promoted_ids: dict[int, str] = {}

    for cluster in clusters:
        source_coverage = len(
            {
                eligible_rows[i].source_id
                for i in cluster
            }
        )
        centroid = np.mean(
            vectors[cluster],
            axis=0,
        )

        for i in cluster:
            cluster_by_index[i] = (
                cluster,
                source_coverage,
                centroid,
            )

        if source_coverage >= min_sources:
            global_id = _stable_registry_id(
                [keys[i] for i in cluster]
            )
            for i in cluster:
                promoted_ids[i] = global_id

    eligible_index = {
        (
            row.recording_id,
            row.source_id,
            row.local_unit_id,
        ): i
        for i, row in enumerate(eligible_rows)
    }

    assignments: list[
        GlobalUnitAssignment
    ] = []

    for row in rows:
        key = (
            row.recording_id,
            row.source_id,
            row.local_unit_id,
        )

        if row.source_id not in eligible_sources:
            assignments.append(
                GlobalUnitAssignment(
                    recording_id=row.recording_id,
                    source_id=row.source_id,
                    local_unit_id=row.local_unit_id,
                    global_unit_id=None,
                    distance_to_centroid=None,
                    source_coverage=1,
                    status=(
                        "INSUFFICIENT_SOURCE_CONTRAST"
                    ),
                )
            )
            continue

        i = eligible_index[key]
        (
            _cluster,
            source_coverage,
            centroid,
        ) = cluster_by_index[i]

        distance = float(
            np.linalg.norm(
                vectors[i] - centroid
            )
            / sqrt(dimension)
        )
        global_id = promoted_ids.get(i)
        status = (
            "CROSS_SOURCE_UNIT_SUPPORTED"
            if global_id is not None
            else "SOURCE_LOCAL_ONLY"
        )

        assignments.append(
            GlobalUnitAssignment(
                recording_id=row.recording_id,
                source_id=row.source_id,
                local_unit_id=row.local_unit_id,
                global_unit_id=global_id,
                distance_to_centroid=distance,
                source_coverage=source_coverage,
                status=status,
            )
        )

    assignments.sort(
        key=lambda a: (
            a.source_id,
            a.recording_id,
            a.local_unit_id,
        )
    )

    return UnitRegistryResult(
        schema=(
            "UNVTRSLR_CROSS_RECORDING_"
            "UNIT_REGISTRY_V1"
        ),
        claim_ceiling=(
            "CROSS_RECORDING_ACOUSTIC_"
            "RECURRENCE_ONLY_NO_SEMANTIC_IDENTITY"
        ),
        assignments=tuple(assignments),
        eligible_source_count=len(
            eligible_sources
        ),
        excluded_source_count=len(
            excluded_sources
        ),
    )
