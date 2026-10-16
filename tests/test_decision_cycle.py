import pytest

from meso_crct import (
    ActionTendencyKind,
    AllocationSample,
    AllocationWindow,
    AssociationMemory,
    CircuitState,
    ControlState,
    DecisionCycleState,
    EventSequencer,
    GoalObligation,
    IntentKind,
    LearningState,
    PlasticityPolicy,
    Provenance,
    ProvenanceVerifier,
    AssociationQuarantinedError,
    ReviewEvidenceKind,
    ReviewEvidenceOutcome,
    RecallMemoryMismatch,
    RecallReplayError,
    RecallStateMismatch,
    RewardState,
    SalienceState,
    SemanticEvidence,
    SourceKind,
    TargetAppraisalInput,
    TargetRecallBinding,
    apply_candidate,
    build_target_appraisal,
    evaluate_transition,
    propose_plasticity,
    assess_review_evidence,
    bind_review_evidence,
    quarantine_association,
    recall_association,
    register_review_evidence,
    release_association,
    run_decision_cycle,
)


def verified(source_id):
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=source_id,
        source_revision="v1",
    )
    return ProvenanceVerifier(
        [claim],
        verifier_id="decision-cycle-verifier",
    ).verify(claim)


def recall_for_current_appraisal(
    appraised,
    association_id,
    *,
    prediction_error,
    current_event,
    memory=None,
):
    learning_state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=prediction_error),
    )
    _, learning_event = EventSequencer(f"learn:{association_id}").issue()
    learning_receipt = evaluate_transition(
        before=CircuitState(),
        after=learning_state,
        provenance=verified(f"learn:{association_id}"),
        event=learning_event,
    )
    candidate = propose_plasticity(
        state=learning_state,
        association_id=association_id,
        receipt=learning_receipt,
        policy=PlasticityPolicy(
            maximum_absolute_delta=1.0,
            minimum_salience_gate=0.0,
        ),
    )
    memory = AssociationMemory() if memory is None else memory
    memory = apply_candidate(
        memory,
        candidate,
        expected_version=memory.current_version(association_id),
    )
    cue_receipt = evaluate_transition(
        before=CircuitState(),
        after=appraised.state,
        provenance=verified("current-cue"),
        event=current_event,
    )
    influence = recall_association(
        memory=memory,
        association_id=association_id,
        cue_match=1.0,
        cue_receipt=cue_receipt,
    )
    return memory, influence



def review_assessment(memory, association_id, *, outcome, ref):
    revision = memory.current(association_id)
    assert revision is not None
    items = []
    suffixes = ("a", "b") if outcome is ReviewEvidenceOutcome.SUPPORTS else ("a",)
    for suffix in suffixes:
        evidence_ref = f"{ref}-{suffix}"
        state = CircuitState(
            salience=SalienceState(semantic_relevance=0.5),
        )
        _, event = EventSequencer(evidence_ref).issue()
        receipt = evaluate_transition(
            before=CircuitState(),
            after=state,
            provenance=verified(evidence_ref),
            event=event,
        )
        item = bind_review_evidence(
            association_id=association_id,
            memory_revision_id=revision.revision_id,
            kind=ReviewEvidenceKind.HOLDOUT,
            outcome=outcome,
            evidence_ref=evidence_ref,
            receipt=receipt,
        )
        memory = register_review_evidence(memory, item)
        items.append(item)
    return memory, assess_review_evidence(items)

def cue_appraisal(target_id="cue-target"):
    return build_target_appraisal(
        TargetAppraisalInput(
            target_id=target_id,
            perceptual_salience=0.7,
        )
    )


def test_negative_recall_flows_to_non_executable_withdraw_intent():
    cue = cue_appraisal()
    _, event = EventSequencer("current-cue-stream").issue()
    memory, recall = recall_for_current_appraisal(
        cue,
        "bad-outcome",
        prediction_error=-0.8,
        current_event=event,
    )
    distractor = build_target_appraisal(
        TargetAppraisalInput(
            target_id="distractor",
            novelty=0.95,
            learning_progress=0.95,
        )
    )

    updated, result = run_decision_cycle(
        DecisionCycleState(),
        [cue, distractor],
        recall_bindings=[
            TargetRecallBinding("cue-target", memory, (recall,))
        ],
    )

    assert (
        result.control_step.guard_result.final_selection.selected_target_id
        == "cue-target"
    )
    assert result.tendency.kind is ActionTendencyKind.LEARNED_WITHDRAW
    assert result.intent.kind is IntentKind.WITHDRAW
    assert not result.intent.can_execute
    assert len(updated.recall_ledger.consumed) == 1


def test_conflicting_recall_becomes_hold_intent():
    cue = cue_appraisal()
    _, event = EventSequencer("current-cue-stream").issue()
    shared_memory, positive = recall_for_current_appraisal(
        cue,
        "positive",
        prediction_error=0.8,
        current_event=event,
    )
    shared_memory, negative = recall_for_current_appraisal(
        cue,
        "negative",
        prediction_error=-0.75,
        current_event=event,
        memory=shared_memory,
    )

    _, result = run_decision_cycle(
        DecisionCycleState(),
        [cue],
        recall_bindings=[
            TargetRecallBinding(
                "cue-target",
                shared_memory,
                (positive, negative),
            )
        ],
    )

    assert result.tendency.kind is ActionTendencyKind.UNCOMMITTED
    assert result.intent.kind is IntentKind.HOLD


def test_protection_overrides_positive_recall_in_cycle():
    attractive = cue_appraisal("attractive")
    _, event = EventSequencer("attractive-cue").issue()
    positive_memory, positive = recall_for_current_appraisal(
        attractive,
        "positive",
        prediction_error=0.9,
        current_event=event,
    )
    danger = build_target_appraisal(
        TargetAppraisalInput(
            target_id="danger",
            reward=RewardState(
                hazard=1.0,
                avoidance=1.0,
            ),
        )
    )

    _, result = run_decision_cycle(
        DecisionCycleState(),
        [attractive, danger],
        recall_bindings=[
            TargetRecallBinding("attractive", positive_memory, (positive,))
        ],
    )

    assert (
        result.control_step.guard_result.final_selection.selected_target_id
        == "danger"
    )
    assert result.tendency.kind is ActionTendencyKind.PROTECTIVE_WITHDRAW
    assert result.intent.kind is IntentKind.WITHDRAW
    assert not result.intent.effect_authorized


def test_allocation_guard_is_part_of_canonical_cycle():
    state = DecisionCycleState(
        control=ControlState(
            allocation_window=AllocationWindow(
                samples=tuple(
                    [
                        AllocationSample(
                            "loop",
                            1.0,
                            "incentive_salience",
                        )
                        for _ in range(9)
                    ]
                    + [
                        AllocationSample(
                            "maintenance",
                            0.4,
                            "semantic_relevance",
                        )
                    ]
                )
            )
        )
    )
    loop = build_target_appraisal(
        TargetAppraisalInput(
            target_id="loop",
            base_incentive_salience=1.0,
        )
    )
    maintenance = build_target_appraisal(
        TargetAppraisalInput(
            target_id="maintenance",
            semantic_evidence=SemanticEvidence(context_relevance=0.4),
        )
    )

    _, result = run_decision_cycle(
        state,
        [loop, maintenance],
        obligations=[GoalObligation("maintenance", 0.2)],
    )

    assert result.control_step.guard_result.base_selection.selected_target_id == "loop"
    assert (
        result.control_step.guard_result.final_selection.selected_target_id
        == "maintenance"
    )
    assert result.intent.kind is IntentKind.INSPECT


def test_reusing_same_recall_event_in_later_cycle_fails():
    cue = cue_appraisal()
    _, event = EventSequencer("current-cue-stream").issue()
    memory, recall = recall_for_current_appraisal(
        cue,
        "same-event",
        prediction_error=0.8,
        current_event=event,
    )
    updated, _ = run_decision_cycle(
        DecisionCycleState(),
        [cue],
        recall_bindings=[TargetRecallBinding("cue-target", memory, (recall,))],
    )

    with pytest.raises(RecallReplayError):
        run_decision_cycle(
            updated,
            [cue],
            recall_bindings=[TargetRecallBinding("cue-target", memory, (recall,))],
        )


def test_recall_receipt_must_match_current_appraised_state():
    original = cue_appraisal()
    changed = build_target_appraisal(
        TargetAppraisalInput(
            target_id="cue-target",
            perceptual_salience=0.9,
        )
    )
    _, event = EventSequencer("current-cue-stream").issue()
    memory, recall = recall_for_current_appraisal(
        original,
        "mismatch",
        prediction_error=0.8,
        current_event=event,
    )

    with pytest.raises(RecallStateMismatch):
        run_decision_cycle(
            DecisionCycleState(),
            [changed],
            recall_bindings=[TargetRecallBinding("cue-target", memory, (recall,))],
        )


def test_unknown_recall_target_fails():
    cue = cue_appraisal()
    _, event = EventSequencer("current-cue-stream").issue()
    memory, recall = recall_for_current_appraisal(
        cue,
        "unknown-target",
        prediction_error=0.8,
        current_event=event,
    )
    with pytest.raises(ValueError):
        run_decision_cycle(
            DecisionCycleState(),
            [cue],
            recall_bindings=[TargetRecallBinding("other", memory, (recall,))],
        )



def test_precomputed_recall_is_blocked_if_memory_is_quarantined_afterward():
    cue = cue_appraisal()
    _, event = EventSequencer("quarantine-after-recall").issue()
    memory, recall = recall_for_current_appraisal(
        cue,
        "quarantine-after",
        prediction_error=0.8,
        current_event=event,
    )
    memory, assessment = review_assessment(
        memory,
        "quarantine-after",
        outcome=ReviewEvidenceOutcome.CONTRADICTS,
        ref="negative-transfer-concern",
    )
    quarantined = quarantine_association(
        memory,
        "quarantine-after",
        assessment=assessment,
    )

    with pytest.raises(AssociationQuarantinedError):
        run_decision_cycle(
            DecisionCycleState(),
            [cue],
            recall_bindings=[
                TargetRecallBinding(
                    "cue-target",
                    quarantined,
                    (recall,),
                )
            ],
        )


def test_old_precomputed_recall_is_stale_after_review_state_changes():
    cue = cue_appraisal()
    _, event = EventSequencer("review-change-after-recall").issue()
    memory, recall = recall_for_current_appraisal(
        cue,
        "review-change",
        prediction_error=0.8,
        current_event=event,
    )
    memory, quarantine_review = review_assessment(
        memory,
        "review-change",
        outcome=ReviewEvidenceOutcome.CONTRADICTS,
        ref="review-change-hold",
    )
    memory = quarantine_association(
        memory,
        "review-change",
        assessment=quarantine_review,
    )
    memory, release_review = review_assessment(
        memory,
        "review-change",
        outcome=ReviewEvidenceOutcome.SUPPORTS,
        ref="review-change-clear",
    )
    memory = release_association(
        memory,
        "review-change",
        assessment=release_review,
    )

    with pytest.raises(RecallMemoryMismatch):
        run_decision_cycle(
            DecisionCycleState(),
            [cue],
            recall_bindings=[
                TargetRecallBinding(
                    "cue-target",
                    memory,
                    (recall,),
                )
            ],
        )


def test_precomputed_recall_is_stale_after_association_revision_changes():
    cue = cue_appraisal()
    _, event = EventSequencer("memory-change-after-recall").issue()
    memory, recall = recall_for_current_appraisal(
        cue,
        "memory-change",
        prediction_error=0.6,
        current_event=event,
    )
    learning_state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=0.2),
    )
    _, learning_event = EventSequencer("memory-change-second-learning").issue()
    receipt = evaluate_transition(
        before=CircuitState(),
        after=learning_state,
        provenance=verified("memory-change-second-learning"),
        event=learning_event,
    )
    candidate = propose_plasticity(
        state=learning_state,
        association_id="memory-change",
        receipt=receipt,
        policy=PlasticityPolicy(
            maximum_absolute_delta=1.0,
            minimum_salience_gate=0.0,
        ),
    )
    memory = apply_candidate(
        memory,
        candidate,
        expected_version=1,
    )

    with pytest.raises(RecallMemoryMismatch):
        run_decision_cycle(
            DecisionCycleState(),
            [cue],
            recall_bindings=[
                TargetRecallBinding(
                    "cue-target",
                    memory,
                    (recall,),
                )
            ],
        )

def test_duplicate_appraised_target_ids_fail():
    one = cue_appraisal("duplicate")
    two = cue_appraisal("duplicate")
    with pytest.raises(ValueError):
        run_decision_cycle(
            DecisionCycleState(),
            [one, two],
        )
