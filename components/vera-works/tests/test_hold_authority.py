import unittest

from vera_works.state_machine import validate_history


def hold_event():
    return {
        "schema_version": "event-v1",
        "event_id": "H-AUTH-1",
        "event_type": "VERA_DECISION_REQUIRED",
        "subject_type": "hold",
        "subject_id": "HOLD-AUTH-1",
        "actor": "automation",
        "recorded_at": "2026-08-29T15:00:00Z",
        "correlation_id": "CORR-H-AUTH",
        "causation_id": None,
        "idempotency_key": "hold:auth:open",
        "from_state": None,
        "to_state": "OPEN",
        "payload": {
            "hold_kind": "VERA_DECISION_REQUIRED",
            "problem": "Choose a price",
            "held_subject_type": "opportunity",
            "held_subject_id": "OPP-1",
            "held_state": "VERA_DECISION",
            "required_from": "vera",
            "recommendation": "Choose 100",
            "alternatives": ["Choose 80"],
            "consequences": ["Lower margin at 80"],
            "inaction_effect": "Workflow remains held",
            "resume_event_type": "VERA_DECISION_RECORDED",
        },
        "external_effect": False,
    }


def resolution(event_type="VERA_DECISION_RECORDED", actor="vera", causation_id="H-AUTH-1"):
    return {
        "schema_version": "event-v1",
        "event_id": "H-AUTH-2",
        "event_type": event_type,
        "subject_type": "hold",
        "subject_id": "HOLD-AUTH-1",
        "actor": actor,
        "recorded_at": "2026-08-29T15:01:00Z",
        "correlation_id": "CORR-H-AUTH",
        "causation_id": causation_id,
        "idempotency_key": f"hold:auth:resolve:{event_type}:{actor}:{causation_id}",
        "from_state": "OPEN",
        "to_state": "RESOLVED",
        "payload": {"resolution_of": "H-AUTH-1", "decision": "100"},
        "external_effect": False,
    }


class HoldAuthorityTests(unittest.TestCase):
    def test_wrong_resume_event_type_is_rejected(self):
        errors = validate_history([hold_event(), resolution(event_type="SOMETHING_ELSE")])
        self.assertIn(
            "hold resolution H-AUTH-2 event_type mismatch: expected VERA_DECISION_RECORDED, got SOMETHING_ELSE",
            errors,
        )

    def test_wrong_resolution_actor_is_rejected(self):
        errors = validate_history([hold_event(), resolution(actor="worker:scout")])
        self.assertIn(
            "hold resolution H-AUTH-2 actor mismatch: expected vera, got worker:scout",
            errors,
        )

    def test_resolution_must_be_caused_by_open_hold(self):
        errors = validate_history([hold_event(), resolution(causation_id="OTHER")])
        self.assertIn(
            "hold resolution H-AUTH-2 causation_id mismatch: expected H-AUTH-1, got OTHER",
            errors,
        )

    def test_correct_resolution_is_accepted(self):
        self.assertEqual(validate_history([hold_event(), resolution()]), [])


    def test_required_actor_can_cancel_hold_with_original_resume_event(self):
        cancel = resolution()
        cancel["to_state"] = "CANCELLED"
        self.assertEqual(validate_history([hold_event(), cancel]), [])

    def test_external_invalidation_can_cancel_hold_without_impersonating_required_actor(self):
        cancel = resolution(
            event_type="HOLD_CANCELLED_EXTERNAL_INVALIDATION",
            actor="automation",
            causation_id="H-AUTH-1",
        )
        cancel["to_state"] = "CANCELLED"
        cancel["payload"] = {
            "resolution_of": "H-AUTH-1",
            "cancellation_reason": "HELD_SUBJECT_NO_LONGER_ACTIONABLE",
            "evidence": "The external opportunity was removed by its owner.",
        }
        self.assertEqual(validate_history([hold_event(), cancel]), [])

    def test_external_invalidation_cancel_requires_automation_actor_and_evidence(self):
        cancel = resolution(
            event_type="HOLD_CANCELLED_EXTERNAL_INVALIDATION",
            actor="vera",
            causation_id="H-AUTH-1",
        )
        cancel["to_state"] = "CANCELLED"
        cancel["payload"] = {
            "resolution_of": "H-AUTH-1",
            "cancellation_reason": "HELD_SUBJECT_NO_LONGER_ACTIONABLE",
            "evidence": "",
        }
        errors = validate_history([hold_event(), cancel])
        self.assertIn(
            "hold cancellation H-AUTH-2 actor mismatch: expected automation, got vera",
            errors,
        )
        self.assertIn("hold cancellation H-AUTH-2 missing evidence", errors)


if __name__ == "__main__":
    unittest.main()
