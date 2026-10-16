import unittest

from vera_works.state_machine import validate_history


def event(event_id, event_type, subject_id, from_state, to_state, payload, causation_id=None, actor="automation"):
    return {
        "schema_version": "event-v1",
        "event_id": event_id,
        "event_type": event_type,
        "subject_type": "hold",
        "subject_id": subject_id,
        "actor": actor,
        "recorded_at": "2026-08-29T13:00:00Z",
        "correlation_id": "CORR-HOLD",
        "causation_id": causation_id,
        "idempotency_key": event_id.lower(),
        "from_state": from_state,
        "to_state": to_state,
        "payload": payload,
        "external_effect": False,
    }


class HoldIsolationRegressionTests(unittest.TestCase):
    def test_invalid_prior_hold_does_not_poison_later_valid_hold_resolution(self):
        bad = event(
            "HBAD", "BAD_KIND", "HOLD-BAD", None, "OPEN",
            {"hold_kind": "BAD_KIND", "problem": "bad", "held_subject_type": "assignment", "held_subject_id": "A0", "held_state": "HELD", "required_from": "nobody", "recommendation": "none", "alternatives": [], "consequences": [], "inaction_effect": "none", "resume_event_type": "NONE"},
        )
        good = event(
            "HGOOD", "VERA_DECISION_REQUIRED", "HOLD-GOOD", None, "OPEN",
            {"hold_kind": "VERA_DECISION_REQUIRED", "problem": "choose", "held_subject_type": "assignment", "held_subject_id": "A1", "held_state": "HELD", "required_from": "vera", "recommendation": "A", "alternatives": ["B"], "consequences": ["C"], "inaction_effect": "held", "resume_event_type": "VERA_DECISION_RECORDED"},
        )
        resolution = event(
            "HRES", "VERA_DECISION_RECORDED", "HOLD-GOOD", "OPEN", "RESOLVED",
            {"resolution_of": "HGOOD", "decision": "A"}, causation_id="HGOOD", actor="vera",
        )
        errors = validate_history([bad, good, resolution])
        self.assertIn("unsupported hold_kind: BAD_KIND", errors)
        self.assertNotIn("hold resolution HRES references non-open hold: HGOOD", errors)


if __name__ == "__main__":
    unittest.main()
