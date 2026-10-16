from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from math import sqrt
from typing import Iterable, Mapping, Sequence

import numpy as np

from .bridge import BridgeLearner, Episode
from .event_evidence import evidence_from_audio_event_result
from .events import discover_candidate_units
from .unit_model import (
    FrozenUnitModel,
    OutOfSampleUnitAssignment,
    fit_frozen_unit_model,
    frozen_unit_model_from_dict,
)
from .unit_registry import LocalUnitEvidence, UnitRegistryResult


_REFERENCE_TRANSLATOR_SCHEMA = "UNVTRSLR_REFERENCE_TRANSLATOR_MODEL_V2"
_REFERENCE_TRANSLATOR_CLAIM_CEILING = (
    "OUT_OF_SAMPLE_ACOUSTIC_MATCH_TO_CROSS_SOURCE_"
    "OPERATIONAL_RELATION_WITHIN_REFERENCE_FIXTURES"
)


@dataclass(frozen=True)
class AcousticContextEpisode:
    episode_id: str
    source_id: str
    context: frozenset[str]
    evidence: tuple[LocalUnitEvidence, ...]

    @classmethod
    def build(
        cls,
        episode_id: str,
        source_id: str,
        context: Iterable[str],
        evidence: Iterable[LocalUnitEvidence],
    ) -> "AcousticContextEpisode":
        rows = tuple(evidence)
        if not rows:
            raise ValueError("episode must contain acoustic evidence")
        if any(row.source_id != source_id for row in rows):
            raise ValueError("episode source_id must match every evidence row")
        return cls(
            episode_id=str(episode_id),
            source_id=str(source_id),
            context=frozenset(str(item) for item in context),
            evidence=rows,
        )


@dataclass(frozen=True)
class FrozenSemanticRelation:
    token: str
    atom: str
    support: int
    positive_source_coverage: int
    p_atom_given_token: float
    p_atom_without_token: float
    effect: float
    information_bits: float


@dataclass(frozen=True)
class ReferenceTranslatorModel:
    schema: str
    model_id: str
    claim_ceiling: str
    acoustic_model: FrozenUnitModel
    semantic_min_sources: int
    semantic_min_positive_per_source: int
    semantic_relations: tuple[FrozenSemanticRelation, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ReferenceTranslation:
    status: str
    model_id: str
    acoustic_model_id: str
    source_profile_id: str
    global_units: tuple[str | None, ...]
    relations: tuple[str, ...]
    unresolved_local_units: tuple[str, ...]
    assignments: tuple[OutOfSampleUnitAssignment, ...]


@dataclass(frozen=True)
class SourceCalibrationProfile:
    schema: str
    profile_id: str
    claim_ceiling: str
    translator_model_id: str
    acoustic_model_id: str
    source_id: str
    feature_dimension: int
    calibration_unit_count: int
    center: tuple[float, ...]
    scale: tuple[float, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _relation_positive_counts(
    episodes: Sequence[Episode],
    token: str,
    atom: str,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for episode in episodes:
        if (
            episode.source is not None
            and token in episode.signal
            and atom in episode.context
        ):
            source = str(episode.source)
            counts[source] = counts.get(source, 0) + 1
    return counts


def freeze_operational_relations(
    bridge: BridgeLearner,
    *,
    min_sources: int = 2,
    min_positive_per_source: int = 2,
) -> tuple[FrozenSemanticRelation, ...]:
    """Freeze only relations replicated positively within multiple sources."""
    if min_sources < 2:
        raise ValueError("min_sources must be >= 2")
    if min_positive_per_source < 1:
        raise ValueError("min_positive_per_source must be >= 1")

    tokens = sorted(
        {
            token
            for episode in bridge.episodes
            for token in episode.signal
        }
    )
    relations: list[FrozenSemanticRelation] = []

    for token in tokens:
        inference = bridge.infer(token)
        if inference.status != "OPERATIONAL_RELATION_SUPPORTED":
            continue

        top = inference.candidates[0]
        counts = _relation_positive_counts(
            bridge.episodes,
            token,
            top.atom,
        )
        qualified_sources = {
            source
            for source, count in counts.items()
            if count >= min_positive_per_source
        }
        if len(qualified_sources) < min_sources:
            continue

        relations.append(
            FrozenSemanticRelation(
                token=token,
                atom=top.atom,
                support=top.support,
                positive_source_coverage=len(qualified_sources),
                p_atom_given_token=top.p_atom_given_token,
                p_atom_without_token=top.p_atom_without_token,
                effect=top.effect,
                information_bits=top.information_bits,
            )
        )

    return tuple(relations)


def _translator_model_id(
    acoustic_model_id: str,
    semantic_min_sources: int,
    semantic_min_positive_per_source: int,
    relations: Sequence[FrozenSemanticRelation],
) -> str:
    rows = [
        acoustic_model_id,
        str(int(semantic_min_sources)),
        str(int(semantic_min_positive_per_source)),
    ]
    for relation in sorted(
        relations,
        key=lambda row: (row.token, row.atom),
    ):
        rows.append(
            "|".join(
                [
                    relation.token,
                    relation.atom,
                    str(relation.support),
                    str(relation.positive_source_coverage),
                    repr(relation.p_atom_given_token),
                    repr(relation.p_atom_without_token),
                    repr(relation.effect),
                    repr(relation.information_bits),
                ]
            )
        )
    return "urt2_" + sha256(
        "\n".join(rows).encode("utf-8")
    ).hexdigest()[:12]


def fit_reference_translator(
    episodes: Iterable[AcousticContextEpisode],
    *,
    semantic_min_sources: int = 2,
    semantic_min_positive_per_source: int = 2,
    min_sources: int = 2,
    min_units_per_source: int = 3,
    cluster_distance: float = 0.65,
    scale_floor: float = 0.25,
    match_threshold: float | None = None,
    acoustic_ambiguity_margin: float = 0.15,
    bridge_alpha: float = 0.5,
    bridge_min_support: int = 2,
    bridge_min_probability: float = 0.70,
    bridge_min_effect: float = 0.35,
    bridge_min_information_bits: float = 0.05,
    bridge_ambiguity_margin: float = 0.08,
) -> tuple[ReferenceTranslatorModel, UnitRegistryResult]:
    """Fit acoustic identity first, then ground only frozen global unit IDs."""
    materialized = list(episodes)
    if not materialized:
        raise ValueError("at least one acoustic/context episode is required")
    if semantic_min_sources < 2:
        raise ValueError("semantic_min_sources must be >= 2")
    if semantic_min_positive_per_source < 1:
        raise ValueError("semantic_min_positive_per_source must be >= 1")
    if min_units_per_source < 3:
        raise ValueError(
            "end-to-end translation requires at least three "
            "acoustic contrasts per source"
        )
    episode_ids = [episode.episode_id for episode in materialized]
    if len(episode_ids) != len(set(episode_ids)):
        raise ValueError("training episode_id values must be unique")

    evidence_by_source: dict[str, list[LocalUnitEvidence]] = {}
    for episode in materialized:
        evidence_by_source.setdefault(episode.source_id, []).extend(episode.evidence)
    for source_id, source_rows in evidence_by_source.items():
        vectors = np.asarray([row.vector for row in source_rows], dtype=float)
        if not np.all(np.isfinite(vectors)):
            raise ValueError("training acoustic vectors must be finite")
        distinct = {
            tuple(float(value) for value in row.vector)
            for row in source_rows
        }
        if len(distinct) < min_units_per_source:
            raise ValueError(
                f"source {source_id!r} has fewer than {min_units_per_source} "
                "distinct acoustic states"
            )

    evidence = [
        row
        for episode in materialized
        for row in episode.evidence
    ]
    acoustic_model, registry = fit_frozen_unit_model(
        evidence,
        min_sources=min_sources,
        min_units_per_source=min_units_per_source,
        cluster_distance=cluster_distance,
        scale_floor=scale_floor,
        match_threshold=match_threshold,
        ambiguity_margin=acoustic_ambiguity_margin,
    )

    assignment_by_key = {
        (
            assignment.recording_id,
            assignment.source_id,
            assignment.local_unit_id,
        ): assignment
        for assignment in registry.assignments
    }

    bridge_episodes: list[Episode] = []
    for episode in materialized:
        tokens: list[str] = []
        for row in episode.evidence:
            key = (
                row.recording_id,
                row.source_id,
                row.local_unit_id,
            )
            assignment = assignment_by_key.get(key)
            if assignment is None:
                raise ValueError("training evidence is missing from acoustic registry")
            if (
                assignment.status != "CROSS_SOURCE_UNIT_SUPPORTED"
                or assignment.global_unit_id is None
            ):
                raise ValueError(
                    "training episode contains an acoustic unit that did not "
                    "survive cross-source recurrence qualification"
                )
            tokens.append(assignment.global_unit_id)

        bridge_episodes.append(
            Episode.build(
                tokens,
                episode.context,
                source=episode.source_id,
            )
        )

    bridge = BridgeLearner(
        alpha=bridge_alpha,
        min_support=bridge_min_support,
        min_probability=bridge_min_probability,
        min_effect=bridge_min_effect,
        min_information_bits=bridge_min_information_bits,
        ambiguity_margin=bridge_ambiguity_margin,
    ).fit(bridge_episodes)

    semantic_relations = freeze_operational_relations(
        bridge,
        min_sources=semantic_min_sources,
        min_positive_per_source=semantic_min_positive_per_source,
    )
    if not semantic_relations:
        raise ValueError(
            "no operational relation survived the cross-source semantic gate"
        )

    model_id = _translator_model_id(
        acoustic_model.model_id,
        semantic_min_sources,
        semantic_min_positive_per_source,
        semantic_relations,
    )
    model = ReferenceTranslatorModel(
        schema=_REFERENCE_TRANSLATOR_SCHEMA,
        model_id=model_id,
        claim_ceiling=_REFERENCE_TRANSLATOR_CLAIM_CEILING,
        acoustic_model=acoustic_model,
        semantic_min_sources=semantic_min_sources,
        semantic_min_positive_per_source=semantic_min_positive_per_source,
        semantic_relations=semantic_relations,
    )
    return model, registry


def _evidence_key(row: LocalUnitEvidence) -> tuple[str, str, str]:
    return (row.recording_id, row.source_id, row.local_unit_id)


_SOURCE_PROFILE_SCHEMA = "UNVTRSLR_SOURCE_CALIBRATION_PROFILE_V1"
_SOURCE_PROFILE_CLAIM_CEILING = (
    "SOURCE_NORMALIZATION_PROFILE_ONLY_NO_SEMANTIC_EVIDENCE"
)


def _aggregate_profile_rows(
    evidence: Iterable[LocalUnitEvidence],
) -> list[LocalUnitEvidence]:
    rows = list(evidence)
    if not rows:
        raise ValueError("at least one calibration unit is required")
    sources = {row.source_id for row in rows}
    if len(sources) != 1:
        raise ValueError("source calibration requires exactly one source")

    grouped: dict[tuple[str, str, str], list[np.ndarray]] = {}
    for row in rows:
        key = _evidence_key(row)
        grouped.setdefault(key, []).append(np.asarray(row.vector, dtype=float))

    result: list[LocalUnitEvidence] = []
    for key in sorted(grouped):
        matrix = np.vstack(grouped[key])
        result.append(
            LocalUnitEvidence(
                recording_id=key[0],
                source_id=key[1],
                local_unit_id=key[2],
                vector=tuple(float(v) for v in np.median(matrix, axis=0)),
            )
        )
    return result


def _source_profile_id(
    model: ReferenceTranslatorModel,
    source_id: str,
    calibration_unit_count: int,
    center: Sequence[float],
    scale: Sequence[float],
) -> str:
    payload = "\n".join(
        [
            model.model_id,
            model.acoustic_model.model_id,
            source_id,
            str(int(calibration_unit_count)),
            repr(tuple(float(v) for v in center)),
            repr(tuple(float(v) for v in scale)),
        ]
    )
    return "usp_" + sha256(payload.encode("utf-8")).hexdigest()[:12]


def fit_source_calibration_profile(
    model: ReferenceTranslatorModel,
    evidence: Iterable[LocalUnitEvidence],
) -> SourceCalibrationProfile:
    """Freeze source normalization from calibration evidence only."""
    rows = _aggregate_profile_rows(evidence)
    source_id = rows[0].source_id
    required = model.acoustic_model.min_units_per_source
    if required < 3:
        required = 3
    if len(rows) < required:
        raise ValueError(
            f"source calibration requires at least {required} distinct acoustic units"
        )
    distinct_vectors = {
        tuple(float(value) for value in row.vector)
        for row in rows
    }
    if len(distinct_vectors) < required:
        raise ValueError(
            f"source calibration requires at least {required} distinct acoustic states"
        )

    dimensions = {len(row.vector) for row in rows}
    if dimensions != {model.acoustic_model.feature_dimension}:
        raise ValueError("calibration vector dimension does not match acoustic model")

    matrix = np.vstack([row.vector for row in rows]).astype(float)
    if not np.all(np.isfinite(matrix)):
        raise ValueError("calibration vectors must be finite")

    center = np.median(matrix, axis=0)
    mad = 1.4826 * np.median(np.abs(matrix - center), axis=0)
    spread = np.ptp(matrix, axis=0)
    scale = np.maximum(
        mad,
        np.maximum(
            spread / 4.0,
            model.acoustic_model.scale_floor,
        ),
    )

    profile_id = _source_profile_id(
        model,
        source_id,
        len(rows),
        center,
        scale,
    )
    return SourceCalibrationProfile(
        schema=_SOURCE_PROFILE_SCHEMA,
        profile_id=profile_id,
        claim_ceiling=_SOURCE_PROFILE_CLAIM_CEILING,
        translator_model_id=model.model_id,
        acoustic_model_id=model.acoustic_model.model_id,
        source_id=source_id,
        feature_dimension=model.acoustic_model.feature_dimension,
        calibration_unit_count=len(rows),
        center=tuple(float(v) for v in center),
        scale=tuple(float(v) for v in scale),
    )


def source_calibration_profile_from_dict(
    obj: Mapping,
    model: ReferenceTranslatorModel,
) -> SourceCalibrationProfile:
    profile = SourceCalibrationProfile(
        schema=str(obj["schema"]),
        profile_id=str(obj["profile_id"]),
        claim_ceiling=str(obj["claim_ceiling"]),
        translator_model_id=str(obj["translator_model_id"]),
        acoustic_model_id=str(obj["acoustic_model_id"]),
        source_id=str(obj["source_id"]),
        feature_dimension=int(obj["feature_dimension"]),
        calibration_unit_count=int(obj["calibration_unit_count"]),
        center=tuple(float(v) for v in obj["center"]),
        scale=tuple(float(v) for v in obj["scale"]),
    )
    if profile.schema != _SOURCE_PROFILE_SCHEMA:
        raise ValueError("unsupported source calibration profile schema")
    if profile.claim_ceiling != _SOURCE_PROFILE_CLAIM_CEILING:
        raise ValueError("unsupported source calibration profile claim ceiling")
    if profile.translator_model_id != model.model_id:
        raise ValueError("source profile belongs to a different translator model")
    if profile.acoustic_model_id != model.acoustic_model.model_id:
        raise ValueError("source profile belongs to a different acoustic model")
    if profile.feature_dimension != model.acoustic_model.feature_dimension:
        raise ValueError("source profile feature dimension mismatch")
    required = max(3, model.acoustic_model.min_units_per_source)
    if profile.calibration_unit_count < required:
        raise ValueError("source profile has insufficient calibration contrast")
    if (
        len(profile.center) != profile.feature_dimension
        or len(profile.scale) != profile.feature_dimension
    ):
        raise ValueError("source profile vector dimension mismatch")
    if not np.all(np.isfinite(np.asarray(profile.center, dtype=float))):
        raise ValueError("source profile center must be finite")
    scale = np.asarray(profile.scale, dtype=float)
    if not np.all(np.isfinite(scale)) or np.any(scale <= 0):
        raise ValueError("source profile scale must be finite and positive")

    expected = _source_profile_id(
        model,
        profile.source_id,
        profile.calibration_unit_count,
        profile.center,
        profile.scale,
    )
    if expected != profile.profile_id:
        raise ValueError("source calibration profile integrity check failed")
    return profile


def _assign_query_units(
    model: ReferenceTranslatorModel,
    profile: SourceCalibrationProfile,
    evidence: Iterable[LocalUnitEvidence],
) -> tuple[OutOfSampleUnitAssignment, ...]:
    rows = list(evidence)
    if not rows:
        raise ValueError("at least one query unit is required")
    if any(row.source_id != profile.source_id for row in rows):
        raise ValueError("query source does not match frozen source profile")
    if any(len(row.vector) != profile.feature_dimension for row in rows):
        raise ValueError("query vector dimension does not match source profile")

    center = np.asarray(profile.center, dtype=float)
    scale = np.asarray(profile.scale, dtype=float)
    prototypes = list(model.acoustic_model.prototypes)
    prototype_vectors = np.vstack(
        [prototype.centroid for prototype in prototypes]
    ).astype(float)

    assignments: list[OutOfSampleUnitAssignment] = []
    for row in rows:
        vector = np.asarray(row.vector, dtype=float)
        if not np.all(np.isfinite(vector)):
            raise ValueError("query vectors must be finite")
        normalized = (vector - center) / scale
        distances = (
            np.linalg.norm(prototype_vectors - normalized, axis=1)
            / sqrt(profile.feature_dimension)
        )
        order = np.argsort(distances, kind="stable")
        best_index = int(order[0])
        best = float(distances[best_index])
        second = (
            float(distances[int(order[1])])
            if len(order) > 1
            else None
        )

        if best > model.acoustic_model.match_threshold:
            status = "NO_MATCH_WITHIN_FROZEN_MODEL"
            global_id = None
        elif (
            second is not None
            and (second - best) < model.acoustic_model.ambiguity_margin
        ):
            status = "AMBIGUOUS_FROZEN_MATCH"
            global_id = None
        else:
            status = "FROZEN_MATCH_SUPPORTED"
            global_id = prototypes[best_index].global_unit_id

        assignments.append(
            OutOfSampleUnitAssignment(
                recording_id=row.recording_id,
                source_id=row.source_id,
                local_unit_id=row.local_unit_id,
                global_unit_id=global_id,
                best_distance=best,
                second_best_distance=second,
                status=status,
            )
        )
    return tuple(assignments)


def translate_query_evidence(
    model: ReferenceTranslatorModel,
    profile: SourceCalibrationProfile,
    evidence: Iterable[LocalUnitEvidence],
    *,
    renderer: Mapping[str, str] | None = None,
) -> ReferenceTranslation:
    """Translate query units without allowing them to alter source normalization."""
    profile = source_calibration_profile_from_dict(profile.to_dict(), model)
    rows = list(evidence)
    assignments = _assign_query_units(model, profile, rows)
    relation_by_token = {
        relation.token: relation
        for relation in model.semantic_relations
    }

    global_units: list[str | None] = []
    relations: list[str] = []
    unresolved: list[str] = []

    for row, assignment in zip(rows, assignments):
        label = f"{row.recording_id}:{row.local_unit_id}"
        if (
            assignment.status != "FROZEN_MATCH_SUPPORTED"
            or assignment.global_unit_id is None
        ):
            global_units.append(None)
            unresolved.append(label)
            continue

        global_units.append(assignment.global_unit_id)
        relation = relation_by_token.get(assignment.global_unit_id)
        if relation is None:
            unresolved.append(label)
            continue

        rendered = (
            renderer.get(relation.atom, relation.atom)
            if renderer is not None
            else relation.atom
        )
        if rendered not in relations:
            relations.append(rendered)

    if relations and not unresolved:
        status = "REFERENCE_TRANSLATION_SUPPORTED"
    elif relations:
        status = "PARTIAL_REFERENCE_TRANSLATION"
    else:
        status = "UNRESOLVED"

    return ReferenceTranslation(
        status=status,
        model_id=model.model_id,
        acoustic_model_id=model.acoustic_model.model_id,
        source_profile_id=profile.profile_id,
        global_units=tuple(global_units),
        relations=tuple(relations),
        unresolved_local_units=tuple(unresolved),
        assignments=assignments,
    )


def translate_source_evidence(
    model: ReferenceTranslatorModel,
    calibration_evidence: Iterable[LocalUnitEvidence],
    query_evidence: Iterable[LocalUnitEvidence],
    *,
    renderer: Mapping[str, str] | None = None,
) -> ReferenceTranslation:
    """Convenience wrapper that freezes calibration before evaluating queries."""
    profile = fit_source_calibration_profile(model, calibration_evidence)
    return translate_query_evidence(
        model,
        profile,
        query_evidence,
        renderer=renderer,
    )


def reference_translator_model_from_dict(
    obj: Mapping,
) -> ReferenceTranslatorModel:
    acoustic_model = frozen_unit_model_from_dict(dict(obj["acoustic_model"]))
    relations = tuple(
        FrozenSemanticRelation(
            token=str(row["token"]),
            atom=str(row["atom"]),
            support=int(row["support"]),
            positive_source_coverage=int(row["positive_source_coverage"]),
            p_atom_given_token=float(row["p_atom_given_token"]),
            p_atom_without_token=float(row["p_atom_without_token"]),
            effect=float(row["effect"]),
            information_bits=float(row["information_bits"]),
        )
        for row in obj["semantic_relations"]
    )
    model = ReferenceTranslatorModel(
        schema=str(obj["schema"]),
        model_id=str(obj["model_id"]),
        claim_ceiling=str(obj["claim_ceiling"]),
        acoustic_model=acoustic_model,
        semantic_min_sources=int(obj["semantic_min_sources"]),
        semantic_min_positive_per_source=int(
            obj["semantic_min_positive_per_source"]
        ),
        semantic_relations=relations,
    )
    if model.schema != _REFERENCE_TRANSLATOR_SCHEMA:
        raise ValueError("unsupported reference translator model schema")
    if model.claim_ceiling != _REFERENCE_TRANSLATOR_CLAIM_CEILING:
        raise ValueError("unsupported reference translator claim ceiling")
    if model.semantic_min_sources < 2:
        raise ValueError("persisted semantic source floor must be >= 2")
    if model.semantic_min_positive_per_source < 1:
        raise ValueError(
            "persisted per-source positive evidence floor must be >= 1"
        )
    if not model.semantic_relations:
        raise ValueError("persisted translator has no semantic relations")
    tokens = [relation.token for relation in model.semantic_relations]
    if len(tokens) != len(set(tokens)):
        raise ValueError("persisted translator contains duplicate token relations")
    if any(
        relation.positive_source_coverage < model.semantic_min_sources
        or relation.positive_source_coverage > relation.support
        for relation in model.semantic_relations
    ):
        raise ValueError("persisted semantic relation violates source-coverage gate")
    expected = _translator_model_id(
        model.acoustic_model.model_id,
        model.semantic_min_sources,
        model.semantic_min_positive_per_source,
        model.semantic_relations,
    )
    if expected != model.model_id:
        raise ValueError("reference translator model integrity check failed")
    return model


def prepare_audio_evidence(
    recording_id: str,
    source_id: str,
    samples,
    sample_rate: int,
    **event_kwargs,
) -> tuple[LocalUnitEvidence, ...]:
    """Raw-audio adapter using the exact acoustic/event stages in this lineage."""
    events = discover_candidate_units(
        samples,
        sample_rate,
        **event_kwargs,
    )
    return evidence_from_audio_event_result(
        recording_id,
        source_id,
        samples,
        sample_rate,
        events,
    )
