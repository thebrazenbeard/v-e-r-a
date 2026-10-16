import unittest

from vera_works.contracts import validate_event


def event(subject_type, to_state, payload, event_type="TEST_EVENT"):
    return {
        "schema_version": "event-v1",
        "event_id": f"PAYLOAD-{subject_type}-{to_state}",
        "event_type": event_type,
        "subject_type": subject_type,
        "subject_id": f"{subject_type}-1",
        "actor": "automation",
        "recorded_at": "2026-08-29T15:10:00Z",
        "correlation_id": "CORR-PAYLOAD",
        "causation_id": None,
        "idempotency_key": f"payload:{subject_type}:{to_state}",
        "from_state": None,
        "to_state": to_state,
        "payload": payload,
        "external_effect": False,
    }


class PayloadContractTests(unittest.TestCase):
    def test_received_financial_event_requires_consistent_net_math(self):
        candidate = event("financial", "RECEIVED", {
            "currency": "USD",
            "gross": "100.00",
            "fees": "5.00",
            "tax_reserve": "10.00",
            "net": "90.00",
        })
        self.assertIn(
            "financial RECEIVED net must equal gross - fees - tax_reserve",
            validate_event(candidate),
        )

    def test_spent_financial_event_requires_positive_amount_and_purpose(self):
        candidate = event("financial", "SPENT", {"currency": "USD", "amount": "0.00", "purpose": ""})
        errors = validate_event(candidate)
        self.assertIn("financial SPENT amount must be greater than zero", errors)
        self.assertIn("financial SPENT purpose must be a non-empty string", errors)

    def test_refund_requires_amount_and_reference(self):
        candidate = event("financial", "REFUNDED", {"currency": "USD"})
        errors = validate_event(candidate)
        self.assertIn("financial REFUNDED amount must be greater than zero", errors)
        self.assertIn("financial REFUNDED reverses_event_id must be a non-empty string", errors)

    def test_vera_hold_cannot_delegate_resolution_actor_through_payload(self):
        candidate = event("hold", "OPEN", {
            "hold_kind": "VERA_DECISION_REQUIRED",
            "problem": "Choose",
            "held_subject_type": "opportunity",
            "held_subject_id": "OPP-1",
            "held_state": "VERA_DECISION",
            "required_from": "worker:scout",
            "recommendation": "Choose A",
            "alternatives": ["B"],
            "consequences": ["C"],
            "inaction_effect": "Held",
            "resume_event_type": "VERA_DECISION_RECORDED",
        }, event_type="VERA_DECISION_REQUIRED")
        self.assertIn(
            "VERA_DECISION_REQUIRED required_from must equal vera",
            validate_event(candidate),
        )

    def test_hold_alternatives_and_consequences_must_be_arrays(self):
        candidate = event("hold", "OPEN", {
            "hold_kind": "PATRICK_ACTION_REQUIRED",
            "problem": "Sign",
            "held_subject_type": "external_action",
            "held_subject_id": "EA-1",
            "held_state": "HELD",
            "required_from": "patrick",
            "recommendation": "Sign after review",
            "alternatives": "decline",
            "consequences": "workflow remains held",
            "inaction_effect": "Held",
            "resume_event_type": "PATRICK_ACTION_RECORDED",
        }, event_type="PATRICK_ACTION_REQUIRED")
        errors = validate_event(candidate)
        self.assertIn("hold alternatives must be an array", errors)
        self.assertIn("hold consequences must be an array", errors)


if __name__ == "__main__":
    unittest.main()
