from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class Sign:
    id: str
    form: str
    modality: str


@dataclass(frozen=True)
class Source:
    id: str
    description: str
    locator: str | None = None
    citation: str | None = None
    published_year: int | None = None


@dataclass(frozen=True)
class InterpretationRelation:
    id: str
    left_id: str
    right_id: str
    kind: str
    source_id: str


@dataclass(frozen=True)
class Interpretation:
    id: str
    sign_id: str
    meaning: str
    source_id: str
    supersedes_id: str | None = None
    required_tags: FrozenSet[str] = frozenset()
    excluded_tags: FrozenSet[str] = frozenset()

    @property
    def specificity(self) -> int:
        return len(self.required_tags) + len(self.excluded_tags)

    def matches(self, tags: set[str]) -> bool:
        return self.required_tags.issubset(tags) and self.excluded_tags.isdisjoint(tags)
