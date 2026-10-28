"""Native Windows custody checks against the pinned real Volition package.

Run only on a Windows host with pywin32; POSIX ACL mocks cannot establish
whether the host's DACLs actually protect a Volition source and replay ledger.
"""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
import unittest

from interface.goal_view import GoalViewError
from interface.verified_volition import (
    VerifiedVolitionGoalProvider, fingerprint_installed_volition, seal_host_state,
)


@unittest.skipUnless(os.name == "nt", "native Windows custody check")
class WindowsVolitionCustodyTests(unittest.TestCase):
    def setUp(self):
        import win32api
        import win32con
        import win32security
        from volition import (DriveKind, ModelWantProposal, ObservationClaim,
                              ObservationVerifier, OperationalMotivation)

        private_root = tempfile.TemporaryDirectory()
        self.addCleanup(private_root.cleanup)
        self.sandbox = Path(private_root.name)
        self.private = self.sandbox / "volition-custody"
        self.private.mkdir()
        self.record = self.private / "latest.json"
        self.ledger = self.private / "highwater.sqlite3"
        token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_QUERY)
        self.current = win32security.GetTokenInformation(token, win32security.TokenUser)[0]
        self._set_acl(self.private)

        claim = ObservationClaim(
            evidence_id="windows-observation", content_digest="sha256:" +
            sha256(b"windows-observation").hexdigest(),
            target="review-native-windows-custody", kind=DriveKind.OPEN_LOOP,
            magnitude=0.9, confidence=0.95, source_ref="test:operator-measurement")
        admitted = ObservationVerifier([claim], verifier_id="windows-operator").admit(claim)
        motivation = OperationalMotivation()
        goal = motivation.propose(ModelWantProposal(
            proposal_id="windows-model-proposal", target=claim.target,
            kind=claim.kind, evidence_id=claim.evidence_id,
            reason="review bounded current work"), admitted)
        self.assertIsNotNone(goal)
        self.snapshot = motivation.snapshot()
        self.key = b"windows-native-test-key-is-not-a-production-secret"
        self.now = datetime.now(timezone.utc)
        self.runtime_sha = fingerprint_installed_volition()
        self._write(1)

    def _set_acl(self, path, *, extra_allow=None, extra_rights=None,
                 extra_inherit_only=False):
        import win32con
        import win32security
        dacl = win32security.ACL()
        inherited = win32con.OBJECT_INHERIT_ACE | win32con.CONTAINER_INHERIT_ACE
        for sid in (self.current,
                    win32security.ConvertStringSidToSid("S-1-5-18"),
                    win32security.ConvertStringSidToSid("S-1-5-32-544")):
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, inherited,
                                       win32con.GENERIC_ALL, sid)
        if extra_allow is not None:
            flags = inherited | (win32con.INHERIT_ONLY_ACE if extra_inherit_only else 0)
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, flags,
                                       win32con.GENERIC_READ if extra_rights is None
                                       else extra_rights, extra_allow)
        win32security.SetNamedSecurityInfo(
            str(path), win32security.SE_FILE_OBJECT,
            win32security.DACL_SECURITY_INFORMATION |
            win32security.PROTECTED_DACL_SECURITY_INFORMATION,
            None, None, dacl, None)

    def _write(self, publication):
        sealed = seal_host_state(snapshot=self.snapshot, owner_id="patrick",
                                 source_id="volition:host", publication=publication,
                                 captured_at=self.now, key=self.key)
        self.record.write_text(json.dumps(sealed), encoding="utf-8")

    def _provider(self):
        return VerifiedVolitionGoalProvider(
            record_path=self.record, ledger_path=self.ledger,
            key=self.key, owner_id="patrick", source_id="volition:host",
            expected_runtime_sha256=self.runtime_sha)

    def test_private_native_dacl_allows_read_only_projection_and_rejects_rollback(self):
        provider = self._provider()
        result = provider.read_projection(now=self.now)
        self.assertEqual(result["status"], "PROPOSED_REVIEW")
        self.assertFalse(result["effect_authority"])
        self._write(2)
        self.assertEqual(provider.read_projection(now=self.now)["status"], "PROPOSED_REVIEW")
        self._write(1)
        with self.assertRaisesRegex(GoalViewError, "rolled back"):
            self._provider().read_projection(now=self.now)

    def test_file_dacl_granting_builtin_users_read_is_refused(self):
        import win32security
        self._set_acl(self.record, extra_allow=win32security.ConvertStringSidToSid("S-1-5-32-545"))
        with self.assertRaisesRegex(GoalViewError, "ACL grants another identity"):
            self._provider()

    def test_parent_dacl_granting_everyone_read_is_refused(self):
        import win32security
        self._set_acl(self.private, extra_allow=win32security.ConvertStringSidToSid("S-1-1-0"))
        with self.assertRaisesRegex(GoalViewError, "ACL grants another identity"):
            self._provider()

    def test_grandparent_delete_child_by_untrusted_identity_is_refused(self):
        import win32security
        self._set_acl(self.sandbox,
                      extra_allow=win32security.ConvertStringSidToSid("S-1-5-32-545"),
                      extra_rights=0x00000040)  # DELETE_CHILD; leaf DACL stays private
        with self.assertRaisesRegex(GoalViewError, "ancestor custody refused"):
            self._provider()

    def test_grandparent_inherit_only_ace_does_not_grant_direct_delete(self):
        import win32security
        self._set_acl(self.sandbox,
                      extra_allow=win32security.ConvertStringSidToSid("S-1-5-32-545"),
                      extra_rights=0x00000040, extra_inherit_only=True)
        self.assertEqual(self._provider().read_projection(now=self.now)["status"],
                         "PROPOSED_REVIEW")

    def test_record_symlink_is_not_accepted(self):
        other = self.private / "target.json"
        other.write_bytes(self.record.read_bytes())
        self.record.unlink()
        try:
            self.record.symlink_to(other)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"runner cannot create Windows symlink: {exc}")
        with self.assertRaisesRegex(GoalViewError, "symlink/reparse"):
            self._provider()

    def test_missing_ledger_broken_symlink_is_not_treated_as_vacant(self):
        try:
            self.ledger.symlink_to(self.private / "nonexistent-ledger.sqlite3")
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"runner cannot create Windows symlink: {exc}")
        with self.assertRaisesRegex(GoalViewError, "symlink/reparse"):
            self._provider()


if __name__ == "__main__":
    unittest.main()
