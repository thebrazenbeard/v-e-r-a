from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BehavioralSourceContract:
    repository: str
    commit: str
    relationship: str
    source_paths: tuple[str, ...]
    use: str


TREK_DATA_CORE = BehavioralSourceContract(
    repository="thebrazenbeard/trek-data-core",
    commit="58f25f8c45e8379df0ef7c7b5db546e037d1c050",
    relationship="METHODOLOGY_DONOR",
    source_paths=(
        "TREK_RESEARCH_METHOD.md",
        "TREK_ROLE_CATALOG.md",
        "TREK_REPO_PROTOCOL.md",
    ),
    use=(
        "Observed utterance/behavior supports an interpretation but does not prove the "
        "speaker's hidden motive or the truth of what was said."
    ),
)

MEDIAPHILE = BehavioralSourceContract(
    repository="thebrazenbeard/mediaphile",
    commit="5540d7e2f0b07c0e91a1158c9c00f63be9d9587a",
    relationship="PATTERN_CORPUS_DONOR",
    source_paths=(
        "films/the-matrix-1999.md",
        "shows/its-always-sunny-in-philadelphia/episodes/s05e10-the-dennis-system.md",
        "shows/its-always-sunny-in-philadelphia/episodes/s07e08-the-anti-social-network.md",
    ),
    use=(
        "Longitudinal fictional character material supplies candidate behavioral-pattern "
        "vocabulary and contrast cases, not evidence about real people's motives."
    ),
)
