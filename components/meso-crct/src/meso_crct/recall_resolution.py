"""Resolve multiple cue-bound recall influences without scalar summation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math
from typing import Iterable

from .recall import RecallInfluence


def _unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return min(1.0, max(0.0, value))


class RecallDisposition(StrEnum):
    APPROACH = "approach"
    AVOID = "avoid"
    CONFLICT = "conflict"
    NEUTRAL = "neutral"


class RecallEventMismatch(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class RecallResolutionPolicy:
    minimum_directional_support: float = 0.20
    conflict_margin: float = 0.10

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "minimum_directional_support",
            _unit(
                self.minimum_directional_support,
                name="minimum_directional_support",
            ),
        )
        object.__setattr__(
            self,
            "conflict_margin",
            _unit(self.conflict_margin, name="conflict_margin"),
        )


_RECALL_RESOLUTION_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class RecallResolution:
    disposition: RecallDisposition
    cue_event_id: str | None
    approach_support: float
    learned_avoidance_support: float
    dominant_support: float
    memory_revision_ids: tuple[str, ...]

    def __init__(
        self,
        *,
        disposition: RecallDisposition,
        cue_event_id: str | None,
        approach_support: float,
        learned_avoidance_support: float,
        dominant_support: float,
        memory_revision_ids: tuple[str, ...],
        _token: object | None = None,
    ) -> None:
        if _token is not _RECALL_RESOLUTION_TOKEN:
            raise TypeError(
                "RecallResolution must be created by resolve_recall_influences"
            )
        object.__setattr__(self, "disposition", disposition)
        object.__setattr__(self, "cue_event_id", cue_event_id)
        object.__setattr__(
            self,
            "approach_support",
            _unit(approach_support, name="approach_support"),
        )
        object.__setattr__(
            self,
            "learned_avoidance_support",
            _unit(
                learned_avoidance_support,
                name="learned_avoidance_support",
            ),
        )
        object.__setattr__(
            self,
            "dominant_support",
            _unit(dominant_support, name="dominant_support"),
        )
        object.__setattr__(
            self,
            "memory_revision_ids",
            tuple(memory_revision_ids),
        )


def resolve_recall_influences(
    influences: Iterable[RecallInfluence],
    *,
    policy: RecallResolutionPolicy | None = None,
) -> RecallResolution:
    """Resolve a same-event recall coalition using strongest support per direction."""
    policy = RecallResolutionPolicy() if policy is None else policy
    influences = tuple(influences)

    if not influences:
        return RecallResolution(
            disposition=RecallDisposition.NEUTRAL,
            cue_event_id=None,
            approach_support=0.0,
            learned_avoidance_support=0.0,
            dominant_support=0.0,
            memory_revision_ids=(),
            _token=_RECALL_RESOLUTION_TOKEN,
        )

    event_ids = {item.cue_event_id for item in influences}
    if len(event_ids) != 1:
        raise RecallEventMismatch(
            "recall influences from different cue events cannot be resolved together"
        )
    cue_event_id = influences[0].cue_event_id

    approach = max(item.approach_support for item in influences)
    avoid = max(item.learned_avoidance_support for item in influences)
    threshold = policy.minimum_directional_support
    approach_active = approach >= threshold
    avoid_active = avoid >= threshold

    if approach_active and avoid_active:
        if abs(approach - avoid) <= policy.conflict_margin:
            disposition = RecallDisposition.CONFLICT
        elif approach > avoid:
            disposition = RecallDisposition.APPROACH
        else:
            disposition = RecallDisposition.AVOID
    elif approach_active:
        disposition = RecallDisposition.APPROACH
    elif avoid_active:
        disposition = RecallDisposition.AVOID
    else:
        disposition = RecallDisposition.NEUTRAL

    return RecallResolution(
        disposition=disposition,
        cue_event_id=cue_event_id,
        approach_support=approach,
        learned_avoidance_support=avoid,
        dominant_support=max(approach, avoid),
        memory_revision_ids=tuple(
            sorted({item.memory_revision_id for item in influences})
        ),
        _token=_RECALL_RESOLUTION_TOKEN,
    )
