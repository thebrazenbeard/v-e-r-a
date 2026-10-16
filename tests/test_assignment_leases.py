import unittest

from vera_works.state_machine import active_lease, validate_history


def event(event_id, event_type, from_state, to_state, payload=None, actor="worker:one"):
    return {
        "schema_version": "event-v1",
        "event_id": event_id,
        "event_type": event_type,
        "subject_type": "assignment",
        "subject_id": "A1",
        "actor": actor,
        "recorded_at": "2026-08-29T13:00:00Z",
        "correlation_id": "CORR-A1",
        "causation_id": None,
        "idempotency_key": event_id.lower(),
        "from_state": from_state,
        "to_state": to_state,
        "payload": payload or {},
        "external_effect": False,
    }


class AssignmentLeaseTests(unittest.TestCase):
    def test_assignment_has_one_active_claimant(self):
        events = [
            event("A0", "ASSIGNMENT_CREATED", None, "CREATED"),
            event("A1", "ASSIGNMENT_CLAIMED", "CREATED", "CLAIMED", {"lease_action": "CLAIM", "holder": "worker:one", "claimed_at": "2026-08-29T13:00:00Z"}),
        ]
        self.assertEqual(validate_history(events), [])
        self.assertEqual(active_lease(events, "A1")["holder"], "worker:one")

    def test_second_claim_is_rejected_while_lease_active(self):
        events = [
            event("A0", "ASSIGNMENT_CREATED", None, "CREATED"),
            event("A1", "ASSIGNMENT_CLAIMED", "CREATED", "CLAIMED", {"lease_action": "CLAIM", "holder": "worker:one", "claimed_at": "2026-08-29T13:00:00Z"}),
            event("A2", "ASSIGNMENT_CLAIMED", "CLAIMED", "IN_PROGRESS", {"lease_action": "CLAIM", "holder": "worker:two", "claimed_at": "2026-08-29T13:05:00Z"}, actor="worker:two"),
        ]
        self.assertIn("assignment A1 already leased to worker:one", validate_history(events))

    def test_stale_holder_is_rejected(self):
        events = [
            event("A0", "ASSIGNMENT_CREATED", None, "CREATED"),
            event("A1", "ASSIGNMENT_CLAIMED", "CREATED", "CLAIMED", {"lease_action": "CLAIM", "holder": "worker:one", "claimed_at": "2026-08-29T13:00:00Z"}),
            event("A2", "ASSIGNMENT_STARTED", "CLAIMED", "IN_PROGRESS", {"holder": "worker:two"}, actor="worker:two"),
        ]
        self.assertIn("assignment A1 lease holder mismatch: expected worker:one, got worker:two", validate_history(events))

    def test_expiration_does_not_silently_transfer_lease(self):
        events = [
            event("A0", "ASSIGNMENT_CREATED", None, "CREATED"),
            event("A1", "ASSIGNMENT_CLAIMED", "CREATED", "CLAIMED", {"lease_action": "CLAIM", "holder": "worker:one", "claimed_at": "2026-08-29T13:00:00Z", "expires_at": "2026-08-29T13:01:00Z"}),
            event("A2", "ASSIGNMENT_STARTED", "CLAIMED", "IN_PROGRESS", {"holder": "worker:two"}, actor="worker:two"),
        ]
        self.assertIn("assignment A1 lease holder mismatch: expected worker:one, got worker:two", validate_history(events))

    def test_explicit_transfer_from_held_changes_holder(self):
        events = [
            event("A0", "ASSIGNMENT_CREATED", None, "CREATED"),
            event("A1", "ASSIGNMENT_CLAIMED", "CREATED", "CLAIMED", {"lease_action": "CLAIM", "holder": "worker:one", "claimed_at": "2026-08-29T13:00:00Z"}),
            event("A2", "ASSIGNMENT_STARTED", "CLAIMED", "IN_PROGRESS", {"holder": "worker:one"}),
            event("A3", "ASSIGNMENT_HELD", "IN_PROGRESS", "HELD", {"holder": "worker:one"}),
            event("A4", "ASSIGNMENT_RECLAIMED", "HELD", "IN_PROGRESS", {"lease_action": "TRANSFER", "previous_holder": "worker:one", "holder": "worker:two"}, actor="worker:two"),
        ]
        self.assertEqual(validate_history(events), [])
        self.assertEqual(active_lease(events, "A1")["holder"], "worker:two")

    def test_completion_terminates_lease(self):
        events = [
            event("A0", "ASSIGNMENT_CREATED", None, "CREATED"),
            event("A1", "ASSIGNMENT_CLAIMED", "CREATED", "CLAIMED", {"lease_action": "CLAIM", "holder": "worker:one", "claimed_at": "2026-08-29T13:00:00Z"}),
            event("A2", "ASSIGNMENT_STARTED", "CLAIMED", "IN_PROGRESS", {"holder": "worker:one"}),
            event("A3", "ASSIGNMENT_COMPLETED", "IN_PROGRESS", "COMPLETED", {"holder": "worker:one"}),
        ]
        self.assertEqual(validate_history(events), [])
        self.assertIsNone(active_lease(events, "A1"))


if __name__ == "__main__":
    unittest.main()
