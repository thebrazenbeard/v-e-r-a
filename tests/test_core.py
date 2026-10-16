import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from redworm.core import Store, GuardrailError, IntegrityError

def event(message="synthetic", episode="episode-white", worm="WHITE", kind="PRIMARY",
          memory="WORKING_PROJECT", modality="REPORTED"):
    return {
        "schema": "redworm.event.v1",
        "producer": {"identity": "Vera", "worm": worm,
                     "designation": "W/W 3" if worm == "WHITE" else None, "episode_id": episode},
        "occurred_at": "2026-08-10T10:00:00-04:00",
        "recorded_at": "2026-08-11T10:00:00-04:00",
        "source": {"locator": "synthetic://not-real", "sha256": hashlib.sha256(message.encode()).hexdigest(),
                   "observed_by": "test", "verification": "UNVERIFIED"},
        "evidence_kind": kind, "memory_class": memory, "privacy": "INTERNAL",
        "claim": {"text": message, "type": "EVENT", "modality": modality,
                  "subject": "synthetic-fixture", "valid_at": "2026-08-10"}
    }

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name)/"evidence.db")

    def tearDown(self):
        self.store.__exit__(None, None, None)
        self.tmp.cleanup()

    def admit(self, eid):
        return self.store.admit(eid, "test://approval", "test://readback", "reviewer")

    def test_ingestion_does_not_admit(self):
        eid, created = self.store.ingest(event())
        self.assertTrue(created)
        eid2, created = self.store.ingest(event())
        self.assertEqual(eid, eid2)
        self.assertFalse(created)
        self.assertEqual([], self.store.project()["events"])

    def test_white_identity_provenance_retained(self):
        eid, _ = self.store.ingest(event())
        self.admit(eid)
        p = self.store.project()["events"][0]["producer"]
        self.assertEqual("Vera", p["identity"])
        self.assertEqual("WHITE", p["worm"])
        self.assertEqual("episode-white", p["episode_id"])

    def test_white_designation_required(self):
        e = event()
        e["producer"]["designation"] = None
        with self.assertRaises(GuardrailError):
            self.store.ingest(e)

    def test_digest_spoof_blocked(self):
        e = event()
        e["event_id"] = "0"*64
        with self.assertRaises(IntegrityError):
            self.store.ingest(e)

    def test_autobiography_not_admitted(self):
        eid, _ = self.store.ingest(event(memory="AUTOBIOGRAPHICAL"))
        with self.assertRaises(GuardrailError):
            self.admit(eid)

    def test_provider_not_promoted_current(self):
        eid, _ = self.store.ingest(event(kind="PROVIDER_SNAPSHOT"))
        with self.assertRaises(GuardrailError):
            self.admit(eid)

    def test_conflict_preserves_both_claims(self):
        a, _ = self.store.ingest(event(message="claim A"))
        b, _ = self.store.ingest(event(message="claim B"))
        self.admit(a)
        self.admit(b)
        self.store.conflict(a,b)
        self.assertEqual([], self.store.project()["events"])
        self.assertEqual(1, len(self.store.project()["unresolved_conflicts"]))
        self.store.resolve(a,b,b,"test://approval","test://readback")
        self.assertEqual([b],[e["event_id"] for e in self.store.project()["events"]])
        self.assertEqual(2,len(self.store.list()))

    def test_supersession_requires_admission(self):
        a, _ = self.store.ingest(event(message="old"))
        b, _ = self.store.ingest(event(message="new"))
        self.admit(a)
        with self.assertRaises(GuardrailError):
            self.store.relate(a,b,"SUPERSEDES","test://approval","test://readback")
        self.admit(b)
        self.store.relate(a,b,"SUPERSEDES","test://approval","test://readback")
        self.assertEqual([b],[e["event_id"] for e in self.store.project()["events"]])

    def test_handoff_never_accepts_without_holder(self):
        a, _ = self.store.ingest(event())
        with self.assertRaises(GuardrailError):
            self.store.prepare("episode-white",[a])
        self.admit(a)
        h=self.store.prepare("episode-white",[a])
        self.assertEqual(64,len(h))
        with self.assertRaises(GuardrailError):
            self.store.accept(h)

    def test_handoff_rejects_mixed_episodes(self):
        a, _ = self.store.ingest(event())
        b, _ = self.store.ingest(event(message="other", episode="red-episode", worm="RED"))
        self.admit(a)
        self.admit(b)
        with self.assertRaises(GuardrailError):
            self.store.prepare("episode-white",[a,b])

    def test_verify_detects_tampering(self):
        a, _ = self.store.ingest(event())
        self.assertEqual(1,self.store.verify()["events"])
        self.store.db.execute("UPDATE events SET payload=? WHERE id=?", ('{}', a))
        self.store.db.commit()
        with self.assertRaises((IntegrityError, GuardrailError)):
            self.store.verify()

    def test_historical_gaps_preserved(self):
        self.store.coverage("old-episode","MISSING","source unavailable")
        r=self.store.db.execute("SELECT status FROM coverage").fetchone()
        self.assertEqual("MISSING",r["status"])

    def test_inference_cannot_be_observed(self):
        with self.assertRaises(GuardrailError):
            self.store.ingest(event(kind="INTERPRETATION", modality="OBSERVED"))

    def test_local_admission_never_claims_provider_authority(self):
        a, _ = self.store.ingest(event())
        self.admit(a)
        self.assertTrue(self.store.project()["non_authoritative"])

if __name__ == "__main__":
    unittest.main()
