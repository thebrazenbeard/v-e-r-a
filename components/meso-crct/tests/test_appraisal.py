import pytest

from meso_crct import (
    AppraisedTarget,
    HomeostaticState,
    NeedAffordance,
    NeedAxis,
    RewardState,
    SemanticEvidence,
    TargetAppraisalInput,
    build_target_appraisal,
)


def test_self_asserted_importance_does_not_enter_semantic_relevance():
    appraised = build_target_appraisal(
        TargetAppraisalInput(
            target_id="claim",
            semantic_evidence=SemanticEvidence(
                source_asserts_importance=True,
            ),
        )
    )
    assert appraised.state.salience.semantic_relevance == 0.0
    assert appraised.semantic.untrusted_importance_claim


def test_grounded_semantic_relation_enters_salience():
    appraised = build_target_appraisal(
        TargetAppraisalInput(
            target_id="goal-related",
            semantic_evidence=SemanticEvidence(goal_relevance=0.8),
        )
    )
    assert appraised.state.salience.semantic_relevance == 0.8
    assert appraised.semantic.grounded_drivers == ("goal_relevance",)


def test_novelty_without_learning_progress_does_not_create_epistemic_priority():
    appraised = build_target_appraisal(
        TargetAppraisalInput(
            target_id="noise",
            novelty=1.0,
            learning_progress=0.0,
        )
    )
    assert appraised.state.learning.novelty == 1.0
    assert appraised.state.salience.epistemic_value == 0.0


def test_homeostatic_deficit_can_raise_incentive_without_pleasure():
    appraised = build_target_appraisal(
        TargetAppraisalInput(
            target_id="resource",
            base_incentive_salience=0.2,
            reward=RewardState(pleasure=0.0),
            homeostasis=HomeostaticState(
                axes=(
                    NeedAxis(
                        "energy",
                        setpoint=0.8,
                        current_level=0.2,
                    ),
                )
            ),
            affordances=(
                NeedAffordance(
                    "energy",
                    corrective_strength=1.0,
                ),
            ),
        )
    )
    assert appraised.state.salience.incentive_salience > 0.2
    assert appraised.state.reward.pleasure == 0.0
    assert appraised.homeostatic.dominant_need == "energy"


def test_maximum_pleasure_does_not_manufacture_other_salience():
    appraised = build_target_appraisal(
        TargetAppraisalInput(
            target_id="pleasant",
            reward=RewardState(pleasure=10.0),
        )
    )
    assert appraised.state.salience.perceptual_salience == 0.0
    assert appraised.state.salience.semantic_relevance == 0.0
    assert appraised.state.salience.motivational_salience == 0.0
    assert appraised.state.salience.incentive_salience == 0.0
    assert appraised.state.salience.epistemic_value == 0.0


def test_attentional_priority_is_always_downstream_zero_at_appraisal():
    appraised = build_target_appraisal(
        TargetAppraisalInput(
            target_id="important",
            semantic_evidence=SemanticEvidence(context_relevance=1.0),
            perceptual_salience=1.0,
            base_motivational_salience=1.0,
        )
    )
    assert appraised.state.salience.attentional_priority == 0.0


def test_appraised_target_converts_to_selection_target_without_mutation():
    appraised = build_target_appraisal(
        TargetAppraisalInput(
            target_id="candidate",
            semantic_evidence=SemanticEvidence(context_relevance=0.7),
        )
    )
    target = appraised.as_target_state()
    assert target.target_id == "candidate"
    assert target.state == appraised.state


def test_empty_target_id_fails():
    with pytest.raises(ValueError):
        TargetAppraisalInput(target_id="   ")


def test_appraised_target_direct_construction_is_blocked():
    genuine = build_target_appraisal(
        TargetAppraisalInput(target_id="genuine")
    )
    with pytest.raises(TypeError):
        AppraisedTarget(
            target_id="fake",
            state=genuine.state,
            semantic=genuine.semantic,
            homeostatic=genuine.homeostatic,
        )
