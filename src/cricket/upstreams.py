from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Any


class UpstreamStatus(str, Enum):
    CURRENT = "CURRENT"
    MOVED = "MOVED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class UpstreamContract:
    repository: str
    pinned_commit: str
    relationship: str
    compatibility_scope: str

    def __post_init__(self) -> None:
        for name, value in (
            ("repository", self.repository),
            ("pinned_commit", self.pinned_commit),
            ("relationship", self.relationship),
            ("compatibility_scope", self.compatibility_scope),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty text")


@dataclass(frozen=True)
class UpstreamResult:
    repository: str
    pinned_commit: str
    observed_commit: str | None
    relationship: str
    status: UpstreamStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository": self.repository,
            "pinned_commit": self.pinned_commit,
            "observed_commit": self.observed_commit,
            "relationship": self.relationship,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class UpstreamReport:
    status: UpstreamStatus
    results: tuple[UpstreamResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "results": [item.to_dict() for item in self.results],
        }


UPSTREAM_CONTRACTS: tuple[UpstreamContract, ...] = (
    UpstreamContract(
        repository="thebrazenbeard/rezon",
        pinned_commit="ec401810990337bf07a5d6473782ba13eba1bb3f",
        relationship="SEMANTIC_UPSTREAM",
        compatibility_scope=(
            "proposition, referent, scope, modality, temporal scope, provenance, "
            "authority, adversarial fidelity, and optional interruption formulation"
        ),
    ),
    UpstreamContract(
        repository="thebrazenbeard/semiotics",
        pinned_commit="37117a2097f7f2aa35968fc9db24eacf7240826e",
        relationship="CONCEPTUAL_DONOR",
        compatibility_scope="context-bound interpretation and explicit semantic relations",
    ),
    UpstreamContract(
        repository="thebrazenbeard/spm",
        pinned_commit="d9ea72798ac892ac75f858177b6ed0c5a6b4c37c",
        relationship="CONCEPTUAL_DONOR",
        compatibility_scope="proposition identity, speech acts, modality, and Righter failure",
    ),
    UpstreamContract(
        repository="thebrazenbeard/roots",
        pinned_commit="1bc3af6aec0bebe383f60f56ad3070e83f0f40b5",
        relationship="CONCEPTUAL_DONOR",
        compatibility_scope="semantic lineage, supersession, and currentness",
    ),
    UpstreamContract(
        repository="thebrazenbeard/semanticatlas",
        pinned_commit="895677a64af5d29b580306ca52ecc0e0607a9ccc",
        relationship="CONCEPTUAL_DONOR",
        compatibility_scope="semantic similarity versus provenance",
    ),
    UpstreamContract(
        repository="thebrazenbeard/ingest",
        pinned_commit="27764c9fb97c84d178a3f66e0da2d669df645ed6",
        relationship="BOUNDARY_DONOR",
        compatibility_scope="raw versus normalized versus interpreted input",
    ),
    UpstreamContract(
        repository="thebrazenbeard/sql-connectome",
        pinned_commit="f81ff43e5358f798f23bab8a718bda743c93e930",
        relationship="CLASSIFICATION_DONOR",
        compatibility_scope="typed transformations instead of one similarity score",
    ),
    UpstreamContract(
        repository="thebrazenbeard/trek-data-core",
        pinned_commit="58f25f8c45e8379df0ef7c7b5db546e037d1c050",
        relationship="METHODOLOGY_DONOR",
        compatibility_scope="evidence-bound behavioral interpretation without mind-reading",
    ),
    UpstreamContract(
        repository="thebrazenbeard/mediaphile",
        pinned_commit="5540d7e2f0b07c0e91a1158c9c00f63be9d9587a",
        relationship="PATTERN_CORPUS_DONOR",
        compatibility_scope="longitudinal behavioral pattern vocabulary and contrast cases",
    ),
)


def evaluate_upstreams(
    observed_heads: Mapping[str, str],
    *,
    contracts: tuple[UpstreamContract, ...] = UPSTREAM_CONTRACTS,
) -> UpstreamReport:
    if not isinstance(observed_heads, Mapping):
        raise ValueError("observed_heads must be a mapping")
    for repository, commit in observed_heads.items():
        if not isinstance(repository, str) or not repository:
            raise ValueError("observed repository names must be non-empty strings")
        if not isinstance(commit, str) or not commit:
            raise ValueError("observed commit values must be non-empty strings")

    results: list[UpstreamResult] = []
    for contract in contracts:
        observed = observed_heads.get(contract.repository)
        if observed is None:
            status = UpstreamStatus.UNKNOWN
        elif observed == contract.pinned_commit:
            status = UpstreamStatus.CURRENT
        else:
            status = UpstreamStatus.MOVED

        results.append(
            UpstreamResult(
                repository=contract.repository,
                pinned_commit=contract.pinned_commit,
                observed_commit=observed,
                relationship=contract.relationship,
                status=status,
            )
        )

    if any(item.status is UpstreamStatus.MOVED for item in results):
        overall = UpstreamStatus.MOVED
    elif any(item.status is UpstreamStatus.UNKNOWN for item in results):
        overall = UpstreamStatus.UNKNOWN
    else:
        overall = UpstreamStatus.CURRENT

    return UpstreamReport(status=overall, results=tuple(results))
