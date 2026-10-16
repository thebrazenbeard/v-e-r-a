from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Iterable, Mapping, Sequence

from .calibration_qualification import (
    QualifiedSourceProfile,
    translate_qualified_query,
)
from .translator import ReferenceTranslatorModel
from .unit_registry import LocalUnitEvidence


_CONSTRUCTION_SCHEMA = "UNVTRSLR_TARGET_CONSTRUCTION_MODEL_V1"
_CONSTRUCTION_CLAIM_CEILING = (
    "MULTIWORD_TARGET_CONSTRUCTION_WITHIN_GROUNDED_REFERENCE_SCOPE"
)


@dataclass(frozen=True)
class TargetConstructionEpisode:
    episode_id: str
    source_id: str
    semantic_atoms: tuple[str, ...]
    target_tokens: tuple[str, ...]

    @classmethod
    def build(
        cls,
        episode_id: str,
        source_id: str,
        semantic_atoms: Iterable[str],
        target_tokens: Iterable[str],
    ) -> "TargetConstructionEpisode":
        atoms = tuple(str(atom) for atom in semantic_atoms)
        tokens = tuple(str(token) for token in target_tokens)
        if not str(episode_id):
            raise ValueError("episode_id must not be empty")
        if not str(source_id):
            raise ValueError("source_id must not be empty")
        if not atoms:
            raise ValueError("construction episode must contain semantic atoms")
        if not tokens:
            raise ValueError("construction episode must contain target tokens")
        if any(not atom for atom in atoms):
            raise ValueError("semantic atoms must not be empty")
        if any(not token for token in tokens):
            raise ValueError("target tokens must not be empty")
        return cls(
            episode_id=str(episode_id),
            source_id=str(source_id),
            semantic_atoms=atoms,
            target_tokens=tokens,
        )


@dataclass(frozen=True)
class FrozenTargetConstruction:
    semantic_atoms: tuple[str, ...]
    target_tokens: tuple[str, ...]
    support: int
    source_coverage: int


@dataclass(frozen=True)
class TargetConstructionModel:
    schema: str
    model_id: str
    claim_ceiling: str
    target_language_id: str
    upstream_model_ids: tuple[str, ...]
    semantic_atoms: tuple[str, ...]
    min_sources: int
    min_positive_per_source: int
    constructions: tuple[FrozenTargetConstruction, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class TargetConstructionRendering:
    semantic_atoms: tuple[str, ...]
    status: str
    realizations: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class OperationalSemanticSequence:
    status: str
    atoms: tuple[str, ...]
    unresolved_positions: tuple[int, ...]


@dataclass(frozen=True)
class QualifiedConstructionTranslation:
    semantic_sequence: OperationalSemanticSequence
    target: TargetConstructionRendering


def _construction_model_id(
    *,
    target_language_id: str,
    upstream_model_ids: Sequence[str],
    semantic_atoms: Sequence[str],
    min_sources: int,
    min_positive_per_source: int,
    constructions: Sequence[FrozenTargetConstruction],
) -> str:
    parts = [
        str(target_language_id),
        repr(tuple(upstream_model_ids)),
        repr(tuple(semantic_atoms)),
        str(int(min_sources)),
        str(int(min_positive_per_source)),
    ]
    for row in sorted(
        constructions,
        key=lambda item: (item.semantic_atoms, item.target_tokens),
    ):
        parts.append(
            "|".join(
                [
                    repr(tuple(row.semantic_atoms)),
                    repr(tuple(row.target_tokens)),
                    str(row.support),
                    str(row.source_coverage),
                ]
            )
        )
    return "utc_" + sha256(
        "\n".join(parts).encode("utf-8")
    ).hexdigest()[:12]


def fit_target_construction_model(
    episodes: Iterable[TargetConstructionEpisode],
    *,
    target_language_id: str,
    semantic_atoms: Iterable[str],
    upstream_model_ids: Iterable[str],
    min_sources: int = 2,
    min_positive_per_source: int = 2,
) -> TargetConstructionModel:
    rows = list(episodes)
    if not rows:
        raise ValueError("at least one construction episode is required")
    if not str(target_language_id):
        raise ValueError("target_language_id must not be empty")
    if min_sources < 2:
        raise ValueError("min_sources must be >= 2")
    if min_positive_per_source < 1:
        raise ValueError("min_positive_per_source must be >= 1")

    namespace = tuple(sorted({str(atom) for atom in semantic_atoms}))
    if not namespace:
        raise ValueError("semantic_atoms must not be empty")
    namespace_set = set(namespace)

    upstream = tuple(sorted({str(value) for value in upstream_model_ids}))
    if not upstream or any(not value for value in upstream):
        raise ValueError("upstream_model_ids must contain nonempty IDs")

    episode_ids = [row.episode_id for row in rows]
    if len(episode_ids) != len(set(episode_ids)):
        raise ValueError("construction episode_id values must be unique")

    for row in rows:
        unknown = set(row.semantic_atoms) - namespace_set
        if unknown:
            raise ValueError(
                "construction episode references atoms outside semantic namespace: "
                f"{sorted(unknown)!r}"
            )

    grouped: dict[
        tuple[tuple[str, ...], tuple[str, ...]],
        list[TargetConstructionEpisode],
    ] = {}
    for row in rows:
        key = (row.semantic_atoms, row.target_tokens)
        grouped.setdefault(key, []).append(row)

    frozen: list[FrozenTargetConstruction] = []
    for (pattern, target), group in sorted(grouped.items()):
        by_source: dict[str, int] = {}
        for row in group:
            by_source[row.source_id] = by_source.get(row.source_id, 0) + 1
        qualified_sources = {
            source
            for source, count in by_source.items()
            if count >= min_positive_per_source
        }
        if len(qualified_sources) < min_sources:
            continue
        frozen.append(
            FrozenTargetConstruction(
                semantic_atoms=pattern,
                target_tokens=target,
                support=len(group),
                source_coverage=len(qualified_sources),
            )
        )

    if not frozen:
        raise ValueError(
            "no target construction survived the frozen replication gates"
        )

    frozen = sorted(
        frozen,
        key=lambda item: (item.semantic_atoms, item.target_tokens),
    )
    model_id = _construction_model_id(
        target_language_id=str(target_language_id),
        upstream_model_ids=upstream,
        semantic_atoms=namespace,
        min_sources=min_sources,
        min_positive_per_source=min_positive_per_source,
        constructions=frozen,
    )
    return TargetConstructionModel(
        schema=_CONSTRUCTION_SCHEMA,
        model_id=model_id,
        claim_ceiling=_CONSTRUCTION_CLAIM_CEILING,
        target_language_id=str(target_language_id),
        upstream_model_ids=upstream,
        semantic_atoms=namespace,
        min_sources=min_sources,
        min_positive_per_source=min_positive_per_source,
        constructions=tuple(frozen),
    )


def target_construction_model_from_dict(
    obj: Mapping,
) -> TargetConstructionModel:
    constructions = tuple(
        FrozenTargetConstruction(
            semantic_atoms=tuple(str(atom) for atom in row["semantic_atoms"]),
            target_tokens=tuple(str(token) for token in row["target_tokens"]),
            support=int(row["support"]),
            source_coverage=int(row["source_coverage"]),
        )
        for row in obj["constructions"]
    )
    model = TargetConstructionModel(
        schema=str(obj["schema"]),
        model_id=str(obj["model_id"]),
        claim_ceiling=str(obj["claim_ceiling"]),
        target_language_id=str(obj["target_language_id"]),
        upstream_model_ids=tuple(str(value) for value in obj["upstream_model_ids"]),
        semantic_atoms=tuple(str(value) for value in obj["semantic_atoms"]),
        min_sources=int(obj["min_sources"]),
        min_positive_per_source=int(obj["min_positive_per_source"]),
        constructions=constructions,
    )

    if model.schema != _CONSTRUCTION_SCHEMA:
        raise ValueError("unsupported target construction model schema")
    if model.claim_ceiling != _CONSTRUCTION_CLAIM_CEILING:
        raise ValueError("unsupported target construction claim ceiling")
    if not model.target_language_id:
        raise ValueError("target language ID must not be empty")
    if not model.upstream_model_ids:
        raise ValueError("target construction model has no upstream binding")
    if tuple(sorted(set(model.upstream_model_ids))) != model.upstream_model_ids:
        raise ValueError("upstream model IDs must be sorted and unique")
    if any(not value for value in model.upstream_model_ids):
        raise ValueError("upstream model IDs must not be empty")
    if not model.semantic_atoms:
        raise ValueError("target construction semantic namespace is empty")
    if tuple(sorted(set(model.semantic_atoms))) != model.semantic_atoms:
        raise ValueError("semantic atoms must be sorted and unique")
    if model.min_sources < 2:
        raise ValueError("construction source floor must be >= 2")
    if model.min_positive_per_source < 1:
        raise ValueError("construction per-source floor must be positive")
    if not model.constructions:
        raise ValueError("target construction model contains no constructions")

    keys = [
        (row.semantic_atoms, row.target_tokens)
        for row in model.constructions
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("target construction model contains duplicates")
    if tuple(sorted(keys)) != tuple(keys):
        raise ValueError("target constructions must be canonically ordered")

    namespace = set(model.semantic_atoms)
    for row in model.constructions:
        if not row.semantic_atoms:
            raise ValueError("target construction has empty semantic pattern")
        if not row.target_tokens:
            raise ValueError("target construction has empty target realization")
        if any(not atom for atom in row.semantic_atoms):
            raise ValueError("target construction contains empty semantic atom")
        if any(not token for token in row.target_tokens):
            raise ValueError("target construction contains empty target token")
        if any(atom not in namespace for atom in row.semantic_atoms):
            raise ValueError(
                "target construction references atom outside semantic namespace"
            )
        if row.source_coverage < model.min_sources:
            raise ValueError("target construction violates source replication gate")
        if row.source_coverage > row.support:
            raise ValueError("construction source coverage exceeds support")
        if (
            row.source_coverage * model.min_positive_per_source
            > row.support
        ):
            raise ValueError(
                "construction replicated-positive count exceeds total support"
            )

    expected = _construction_model_id(
        target_language_id=model.target_language_id,
        upstream_model_ids=model.upstream_model_ids,
        semantic_atoms=model.semantic_atoms,
        min_sources=model.min_sources,
        min_positive_per_source=model.min_positive_per_source,
        constructions=model.constructions,
    )
    if expected != model.model_id:
        raise ValueError("target construction model integrity check failed")
    return model


def render_semantic_sequence(
    model: TargetConstructionModel,
    semantic_atoms: Sequence[str],
) -> TargetConstructionRendering:
    model = target_construction_model_from_dict(model.to_dict())
    pattern = tuple(str(atom) for atom in semantic_atoms)
    if not pattern:
        raise ValueError("semantic sequence must not be empty")

    if any(atom not in set(model.semantic_atoms) for atom in pattern):
        return TargetConstructionRendering(
            semantic_atoms=pattern,
            status="OUTSIDE_TARGET_CONSTRUCTION_NAMESPACE",
            realizations=(),
        )

    realizations = tuple(
        sorted(
            {
                row.target_tokens
                for row in model.constructions
                if row.semantic_atoms == pattern
            }
        )
    )
    if len(realizations) == 1:
        status = "TARGET_CONSTRUCTION_SUPPORTED"
    elif len(realizations) > 1:
        status = "MULTIPLE_TARGET_CONSTRUCTIONS_SUPPORTED"
    else:
        status = "UNKNOWN_TARGET_CONSTRUCTION"

    return TargetConstructionRendering(
        semantic_atoms=pattern,
        status=status,
        realizations=realizations,
    )


def operational_semantic_sequence(
    translator_model: ReferenceTranslatorModel,
    qualified_source: QualifiedSourceProfile,
    evidence: Iterable[LocalUnitEvidence],
) -> OperationalSemanticSequence:
    """Preserve position and duplicates while mapping qualified acoustic units to atoms."""
    translation = translate_qualified_query(
        translator_model,
        qualified_source,
        evidence,
    )
    relation_by_token = {
        relation.token: relation.atom
        for relation in translator_model.semantic_relations
    }

    atoms: list[str] = []
    unresolved: list[int] = []
    for index, token in enumerate(translation.global_units):
        if token is None:
            unresolved.append(index)
            continue
        atom = relation_by_token.get(token)
        if atom is None:
            unresolved.append(index)
            continue
        atoms.append(atom)

    if unresolved:
        return OperationalSemanticSequence(
            status="UNRESOLVED_OPERATIONAL_SEQUENCE",
            atoms=tuple(atoms),
            unresolved_positions=tuple(unresolved),
        )
    return OperationalSemanticSequence(
        status="OPERATIONAL_SEQUENCE_SUPPORTED",
        atoms=tuple(atoms),
        unresolved_positions=(),
    )


def translate_qualified_construction(
    translator_model: ReferenceTranslatorModel,
    qualified_source: QualifiedSourceProfile,
    construction_model: TargetConstructionModel,
    evidence: Iterable[LocalUnitEvidence],
) -> QualifiedConstructionTranslation:
    construction_model = target_construction_model_from_dict(
        construction_model.to_dict()
    )
    if translator_model.model_id not in set(construction_model.upstream_model_ids):
        raise ValueError(
            "target construction model is not bound to this translator model"
        )

    sequence = operational_semantic_sequence(
        translator_model,
        qualified_source,
        evidence,
    )
    if sequence.status != "OPERATIONAL_SEQUENCE_SUPPORTED":
        target = TargetConstructionRendering(
            semantic_atoms=sequence.atoms,
            status="UNRESOLVED_TARGET_CONSTRUCTION",
            realizations=(),
        )
    else:
        target = render_semantic_sequence(
            construction_model,
            sequence.atoms,
        )

    return QualifiedConstructionTranslation(
        semantic_sequence=sequence,
        target=target,
    )
