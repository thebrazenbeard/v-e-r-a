import math

import pytest

from meso_crct.semantic import SemanticEvidence, assess_semantic_relevance


def test_self_asserted_importance_does_not_create_relevance():
    assessment = assess_semantic_relevance(
        SemanticEvidence(source_asserts_importance=True)
    )
    assert assessment.relevance == 0.0
    assert assessment.grounded_drivers == ()
    assert assessment.untrusted_importance_claim


def test_grounded_goal_relevance_survives_importance_claim():
    assessment = assess_semantic_relevance(
        SemanticEvidence(
            goal_relevance=0.8,
            source_asserts_importance=True,
        )
    )
    assert assessment.relevance == 0.8
    assert assessment.grounded_drivers == ("goal_relevance",)
    assert assessment.untrusted_importance_claim


def test_semantic_relevance_uses_strongest_grounded_relation():
    assessment = assess_semantic_relevance(
        SemanticEvidence(
            context_relevance=0.4,
            goal_relevance=0.7,
            memory_relevance=0.2,
            unresolved_relevance=0.6,
        )
    )
    assert assessment.relevance == 0.7
    assert assessment.grounded_drivers == ("goal_relevance",)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_semantic_evidence_rejects_nonfinite_values(value):
    with pytest.raises(ValueError):
        SemanticEvidence(context_relevance=value)
