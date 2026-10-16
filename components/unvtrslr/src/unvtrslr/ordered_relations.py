from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from math import log2
from typing import Iterable, Mapping, Sequence

from .bridge import Episode
from .calibration_qualification import (
    QualifiedSourceProfile,
    translate_qualified_query,
)
from .translator import ReferenceTranslation, ReferenceTranslatorModel
from .unit_registry import LocalUnitEvidence


_EPS = 1e-12
_ORDER_SCHEMA = "UNVTRSLR_ORDERED_RELATION_MODEL_V1"
_ORDER_CLAIM_CEILING = (
    "ORDER_SENSITIVE_OPERATIONAL_RELATION_WITHIN_REFERENCE_FIXTURES"
)


@dataclass(frozen=True)
class OrderedRelationHypothesis:
    first_token: str
    second_token: str
    atom: str
    ordered_support: int
    reverse_support: int
    ordered_source_coverage: int
    reverse_source_coverage: int
    positive_source_coverage: int
    p_atom_given_ordered: float
    p_atom_given_reverse: float
    effect: float
    information_bits: float


@dataclass(frozen=True)
class OrderedPairInference:
    first_token: str
    second_token: str
    status: str
    candidates: tuple[OrderedRelationHypothesis, ...]
    reason: str


@dataclass(frozen=True)
class FrozenOrderedRelation:
    first_token: str
    second_token: str
    atom: str
    ordered_support: int
    reverse_support: int
    ordered_source_coverage: int
    reverse_source_coverage: int
    positive_source_coverage: int
    p_atom_given_ordered: float
    p_atom_given_reverse: float
    effect: float
    information_bits: float


@dataclass(frozen=True)
class OrderedRelationModel:
    schema: str
    model_id: str
    claim_ceiling: str
    translator_model_id: str
    acoustic_model_id: str
    min_ordered_support: int
    min_reverse_support: int
    min_order_source_coverage: int
    min_positive_sources: int
    min_positive_per_source: int
    min_probability: float
    min_effect: float
    min_information_bits: float
    ambiguity_margin: float
    relations: tuple[FrozenOrderedRelation, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class OrderedSequenceTranslation:
    status: str
    relations: tuple[str, ...]
    unresolved_patterns: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class StructuredReferenceTranslation:
    status: str
    lexical: ReferenceTranslation
    ordered: OrderedSequenceTranslation


def _binary_mutual_information(
    n11: int,
    n10: int,
    n01: int,
    n00: int,
) -> float:
    counts = ((1, 1, n11), (1, 0, n10), (0, 1, n01), (0, 0, n00))
    total = n11 + n10 + n01 + n00
    if total <= 0:
        return 0.0
    px = {
        1: (n11 + n10) / total,
        0: (n01 + n00) / total,
    }
    py = {
        1: (n11 + n01) / total,
        0: (n10 + n00) / total,
    }
    result = 0.0
    for x, y, count in counts:
        if count <= 0:
            continue
        pxy = count / total
        result += pxy * log2(pxy / max(px[x] * py[y], _EPS))
    return max(0.0, result)


def _has_adjacent(signal: Sequence[str], first: str, second: str) -> bool:
    return any(
        signal[index] == first and signal[index + 1] == second
        for index in range(len(signal) - 1)
    )


def _contrast_episodes(
    episodes: Sequence[Episode],
    first: str,
    second: str,
) -> tuple[list[Episode], list[Episode]]:
    ordered: list[Episode] = []
    reversed_rows: list[Episode] = []
    for episode in episodes:
        has_ordered = _has_adjacent(episode.signal, first, second)
        has_reverse = _has_adjacent(episode.signal, second, first)
        # Episodes containing both directions are not discriminating evidence.
        if has_ordered == has_reverse:
            continue
        if has_ordered:
            ordered.append(episode)
        else:
            reversed_rows.append(episode)
    return ordered, reversed_rows


def _source_coverage(episodes: Sequence[Episode]) -> int:
    return len(
        {
            str(episode.source)
            for episode in episodes
            if episode.source is not None
        }
    )


def _positive_source_counts(
    episodes: Sequence[Episode],
    atom: str,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for episode in episodes:
        if episode.source is None or atom not in episode.context:
            continue
        source = str(episode.source)
        counts[source] = counts.get(source, 0) + 1
    return counts


class OrderedRelationLearner:
    """Learn order-sensitive operational relations from AB versus BA contrasts."""

    def __init__(
        self,
        *,
        alpha: float = 0.5,
        min_ordered_support: int = 4,
        min_reverse_support: int = 4,
        min_order_source_coverage: int = 2,
        min_positive_sources: int = 2,
        min_positive_per_source: int = 2,
        min_probability: float = 0.75,
        min_effect: float = 0.40,
        min_information_bits: float = 0.05,
        ambiguity_margin: float = 0.08,
    ) -> None:
        if alpha <= 0:
            raise ValueError("alpha must be > 0")
        if min_ordered_support < 1 or min_reverse_support < 1:
            raise ValueError("order support floors must be positive")
        if min_order_source_coverage < 1:
            raise ValueError("min_order_source_coverage must be positive")
        if min_positive_sources < 1 or min_positive_per_source < 1:
            raise ValueError("positive-source floors must be positive")
        self.alpha = float(alpha)
        self.min_ordered_support = int(min_ordered_support)
        self.min_reverse_support = int(min_reverse_support)
        self.min_order_source_coverage = int(min_order_source_coverage)
        self.min_positive_sources = int(min_positive_sources)
        self.min_positive_per_source = int(min_positive_per_source)
        self.min_probability = float(min_probability)
        self.min_effect = float(min_effect)
        self.min_information_bits = float(min_information_bits)
        self.ambiguity_margin = float(ambiguity_margin)
        self._episodes: list[Episode] = []
        self._atoms: set[str] = set()
        self._pairs: set[tuple[str, str]] = set()

    def fit(self, episodes: Iterable[Episode]) -> "OrderedRelationLearner":
        rows = list(episodes)
        if not rows:
            raise ValueError("at least one episode is required")
        self._episodes = rows
        self._atoms = {
            atom
            for episode in rows
            for atom in episode.context
        }
        self._pairs = {
            (episode.signal[index], episode.signal[index + 1])
            for episode in rows
            for index in range(len(episode.signal) - 1)
            if episode.signal[index] != episode.signal[index + 1]
        }
        if not self._pairs:
            raise ValueError("episodes contain no ordered token contrasts")
        if not self._atoms:
            raise ValueError("episodes contain no context distinctions")
        return self

    @property
    def episodes(self) -> tuple[Episode, ...]:
        return tuple(self._episodes)

    @property
    def pairs(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(self._pairs))

    def hypotheses(
        self,
        first: str,
        second: str,
    ) -> tuple[OrderedRelationHypothesis, ...]:
        if not self._episodes:
            raise RuntimeError("fit() must be called before inference")
        if first == second:
            return ()

        ordered, reversed_rows = _contrast_episodes(
            self._episodes,
            first,
            second,
        )
        if not ordered and not reversed_rows:
            return ()

        ordered_source_coverage = _source_coverage(ordered)
        reverse_source_coverage = _source_coverage(reversed_rows)
        rows: list[OrderedRelationHypothesis] = []

        for atom in sorted(self._atoms):
            n11 = sum(atom in episode.context for episode in ordered)
            n10 = len(ordered) - n11
            n01 = sum(atom in episode.context for episode in reversed_rows)
            n00 = len(reversed_rows) - n01
            a = self.alpha
            p_ordered = (n11 + a) / (n11 + n10 + 2.0 * a)
            p_reverse = (n01 + a) / (n01 + n00 + 2.0 * a)
            effect = p_ordered - p_reverse
            positive_counts = _positive_source_counts(ordered, atom)
            positive_source_coverage = sum(
                count >= self.min_positive_per_source
                for count in positive_counts.values()
            )
            rows.append(
                OrderedRelationHypothesis(
                    first_token=first,
                    second_token=second,
                    atom=atom,
                    ordered_support=len(ordered),
                    reverse_support=len(reversed_rows),
                    ordered_source_coverage=ordered_source_coverage,
                    reverse_source_coverage=reverse_source_coverage,
                    positive_source_coverage=positive_source_coverage,
                    p_atom_given_ordered=p_ordered,
                    p_atom_given_reverse=p_reverse,
                    effect=effect,
                    information_bits=_binary_mutual_information(
                        n11,
                        n10,
                        n01,
                        n00,
                    ),
                )
            )

        rows.sort(
            key=lambda row: (
                row.effect,
                row.information_bits,
                row.p_atom_given_ordered,
                row.atom,
            ),
            reverse=True,
        )
        return tuple(rows)

    def infer(
        self,
        first: str,
        second: str,
        *,
        limit: int = 5,
    ) -> OrderedPairInference:
        ranked = self.hypotheses(first, second)
        if not ranked:
            return OrderedPairInference(
                first,
                second,
                "UNKNOWN_ORDERED_PAIR",
                (),
                "ordered pair was not observed in a discriminating contrast",
            )

        top = ranked[0]
        candidates = tuple(ranked[: max(1, limit)])

        if (
            top.ordered_support < self.min_ordered_support
            or top.reverse_support < self.min_reverse_support
        ):
            return OrderedPairInference(
                first,
                second,
                "INSUFFICIENT_ORDER_CONTRAST",
                candidates,
                "ordered/reversed support does not clear the frozen floors",
            )

        if (
            top.ordered_source_coverage < self.min_order_source_coverage
            or top.reverse_source_coverage < self.min_order_source_coverage
        ):
            return OrderedPairInference(
                first,
                second,
                "SOURCE_CONFOUNDED_ORDER_CONTRAST",
                candidates,
                "both order directions must recur across multiple sources",
            )

        if top.positive_source_coverage < self.min_positive_sources:
            return OrderedPairInference(
                first,
                second,
                "INSUFFICIENT_CROSS_SOURCE_REPLICATION",
                candidates,
                "positive ordered relation lacks replicated source support",
            )

        if (
            top.p_atom_given_ordered < self.min_probability
            or top.effect < self.min_effect
            or top.information_bits < self.min_information_bits
        ):
            return OrderedPairInference(
                first,
                second,
                "UNRESOLVED",
                candidates,
                "no ordered relation clears probability/effect/information gates",
            )

        if len(ranked) > 1:
            second_best = ranked[1]
            if (
                top.effect - second_best.effect < self.ambiguity_margin
                and abs(
                    top.information_bits - second_best.information_bits
                ) < self.ambiguity_margin
            ):
                return OrderedPairInference(
                    first,
                    second,
                    "AMBIGUOUS",
                    candidates,
                    "top ordered relations are not discriminated",
                )

        return OrderedPairInference(
            first,
            second,
            "ORDERED_OPERATIONAL_RELATION_SUPPORTED",
            candidates,
            "AB versus BA contrast survives support, source, replication, "
            "probability, effect, information, and ambiguity gates",
        )


def _ordered_model_id(
    learner: OrderedRelationLearner,
    relations: Sequence[FrozenOrderedRelation],
    translator_model_id: str,
    acoustic_model_id: str,
) -> str:
    parts = [
        str(translator_model_id),
        str(acoustic_model_id),
        str(learner.min_ordered_support),
        str(learner.min_reverse_support),
        str(learner.min_order_source_coverage),
        str(learner.min_positive_sources),
        str(learner.min_positive_per_source),
        repr(learner.min_probability),
        repr(learner.min_effect),
        repr(learner.min_information_bits),
        repr(learner.ambiguity_margin),
    ]
    for relation in sorted(
        relations,
        key=lambda row: (row.first_token, row.second_token, row.atom),
    ):
        parts.append(
            "|".join(
                [
                    relation.first_token,
                    relation.second_token,
                    relation.atom,
                    str(relation.ordered_support),
                    str(relation.reverse_support),
                    str(relation.ordered_source_coverage),
                    str(relation.reverse_source_coverage),
                    str(relation.positive_source_coverage),
                    repr(relation.p_atom_given_ordered),
                    repr(relation.p_atom_given_reverse),
                    repr(relation.effect),
                    repr(relation.information_bits),
                ]
            )
        )
    return "uor_" + sha256(
        "\n".join(parts).encode("utf-8")
    ).hexdigest()[:12]


def fit_ordered_relation_model(
    episodes: Iterable[Episode],
    *,
    translator_model_id: str,
    acoustic_model_id: str,
    valid_token_ids: Iterable[str],
    **learner_kwargs,
) -> OrderedRelationModel:
    if not translator_model_id or not acoustic_model_id:
        raise ValueError("translator/acoustic model IDs are required")
    rows = list(episodes)
    vocabulary = {str(token) for token in valid_token_ids}
    if not vocabulary:
        raise ValueError("valid_token_ids must not be empty")
    observed = {
        token
        for episode in rows
        for token in episode.signal
    }
    unknown = observed - vocabulary
    if unknown:
        raise ValueError(
            "ordered training contains tokens outside the frozen acoustic "
            f"vocabulary: {sorted(unknown)!r}"
        )
    learner = OrderedRelationLearner(**learner_kwargs).fit(rows)
    relations: list[FrozenOrderedRelation] = []
    for first, second in learner.pairs:
        inference = learner.infer(first, second)
        if inference.status != "ORDERED_OPERATIONAL_RELATION_SUPPORTED":
            continue
        top = inference.candidates[0]
        relations.append(
            FrozenOrderedRelation(
                first_token=first,
                second_token=second,
                atom=top.atom,
                ordered_support=top.ordered_support,
                reverse_support=top.reverse_support,
                ordered_source_coverage=top.ordered_source_coverage,
                reverse_source_coverage=top.reverse_source_coverage,
                positive_source_coverage=top.positive_source_coverage,
                p_atom_given_ordered=top.p_atom_given_ordered,
                p_atom_given_reverse=top.p_atom_given_reverse,
                effect=top.effect,
                information_bits=top.information_bits,
            )
        )
    if not relations:
        raise ValueError("no ordered relation survived the frozen evidence gates")

    model_id = _ordered_model_id(
        learner,
        relations,
        translator_model_id,
        acoustic_model_id,
    )
    return OrderedRelationModel(
        schema=_ORDER_SCHEMA,
        model_id=model_id,
        claim_ceiling=_ORDER_CLAIM_CEILING,
        translator_model_id=str(translator_model_id),
        acoustic_model_id=str(acoustic_model_id),
        min_ordered_support=learner.min_ordered_support,
        min_reverse_support=learner.min_reverse_support,
        min_order_source_coverage=learner.min_order_source_coverage,
        min_positive_sources=learner.min_positive_sources,
        min_positive_per_source=learner.min_positive_per_source,
        min_probability=learner.min_probability,
        min_effect=learner.min_effect,
        min_information_bits=learner.min_information_bits,
        ambiguity_margin=learner.ambiguity_margin,
        relations=tuple(relations),
    )


def ordered_relation_model_from_dict(obj: Mapping) -> OrderedRelationModel:
    relations = tuple(
        FrozenOrderedRelation(
            first_token=str(row["first_token"]),
            second_token=str(row["second_token"]),
            atom=str(row["atom"]),
            ordered_support=int(row["ordered_support"]),
            reverse_support=int(row["reverse_support"]),
            ordered_source_coverage=int(row["ordered_source_coverage"]),
            reverse_source_coverage=int(row["reverse_source_coverage"]),
            positive_source_coverage=int(row["positive_source_coverage"]),
            p_atom_given_ordered=float(row["p_atom_given_ordered"]),
            p_atom_given_reverse=float(row["p_atom_given_reverse"]),
            effect=float(row["effect"]),
            information_bits=float(row["information_bits"]),
        )
        for row in obj["relations"]
    )
    model = OrderedRelationModel(
        schema=str(obj["schema"]),
        model_id=str(obj["model_id"]),
        claim_ceiling=str(obj["claim_ceiling"]),
        translator_model_id=str(obj["translator_model_id"]),
        acoustic_model_id=str(obj["acoustic_model_id"]),
        min_ordered_support=int(obj["min_ordered_support"]),
        min_reverse_support=int(obj["min_reverse_support"]),
        min_order_source_coverage=int(obj["min_order_source_coverage"]),
        min_positive_sources=int(obj["min_positive_sources"]),
        min_positive_per_source=int(obj["min_positive_per_source"]),
        min_probability=float(obj["min_probability"]),
        min_effect=float(obj["min_effect"]),
        min_information_bits=float(obj["min_information_bits"]),
        ambiguity_margin=float(obj["ambiguity_margin"]),
        relations=relations,
    )
    if model.schema != _ORDER_SCHEMA:
        raise ValueError("unsupported ordered relation model schema")
    if model.claim_ceiling != _ORDER_CLAIM_CEILING:
        raise ValueError("unsupported ordered relation claim ceiling")
    if not model.relations:
        raise ValueError("ordered relation model contains no relations")

    patterns = [
        (row.first_token, row.second_token)
        for row in model.relations
    ]
    if len(patterns) != len(set(patterns)):
        raise ValueError("ordered relation model contains duplicate patterns")
    if any(first == second for first, second in patterns):
        raise ValueError("self-pairs cannot be order contrasts")
    if model.min_ordered_support < 1 or model.min_reverse_support < 1:
        raise ValueError("ordered relation support floors must be positive")
    if model.min_order_source_coverage < 1:
        raise ValueError("ordered relation source-coverage floor must be positive")
    if model.min_positive_sources < 1 or model.min_positive_per_source < 1:
        raise ValueError("ordered relation replication floors must be positive")
    if not 0.0 < model.min_probability <= 1.0:
        raise ValueError("ordered relation probability floor is invalid")
    if model.min_effect <= 0.0:
        raise ValueError("ordered relation effect floor must be positive")
    if model.min_information_bits < 0.0:
        raise ValueError("ordered relation information floor is invalid")
    if model.ambiguity_margin < 0.0:
        raise ValueError("ordered relation ambiguity margin is invalid")
    for relation in model.relations:
        if relation.ordered_support < model.min_ordered_support:
            raise ValueError("frozen ordered relation violates ordered-support gate")
        if relation.reverse_support < model.min_reverse_support:
            raise ValueError("frozen ordered relation violates reverse-support gate")
        if relation.ordered_source_coverage < model.min_order_source_coverage:
            raise ValueError("frozen ordered relation violates ordered-source gate")
        if relation.reverse_source_coverage < model.min_order_source_coverage:
            raise ValueError("frozen ordered relation violates reverse-source gate")
        if relation.positive_source_coverage < model.min_positive_sources:
            raise ValueError("frozen ordered relation violates positive-source gate")
        if relation.ordered_source_coverage > relation.ordered_support:
            raise ValueError("ordered source coverage exceeds ordered support")
        if relation.reverse_source_coverage > relation.reverse_support:
            raise ValueError("reverse source coverage exceeds reverse support")
        if relation.positive_source_coverage > relation.ordered_source_coverage:
            raise ValueError("positive source coverage exceeds ordered source coverage")
        if (
            relation.positive_source_coverage * model.min_positive_per_source
            > relation.ordered_support
        ):
            raise ValueError("positive source replication exceeds ordered support")
        if not 0.0 <= relation.p_atom_given_ordered <= 1.0:
            raise ValueError("ordered relation probability is invalid")
        if not 0.0 <= relation.p_atom_given_reverse <= 1.0:
            raise ValueError("reverse relation probability is invalid")
        if relation.p_atom_given_ordered < model.min_probability:
            raise ValueError("frozen ordered relation violates probability gate")
        expected_effect = (
            relation.p_atom_given_ordered
            - relation.p_atom_given_reverse
        )
        if abs(relation.effect - expected_effect) > 1e-12:
            raise ValueError("ordered relation effect is inconsistent")
        if relation.effect < model.min_effect:
            raise ValueError("frozen ordered relation violates effect gate")
        if not 0.0 <= relation.information_bits <= 1.0 + 1e-12:
            raise ValueError("ordered relation information value is invalid")
        if relation.information_bits < model.min_information_bits:
            raise ValueError("frozen ordered relation violates information gate")

    learner = OrderedRelationLearner(
        min_ordered_support=model.min_ordered_support,
        min_reverse_support=model.min_reverse_support,
        min_order_source_coverage=model.min_order_source_coverage,
        min_positive_sources=model.min_positive_sources,
        min_positive_per_source=model.min_positive_per_source,
        min_probability=model.min_probability,
        min_effect=model.min_effect,
        min_information_bits=model.min_information_bits,
        ambiguity_margin=model.ambiguity_margin,
    )
    expected = _ordered_model_id(
        learner,
        model.relations,
        model.translator_model_id,
        model.acoustic_model_id,
    )
    if expected != model.model_id:
        raise ValueError("ordered relation model integrity check failed")
    return model


def translate_ordered_sequence(
    model: OrderedRelationModel,
    signal: Sequence[str],
    *,
    renderer: Mapping[str, str] | None = None,
) -> OrderedSequenceTranslation:
    model = ordered_relation_model_from_dict(model.to_dict())
    relation_by_pattern = {
        (row.first_token, row.second_token): row
        for row in model.relations
    }
    relations: list[str] = []
    unresolved: list[tuple[str, str]] = []

    for index in range(len(signal) - 1):
        pattern = (str(signal[index]), str(signal[index + 1]))
        relation = relation_by_pattern.get(pattern)
        if relation is None:
            unresolved.append(pattern)
            continue
        rendered = (
            renderer.get(relation.atom, relation.atom)
            if renderer is not None
            else relation.atom
        )
        if rendered not in relations:
            relations.append(rendered)

    if relations and not unresolved:
        status = "ORDERED_TRANSLATION_SUPPORTED"
    elif relations:
        status = "PARTIAL_ORDERED_TRANSLATION"
    else:
        status = "UNRESOLVED"

    return OrderedSequenceTranslation(
        status=status,
        relations=tuple(relations),
        unresolved_patterns=tuple(unresolved),
    )


def translate_qualified_sequence(
    translator_model: ReferenceTranslatorModel,
    qualified_source: QualifiedSourceProfile,
    ordered_model: OrderedRelationModel,
    evidence: Iterable[LocalUnitEvidence],
    *,
    renderer: Mapping[str, str] | None = None,
) -> StructuredReferenceTranslation:
    """Compose qualified acoustic/lexical translation with ordered relations."""
    ordered_model = ordered_relation_model_from_dict(ordered_model.to_dict())
    if ordered_model.translator_model_id != translator_model.model_id:
        raise ValueError("ordered model belongs to a different translator model")
    if ordered_model.acoustic_model_id != translator_model.acoustic_model.model_id:
        raise ValueError("ordered model belongs to a different acoustic model")

    lexical = translate_qualified_query(
        translator_model,
        qualified_source,
        evidence,
        renderer=renderer,
    )
    token_signal = tuple(
        token
        for token in lexical.global_units
        if token is not None
    )

    # Missing acoustic identities break adjacency. Do not fabricate a shorter
    # sequence by silently bridging across unresolved positions.
    if any(token is None for token in lexical.global_units):
        ordered = OrderedSequenceTranslation(
            status="UNRESOLVED",
            relations=(),
            unresolved_patterns=(),
        )
    else:
        ordered = translate_ordered_sequence(
            ordered_model,
            token_signal,
            renderer=renderer,
        )

    if (
        lexical.status == "REFERENCE_TRANSLATION_SUPPORTED"
        and ordered.status == "ORDERED_TRANSLATION_SUPPORTED"
    ):
        status = "STRUCTURED_REFERENCE_TRANSLATION_SUPPORTED"
    elif lexical.relations or ordered.relations:
        status = "PARTIAL_STRUCTURED_REFERENCE_TRANSLATION"
    else:
        status = "UNRESOLVED"

    return StructuredReferenceTranslation(
        status=status,
        lexical=lexical,
        ordered=ordered,
    )
