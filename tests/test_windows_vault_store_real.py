"""Native Windows encrypted-vault round trip under a genuinely private DACL.

Linux runs skip this test. The Windows job must run it with pywin32; an
emulated Windows ACL test does not qualify real file custody.
"""

from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from interface.local_transcript import TranscriptStore
from interface.vault_acl import require_private_regular_file, require_protected_parent_directory


@contextmanager
def _windows_private_directory():
    """Create an inherited owner-only Win32 DACL for disposable test files."""
    import win32api
    import win32con
    import win32security

    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder)
        token = win32security.OpenProcessToken(win32api.GetCurrentProcess(),
                                               win32con.TOKEN_QUERY)
        current_sid = win32security.GetTokenInformation(token,
                                                         win32security.TokenUser)[0]
        private = win32security.ACL()
        inheritable = win32con.OBJECT_INHERIT_ACE | win32con.CONTAINER_INHERIT_ACE
        for sid in (
            current_sid,
            win32security.ConvertStringSidToSid("S-1-5-18"),
            win32security.ConvertStringSidToSid("S-1-5-32-544"),
        ):
            private.AddAccessAllowedAceEx(win32security.ACL_REVISION,
                                          inheritable, win32con.FILE_ALL_ACCESS, sid)
        win32security.SetNamedSecurityInfo(
            str(target), win32security.SE_FILE_OBJECT,
            win32security.DACL_SECURITY_INFORMATION |
            win32security.PROTECTED_DACL_SECURITY_INFORMATION,
            None, None, private, None)
        yield target


@unittest.skipUnless(os.name == "nt", "native Windows DACL qualification")
class NativeWindowsEncryptedVaultTests(unittest.TestCase):
    def test_leaf_symlink_cannot_impersonate_a_private_file(self):
        with _windows_private_directory() as private:
            target = private / "actual.sqlite3"
            target.write_bytes(b"synthetic-test-content")
            alias = private / "alias.sqlite3"
            try:
                alias.symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Windows runner cannot create test symlink: {exc}")
            with self.assertRaisesRegex(ValueError, "symlink|reparse point refused"):
                require_private_regular_file(alias, label="vault")

    def test_shared_delete_child_on_grandparent_blocks_private_vault(self):
        import win32security

        with _windows_private_directory() as private:
            private_child = private / "child"
            private_child.mkdir()
            security = win32security.GetFileSecurity(str(private),
                win32security.DACL_SECURITY_INFORMATION)
            dacl = security.GetSecurityDescriptorDacl()
            world = win32security.ConvertStringSidToSid("S-1-1-0")
            # FILE_DELETE_CHILD on the grandparent can replace a private
            # child even when that child's own DACL is owner-only.
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, 0, 0x40, world)
            win32security.SetNamedSecurityInfo(str(private),
                win32security.SE_FILE_OBJECT,
                win32security.DACL_SECURITY_INFORMATION |
                win32security.PROTECTED_DACL_SECURITY_INFORMATION,
                None, None, dacl, None)

            with self.assertRaisesRegex(ValueError, "grants access"):
                require_protected_parent_directory(private_child / "vault.sqlite3",
                                                   label="vault")

    def test_encrypted_save_restart_delete_under_private_inherited_dacl(self):
        marker = "PRIVATE-NATIVE-WINDOWS-VAULT-MARKER-873492"
        key = "test-native-win-vault-secret-0123456789"
        with _windows_private_directory() as private:
            db_path = private / "private.sqlite3"
            first = TranscriptStore(db_path, key)
            self.assertEqual(first.read()["revision"], 0)
            self.assertEqual(first.save([{"role": "user", "content": marker}], 0)["revision"], 1)

            # Child-file custody must be genuinely verified by Win32, not mode bits.
            self.assertEqual(require_private_regular_file(db_path, label="vault"),
                             db_path.resolve())
            self.assertNotIn(marker.encode("utf-8"), db_path.read_bytes())
            with sqlite3.connect(db_path) as database:
                stored = database.execute("SELECT body FROM transcript WHERE slot=1").fetchone()[0]
            self.assertTrue(stored.startswith("v1.aes256gcm."))

            reopened = TranscriptStore(db_path, key)
            self.assertEqual(reopened.read()["messages"],
                             [{"role": "user", "content": marker}])
            self.assertEqual(reopened.delete(1)["revision"], 2)
            self.assertEqual(TranscriptStore(db_path, key).read()["status"], "empty")

    def test_vault_read_halts_if_existing_file_dacl_gains_world_read(self):
        import win32con
        import win32security

        key = "test-native-win-vault-secret-0123456789"
        with _windows_private_directory() as private:
            db_path = private / "private.sqlite3"
            store = TranscriptStore(db_path, key)
            store.save([{"role": "user", "content": "test"}], 0)
            security = win32security.GetFileSecurity(str(db_path),
                win32security.DACL_SECURITY_INFORMATION)
            dacl = security.GetSecurityDescriptorDacl()
            world = win32security.ConvertStringSidToSid("S-1-1-0")
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, 0,
                win32con.FILE_GENERIC_READ, world)
            win32security.SetNamedSecurityInfo(str(db_path),
                win32security.SE_FILE_OBJECT,
                win32security.DACL_SECURITY_INFORMATION |
                win32security.PROTECTED_DACL_SECURITY_INFORMATION,
                None, None, dacl, None)

            with self.assertRaisesRegex(ValueError, "grants access"):
                store.read()
            with self.assertRaisesRegex(ValueError, "grants access"):
                TranscriptStore(db_path, key)


if __name__ == "__main__":
    unittest.main()
