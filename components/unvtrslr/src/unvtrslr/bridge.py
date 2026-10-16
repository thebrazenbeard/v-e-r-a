from __future__ import annotations

from dataclasses import dataclass
from math import log2
from typing import Iterable, Mapping, Sequence


_EPS = 1e-12


@dataclass(frozen=True)
class Episode:
    """One learner-visible interaction episode.

    `signal` and `context` are deliberately opaque IDs. They may represent token
    hypotheses, acoustic-event clusters, observed world features, actions, or other
    measurable distinctions. The bridge does not assign natural-language meaning.
    """

    signal: tuple[str, ...]
    context: frozenset[str]
    source: str | None = None

    @classmethod
    def build(
        cls,
        signal: Iterable[str],
        context: Iterable[str],
        *,
        source: str | None = None,
    ) -> "Episode":
        return cls(tuple(signal), frozenset(context), source)


@dataclass(frozen=True)
class RelationHypothesis:
    token: str
    atom: str
    support: int
    p_atom_given_token: float
    p_atom_without_token: float
    effect: float
    information_bits: float
    source_coverage: int


@dataclass(frozen=True)
class TokenInference:
    token: str
    status: str
    candidates: tuple[RelationHypothesis, ...]
    reason: str


@dataclass(frozen=True)
class TranslationResult:
    signal: tuple[str, ...]
    status: str
    relations: tuple[str, ...]
    unresolved_tokens: tuple[str, ...]
    token_inferences: tuple[TokenInference, ...]


@dataclass(frozen=True)
class ProbeSuggestion:
    token: str
    status: str
    candidate_a: str | None
    candidate_b: str | None
    requested_contrast: tuple[frozenset[str], frozenset[str]] | None
    reason: str


def _binary_mutual_information(n11: int, n10: int, n01: int, n00: int) -> float:
    """Exact empirical mutual information for two binary variables."""
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
    mi = 0.0
    for x, y, count in counts:
        if count == 0:
            continue
        pxy = count / total
        mi += pxy * log2(pxy / max(px[x] * py[y], _EPS))
    return max(0.0, mi)


class BridgeLearner:
    """Cross-situational learner for operational token/context correspondences.

    This is a reference semantic-bootstrap component, not a universal ontology.
    It learns which opaque context distinctions are statistically associated with
    opaque signal units across ambiguous episodes, preserves ties as ambiguity,
    and exposes a contrastive probe when current evidence cannot discriminate.
    """

    def __init__(
        self,
        *,
        alpha: float = 0.5,
        min_support: int = 2,
        min_probability: float = 0.70,
        min_effect: float = 0.35,
        min_information_bits: float = 0.05,
        ambiguity_margin: float = 0.08,
    ) -> None:
        if alpha <= 0:
            raise ValueError("alpha must be > 0")
        self.alpha = float(alpha)
        self.min_support = int(min_support)
        self.min_probability = float(min_probability)
        self.min_effect = float(min_effect)
        self.min_information_bits = float(min_information_bits)
        self.ambiguity_margin = float(ambiguity_margin)
        self._episodes: list[Episode] = []
        self._tokens: set[str] = set()
        self._atoms: set[str] = set()

    def fit(self, episodes: Iterable[Episode]) -> "BridgeLearner":
        materialized = list(episodes)
        if not materialized:
            raise ValueError("at least one episode is required")
        self._episodes = materialized
        self._tokens = {token for episode in materialized for token in set(episode.signal)}
        self._atoms = {atom for episode in materialized for atom in episode.context}
        if not self._tokens:
            raise ValueError("episodes contain no signal units")
        if not self._atoms:
            raise ValueError("episodes contain no context distinctions")
        return self

    @property
    def episodes(self) -> tuple[Episode, ...]:
        return tuple(self._episodes)

    def hypotheses(self, token: str) -> tuple[RelationHypothesis, ...]:
        self._require_fit()
        if token not in self._tokens:
            return ()

        token_present = [token in set(ep.signal) for ep in self._episodes]
        support = sum(token_present)
        source_coverage = len(
            {
                ep.source
                for ep, present in zip(self._episodes, token_present)
                if present and ep.source is not None
            }
        )

        rows: list[RelationHypothesis] = []
        for atom in sorted(self._atoms):
            n11 = n10 = n01 = n00 = 0
            for ep, present in zip(self._episodes, token_present):
                atom_present = atom in ep.context
                if present and atom_present:
                    n11 += 1
                elif present and not atom_present:
                    n10 += 1
                elif not present and atom_present:
                    n01 += 1
                else:
                    n00 += 1

            a = self.alpha
            p_with = (n11 + a) / (n11 + n10 + 2.0 * a)
            p_without = (n01 + a) / (n01 + n00 + 2.0 * a)
            effect = p_with - p_without
            mi = _binary_mutual_information(n11, n10, n01, n00)
            rows.append(
                RelationHypothesis(
                    token=token,
                    atom=atom,
                    support=support,
                    p_atom_given_token=p_with,
                    p_atom_without_token=p_without,
                    effect=effect,
                    information_bits=mi,
                    source_coverage=source_coverage,
                )
            )

        rows.sort(
            key=lambda h: (
                h.effect,
                h.information_bits,
                h.p_atom_given_token,
                h.atom,
            ),
            reverse=True,
        )
        return tuple(rows)

    def infer(self, token: str, *, limit: int = 5) -> TokenInference:
        ranked = self.hypotheses(token)
        if not ranked:
            return TokenInference(token, "UNKNOWN_TOKEN", (), "token was not observed in training episodes")

        top = ranked[0]
        candidates = tuple(ranked[: max(1, limit)])
        if top.support < self.min_support:
            return TokenInference(
                token,
                "INSUFFICIENT_EVIDENCE",
                candidates,
                f"support={top.support} < min_support={self.min_support}",
            )

        if (
            top.p_atom_given_token < self.min_probability
            or top.effect < self.min_effect
            or top.information_bits < self.min_information_bits
        ):
            return TokenInference(
                token,
                "UNRESOLVED",
                candidates,
                "no context relation clears the frozen evidence thresholds",
            )

        if len(ranked) > 1:
            second = ranked[1]
            score_gap = top.effect - second.effect
            information_gap = top.information_bits - second.information_bits
            if score_gap < self.ambiguity_margin and abs(information_gap) < self.ambiguity_margin:
                return TokenInference(
                    token,
                    "AMBIGUOUS",
                    candidates,
                    f"top relations are not discriminated (effect gap={score_gap:.3f})",
                )

        return TokenInference(
            token,
            "OPERATIONAL_RELATION_SUPPORTED",
            candidates,
            "top relation clears support, probability, effect, information, and ambiguity gates",
        )

    def translate(
        self,
        signal: Sequence[str],
        *,
        renderer: Mapping[str, str] | None = None,
    ) -> TranslationResult:
        inferences = tuple(self.infer(token) for token in signal)
        relations: list[str] = []
        unresolved: list[str] = []

        for inf in inferences:
            if inf.status != "OPERATIONAL_RELATION_SUPPORTED":
                unresolved.append(inf.token)
                continue
            atom = inf.candidates[0].atom
            rendered = renderer.get(atom, atom) if renderer is not None else atom
            if rendered not in relations:
                relations.append(rendered)

        if not unresolved and relations:
            status = "OPERATIONAL_TRANSLATION_SUPPORTED"
        elif relations:
            status = "PARTIAL_TRANSLATION"
        else:
            status = "UNRESOLVED"

        return TranslationResult(
            signal=tuple(signal),
            status=status,
            relations=tuple(relations),
            unresolved_tokens=tuple(unresolved),
            token_inferences=inferences,
        )

    def suggest_probe(self, token: str) -> ProbeSuggestion:
        inf = self.infer(token, limit=2)
        if inf.status == "OPERATIONAL_RELATION_SUPPORTED":
            return ProbeSuggestion(
                token,
                "NO_PROBE_REQUIRED",
                inf.candidates[0].atom,
                None,
                None,
                "current evidence discriminates a leading relation",
            )
        if len(inf.candidates) < 2:
            return ProbeSuggestion(
                token,
                "NO_DISCRIMINATING_PAIR_AVAILABLE",
                inf.candidates[0].atom if inf.candidates else None,
                None,
                None,
                inf.reason,
            )

        a = inf.candidates[0].atom
        b = inf.candidates[1].atom
        return ProbeSuggestion(
            token,
            "CONTRAST_REQUESTED",
            a,
            b,
            (frozenset({a}), frozenset({b})),
            "observe the token in contexts that separate the two leading hypotheses",
        )

    def _require_fit(self) -> None:
        if not self._episodes:
            raise RuntimeError("fit() must be called before inference")
