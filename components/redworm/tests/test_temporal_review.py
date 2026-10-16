"""Adversarial temporal / admission / reconciliation checks with synthetic records."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from redworm.core import Store, GuardrailError, IntegrityError

def event(message="synthetic", episode="white-1", designation="W/W 1",
          schema="redworm.event.v2", temporal=None, memory="WORKING_PROJECT"):
    obj = {
        "schema": schema,
        "producer": {"identity": "Vera", "worm": "WHITE", "designation": designation,
                     "episode_id": episode},
        "recorded_at": "2026-10-13T19:00:00Z",
        "source": {"locator": "synthetic://fixture/" + message,
                   "sha256": hashlib.sha256(message.encode("utf-8")).hexdigest(),
                   "observed_by": "test", "verification": "UNVERIFIED"},
        "evidence_kind": "DERIVED", "memory_class": memory, "privacy": "INTERNAL",
        "claim": {"text": message, "type": "EVENT", "modality": "REPORTED",
                  "subject": "synthetic-only", "valid_at": None},
    }
    if schema == "redworm.event.v1":
        obj["occurred_at"] = "2026-08-10T10:00:00Z"
    else:
        obj["event_time"] = temporal if temporal is not None else {
            "precision": "UNKNOWN", "earliest_at": None, "latest_at": None,
            "basis": "UNAVAILABLE"
        }
    return obj

def window(precision, start, end, basis="SOURCE_EVENT_DATE"):
    return {"precision": precision, "earliest_at": start, "latest_at": end, "basis": basis}

class TemporalReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "synthetic.db")

    def tearDown(self):
        self.store.__exit__(None, None, None)
        self.tmp.cleanup()

    def admit(self, eid):
        self.store.admit(eid, "test://approval", "test://readback", "test-reviewer")

    def test_unknown_time_never_borrows_recorded_at(self):
        eid, _ = self.store.ingest(event("unknown"))
        self.assertNotIn("occurred_at", self.store.get(eid))
        self.assertEqual(1, len(self.store.timeline()["unplaced_unknown_time"]))

    def test_unknown_with_fake_bound_rejected(self):
        with self.assertRaises(GuardrailError):
            self.store.ingest(event(temporal=window("UNKNOWN", "2026-08-10T00:00:00Z", None, "UNAVAILABLE")))

    def test_reversed_interval_rejected(self):
        with self.assertRaises(GuardrailError):
            self.store.ingest(event(temporal=window("INTERVAL",
                "2026-08-11T00:00:00Z", "2026-08-10T00:00:00Z", "INFERRED_INTERVAL")))

    def test_instant_requires_equal_bounds(self):
        with self.assertRaises(GuardrailError):
            self.store.ingest(event(temporal=window("INSTANT",
                "2026-08-10T00:00:00Z", "2026-08-11T00:00:00Z", "MESSAGE_TIMESTAMP")))

    def test_day_must_span_one_day(self):
        with self.assertRaises(GuardrailError):
            self.store.ingest(event(temporal=window("DAY",
                "2026-08-10T00:00:00Z", "2026-08-12T00:00:00Z")))

    def test_overlapping_intervals_not_ordered_as_certain(self):
        a, _ = self.store.ingest(event("day", temporal=window("DAY",
            "2026-08-10T00:00:00Z", "2026-08-11T00:00:00Z")))
        b, _ = self.store.ingest(event("noon", temporal=window("INSTANT",
            "2026-08-10T12:00:00Z", "2026-08-10T12:00:00Z", "MESSAGE_TIMESTAMP")))
        rows = self.store.timeline()["ordered_candidates"]
        self.assertIn(b, rows[0]["overlaps"])
        self.assertIn(a, rows[1]["overlaps"])
        self.assertFalse(rows[0]["sequence_proven"])

    def test_oldest_first_not_ingestion_order(self):
        newer, _ = self.store.ingest(event("newer", temporal=window("INSTANT",
            "2026-08-11T00:00:00Z", "2026-08-11T00:00:00Z", "MESSAGE_TIMESTAMP")))
        older, _ = self.store.ingest(event("older", temporal=window("INSTANT",
            "2026-08-10T00:00:00Z", "2026-08-10T00:00:00Z", "MESSAGE_TIMESTAMP")))
        self.assertEqual([older, newer],
            [r["event"]["event_id"] for r in self.store.timeline()["ordered_candidates"]])

    def test_v1_compatibility_and_digest(self):
        eid, _ = self.store.ingest(event("legacy", schema="redworm.event.v1"))
        self.assertEqual(eid, self.store.get(eid)["event_id"])

    def test_no_supersession_cycles(self):
        a, _ = self.store.ingest(event("A"))
        b, _ = self.store.ingest(event("B"))
        self.admit(a); self.admit(b)
        self.store.relate(a, b, "SUPERSEDES", "test://approval", "test://readback")
        with self.assertRaises(GuardrailError):
            self.store.relate(b, a, "SUPERSEDES", "test://approval", "test://readback")

    def test_conflict_and_losing_claims_block_handoff(self):
        a, _ = self.store.ingest(event("A"))
        b, _ = self.store.ingest(event("B"))
        self.admit(a); self.admit(b)
        self.store.conflict(a, b)
        with self.assertRaises(GuardrailError):
            self.store.prepare("white-1", [a])
        self.store.resolve(a, b, a, "test://approval", "test://readback")
        self.assertEqual(64, len(self.store.prepare("white-1", [a])))
        with self.assertRaises(GuardrailError):
            self.store.prepare("white-1", [b])

    def test_resolution_requires_both_admitted(self):
        a, _ = self.store.ingest(event("A"))
        b, _ = self.store.ingest(event("B"))
        self.admit(a)
        self.store.conflict(a, b)
        with self.assertRaises(GuardrailError):
            self.store.resolve(a, b, a, "test://approval", "test://readback")

    def test_handoff_no_mixed_designation_same_episode(self):
        a, _ = self.store.ingest(event("A"))
        b, _ = self.store.ingest(event("B", designation="W/W 2"))
        self.admit(a); self.admit(b)
        with self.assertRaises(GuardrailError):
            self.store.prepare("white-1", [a, b])

    def test_handoff_no_superseded_evidence(self):
        a, _ = self.store.ingest(event("A"))
        b, _ = self.store.ingest(event("B"))
        self.admit(a); self.admit(b)
        self.store.relate(a, b, "SUPERSEDES", "test://approval", "test://readback")
        with self.assertRaises(GuardrailError):
            self.store.prepare("white-1", [a])

    def test_verify_prohibited_backdoor_admission(self):
        a, _ = self.store.ingest(event("private", memory="AUTOBIOGRAPHICAL"))
        self.store.db.execute("INSERT INTO admissions VALUES(?,?,?,?)", (a, "fake", "fake", "fake"))
        self.store.db.commit()
        with self.assertRaises(IntegrityError):
            self.store.verify()

if __name__ == "__main__":
    unittest.main()
