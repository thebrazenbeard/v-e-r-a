"""Canonical current-decision cycle for MESO-CRCT.

This composes current appraisal, cue-bound recall, rolling allocation control,
action tendency, and non-executable intent. Durable learning remains owned by
the separate experience transaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .allocation import GoalObligation
from .appraisal import AppraisedTarget
from .control import ControlPolicy, ControlState, ControlStepResult, control_step
from .intent import IntentPolicy, IntentProposal, propose_action_intent
from .memory import AssociationMemory
from .provenance import state_fingerprint
from .recall import RecallInfluence, RecallLedger, apply_recall_motivation
from .recall_resolution import (
    RecallResolution,
    RecallResolutionPolicy,
    resolve_recall_influences,
)
from .review import (
    AssociationQuarantinedError,
    AssociationReviewStaleError,
    ReviewAdmission,
)
from .selection import TargetState
from .tendency import (
    ActionTendency,
    ActionTendencyPolicy,
    derive_action_tendency,
)


class RecallStateMismatch(ValueError):
    pass


class RecallMemoryMismatch(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class TargetRecallBinding:
    target_id: str
    memory: AssociationMemory
    influences: tuple[RecallInfluence, ...]

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ValueError("target_id must be non-empty")
        if not self.influences:
            raise ValueError("recall binding must contain at least one influence")


@dataclass(frozen=True, slots=True)
class DecisionCyclePolicy:
    control: ControlPolicy = field(default_factory=ControlPolicy)
    recall_resolution: RecallResolutionPolicy = field(
        default_factory=RecallResolutionPolicy
    )
    tendency: ActionTendencyPolicy = field(default_factory=ActionTendencyPolicy)
    intent: IntentPolicy = field(default_factory=IntentPolicy)


@dataclass(frozen=True, slots=True)
class DecisionCycleState:
    control: ControlState = field(default_factory=ControlState)
    recall_ledger: RecallLedger = field(default_factory=RecallLedger)


@dataclass(frozen=True, slots=True)
class TargetRecallResolution:
    target_id: str
    resolution: RecallResolution


@dataclass(frozen=True, slots=True)
class DecisionCycleResult:
    control_step: ControlStepResult
    tendency: ActionTendency
    intent: IntentProposal
    recall_resolutions: tuple[TargetRecallResolution, ...]


def run_decision_cycle(
    state: DecisionCycleState,
    appraised_targets: Iterable[AppraisedTarget],
    *,
    obligations: Iterable[GoalObligation] = (),
    recall_bindings: Iterable[TargetRecallBinding] = (),
    policy: DecisionCyclePolicy | None = None,
) -> tuple[DecisionCycleState, DecisionCycleResult]:
    """Run one canonical current-decision cycle without durable learning."""
    policy = DecisionCyclePolicy() if policy is None else policy
    appraised_targets = tuple(appraised_targets)
    obligations = tuple(obligations)
    recall_bindings = tuple(recall_bindings)

    if not appraised_targets:
        raise ValueError("at least one appraised target is required")

    target_ids = [item.target_id for item in appraised_targets]
    if len(target_ids) != len(set(target_ids)):
        raise ValueError("appraised target IDs must be unique")

    binding_ids = [item.target_id for item in recall_bindings]
    if len(binding_ids) != len(set(binding_ids)):
        raise ValueError("at most one recall binding is allowed per target")

    current_states = {
        item.target_id: item.state
        for item in appraised_targets
    }
    ledger = state.recall_ledger
    resolutions: dict[str, RecallResolution] = {}

    for binding in recall_bindings:
        if binding.target_id not in current_states:
            raise ValueError(
                f"recall binding target is not appraised: {binding.target_id}"
            )

        current = current_states[binding.target_id]
        current_fingerprint = state_fingerprint(current)

        for influence in binding.influences:
            if influence.cue_after_fingerprint != current_fingerprint:
                raise RecallStateMismatch(
                    "recall cue receipt does not match current appraised target state"
                )

            current_revision = binding.memory.current(influence.association_id)
            if (
                current_revision is None
                or current_revision.revision_id != influence.memory_revision_id
            ):
                raise RecallMemoryMismatch(
                    "recall influence does not match current association revision"
                )

            admission = binding.memory.reviews.admission(
                association_id=influence.association_id,
                memory_revision_id=current_revision.revision_id,
            )
            if admission is ReviewAdmission.QUARANTINED:
                raise AssociationQuarantinedError(
                    f"association is quarantined: {influence.association_id}"
                )
            if admission is ReviewAdmission.STALE:
                raise AssociationReviewStaleError(
                    f"association review is stale: {influence.association_id}"
                )

            review_record = binding.memory.reviews.current(
                influence.association_id
            )
            expected_review_id = (
                None if review_record is None else review_record.review_id
            )
            if influence.review_record_id != expected_review_id:
                raise RecallMemoryMismatch(
                    "recall influence review snapshot is no longer current"
                )

        resolution = resolve_recall_influences(
            binding.influences,
            policy=policy.recall_resolution,
        )
        resolutions[binding.target_id] = resolution

        for influence in binding.influences:
            current, ledger = apply_recall_motivation(
                current,
                influence,
                ledger,
            )
        current_states[binding.target_id] = current

    targets = [
        TargetState(
            item.target_id,
            current_states[item.target_id],
        )
        for item in appraised_targets
    ]

    updated_control, control_result = control_step(
        state.control,
        targets,
        obligations=obligations,
        policy=policy.control,
    )
    final_selection = control_result.guard_result.final_selection
    selected_id = final_selection.selected_target_id
    selected_resolution = (
        None if selected_id is None else resolutions.get(selected_id)
    )

    tendency = derive_action_tendency(
        final_selection,
        recall_resolution=selected_resolution,
        recall_target_id=selected_id if selected_resolution is not None else None,
        policy=policy.tendency,
    )
    intent = propose_action_intent(
        tendency,
        policy=policy.intent,
    )

    return (
        DecisionCycleState(
            control=updated_control,
            recall_ledger=ledger,
        ),
        DecisionCycleResult(
            control_step=control_result,
            tendency=tendency,
            intent=intent,
            recall_resolutions=tuple(
                TargetRecallResolution(
                    target_id=target_id,
                    resolution=resolution,
                )
                for target_id, resolution in sorted(resolutions.items())
            ),
        ),
    )
