from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Iterable, Mapping, Sequence

from .bridge import BridgeLearner, Episode


_TARGET_SCHEMA = "UNVTRSLR_TARGET_GROUNDING_MODEL_V1"
_TARGET_CLAIM_CEILING = (
    "TARGET_LANGUAGE_OPERATIONAL_RENDERING_WITHIN_GROUNDED_REFERENCE_SCOPE"
)


@dataclass(frozen=True)
class TargetGroundingEpisode:
    episode_id: str
    source_id: str
    target_tokens: tuple[str, ...]
    context: frozenset[str]

    @classmethod
    def build(
        cls,
        episode_id: str,
        source_id: str,
        target_tokens: Iterable[str],
        context: Iterable[str],
    ) -> "TargetGroundingEpisode":
        tokens = tuple(str(token) for token in target_tokens)
        atoms = frozenset(str(atom) for atom in context)
        if not tokens:
            raise ValueError("target grounding episode must contain target tokens")
        if not atoms:
            raise ValueError("target grounding episode must contain context")
        return cls(
            episode_id=str(episode_id),
            source_id=str(source_id),
            target_tokens=tokens,
            context=atoms,
        )


@dataclass(frozen=True)
class NonEquivalenceObservation:
    observation_id: str
    source_id: str
    atom: str
    scope_id: str

    @classmethod
    def build(
        cls,
        observation_id: str,
        source_id: str,
        atom: str,
        scope_id: str,
    ) -> "NonEquivalenceObservation":
        if not str(scope_id):
            raise ValueError("scope_id must not be empty")
        return cls(
            observation_id=str(observation_id),
            source_id=str(source_id),
            atom=str(atom),
            scope_id=str(scope_id),
        )


@dataclass(frozen=True)
class FrozenTargetLexeme:
    target_token: str
    atom: str
    support: int
    positive_source_coverage: int
    p_atom_given_token: float
    p_atom_without_token: float
    effect: float
    information_bits: float


@dataclass(frozen=True)
class FrozenNonEquivalence:
    atom: str
    scope_id: str
    observation_count: int
    source_coverage: int


@dataclass(frozen=True)
class TargetGroundingModel:
    schema: str
    model_id: str
    claim_ceiling: str
    target_language_id: str
    upstream_model_ids: tuple[str, ...]
    semantic_atoms: tuple[str, ...]
    bridge_alpha: float
    bridge_min_support: int
    bridge_min_probability: float
    bridge_min_effect: float
    bridge_min_information_bits: float
    bridge_ambiguity_margin: float
    min_positive_sources: int
    min_positive_per_source: int
    min_non_equivalence_sources: int
    min_non_equivalence_per_source: int
    lexemes: tuple[FrozenTargetLexeme, ...]
    non_equivalences: tuple[FrozenNonEquivalence, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class TargetAtomRendering:
    atom: str
    status: str
    realizations: tuple[str, ...]
    non_equivalence_scopes: tuple[str, ...]


@dataclass(frozen=True)
class TargetRenderingResult:
    status: str
    model_id: str
    target_language_id: str
    atoms: tuple[str, ...]
    renderings: tuple[TargetAtomRendering, ...]


def _positive_source_counts(
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


def _target_model_id(
    *,
    target_language_id: str,
    upstream_model_ids: Sequence[str],
    semantic_atoms: Sequence[str],
    bridge_alpha: float,
    bridge_min_support: int,
    bridge_min_probability: float,
    bridge_min_effect: float,
    bridge_min_information_bits: float,
    bridge_ambiguity_margin: float,
    min_positive_sources: int,
    min_positive_per_source: int,
    min_non_equivalence_sources: int,
    min_non_equivalence_per_source: int,
    lexemes: Sequence[FrozenTargetLexeme],
    non_equivalences: Sequence[FrozenNonEquivalence],
) -> str:
    parts = [
        str(target_language_id),
        repr(tuple(upstream_model_ids)),
        repr(tuple(semantic_atoms)),
        repr(float(bridge_alpha)),
        str(int(bridge_min_support)),
        repr(float(bridge_min_probability)),
        repr(float(bridge_min_effect)),
        repr(float(bridge_min_information_bits)),
        repr(float(bridge_ambiguity_margin)),
        str(int(min_positive_sources)),
        str(int(min_positive_per_source)),
        str(int(min_non_equivalence_sources)),
        str(int(min_non_equivalence_per_source)),
    ]
    for row in sorted(lexemes, key=lambda item: (item.atom, item.target_token)):
        parts.append(
            "|".join(
                [
                    "LEX",
                    row.target_token,
                    row.atom,
                    str(row.support),
                    str(row.positive_source_coverage),
                    repr(row.p_atom_given_token),
                    repr(row.p_atom_without_token),
                    repr(row.effect),
                    repr(row.information_bits),
                ]
            )
        )
    for row in sorted(
        non_equivalences,
        key=lambda item: (item.atom, item.scope_id),
    ):
        parts.append(
            "|".join(
                [
                    "NOEQ",
                    row.atom,
                    row.scope_id,
                    str(row.observation_count),
                    str(row.source_coverage),
                ]
            )
        )
    return "utg_" + sha256(
        "\n".join(parts).encode("utf-8")
    ).hexdigest()[:12]


def fit_target_grounding_model(
    episodes: Iterable[TargetGroundingEpisode],
    *,
    target_language_id: str,
    semantic_atoms: Iterable[str],
    upstream_model_ids: Iterable[str],
    non_equivalence_observations: Iterable[NonEquivalenceObservation] = (),
    min_positive_sources: int = 2,
    min_positive_per_source: int = 2,
    min_non_equivalence_sources: int = 2,
    min_non_equivalence_per_source: int = 2,
    bridge_alpha: float = 0.5,
    bridge_min_support: int = 2,
    bridge_min_probability: float = 0.70,
    bridge_min_effect: float = 0.35,
    bridge_min_information_bits: float = 0.05,
    bridge_ambiguity_margin: float = 0.08,
) -> TargetGroundingModel:
    rows = list(episodes)
    if not rows:
        raise ValueError("at least one target grounding episode is required")
    if not str(target_language_id):
        raise ValueError("target_language_id must not be empty")
    if min_positive_sources < 2:
        raise ValueError("min_positive_sources must be >= 2")
    if min_positive_per_source < 1:
        raise ValueError("min_positive_per_source must be >= 1")
    if min_non_equivalence_sources < 2:
        raise ValueError("min_non_equivalence_sources must be >= 2")
    if min_non_equivalence_per_source < 1:
        raise ValueError("min_non_equivalence_per_source must be >= 1")

    atoms = tuple(sorted({str(atom) for atom in semantic_atoms}))
    if not atoms:
        raise ValueError("semantic_atoms must not be empty")
    atom_set = set(atoms)
    upstream = tuple(sorted({str(value) for value in upstream_model_ids}))
    if not upstream:
        raise ValueError("upstream_model_ids must not be empty")

    episode_ids = [row.episode_id for row in rows]
    if len(episode_ids) != len(set(episode_ids)):
        raise ValueError("target grounding episode_id values must be unique")

    bridge = BridgeLearner(
        alpha=bridge_alpha,
        min_support=bridge_min_support,
        min_probability=bridge_min_probability,
        min_effect=bridge_min_effect,
        min_information_bits=bridge_min_information_bits,
        ambiguity_margin=bridge_ambiguity_margin,
    ).fit(
        Episode.build(
            row.target_tokens,
            row.context,
            source=row.source_id,
        )
        for row in rows
    )

    tokens = sorted(
        {
            token
            for episode in bridge.episodes
            for token in episode.signal
        }
    )
    lexemes: list[FrozenTargetLexeme] = []

    for token in tokens:
        inference = bridge.infer(token)
        if inference.status != "OPERATIONAL_RELATION_SUPPORTED":
            continue
        top = inference.candidates[0]
        if top.atom not in atom_set:
            continue

        positive_counts = _positive_source_counts(
            bridge.episodes,
            token,
            top.atom,
        )
        qualified_sources = {
            source
            for source, count in positive_counts.items()
            if count >= min_positive_per_source
        }
        if len(qualified_sources) < min_positive_sources:
            continue

        lexemes.append(
            FrozenTargetLexeme(
                target_token=token,
                atom=top.atom,
                support=top.support,
                positive_source_coverage=len(qualified_sources),
                p_atom_given_token=top.p_atom_given_token,
                p_atom_without_token=top.p_atom_without_token,
                effect=top.effect,
                information_bits=top.information_bits,
            )
        )

    observations = list(non_equivalence_observations)
    observation_ids = [row.observation_id for row in observations]
    if len(observation_ids) != len(set(observation_ids)):
        raise ValueError("non-equivalence observation_id values must be unique")
    if any(row.atom not in atom_set for row in observations):
        raise ValueError(
            "non-equivalence observation refers to atom outside semantic namespace"
        )

    grouped: dict[tuple[str, str], list[NonEquivalenceObservation]] = {}
    for row in observations:
        grouped.setdefault((row.atom, row.scope_id), []).append(row)

    non_equivalences: list[FrozenNonEquivalence] = []
    for (atom, scope_id), group in sorted(grouped.items()):
        by_source: dict[str, int] = {}
        for row in group:
            by_source[row.source_id] = by_source.get(row.source_id, 0) + 1
        qualified_sources = {
            source
            for source, count in by_source.items()
            if count >= min_non_equivalence_per_source
        }
        if len(qualified_sources) < min_non_equivalence_sources:
            continue
        non_equivalences.append(
            FrozenNonEquivalence(
                atom=atom,
                scope_id=scope_id,
                observation_count=len(group),
                source_coverage=len(qualified_sources),
            )
        )

    model_id = _target_model_id(
        target_language_id=str(target_language_id),
        upstream_model_ids=upstream,
        semantic_atoms=atoms,
        bridge_alpha=bridge_alpha,
        bridge_min_support=bridge_min_support,
        bridge_min_probability=bridge_min_probability,
        bridge_min_effect=bridge_min_effect,
        bridge_min_information_bits=bridge_min_information_bits,
        bridge_ambiguity_margin=bridge_ambiguity_margin,
        min_positive_sources=min_positive_sources,
        min_positive_per_source=min_positive_per_source,
        min_non_equivalence_sources=min_non_equivalence_sources,
        min_non_equivalence_per_source=min_non_equivalence_per_source,
        lexemes=lexemes,
        non_equivalences=non_equivalences,
    )
    return TargetGroundingModel(
        schema=_TARGET_SCHEMA,
        model_id=model_id,
        claim_ceiling=_TARGET_CLAIM_CEILING,
        target_language_id=str(target_language_id),
        upstream_model_ids=upstream,
        semantic_atoms=atoms,
        bridge_alpha=bridge_alpha,
        bridge_min_support=bridge_min_support,
        bridge_min_probability=bridge_min_probability,
        bridge_min_effect=bridge_min_effect,
        bridge_min_information_bits=bridge_min_information_bits,
        bridge_ambiguity_margin=bridge_ambiguity_margin,
        min_positive_sources=min_positive_sources,
        min_positive_per_source=min_positive_per_source,
        min_non_equivalence_sources=min_non_equivalence_sources,
        min_non_equivalence_per_source=min_non_equivalence_per_source,
        lexemes=tuple(sorted(lexemes, key=lambda item: (item.atom, item.target_token))),
        non_equivalences=tuple(
            sorted(non_equivalences, key=lambda item: (item.atom, item.scope_id))
        ),
    )


def target_grounding_model_from_dict(
    obj: Mapping,
) -> TargetGroundingModel:
    lexemes = tuple(
        FrozenTargetLexeme(
            target_token=str(row["target_token"]),
            atom=str(row["atom"]),
            support=int(row["support"]),
            positive_source_coverage=int(row["positive_source_coverage"]),
            p_atom_given_token=float(row["p_atom_given_token"]),
            p_atom_without_token=float(row["p_atom_without_token"]),
            effect=float(row["effect"]),
            information_bits=float(row["information_bits"]),
        )
        for row in obj["lexemes"]
    )
    non_equivalences = tuple(
        FrozenNonEquivalence(
            atom=str(row["atom"]),
            scope_id=str(row["scope_id"]),
            observation_count=int(row["observation_count"]),
            source_coverage=int(row["source_coverage"]),
        )
        for row in obj["non_equivalences"]
    )
    model = TargetGroundingModel(
        schema=str(obj["schema"]),
        model_id=str(obj["model_id"]),
        claim_ceiling=str(obj["claim_ceiling"]),
        target_language_id=str(obj["target_language_id"]),
        upstream_model_ids=tuple(str(value) for value in obj["upstream_model_ids"]),
        semantic_atoms=tuple(str(value) for value in obj["semantic_atoms"]),
        bridge_alpha=float(obj["bridge_alpha"]),
        bridge_min_support=int(obj["bridge_min_support"]),
        bridge_min_probability=float(obj["bridge_min_probability"]),
        bridge_min_effect=float(obj["bridge_min_effect"]),
        bridge_min_information_bits=float(obj["bridge_min_information_bits"]),
        bridge_ambiguity_margin=float(obj["bridge_ambiguity_margin"]),
        min_positive_sources=int(obj["min_positive_sources"]),
        min_positive_per_source=int(obj["min_positive_per_source"]),
        min_non_equivalence_sources=int(obj["min_non_equivalence_sources"]),
        min_non_equivalence_per_source=int(obj["min_non_equivalence_per_source"]),
        lexemes=lexemes,
        non_equivalences=non_equivalences,
    )

    if model.schema != _TARGET_SCHEMA:
        raise ValueError("unsupported target grounding model schema")
    if model.claim_ceiling != _TARGET_CLAIM_CEILING:
        raise ValueError("unsupported target grounding claim ceiling")
    if not model.target_language_id:
        raise ValueError("target language ID must not be empty")
    if not model.upstream_model_ids:
        raise ValueError("target model has no upstream model binding")
    if tuple(sorted(set(model.upstream_model_ids))) != model.upstream_model_ids:
        raise ValueError("upstream model IDs must be sorted and unique")
    if any(not value for value in model.upstream_model_ids):
        raise ValueError("upstream model IDs must not be empty")
    if not model.semantic_atoms:
        raise ValueError("target model semantic namespace is empty")
    if tuple(sorted(set(model.semantic_atoms))) != model.semantic_atoms:
        raise ValueError("semantic atoms must be sorted and unique")
    atom_set = set(model.semantic_atoms)

    if model.bridge_alpha <= 0:
        raise ValueError("target bridge alpha must be > 0")
    if model.bridge_min_support < 1:
        raise ValueError("target bridge support floor must be positive")
    if not 0.0 < model.bridge_min_probability <= 1.0:
        raise ValueError("target bridge probability floor is invalid")
    if model.bridge_min_effect <= 0.0:
        raise ValueError("target bridge effect floor must be positive")
    if model.bridge_min_information_bits < 0.0:
        raise ValueError("target bridge information floor is invalid")
    if model.bridge_ambiguity_margin < 0.0:
        raise ValueError("target bridge ambiguity margin is invalid")
    if model.min_positive_sources < 2 or model.min_positive_per_source < 1:
        raise ValueError("target lexeme replication floors are invalid")
    if (
        model.min_non_equivalence_sources < 2
        or model.min_non_equivalence_per_source < 1
    ):
        raise ValueError("non-equivalence replication floors are invalid")

    lexeme_keys = [(row.atom, row.target_token) for row in model.lexemes]
    if len(lexeme_keys) != len(set(lexeme_keys)):
        raise ValueError("target model contains duplicate lexeme relations")
    if tuple(sorted(lexeme_keys)) != tuple(lexeme_keys):
        raise ValueError("target lexeme relations must be canonically ordered")

    for row in model.lexemes:
        if not row.target_token:
            raise ValueError("target token must not be empty")
        if row.atom not in atom_set:
            raise ValueError("target lexeme references atom outside semantic namespace")
        if row.support < model.bridge_min_support:
            raise ValueError("target lexeme violates bridge support gate")
        if row.support < model.min_positive_sources * model.min_positive_per_source:
            raise ValueError("target lexeme support is inconsistent with replication gate")
        if row.positive_source_coverage < model.min_positive_sources:
            raise ValueError("target lexeme violates source replication gate")
        if row.positive_source_coverage > row.support:
            raise ValueError("target lexeme source coverage exceeds support")
        if (
            row.positive_source_coverage * model.min_positive_per_source
            > row.support
        ):
            raise ValueError(
                "target lexeme replicated positive count exceeds total support"
            )
        if not 0.0 <= row.p_atom_given_token <= 1.0:
            raise ValueError("target lexeme probability is invalid")
        if not 0.0 <= row.p_atom_without_token <= 1.0:
            raise ValueError("target lexeme background probability is invalid")
        if abs(
            row.effect - (row.p_atom_given_token - row.p_atom_without_token)
        ) > 1e-12:
            raise ValueError("target lexeme effect is inconsistent")
        if row.p_atom_given_token < model.bridge_min_probability:
            raise ValueError("target lexeme violates probability gate")
        if row.effect < model.bridge_min_effect:
            raise ValueError("target lexeme violates effect gate")
        if not 0.0 <= row.information_bits <= 1.0 + 1e-12:
            raise ValueError("target lexeme information value is invalid")
        if row.information_bits < model.bridge_min_information_bits:
            raise ValueError("target lexeme violates information gate")

    noeq_keys = [(row.atom, row.scope_id) for row in model.non_equivalences]
    if len(noeq_keys) != len(set(noeq_keys)):
        raise ValueError("target model contains duplicate non-equivalence claims")
    if tuple(sorted(noeq_keys)) != tuple(noeq_keys):
        raise ValueError("non-equivalence claims must be canonically ordered")
    for row in model.non_equivalences:
        if not row.scope_id:
            raise ValueError("non-equivalence scope ID must not be empty")
        if row.atom not in atom_set:
            raise ValueError(
                "non-equivalence claim references atom outside semantic namespace"
            )
        if row.source_coverage < model.min_non_equivalence_sources:
            raise ValueError("non-equivalence claim violates source replication gate")
        if (
            row.observation_count
            < row.source_coverage * model.min_non_equivalence_per_source
        ):
            raise ValueError("non-equivalence observation count is inconsistent")

    expected = _target_model_id(
        target_language_id=model.target_language_id,
        upstream_model_ids=model.upstream_model_ids,
        semantic_atoms=model.semantic_atoms,
        bridge_alpha=model.bridge_alpha,
        bridge_min_support=model.bridge_min_support,
        bridge_min_probability=model.bridge_min_probability,
        bridge_min_effect=model.bridge_min_effect,
        bridge_min_information_bits=model.bridge_min_information_bits,
        bridge_ambiguity_margin=model.bridge_ambiguity_margin,
        min_positive_sources=model.min_positive_sources,
        min_positive_per_source=model.min_positive_per_source,
        min_non_equivalence_sources=model.min_non_equivalence_sources,
        min_non_equivalence_per_source=model.min_non_equivalence_per_source,
        lexemes=model.lexemes,
        non_equivalences=model.non_equivalences,
    )
    if expected != model.model_id:
        raise ValueError("target grounding model integrity check failed")
    return model


def render_atom(
    model: TargetGroundingModel,
    atom: str,
) -> TargetAtomRendering:
    model = target_grounding_model_from_dict(model.to_dict())
    atom = str(atom)
    if atom not in set(model.semantic_atoms):
        return TargetAtomRendering(
            atom=atom,
            status="OUTSIDE_TARGET_SEMANTIC_NAMESPACE",
            realizations=(),
            non_equivalence_scopes=(),
        )

    realizations = tuple(
        sorted(
            {
                row.target_token
                for row in model.lexemes
                if row.atom == atom
            }
        )
    )
    scopes = tuple(
        sorted(
            {
                row.scope_id
                for row in model.non_equivalences
                if row.atom == atom
            }
        )
    )

    if realizations and scopes:
        status = "CONFLICTING_TARGET_EVIDENCE"
    elif len(realizations) == 1:
        status = "TARGET_RENDERING_SUPPORTED"
    elif len(realizations) > 1:
        status = "MULTIPLE_TARGET_REALIZATIONS_SUPPORTED"
    elif scopes:
        status = "NO_FAITHFUL_EQUIVALENT_FOUND_WITHIN_DECLARED_SCOPE"
    else:
        status = "UNKNOWN_TARGET_RENDERING"

    return TargetAtomRendering(
        atom=atom,
        status=status,
        realizations=realizations,
        non_equivalence_scopes=scopes,
    )


def render_relations(
    model: TargetGroundingModel,
    atoms: Sequence[str],
) -> TargetRenderingResult:
    model = target_grounding_model_from_dict(model.to_dict())
    renderings = tuple(render_atom(model, atom) for atom in atoms)

    statuses = {row.status for row in renderings}
    successful = {
        "TARGET_RENDERING_SUPPORTED",
        "MULTIPLE_TARGET_REALIZATIONS_SUPPORTED",
    }
    if renderings and statuses <= successful:
        status = "TARGET_RENDERING_COMPLETE"
    elif any(row.status in successful for row in renderings):
        status = "TARGET_RENDERING_PARTIAL"
    else:
        status = "TARGET_RENDERING_UNRESOLVED"

    return TargetRenderingResult(
        status=status,
        model_id=model.model_id,
        target_language_id=model.target_language_id,
        atoms=tuple(str(atom) for atom in atoms),
        renderings=renderings,
    )


def strict_renderer_mapping(
    model: TargetGroundingModel,
) -> dict[str, str]:
    """Return only atoms with one unconflicted, uniquely supported realization."""
    model = target_grounding_model_from_dict(model.to_dict())
    mapping: dict[str, str] = {}
    for atom in model.semantic_atoms:
        rendering = render_atom(model, atom)
        if rendering.status == "TARGET_RENDERING_SUPPORTED":
            mapping[atom] = rendering.realizations[0]
    return mapping
