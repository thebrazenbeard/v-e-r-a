import unittest

from vera_works.state_machine import validate_history


def event(subject_type, to_state):
    payload = {}
    event_type = "INITIAL_EVENT"
    if subject_type == "hold":
        event_type = "VERA_DECISION_REQUIRED"
        payload = {
            "hold_kind": "VERA_DECISION_REQUIRED",
            "problem": "Choose",
            "held_subject_type": "assignment",
            "held_subject_id": "A1",
            "held_state": "HELD",
            "required_from": "vera",
            "recommendation": "A",
            "alternatives": ["B"],
            "consequences": ["C"],
            "inaction_effect": "Workflow remains held",
            "resume_event_type": "VERA_DECISION_RECORDED",
        }
    elif subject_type == "financial" and to_state == "EARNED":
        payload = {"currency": "USD", "gross": "100.00"}
    elif subject_type == "financial" and to_state == "SPENT":
        payload = {"currency": "USD", "amount": "10.00", "purpose": "approved test expense"}
    return {
        "schema_version": "event-v1",
        "event_id": f"INIT-{subject_type}-{to_state}",
        "event_type": event_type,
        "subject_type": subject_type,
        "subject_id": f"{subject_type}-1",
        "actor": "automation",
        "recorded_at": "2026-08-29T14:50:00Z",
        "correlation_id": "CORR-INITIAL",
        "causation_id": None,
        "idempotency_key": f"init:{subject_type}:{to_state}",
        "from_state": None,
        "to_state": to_state,
        "payload": payload,
        "external_effect": False,
    }


class InitialStateTests(unittest.TestCase):
    def test_financial_policy_can_begin_authorized_in_principle(self):
        event = {
            "schema_version": "event-v1",
            "event_id": "evt-policy",
            "event_type": "OPERATING_DECISION_RECORDED",
            "subject_type": "financial_policy",
            "subject_id": "policy-1",
            "actor": "patrick:legal-custodian",
            "recorded_at": "2026-10-05T17:14:00Z",
            "correlation_id": "corr-policy",
            "causation_id": None,
            "idempotency_key": "policy-1",
            "from_state": None,
            "to_state": "AUTHORIZED_IN_PRINCIPLE",
            "payload": {"allocation_rate": None},
            "external_effect": False,
        }
        self.assertEqual(validate_history([event]), [])

    def test_opportunity_cannot_begin_approved(self):
        errors = validate_history([event("opportunity", "APPROVED")])
        self.assertIn("illegal initial state for opportunity opportunity-1: APPROVED", errors)

    def test_defined_initial_states_are_accepted(self):
        cases = [
            ("opportunity", "DISCOVERED"),
            ("assignment", "CREATED"),
            ("deliverable", "DRAFTING"),
            ("financial", "EARNED"),
            ("financial", "SPENT"),
            ("hold", "OPEN"),
        ]
        for subject_type, to_state in cases:
            with self.subTest(subject_type=subject_type, to_state=to_state):
                self.assertEqual(validate_history([event(subject_type, to_state)]), [])


if __name__ == "__main__":
    unittest.main()
