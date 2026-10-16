import pytest

from meso_crct import (
    ActionTendencyKind,
    CircuitState,
    RecallDisposition,
    RecallResolutionPolicy,
    SalienceState,
    TargetState,
    derive_action_tendency,
    resolve_recall_influences,
    select_target,
)

from test_recall_resolution import cue_receipt, recall_for


def selected_target():
    return select_target([
        TargetState(
            "target",
            CircuitState(
                salience=SalienceState(motivational_salience=0.9),
            ),
        )
    ])


def test_conflicting_recall_keeps_action_direction_uncommitted():
    cue = cue_receipt()
    positive = recall_for("positive-tendency", prediction_error=0.8, cue_receipt=cue)
    negative = recall_for("negative-tendency", prediction_error=-0.75, cue_receipt=cue)
    resolution = resolve_recall_influences(
        [positive, negative],
        policy=RecallResolutionPolicy(conflict_margin=0.10),
    )
    assert resolution.disposition is RecallDisposition.CONFLICT

    tendency = derive_action_tendency(
        selected_target(),
        recall_resolution=resolution,
        recall_target_id="target",
    )
    assert tendency.kind is ActionTendencyKind.UNCOMMITTED
    assert tendency.source == "recall_direction_conflict"
    assert len(tendency.recall_revision_ids) == 2


def test_resolved_avoidance_becomes_learned_withdrawal():
    cue = cue_receipt()
    positive = recall_for("positive-weak", prediction_error=0.3, cue_receipt=cue)
    negative = recall_for("negative-strong", prediction_error=-0.9, cue_receipt=cue)
    resolution = resolve_recall_influences([positive, negative])

    tendency = derive_action_tendency(
        selected_target(),
        recall_resolution=resolution,
        recall_target_id="target",
    )
    assert tendency.kind is ActionTendencyKind.LEARNED_WITHDRAW
    assert tendency.strength == pytest.approx(0.9)


def test_resolved_approach_becomes_approach():
    cue = cue_receipt()
    positive = recall_for("positive-strong", prediction_error=0.9, cue_receipt=cue)
    negative = recall_for("negative-weak", prediction_error=-0.3, cue_receipt=cue)
    resolution = resolve_recall_influences([positive, negative])

    tendency = derive_action_tendency(
        selected_target(),
        recall_resolution=resolution,
        recall_target_id="target",
    )
    assert tendency.kind is ActionTendencyKind.APPROACH
    assert tendency.strength == pytest.approx(0.9)
