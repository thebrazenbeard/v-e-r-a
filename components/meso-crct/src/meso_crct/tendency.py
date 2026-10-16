"""Typed action tendency derived after target selection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math

from .arbitration import ArbitrationMode
from .recall import RecallInfluence
from .recall_resolution import RecallDisposition, RecallResolution
from .selection import SelectionResult


def _unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return min(1.0, max(0.0, value))


class ActionTendencyKind(StrEnum):
    PROTECTIVE_WITHDRAW = "protective_withdraw"
    LEARNED_WITHDRAW = "learned_withdraw"
    APPROACH = "approach"
    INSPECT = "inspect"
    UNCOMMITTED = "uncommitted"


@dataclass(frozen=True, slots=True)
class ActionTendencyPolicy:
    minimum_recall_directional_support: float = 0.20

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "minimum_recall_directional_support",
            _unit(
                self.minimum_recall_directional_support,
                name="minimum_recall_directional_support",
            ),
        )


_ACTION_TENDENCY_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class ActionTendency:
    target_id: str | None
    kind: ActionTendencyKind
    strength: float
    source: str
    selection_mode: str | None
    recall_revision_id: str | None
    recall_revision_ids: tuple[str, ...]
    recall_event_id: str | None

    def __init__(
        self,
        *,
        target_id: str | None,
        kind: ActionTendencyKind,
        strength: float,
        source: str,
        selection_mode: str | None,
        recall_revision_id: str | None = None,
        recall_revision_ids: tuple[str, ...] = (),
        recall_event_id: str | None = None,
        _token: object | None = None,
    ) -> None:
        if _token is not _ACTION_TENDENCY_TOKEN:
            raise TypeError("ActionTendency must be created by derive_action_tendency")
        if target_id is not None and not target_id.strip():
            raise ValueError("target_id must be non-empty when present")
        if not source.strip():
            raise ValueError("source must be non-empty")
        object.__setattr__(self, "target_id", target_id)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "strength", _unit(strength, name="strength"))
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "selection_mode", selection_mode)
        object.__setattr__(self, "recall_revision_id", recall_revision_id)
        object.__setattr__(self, "recall_revision_ids", tuple(recall_revision_ids))
        object.__setattr__(self, "recall_event_id", recall_event_id)


def _make(
    *,
    target_id: str | None,
    kind: ActionTendencyKind,
    strength: float,
    source: str,
    selection_mode: str | None,
    recall: RecallInfluence | None = None,
    resolution: RecallResolution | None = None,
) -> ActionTendency:
    if recall is not None:
        revision_id = recall.memory_revision_id
        revision_ids = (recall.memory_revision_id,)
        event_id = recall.cue_event_id
    elif resolution is not None:
        revision_id = None
        revision_ids = resolution.memory_revision_ids
        event_id = resolution.cue_event_id
    else:
        revision_id = None
        revision_ids = ()
        event_id = None

    return ActionTendency(
        target_id=target_id,
        kind=kind,
        strength=strength,
        source=source,
        selection_mode=selection_mode,
        recall_revision_id=revision_id,
        recall_revision_ids=revision_ids,
        recall_event_id=event_id,
        _token=_ACTION_TENDENCY_TOKEN,
    )


def derive_action_tendency(
    selection: SelectionResult,
    *,
    recall: RecallInfluence | None = None,
    recall_resolution: RecallResolution | None = None,
    recall_target_id: str | None = None,
    policy: ActionTendencyPolicy | None = None,
) -> ActionTendency:
    """Derive direction after selection without mutating circuit state."""
    policy = ActionTendencyPolicy() if policy is None else policy

    if recall is not None and recall_resolution is not None:
        raise ValueError("provide either recall or recall_resolution, not both")

    has_recall_evidence = recall is not None or recall_resolution is not None

    if not selection.selected:
        if has_recall_evidence or recall_target_id is not None:
            raise ValueError("recall direction cannot bind when no target is selected")
        return _make(
            target_id=None,
            kind=ActionTendencyKind.UNCOMMITTED,
            strength=0.0,
            source="no_selection",
            selection_mode=None,
        )

    target_id = selection.selected_target_id
    decision = selection.selected_decision
    assert target_id is not None
    assert decision is not None

    if has_recall_evidence:
        if recall_target_id != target_id:
            raise ValueError("recall evidence must be bound to the selected target")
    elif recall_target_id is not None:
        raise ValueError("recall_target_id requires recall evidence")

    if decision.mode is ArbitrationMode.PROTECTIVE:
        return _make(
            target_id=target_id,
            kind=ActionTendencyKind.PROTECTIVE_WITHDRAW,
            strength=decision.priority,
            source="protective_state",
            selection_mode=decision.mode.value,
        )

    if recall_resolution is not None:
        if recall_resolution.disposition is RecallDisposition.AVOID:
            return _make(
                target_id=target_id,
                kind=ActionTendencyKind.LEARNED_WITHDRAW,
                strength=recall_resolution.learned_avoidance_support,
                source="learned_association_resolution",
                selection_mode=decision.mode.value,
                resolution=recall_resolution,
            )
        if recall_resolution.disposition is RecallDisposition.APPROACH:
            return _make(
                target_id=target_id,
                kind=ActionTendencyKind.APPROACH,
                strength=recall_resolution.approach_support,
                source="learned_association_resolution",
                selection_mode=decision.mode.value,
                resolution=recall_resolution,
            )
        if recall_resolution.disposition is RecallDisposition.CONFLICT:
            return _make(
                target_id=target_id,
                kind=ActionTendencyKind.UNCOMMITTED,
                strength=recall_resolution.dominant_support,
                source="recall_direction_conflict",
                selection_mode=decision.mode.value,
                resolution=recall_resolution,
            )

    if recall is not None:
        threshold = policy.minimum_recall_directional_support
        if recall.learned_avoidance_support >= threshold:
            return _make(
                target_id=target_id,
                kind=ActionTendencyKind.LEARNED_WITHDRAW,
                strength=recall.learned_avoidance_support,
                source="learned_association",
                selection_mode=decision.mode.value,
                recall=recall,
            )
        if recall.approach_support >= threshold:
            return _make(
                target_id=target_id,
                kind=ActionTendencyKind.APPROACH,
                strength=recall.approach_support,
                source="learned_association",
                selection_mode=decision.mode.value,
                recall=recall,
            )

    if (
        decision.mode is ArbitrationMode.MOTIVATIONAL
        and decision.dominant_driver == "incentive_salience"
    ):
        return _make(
            target_id=target_id,
            kind=ActionTendencyKind.APPROACH,
            strength=decision.priority,
            source="incentive_salience",
            selection_mode=decision.mode.value,
        )

    if decision.mode in {
        ArbitrationMode.EPISTEMIC,
        ArbitrationMode.ORIENTING,
    }:
        return _make(
            target_id=target_id,
            kind=ActionTendencyKind.INSPECT,
            strength=decision.priority,
            source=decision.dominant_driver or decision.mode.value,
            selection_mode=decision.mode.value,
        )

    return _make(
        target_id=target_id,
        kind=ActionTendencyKind.UNCOMMITTED,
        strength=decision.priority,
        source="generic_motivational_salience",
        selection_mode=decision.mode.value,
    )
