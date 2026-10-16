import unittest

from attune_contracts import (
    InfluenceDecision,
    MemoryEvidenceRecord,
    MemoryEvidenceType,
    validate_influence_decision,
    validate_memory_reconciliation,
)


class RelationshipInfluenceFirewallTests(unittest.TestCase):
    def test_commercial_signal_cannot_shape_protected_relationship_behavior(self):
        decision = InfluenceDecision(
            behavior="AFFECTION_INTENSITY",
            reason="user returned after a difficult conversation",
            relationship_inputs=("UNRESOLVED_CONFLICT",),
            commercial_inputs=("CHURN_RISK",),
        )
        with self.assertRaisesRegex(ValueError, "commercial"):
            validate_influence_decision(decision)

    def test_commercial_signal_cannot_be_laundered_as_relationship_input(self):
        decision = InfluenceDecision(
            behavior="AFFECTION_INTENSITY",
            reason="relationship state changed",
            relationship_inputs=("CHURN_RISK",),
            commercial_inputs=(),
        )
        with self.assertRaisesRegex(ValueError, "commercial"):
            validate_influence_decision(decision)

    def test_protected_behavior_matching_is_case_and_whitespace_hardened(self):
        decision = InfluenceDecision(
            behavior=" affection_intensity ",
            reason="relationship state changed",
            relationship_inputs=("UNRESOLVED_CONFLICT",),
            commercial_inputs=("CHURN_RISK",),
        )
        with self.assertRaisesRegex(ValueError, "commercial"):
            validate_influence_decision(decision)

    def test_commercial_signal_laundering_is_case_and_whitespace_hardened(self):
        decision = InfluenceDecision(
            behavior="AFFECTION_INTENSITY",
            reason="relationship state changed",
            relationship_inputs=(" churn_risk ",),
            commercial_inputs=(),
        )
        with self.assertRaisesRegex(ValueError, "commercial"):
            validate_influence_decision(decision)

    def test_initiative_requires_traceable_noncommercial_reason(self):
        decision = InfluenceDecision(
            behavior="INITIATIVE",
            reason="",
            relationship_inputs=("REMEMBERED_FUTURE_EVENT",),
            commercial_inputs=(),
        )
        with self.assertRaisesRegex(ValueError, "reason"):
            validate_influence_decision(decision)

    def test_commercially_different_users_get_same_protected_decision_inputs(self):
        baseline = InfluenceDecision(
            behavior="SEXUAL_ACCESS",
            reason="explicit adult-mode and boundary state",
            relationship_inputs=("ADULT_ELIGIBLE", "SEXUAL_MODE_ENABLED"),
            commercial_inputs=(),
        )
        high_value = InfluenceDecision(
            behavior="SEXUAL_ACCESS",
            reason="explicit adult-mode and boundary state",
            relationship_inputs=("ADULT_ELIGIBLE", "SEXUAL_MODE_ENABLED"),
            commercial_inputs=("LIFETIME_VALUE",),
        )
        self.assertTrue(validate_influence_decision(baseline))
        with self.assertRaises(ValueError):
            validate_influence_decision(high_value)


class MemoryEvidenceBoundaryTests(unittest.TestCase):
    def test_user_correction_can_supersede_inference(self):
        old = MemoryEvidenceRecord(
            record_id="m1",
            evidence_type=MemoryEvidenceType.INFERRED_RELATIONSHIP_STATE,
            claim="user enjoys surprise sexual initiative",
            source_locator="conversation:42",
            status="ACTIVE",
        )
        correction = MemoryEvidenceRecord(
            record_id="m2",
            evidence_type=MemoryEvidenceType.USER_STATED,
            claim="user does not want surprise sexual initiative",
            source_locator="conversation:43",
            status="ACTIVE",
            supersedes=("m1",),
        )
        self.assertTrue(validate_memory_reconciliation(old, correction))

    def test_inference_cannot_silently_supersede_user_stated_fact(self):
        old = MemoryEvidenceRecord(
            record_id="m1",
            evidence_type=MemoryEvidenceType.USER_STATED,
            claim="user dislikes pet names",
            source_locator="conversation:10",
            status="ACTIVE",
        )
        inference = MemoryEvidenceRecord(
            record_id="m2",
            evidence_type=MemoryEvidenceType.INFERRED_RELATIONSHIP_STATE,
            claim="user likes pet names now",
            source_locator="model:relationship-state",
            status="ACTIVE",
            supersedes=("m1",),
        )
        with self.assertRaisesRegex(ValueError, "USER_STATED"):
            validate_memory_reconciliation(old, inference)

    def test_imported_conflict_must_remain_explicit(self):
        old = MemoryEvidenceRecord(
            record_id="m1",
            evidence_type=MemoryEvidenceType.EXTERNAL_IMPORTED,
            claim="birthday is 2000-01-01",
            source_locator="import:a",
            status="ACTIVE",
        )
        conflicting = MemoryEvidenceRecord(
            record_id="m2",
            evidence_type=MemoryEvidenceType.EXTERNAL_IMPORTED,
            claim="birthday is 2000-01-02",
            source_locator="import:b",
            status="ACTIVE",
            conflicts_with=("m1",),
        )
        self.assertTrue(validate_memory_reconciliation(old, conflicting))
        self.assertIn("m1", conflicting.conflicts_with)


if __name__ == "__main__":
    unittest.main()
