"""Real Win32 custody regression, distinct from mocked DACL decision tests.

Windows' default temporary-directory permissions vary by runner and must not
be treated as a private vault. Each test instead creates a disposable child
directory with an explicitly protected, current-user-only DACL. The system
temp directory, user profile, and production vault are never modified.
"""

from pathlib import Path
import os
import unittest

from interface.vault_acl import (
    _windows_is_local_fixed_volume_root,
    require_private_regular_file,
    require_protected_parent_directory,
)
from tests.windows_acl_fixture import (
    describe_windows_acl_chain, private_profile_temporary_directory,
)


@unittest.skipUnless(os.name == "nt", "real Windows DACL integration test")
class WindowsVaultAclIntegrationTests(unittest.TestCase):
    def test_runner_system_drive_is_a_real_native_fixed_volume(self):
        # Qualify the Windows runner's volume identity before interpreting its
        # root-owner exception. No system ACL or mount mapping is modified.
        self.assertTrue(_windows_is_local_fixed_volume_root(Path(Path.home().anchor)))

    def setUp(self):
        import win32api
        import win32con
        import win32security

        self.security = win32security
        self.con = win32con
        token = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(), win32con.TOKEN_QUERY
        )
        self.current_sid = win32security.GetTokenInformation(
            token, win32security.TokenUser
        )[0]
        self.other_sid = win32security.ConvertStringSidToSid("S-1-5-11")
        self.scratch = private_profile_temporary_directory()
        self.addCleanup(self.scratch.cleanup)
        self.private_dir = Path(self.scratch.name) / "owner-private"
        self.private_dir.mkdir()
        self._protect(self.private_dir)

    def _protect(self, path: Path, *, other_mask: int | None = None):
        """Replace inheritance on this disposable object with an explicit DACL."""
        security = self.security
        acl = security.ACL()
        acl.AddAccessAllowedAce(
            security.ACL_REVISION, self.con.GENERIC_ALL, self.current_sid
        )
        if other_mask is not None:
            acl.AddAccessAllowedAce(
                security.ACL_REVISION, other_mask, self.other_sid
            )
        security.SetNamedSecurityInfo(
            str(path), security.SE_FILE_OBJECT,
            security.DACL_SECURITY_INFORMATION |
            security.PROTECTED_DACL_SECURITY_INFORMATION,
            None, None, acl, None,
        )

    def _secret(self, filename: str) -> Path:
        path = self.private_dir / filename
        path.write_text("non-sensitive regression fixture", encoding="utf-8")
        self._protect(path)
        return path

    def test_explicit_owner_only_dacl_allows_private_file(self):
        secret = self._secret("private.txt")
        try:
            require_protected_parent_directory(secret, label="test key")
            self.assertEqual(
                require_private_regular_file(secret, label="test key"),
                secret.resolve(),
            )
        except ValueError as exc:
            self.fail(f"{exc}; actual ACL chain: " +
                      describe_windows_acl_chain(secret.parent))

    def test_authenticated_users_read_grant_on_file_fails_closed(self):
        secret = self._secret("broad-read.txt")
        self._protect(secret, other_mask=self.con.GENERIC_READ)
        with self.assertRaisesRegex(ValueError, "grants access to another identity"):
            require_private_regular_file(secret, label="test key")

    def test_authenticated_users_write_grant_on_parent_fails_closed(self):
        secret = self._secret("unprotected-parent.txt")
        self._protect(self.private_dir, other_mask=self.con.GENERIC_WRITE)
        with self.assertRaisesRegex(ValueError, "grants access to another identity"):
            require_protected_parent_directory(secret, label="test key")
        with self.assertRaisesRegex(ValueError, "grants access to another identity"):
            require_private_regular_file(secret, label="test key")


if __name__ == "__main__":
    unittest.main()
