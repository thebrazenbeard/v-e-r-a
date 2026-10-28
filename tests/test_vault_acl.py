"""Private vault custody checks, independent from the network interface."""

from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
from tests.windows_acl_fixture import private_test_temporary_directory

from interface.vault_acl import require_private_regular_file, require_protected_parent_directory


class VaultAclTests(unittest.TestCase):
    @unittest.skipIf(os.name == "nt", "Unix-specific mode assertions")
    def test_private_regular_file_allowed_but_broad_read_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "secret.txt"
            path.write_text("only a harmless test secret")
            path.chmod(0o600)
            self.assertEqual(require_private_regular_file(path, label="vault key"), path.resolve())
            path.chmod(0o644)
            with self.assertRaisesRegex(ValueError, "owner-only"):
                require_private_regular_file(path, label="vault key")

    def test_symlink_is_never_a_secret_file(self):
        with private_test_temporary_directory() as folder:
            path = Path(folder) / "secret.txt"
            path.write_text("only a harmless test secret")
            link = Path(folder) / "shortcut.txt"
            try:
                link.symlink_to(path)
            except OSError:
                self.skipTest("no symlink permission on this filesystem")
            with self.assertRaisesRegex(ValueError, "symlink refused"):
                require_private_regular_file(link, label="vault key")

    @unittest.skipIf(os.name == "nt", "Unix-specific mode assertions")
    def test_writable_parent_cannot_custody_vault_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "secret.txt"
            path.write_text("only a harmless test secret")
            path.chmod(0o600)
            Path(folder).chmod(0o777)
            with self.assertRaisesRegex(ValueError, "parent must not"):
                require_protected_parent_directory(path, label="vault key")
            with self.assertRaisesRegex(ValueError, "parent must not"):
                require_private_regular_file(path, label="vault key")

    @unittest.skipIf(os.name == "nt", "Unix-specific mode assertions")
    def test_writable_grandparent_without_sticky_bit_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            outer = Path(folder) / "untrusted"
            private = outer / "vault"
            private.mkdir(parents=True, mode=0o700)
            secret = private / "secret.txt"
            secret.write_text("test secret")
            secret.chmod(0o600)
            outer.chmod(0o777)
            with self.assertRaisesRegex(ValueError, "ancestor.*writable"):
                require_private_regular_file(secret, label="vault key")

    @unittest.skipIf(os.name == "nt", "Unix-specific mode assertions")
    def test_trusted_private_child_of_sticky_writable_ancestor_is_allowed(self):
        with tempfile.TemporaryDirectory() as folder:
            shared = Path(folder) / "shared"
            shared.mkdir(mode=0o700)
            shared.chmod(0o1777)
            private = shared / "vault"
            private.mkdir(mode=0o700)
            secret = private / "secret.txt"
            secret.write_text("test secret")
            secret.chmod(0o600)
            self.assertEqual(require_private_regular_file(secret, label="vault key"),
                             secret.resolve())

    @unittest.skipIf(os.name == "nt", "Unix-specific mode assertions")
    def test_symlink_grandparent_is_refused_even_if_target_private(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "target"
            private = target / "vault"
            private.mkdir(parents=True, mode=0o700)
            secret = private / "secret.txt"
            secret.write_text("test secret")
            secret.chmod(0o600)
            link = root / "alias"
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest("no symlink permission on this filesystem")
            with self.assertRaisesRegex(ValueError, "ancestor symlink"):
                require_private_regular_file(link / "vault" / "secret.txt", label="vault key")

    @unittest.skipIf(os.name == "nt", "Unix-specific mode assertions")
    def test_cli_refuses_secret_file_readable_by_another_user(self):
        with tempfile.TemporaryDirectory() as folder:
            secret = Path(folder) / "private-key"
            secret.write_text("operator-test-secret-0123456789abcdef")
            secret.chmod(0o644)
            attempted = subprocess.run([
                sys.executable, "-m", "interface", "--memory-db",
                str(Path(folder) / "unused.sqlite3"), "--memory-secret-file",
                str(secret), "--port", "0"], capture_output=True, text=True,
                cwd=Path(__file__).resolve().parents[1], timeout=10)
            self.assertNotEqual(attempted.returncode, 0)
            self.assertIn("invalid vault secret file", attempted.stderr)
            self.assertFalse((Path(folder) / "unused.sqlite3").exists())


if __name__ == "__main__":
    unittest.main()
