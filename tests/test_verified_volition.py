"""Host-custodied Volition projection against the REAL optional Volition module.

Run with PYTHONPATH=/path/to/pinned/volition/src for full integration. The
ordinary Vera test suite remains dependency-free and skips these if absent.
"""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from interface.goal_view import GoalViewError
from interface.server import make_server
from interface.verified_volition import (VerifiedVolitionGoalProvider,
                                        fingerprint_installed_volition,
                                        seal_host_state)


@unittest.skipUnless(importlib.util.find_spec("volition"),
                     "requires an independently pinned real Volition package")
class VerifiedVolitionTests(unittest.TestCase):
    def setUp(self):
        from volition import (DriveKind, ModelWantProposal, ObservationClaim,
                              ObservationVerifier, OperationalMotivation)

        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "current-goal.json"
        self.ledger = self.folder / "highwater.sqlite3"
        self.key = b"test-private-host-key-not-a-production-secret-20261027"
        self.now = datetime.now(timezone.utc)
        claim = ObservationClaim(
            evidence_id="obs-1", content_digest="sha256:" + sha256(b"obs-1").hexdigest(),
            target="repair-open-work-item", kind=DriveKind.OPEN_LOOP,
            magnitude=0.9, confidence=0.95, source_ref="test:operator-measurement")
        admitted = ObservationVerifier([claim], verifier_id="test-operator").admit(claim)
        motivation = OperationalMotivation()
        goal = motivation.propose(ModelWantProposal(
            proposal_id="model-proposal-1", target=claim.target,
            kind=claim.kind, evidence_id=claim.evidence_id,
            reason="review bounded current work"), admitted)
        self.assertIsNotNone(goal)
        self.snapshot = motivation.snapshot()
        self.runtime_sha = fingerprint_installed_volition()
        self._write(1)

    def _write(self, seq, *, snapshot=None, owner="patrick", source="volition:host",
               at=None):
        record = seal_host_state(
            snapshot=self.snapshot if snapshot is None else snapshot,
            owner_id=owner, source_id=source, publication=seq,
            captured_at=self.now if at is None else at, key=self.key)
        self.path.write_text(json.dumps(record), encoding="utf-8")
        os.chmod(self.path, 0o600)
        return record

    def _provider(self, **overrides):
        kwargs = dict(record_path=self.path, ledger_path=self.ledger,
                      key=self.key, owner_id="patrick", source_id="volition:host",
                      expected_runtime_sha256=self.runtime_sha)
        kwargs.update(overrides)
        return VerifiedVolitionGoalProvider(**kwargs)

    def test_real_restoration_and_durable_highwater_reject_rollback(self):
        reader = self._provider()
        first = reader.read_projection(now=self.now)
        self.assertEqual(first["status"], "PROPOSED_REVIEW")
        self.assertEqual(first["choice_class"], "MODEL_PROPOSED")
        self.assertFalse(first["effect_authority"])
        self.assertEqual(reader.read_projection(now=self.now), first)

        self._write(2)
        self.assertEqual(reader.read_projection(now=self.now)["status"], "PROPOSED_REVIEW")
        self._write(1)
        with self.assertRaisesRegex(GoalViewError, "rolled back"):
            self._provider().read_projection(now=self.now)  # separate process-like restore

    def test_owner_source_signature_and_timestamp_tampering_refused(self):
        self._provider()
        self._write(1, owner="stranger")
        with self.assertRaisesRegex(GoalViewError, "owner/source"):
            self._provider().read_projection(now=self.now)
        self._write(1, source="model:fake-host")
        with self.assertRaises(GoalViewError):
            self._provider().read_projection(now=self.now)

        good = self._write(1)
        good["captured_at_utc"] = (self.now + timedelta(minutes=2)).isoformat()
        self.path.write_text(json.dumps(good), encoding="utf-8")
        os.chmod(self.path, 0o600)
        with self.assertRaisesRegex(GoalViewError, "signature"):
            self._provider().read_projection(now=self.now)

        self._write(1, at=self.now - timedelta(minutes=10))
        with self.assertRaisesRegex(GoalViewError, "stale"):
            self._provider().read_projection(now=self.now)

    def test_signed_semantically_forged_volition_state_is_not_current(self):
        # A valid MAC does not make forged state internally consistent.
        forged = json.loads(json.dumps(self.snapshot))
        forged["engine"]["active_goal"]["target"] = "forged-target"
        self._write(1, snapshot=forged)
        with self.assertRaisesRegex(GoalViewError, "restoration"):
            self._provider().read_projection(now=self.now)

    def test_module_pin_and_file_permissions_fail_closed(self):
        with self.assertRaisesRegex(GoalViewError, "module revision"):
            self._provider(expected_runtime_sha256="0" * 64).read_projection(now=self.now)
        os.chmod(self.path, 0o644)
        with self.assertRaises(GoalViewError):
            self._provider()

    def test_windows_acl_unavailable_and_symlink_not_trusted(self):
        # These checks intentionally block a Lappy rollout without a qualified
        # native Windows ACL implementation and host-managed secret custody.
        with patch("interface.verified_volition.os.name", "nt"):
            with self.assertRaisesRegex(GoalViewError, "Windows source/key ACL"):
                self._provider()
        self.path.unlink()
        self.path.symlink_to(self.ledger)
        with self.assertRaisesRegex(GoalViewError, "symlink"):
            self._provider()

    def test_foreign_uid_custody_not_accepted_even_when_mode_private(self):
        # Root privileges do not make a different owner's 0600 file
        # equivalent to a host-owned source of truth.
        with patch("interface.verified_volition.os.geteuid", return_value=-1):
            with self.assertRaisesRegex(GoalViewError, "same-owner"):
                self._provider()

    def test_duplicate_json_keys_fail_before_trust(self):
        raw = self.path.read_text(encoding="utf-8")
        self.path.write_text(raw.replace('"schema":', '"schema":"forged", "schema":', 1),
                             encoding="utf-8")
        with self.assertRaisesRegex(GoalViewError, "duplicate"):
            self._provider().read_projection(now=self.now)

    def test_real_host_custody_through_private_read_only_http_route(self):
        provider = self._provider()
        token = "separate-operator-goal-read-token-0123456789"
        server = make_server(port=0, goal_provider=provider, goal_access_token=token)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/api/goals/current"
            with self.assertRaises(HTTPError) as denied:
                urlopen(Request(url, headers={"X-Vera-Session": server.session_token}), timeout=5)
            self.assertEqual(denied.exception.code, 403)
            with urlopen(Request(url, headers={"X-Vera-Goal-Access": token}), timeout=5) as response:
                result = json.loads(response.read())
            self.assertEqual(result["status"], "PROPOSED_REVIEW")
            self.assertFalse(result["effect_authority"])

            # Even an authenticated browser gets HOLD if the signed host state
            # is replaced with a fresh-looking but semantically forged state.
            forged = json.loads(json.dumps(self.snapshot))
            forged["engine"]["active_goal"]["target"] = "forged-target"
            self._write(2, snapshot=forged)
            with self.assertRaises(HTTPError) as held:
                urlopen(Request(url, headers={"X-Vera-Goal-Access": token}), timeout=5)
            self.assertEqual(held.exception.code, 503)
            self.assertEqual(json.loads(held.exception.read()),
                             {"status": "HOLD_UNVERIFIED", "effect_authority": False})
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
