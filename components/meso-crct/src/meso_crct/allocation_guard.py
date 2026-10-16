"""Governed response to long-horizon allocation pathology.

The guard can temporarily redirect one non-protective selection toward a
neglected goal that is currently non-quiescent. It never overrides a protective
selection and never manufactures relevance for a quiescent goal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .allocation import AllocationAudit, GoalObligation
from .arbitration import ArbitrationMode
from .selection import (
    SelectionPolicy,
    SelectionResult,
    TargetState,
    select_target,
)


@dataclass(frozen=True, slots=True)
class AllocationGuardResult:
    base_selection: SelectionResult
    final_selection: SelectionResult
    guard_applied: bool
    reason: str | None
    rebalanced_goal_id: str | None


def select_with_allocation_guard(
    targets: tuple[TargetState, ...] | list[TargetState],
    *,
    audit: AllocationAudit,
    obligations: Iterable[GoalObligation],
    policy: SelectionPolicy | None = None,
) -> AllocationGuardResult:
    """Apply one explicit rebalancing opportunity after ordinary selection."""
    base = select_target(targets, policy=policy)

    if base.used_protective_override:
        return AllocationGuardResult(
            base_selection=base,
            final_selection=base,
            guard_applied=False,
            reason="protective_override",
            rebalanced_goal_id=None,
        )

    if "goal_neglect" not in audit.flags:
        return AllocationGuardResult(
            base_selection=base,
            final_selection=base,
            guard_applied=False,
            reason=None,
            rebalanced_goal_id=None,
        )

    shares = dict(audit.goal_shares)
    obligations_by_id = {item.goal_id: item for item in obligations}
    neglected = []
    for goal_id in audit.neglected_goals:
        obligation = obligations_by_id.get(goal_id)
        if obligation is None:
            continue
        deficit = obligation.minimum_nonprotective_share - shares.get(goal_id, 0.0)
        neglected.append((goal_id, deficit))

    neglected.sort(key=lambda item: (-item[1], item[0]))
    evaluations = {item.target_id: item for item in base.evaluations}

    for goal_id, _ in neglected:
        evaluation = evaluations.get(goal_id)
        if evaluation is None:
            continue
        if evaluation.decision.mode not in {
            ArbitrationMode.ORIENTING,
            ArbitrationMode.MOTIVATIONAL,
            ArbitrationMode.EPISTEMIC,
        }:
            continue

        final = SelectionResult(
            selected_target_id=goal_id,
            selected_decision=evaluation.decision,
            evaluations=base.evaluations,
            used_protective_override=False,
        )
        return AllocationGuardResult(
            base_selection=base,
            final_selection=final,
            guard_applied=(base.selected_target_id != goal_id),
            reason="goal_obligation_rebalance",
            rebalanced_goal_id=goal_id,
        )

    return AllocationGuardResult(
        base_selection=base,
        final_selection=base,
        guard_applied=False,
        reason="no_currently_relevant_neglected_goal",
        rebalanced_goal_id=None,
    )
