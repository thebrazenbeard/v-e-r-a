from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from math import sqrt
from typing import Iterable

import numpy as np

from .unit_registry import (
    LocalUnitEvidence,
    UnitRegistryResult,
    _aggregate,
    _normalize_by_source,
    build_unit_registry,
)


@dataclass(frozen=True)
class FrozenUnitPrototype:
    global_unit_id: str
    centroid: tuple[float, ...]
    training_members: int
    source_coverage: int


@dataclass(frozen=True)
class FrozenUnitModel:
    schema: str
    model_id: str
    claim_ceiling: str
    feature_dimension: int
    min_units_per_source: int
    scale_floor: float
    match_threshold: float
    ambiguity_margin: float
    prototypes: tuple[FrozenUnitPrototype, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class OutOfSampleUnitAssignment:
    recording_id: str
    source_id: str
    local_unit_id: str
    global_unit_id: str | None
    best_distance: float | None
    second_best_distance: float | None
    status: str


def _model_id(
    prototypes: list[FrozenUnitPrototype],
    config: tuple,
) -> str:
    parts = [repr(config)]
    for proto in prototypes:
        parts.append(
            f"{proto.global_unit_id}|"
            f"{proto.centroid}|"
            f"{proto.training_members}|"
            f"{proto.source_coverage}"
        )
    return (
        "urm_"
        + sha256(
            "\n".join(parts).encode("utf-8")
        ).hexdigest()[:12]
    )


def fit_frozen_unit_model(
    evidence: Iterable[LocalUnitEvidence],
    *,
    min_sources: int = 2,
    min_units_per_source: int = 2,
    cluster_distance: float = 0.65,
    scale_floor: float = 0.25,
    match_threshold: float | None = None,
    ambiguity_margin: float = 0.15,
) -> tuple[
    FrozenUnitModel,
    UnitRegistryResult,
]:
    rows = _aggregate(list(evidence))

    registry = build_unit_registry(
        rows,
        min_sources=min_sources,
        min_units_per_source=(
            min_units_per_source
        ),
        cluster_distance=cluster_distance,
        scale_floor=scale_floor,
    )

    normalized, eligible, _ = (
        _normalize_by_source(
            rows,
            min_units_per_source=(
                min_units_per_source
            ),
            scale_floor=scale_floor,
        )
    )

    by_key = {
        (
            a.recording_id,
            a.source_id,
            a.local_unit_id,
        ): a
        for a in registry.assignments
    }

    vectors_by_global: dict[
        str,
        list[np.ndarray],
    ] = {}
    sources_by_global: dict[
        str,
        set[str],
    ] = {}

    for row in rows:
        key = (
            row.recording_id,
            row.source_id,
            row.local_unit_id,
        )
        assignment = by_key[key]

        if (
            assignment.global_unit_id is None
            or row.source_id not in eligible
        ):
            continue

        vectors_by_global.setdefault(
            assignment.global_unit_id,
            [],
        ).append(normalized[key])

        sources_by_global.setdefault(
            assignment.global_unit_id,
            set(),
        ).add(row.source_id)

    prototypes: list[
        FrozenUnitPrototype
    ] = []

    for global_id in sorted(
        vectors_by_global
    ):
        matrix = np.vstack(
            vectors_by_global[global_id]
        )
        prototypes.append(
            FrozenUnitPrototype(
                global_unit_id=global_id,
                centroid=tuple(
                    float(v)
                    for v in np.mean(
                        matrix,
                        axis=0,
                    )
                ),
                training_members=len(matrix),
                source_coverage=len(
                    sources_by_global[
                        global_id
                    ]
                ),
            )
        )

    if not prototypes:
        raise ValueError(
            "training evidence produced no "
            "cross-source-supported prototypes"
        )

    dimension = len(
        prototypes[0].centroid
    )
    threshold = (
        cluster_distance
        if match_threshold is None
        else float(match_threshold)
    )
    config = (
        dimension,
        min_units_per_source,
        scale_floor,
        threshold,
        ambiguity_margin,
    )

    model = FrozenUnitModel(
        schema=(
            "UNVTRSLR_FROZEN_"
            "UNIT_MODEL_V1"
        ),
        model_id=_model_id(
            prototypes,
            config,
        ),
        claim_ceiling=(
            "OUT_OF_SAMPLE_ACOUSTIC_"
            "RECURRENCE_MATCH_ONLY_"
            "NO_SEMANTIC_IDENTITY"
        ),
        feature_dimension=dimension,
        min_units_per_source=(
            min_units_per_source
        ),
        scale_floor=scale_floor,
        match_threshold=threshold,
        ambiguity_margin=float(
            ambiguity_margin
        ),
        prototypes=tuple(prototypes),
    )

    return model, registry


def assign_source_units(
    model: FrozenUnitModel,
    evidence: Iterable[LocalUnitEvidence],
) -> tuple[
    OutOfSampleUnitAssignment,
    ...,
]:
    rows = _aggregate(list(evidence))
    if not rows:
        raise ValueError(
            "at least one local unit is required"
        )

    sources = {
        row.source_id for row in rows
    }
    if len(sources) != 1:
        raise ValueError(
            "assign_source_units requires "
            "evidence from exactly one source"
        )

    dimensions = {
        len(row.vector) for row in rows
    }
    if dimensions != {
        model.feature_dimension
    }:
        raise ValueError(
            "evidence vector dimension does "
            "not match frozen model"
        )

    normalized, eligible, _ = (
        _normalize_by_source(
            rows,
            min_units_per_source=(
                model.min_units_per_source
            ),
            scale_floor=model.scale_floor,
        )
    )

    source_id = next(iter(sources))
    if source_id not in eligible:
        return tuple(
            OutOfSampleUnitAssignment(
                recording_id=(
                    row.recording_id
                ),
                source_id=row.source_id,
                local_unit_id=(
                    row.local_unit_id
                ),
                global_unit_id=None,
                best_distance=None,
                second_best_distance=None,
                status=(
                    "INSUFFICIENT_"
                    "SOURCE_CONTRAST"
                ),
            )
            for row in rows
        )

    prototypes = list(
        model.prototypes
    )
    proto_vectors = np.vstack(
        [
            prototype.centroid
            for prototype in prototypes
        ]
    )

    result: list[
        OutOfSampleUnitAssignment
    ] = []

    for row in rows:
        key = (
            row.recording_id,
            row.source_id,
            row.local_unit_id,
        )
        vector = normalized[key]

        distances = (
            np.linalg.norm(
                proto_vectors - vector,
                axis=1,
            )
            / sqrt(
                model.feature_dimension
            )
        )
        order = np.argsort(
            distances,
            kind="stable",
        )

        best_index = int(order[0])
        best = float(
            distances[best_index]
        )
        second = (
            float(
                distances[
                    int(order[1])
                ]
            )
            if len(order) > 1
            else None
        )

        if (
            best
            > model.match_threshold
        ):
            status = (
                "NO_MATCH_WITHIN_"
                "FROZEN_MODEL"
            )
            global_id = None

        elif (
            second is not None
            and (second - best)
            < model.ambiguity_margin
        ):
            status = (
                "AMBIGUOUS_FROZEN_MATCH"
            )
            global_id = None

        else:
            status = (
                "FROZEN_MATCH_SUPPORTED"
            )
            global_id = prototypes[
                best_index
            ].global_unit_id

        result.append(
            OutOfSampleUnitAssignment(
                recording_id=(
                    row.recording_id
                ),
                source_id=row.source_id,
                local_unit_id=(
                    row.local_unit_id
                ),
                global_unit_id=global_id,
                best_distance=best,
                second_best_distance=second,
                status=status,
            )
        )

    result.sort(
        key=lambda a: (
            a.recording_id,
            a.local_unit_id,
        )
    )
    return tuple(result)


def frozen_unit_model_from_dict(
    obj: dict,
) -> FrozenUnitModel:
    """Reconstruct a frozen model from its JSON-compatible dictionary form."""
    prototypes = tuple(
        FrozenUnitPrototype(
            global_unit_id=str(
                row["global_unit_id"]
            ),
            centroid=tuple(
                float(v)
                for v in row["centroid"]
            ),
            training_members=int(
                row["training_members"]
            ),
            source_coverage=int(
                row["source_coverage"]
            ),
        )
        for row in obj["prototypes"]
    )

    model = FrozenUnitModel(
        schema=str(obj["schema"]),
        model_id=str(obj["model_id"]),
        claim_ceiling=str(
            obj["claim_ceiling"]
        ),
        feature_dimension=int(
            obj["feature_dimension"]
        ),
        min_units_per_source=int(
            obj["min_units_per_source"]
        ),
        scale_floor=float(
            obj["scale_floor"]
        ),
        match_threshold=float(
            obj["match_threshold"]
        ),
        ambiguity_margin=float(
            obj["ambiguity_margin"]
        ),
        prototypes=prototypes,
    )

    if (
        model.schema
        != "UNVTRSLR_FROZEN_"
        "UNIT_MODEL_V1"
    ):
        raise ValueError(
            "unsupported frozen unit "
            "model schema"
        )

    if any(
        len(prototype.centroid)
        != model.feature_dimension
        for prototype in model.prototypes
    ):
        raise ValueError(
            "prototype dimension does "
            "not match frozen model"
        )

    expected = _model_id(
        list(model.prototypes),
        (
            model.feature_dimension,
            model.min_units_per_source,
            model.scale_floor,
            model.match_threshold,
            model.ambiguity_margin,
        ),
    )

    if expected != model.model_id:
        raise ValueError(
            "frozen unit model integrity "
            "check failed"
        )

    return model
