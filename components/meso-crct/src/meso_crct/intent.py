"""Non-executable action-intent proposals for MESO-CRCT."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math

from .tendency import ActionTendency, ActionTendencyKind


def _unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return min(1.0, max(0.0, value))


class IntentKind(StrEnum):
    WITHDRAW = "withdraw"
    APPROACH = "approach"
    INSPECT = "inspect"
    HOLD = "hold"


@dataclass(frozen=True, slots=True)
class IntentPolicy:
    minimum_committed_strength: float = 0.20

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "minimum_committed_strength",
            _unit(
                self.minimum_committed_strength,
                name="minimum_committed_strength",
            ),
        )


_INTENT_PROPOSAL_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class IntentProposal:
    target_id: str | None
    kind: IntentKind
    strength: float
    source_tendency: str
    source: str
    effect_authorized: bool

    def __init__(
        self,
        *,
        target_id: str | None,
        kind: IntentKind,
        strength: float,
        source_tendency: str,
        source: str,
        _token: object | None = None,
    ) -> None:
        if _token is not _INTENT_PROPOSAL_TOKEN:
            raise TypeError("IntentProposal must be created by propose_action_intent")
        if target_id is not None and not target_id.strip():
            raise ValueError("target_id must be non-empty when present")
        if not source_tendency.strip():
            raise ValueError("source_tendency must be non-empty")
        if not source.strip():
            raise ValueError("source must be non-empty")
        object.__setattr__(self, "target_id", target_id)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "strength", _unit(strength, name="strength"))
        object.__setattr__(self, "source_tendency", source_tendency)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "effect_authorized", False)

    @property
    def can_execute(self) -> bool:
        return False


def propose_action_intent(
    tendency: ActionTendency,
    *,
    policy: IntentPolicy | None = None,
) -> IntentProposal:
    """Convert a typed tendency into a non-executable proposal."""
    policy = IntentPolicy() if policy is None else policy

    if (
        tendency.target_id is None
        or tendency.kind is ActionTendencyKind.UNCOMMITTED
        or tendency.strength < policy.minimum_committed_strength
    ):
        return IntentProposal(
            target_id=tendency.target_id,
            kind=IntentKind.HOLD,
            strength=tendency.strength,
            source_tendency=tendency.kind.value,
            source=tendency.source,
            _token=_INTENT_PROPOSAL_TOKEN,
        )

    if tendency.kind in {
        ActionTendencyKind.PROTECTIVE_WITHDRAW,
        ActionTendencyKind.LEARNED_WITHDRAW,
    }:
        kind = IntentKind.WITHDRAW
    elif tendency.kind is ActionTendencyKind.APPROACH:
        kind = IntentKind.APPROACH
    elif tendency.kind is ActionTendencyKind.INSPECT:
        kind = IntentKind.INSPECT
    else:
        kind = IntentKind.HOLD

    return IntentProposal(
        target_id=tendency.target_id,
        kind=kind,
        strength=tendency.strength,
        source_tendency=tendency.kind.value,
        source=tendency.source,
        _token=_INTENT_PROPOSAL_TOKEN,
    )
