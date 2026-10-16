"""Closed reference control loop for MESO-CRCT target allocation."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Iterable

from .allocation import (
    AllocationAudit,
    AllocationWindow,
    GoalObligation,
    audit_allocation_window,
)
from .allocation_guard import AllocationGuardResult, select_with_allocation_guard
from .selection import SelectionPolicy, TargetState


def _unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return min(1.0, max(0.0, value))


@dataclass(frozen=True, slots=True)
class ControlPolicy:
    selection_policy: SelectionPolicy = field(default_factory=SelectionPolicy)
    crowdout_fraction: float = 0.75
    selected_window_size: int = 20

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "crowdout_fraction",
            _unit(self.crowdout_fraction, name="crowdout_fraction"),
        )
        if self.selected_window_size < 1:
            raise ValueError("selected_window_size must be >= 1")


@dataclass(frozen=True, slots=True)
class ControlState:
    allocation_window: AllocationWindow = field(default_factory=AllocationWindow)


@dataclass(frozen=True, slots=True)
class ControlStepResult:
    guard_result: AllocationGuardResult
    audit_before: AllocationAudit
    audit_after: AllocationAudit


def _trim_selected_window(
    window: AllocationWindow,
    selected_window_size: int,
) -> AllocationWindow:
    if len(window.samples) <= selected_window_size:
        return window
    return AllocationWindow(
        samples=window.samples[-selected_window_size:],
        no_selection_cycles=window.no_selection_cycles,
    )


def control_step(
    state: ControlState,
    targets: tuple[TargetState, ...] | list[TargetState],
    *,
    obligations: Iterable[GoalObligation],
    policy: ControlPolicy | None = None,
) -> tuple[ControlState, ControlStepResult]:
    """Run one closed local-selection / allocation-health control step."""
    policy = ControlPolicy() if policy is None else policy
    obligations = tuple(obligations)

    audit_before = audit_allocation_window(
        state.allocation_window,
        obligations,
        crowdout_fraction=policy.crowdout_fraction,
    )

    guard_result = select_with_allocation_guard(
        targets,
        audit=audit_before,
        obligations=obligations,
        policy=policy.selection_policy,
    )

    window = state.allocation_window.record(guard_result.final_selection)
    window = _trim_selected_window(window, policy.selected_window_size)

    audit_after = audit_allocation_window(
        window,
        obligations,
        crowdout_fraction=policy.crowdout_fraction,
    )

    return (
        ControlState(allocation_window=window),
        ControlStepResult(
            guard_result=guard_result,
            audit_before=audit_before,
            audit_after=audit_after,
        ),
    )
