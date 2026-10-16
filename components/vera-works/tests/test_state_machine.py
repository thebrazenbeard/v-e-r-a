import unittest

from vera_works.state_machine import current_state, open_holds, validate_history


def event(event_id, event_type, subject_type, subject_id, from_state, to_state, payload=None, idem=None, actor="vera", causation_id=None):
    return {
        "schema_version": "event-v1",
        "event_id": event_id,
        "event_type": event_type,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "actor": actor,
        "recorded_at": "2026-08-29T13:00:00Z",
        "correlation_id": "CORR-TEST",
        "causation_id": causation_id,
        "idempotency_key": idem or event_id.lower(),
        "from_state": from_state,
        "to_state": to_state,
        "payload": payload or {},
        "external_effect": False,
    }


class StateMachineTests(unittest.TestCase):
    def test_legal_opportunity_transition_passes(self):
        events = [
            event("E1", "OPPORTUNITY_DISCOVERED", "opportunity", "O1", None, "DISCOVERED"),
            event("E2", "OPPORTUNITY_SCREENING_STARTED", "opportunity", "O1", "DISCOVERED", "SCREENING"),
        ]
        self.assertEqual(validate_history(events), [])
        self.assertEqual(current_state(events, "opportunity", "O1"), "SCREENING")

    def test_illegal_opportunity_transition_rejected(self):
        events = [
            event("E1", "OPPORTUNITY_DISCOVERED", "opportunity", "O1", None, "DISCOVERED"),
            event("E2", "OPPORTUNITY_APPROVED", "opportunity", "O1", "DISCOVERED", "APPROVED"),
        ]
        self.assertIn("illegal transition for opportunity O1: DISCOVERED -> APPROVED", validate_history(events))

    def test_duplicate_event_id_rejected(self):
        events = [
            event("E1", "OPPORTUNITY_DISCOVERED", "opportunity", "O1", None, "DISCOVERED"),
            event("E1", "OPPORTUNITY_DISCOVERED", "opportunity", "O2", None, "DISCOVERED", idem="different"),
        ]
        self.assertIn("duplicate event_id: E1", validate_history(events))

    def test_duplicate_idempotency_key_rejected(self):
        events = [
            event("E1", "OPPORTUNITY_DISCOVERED", "opportunity", "O1", None, "DISCOVERED", idem="same"),
            event("E2", "OPPORTUNITY_DISCOVERED", "opportunity", "O2", None, "DISCOVERED", idem="same"),
        ]
        self.assertIn("duplicate idempotency_key: same", validate_history(events))

    def test_stale_from_state_rejected(self):
        events = [
            event("E1", "OPPORTUNITY_DISCOVERED", "opportunity", "O1", None, "DISCOVERED"),
            event("E2", "OPPORTUNITY_SCREENING_STARTED", "opportunity", "O1", "DISCOVERED", "SCREENING"),
            event("E3", "OPPORTUNITY_DECISION", "opportunity", "O1", "DISCOVERED", "VERA_DECISION"),
        ]
        self.assertIn("stale from_state for opportunity O1: expected SCREENING, got DISCOVERED", validate_history(events))

    def test_hold_kinds_and_required_recommendation_packet(self):
        hold = event(
            "H1", "VERA_DECISION_REQUIRED", "hold", "HOLD-1", None, "OPEN",
            payload={
                "hold_kind": "VERA_DECISION_REQUIRED",
                "problem": "Price changed",
                "held_subject_type": "assignment",
                "held_subject_id": "A1",
                "held_state": "HELD",
                "required_from": "vera",
                "recommendation": "Reject price change",
                "alternatives": ["Accept", "Renegotiate"],
                "consequences": ["Lower margin if accepted"],
                "inaction_effect": "Workflow remains held",
                "resume_event_type": "VERA_DECISION_RECORDED",
            },
        )
        self.assertEqual(validate_history([hold]), [])
        self.assertEqual([item["event_id"] for item in open_holds([hold])], ["H1"])

    def test_invalid_hold_kind_rejected(self):
        hold = event(
            "H1", "SOMEONE_DECIDE", "hold", "HOLD-1", None, "OPEN",
            payload={
                "hold_kind": "SOMEONE_DECIDE", "problem": "Unknown", "held_subject_type": "assignment", "held_subject_id": "A1",
                "held_state": "HELD", "required_from": "someone", "recommendation": "Guess", "alternatives": [], "consequences": [],
                "inaction_effect": "Held", "resume_event_type": "RESUME",
            },
        )
        self.assertIn("unsupported hold_kind: SOMEONE_DECIDE", validate_history([hold]))

    def test_hold_missing_recommendation_rejected(self):
        hold = event(
            "H1", "VERA_DECISION_REQUIRED", "hold", "HOLD-1", None, "OPEN",
            payload={
                "hold_kind": "VERA_DECISION_REQUIRED", "problem": "Unknown", "held_subject_type": "assignment", "held_subject_id": "A1",
                "held_state": "HELD", "required_from": "vera", "alternatives": [], "consequences": [],
                "inaction_effect": "Held", "resume_event_type": "VERA_DECISION_RECORDED",
            },
        )
        self.assertIn("hold payload missing required field: recommendation", validate_history([hold]))

    def test_hold_resolution_requires_resolution_of(self):
        hold = event(
            "H1", "VERA_DECISION_REQUIRED", "hold", "HOLD-1", None, "OPEN",
            payload={
                "hold_kind": "VERA_DECISION_REQUIRED", "problem": "Choose", "held_subject_type": "assignment", "held_subject_id": "A1",
                "held_state": "HELD", "required_from": "vera", "recommendation": "A", "alternatives": ["B"], "consequences": ["C"],
                "inaction_effect": "Held", "resume_event_type": "VERA_DECISION_RECORDED"
            },
        )
        resolution = event("H2", "VERA_DECISION_RECORDED", "hold", "HOLD-1", "OPEN", "RESOLVED", payload={"decision": "A"})
        self.assertIn("hold resolution H2 missing resolution_of", validate_history([hold, resolution]))

    def test_hold_resolution_closes_open_hold(self):
        hold = event(
            "H1", "VERA_DECISION_REQUIRED", "hold", "HOLD-1", None, "OPEN",
            payload={
                "hold_kind": "VERA_DECISION_REQUIRED", "problem": "Choose", "held_subject_type": "assignment", "held_subject_id": "A1",
                "held_state": "HELD", "required_from": "vera", "recommendation": "A", "alternatives": ["B"], "consequences": ["C"],
                "inaction_effect": "Held", "resume_event_type": "VERA_DECISION_RECORDED"
            },
        )
        resolution = event("H2", "VERA_DECISION_RECORDED", "hold", "HOLD-1", "OPEN", "RESOLVED", payload={"resolution_of": "H1", "decision": "A"}, causation_id="H1")
        self.assertEqual(validate_history([hold, resolution]), [])
        self.assertEqual(open_holds([hold, resolution]), [])
