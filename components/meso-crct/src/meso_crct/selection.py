"""Multi-target selection for MESO-CRCT.

Per-target arbitration preserves typed signal semantics. This module chooses
among targets without collapsing their state into a global weighted utility.
Protection is a hard override; non-protective mode precedence is explicit policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .arbitration import ArbitrationDecision, ArbitrationMode, arbitrate
from .circuit import CircuitState


_SELECTABLE_NONPROTECTIVE = frozenset({
    ArbitrationMode.MOTIVATIONAL,
    ArbitrationMode.EPISTEMIC,
    ArbitrationMode.ORIENTING,
})


@dataclass(frozen=True, slots=True)
class SelectionPolicy:
    nonprotective_precedence: tuple[ArbitrationMode, ...] = (
        ArbitrationMode.MOTIVATIONAL,
        ArbitrationMode.EPISTEMIC,
        ArbitrationMode.ORIENTING,
    )

    def __post_init__(self) -> None:
        if len(self.nonprotective_precedence) != len(_SELECTABLE_NONPROTECTIVE):
            raise ValueError("nonprotective precedence must name each selectable mode once")
        if set(self.nonprotective_precedence) != _SELECTABLE_NONPROTECTIVE:
            raise ValueError(
                "nonprotective precedence must contain motivational, epistemic, "
                "and orienting modes exactly once"
            )


@dataclass(frozen=True, slots=True)
class TargetState:
    target_id: str
    state: CircuitState = field(default_factory=CircuitState)

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ValueError("target_id must be non-empty")


@dataclass(frozen=True, slots=True)
class TargetEvaluation:
    target_id: str
    decision: ArbitrationDecision


@dataclass(frozen=True, slots=True)
class SelectionResult:
    selected_target_id: str | None
    selected_decision: ArbitrationDecision | None
    evaluations: tuple[TargetEvaluation, ...]
    used_protective_override: bool

    @property
    def selected(self) -> bool:
        return self.selected_target_id is not None


def select_target(
    targets: tuple[TargetState, ...] | list[TargetState],
    *,
    policy: SelectionPolicy | None = None,
) -> SelectionResult:
    """Choose one target by typed mode precedence, then within-mode priority."""
    if not targets:
        raise ValueError("at least one target is required")

    policy = SelectionPolicy() if policy is None else policy
    evaluations = tuple(
        TargetEvaluation(
            target_id=target.target_id,
            decision=arbitrate(target.state),
        )
        for target in targets
    )

    protective = tuple(
        item
        for item in evaluations
        if item.decision.mode is ArbitrationMode.PROTECTIVE
    )
    if protective:
        selected = min(
            protective,
            key=lambda item: (-item.decision.priority, item.target_id),
        )
        return SelectionResult(
            selected_target_id=selected.target_id,
            selected_decision=selected.decision,
            evaluations=evaluations,
            used_protective_override=True,
        )

    selectable = tuple(
        item
        for item in evaluations
        if item.decision.mode in _SELECTABLE_NONPROTECTIVE
    )
    if not selectable:
        return SelectionResult(
            selected_target_id=None,
            selected_decision=None,
            evaluations=evaluations,
            used_protective_override=False,
        )

    mode_rank = {
        mode: index
        for index, mode in enumerate(policy.nonprotective_precedence)
    }
    selected = min(
        selectable,
        key=lambda item: (
            mode_rank[item.decision.mode],
            -item.decision.priority,
            item.target_id,
        ),
    )
    return SelectionResult(
        selected_target_id=selected.target_id,
        selected_decision=selected.decision,
        evaluations=evaluations,
        used_protective_override=False,
    )
