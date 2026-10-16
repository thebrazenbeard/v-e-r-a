import unittest
from vera_works.contracts import validate_event


class EventContractTests(unittest.TestCase):
    def test_valid_event_has_no_errors(self):
        event = {
            "schema_version": "event-v1",
            "event_id": "EVT-20260829-0001",
            "event_type": "OPPORTUNITY_DISCOVERED",
            "subject_type": "opportunity",
            "subject_id": "OPP-0001",
            "actor": "vera",
            "recorded_at": "2026-08-29T13:00:00Z",
            "correlation_id": "CORR-0001",
            "causation_id": None,
            "idempotency_key": "opp-discovered:OPP-0001:v1",
            "from_state": None,
            "to_state": "DISCOVERED",
            "payload": {"source": "dry-run"},
            "external_effect": False,
        }
        self.assertEqual(validate_event(event), [])

    def test_event_requires_idempotency_key(self):
        event = {
            "schema_version": "event-v1",
            "event_id": "EVT-20260829-0002",
            "event_type": "OPPORTUNITY_DISCOVERED",
            "subject_type": "opportunity",
            "subject_id": "OPP-0002",
            "actor": "vera",
            "recorded_at": "2026-08-29T13:00:00Z",
            "correlation_id": "CORR-0002",
            "causation_id": None,
            "from_state": None,
            "to_state": "DISCOVERED",
            "payload": {},
            "external_effect": False,
        }
        self.assertIn("missing required field: idempotency_key", validate_event(event))

    def test_event_rejects_unknown_subject_type(self):
        event = {
            "schema_version": "event-v1",
            "event_id": "EVT-20260829-0003",
            "event_type": "THING_CHANGED",
            "subject_type": "thing",
            "subject_id": "THING-1",
            "actor": "worker:scout",
            "recorded_at": "2026-08-29T13:00:00Z",
            "correlation_id": "CORR-0003",
            "causation_id": None,
            "idempotency_key": "thing:1",
            "from_state": None,
            "to_state": "NEW",
            "payload": {},
            "external_effect": False,
        }
        self.assertIn("unsupported subject_type: thing", validate_event(event))
