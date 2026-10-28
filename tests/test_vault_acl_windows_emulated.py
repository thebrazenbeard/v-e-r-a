"""Emulated Windows DACL logic tests; NOT a real Win32 ACL qualification.

Keep the distinction explicit: these verify deny/allow decisions given pywin32
return values. They cannot establish filesystem custody on Lappy.
"""

from pathlib import Path, PureWindowsPath
import ctypes
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from interface.vault_acl import (
    _windows_is_local_fixed_volume_root,
    _windows_is_reparse, _windows_private_dacl, _windows_reject_reparse,
    _windows_verify_directory_chain,
)


CURRENT = "S-1-5-21-12345-67890-13579-1001"
OTHER = "S-1-5-21-12345-67890-13579-1002"
SYSTEM = "S-1-5-18"
TRUSTED_INSTALLER = "S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464"
OWNER_RIGHTS = "S-1-3-4"


class _Dacl:
    def __init__(self, aces):
        self.aces = aces

    def GetAceCount(self):
        return len(self.aces)

    def GetAce(self, index):
        return self.aces[index]


class _SecurityDescriptor:
    def __init__(self, aces, *, owner=CURRENT, has_dacl=True):
        self.aces = aces
        self.owner = owner
        self.has_dacl = has_dacl

    def GetSecurityDescriptorDacl(self):
        return _Dacl(self.aces) if self.has_dacl else None

    def GetSecurityDescriptorOwner(self):
        return self.owner


class WindowsAclEmulationTests(unittest.TestCase):
    def test_volume_identity_rejects_subst_and_remote_drive_targets(self):
        def inspect(target: str, drive_type: int) -> bool:
            def get_drive_type(_root):
                return drive_type

            def query(_name, buffer, _size):
                buffer.value = target
                return len(target) + 2

            kernel = SimpleNamespace(GetDriveTypeW=get_drive_type,
                                     QueryDosDeviceW=query)
            with patch.object(ctypes, "WinDLL", return_value=kernel, create=True):
                return _windows_is_local_fixed_volume_root(PureWindowsPath("X:/"))

        self.assertTrue(inspect(r"\Device\HarddiskVolume3", 3))
        for target, drive_type in (
            (r"\??\C:\sensitive\subdir", 3),  # SUBST points into directory
            (r"\Device\Mup\server\share", 4),  # Mapped SMB share
            (r"\Device\HarddiskVolume3\ordinary-subdir", 3),
            (r"\Device\HarddiskVolume3", 4),
        ):
            with self.subTest(target=target):
                self.assertFalse(inspect(target, drive_type))

    def _inspect(self, *, aces, owner=CURRENT, directory=False, ancestor=False,
                 has_dacl=True, path=None, native_volume=True):
        sd = _SecurityDescriptor(aces, owner=owner, has_dacl=has_dacl)
        security = SimpleNamespace(
            OWNER_SECURITY_INFORMATION=1, DACL_SECURITY_INFORMATION=4,
            TOKEN_QUERY=8, TokenUser=1,
            ACCESS_DENIED_ACE_TYPE=1, ACCESS_ALLOWED_ACE_TYPE=0,
            GetFileSecurity=lambda *_: sd,
            OpenProcessToken=lambda *_: object(),
            GetTokenInformation=lambda *_: (CURRENT, 0),
            ConvertSidToStringSid=str,
        )
        win32api = SimpleNamespace(GetCurrentProcess=lambda: object())
        win32con = SimpleNamespace(TOKEN_QUERY=8)
        with patch.dict(sys.modules, {
            "win32security": security,
            "win32api": win32api,
            "win32con": win32con,
        }), patch("interface.vault_acl._windows_is_local_fixed_volume_root",
                 return_value=native_volume):
            _windows_private_dacl(path or Path("X:/private/vault"), directory=directory,
                                  ancestor=ancestor)

    def test_trustedinstaller_owner_allowed_only_at_local_volume_root(self):
        own = ((0, 0), 0x001F01FF, SYSTEM)
        ordinary_reader = ((0, 0), 0x001200A9, OTHER)
        sibling_creator = ((0, 0), 0x00000004, OTHER)
        volume = PureWindowsPath("X:/")
        self._inspect(path=volume, directory=True, ancestor=True,
                      owner=TRUSTED_INSTALLER,
                      aces=[own, ordinary_reader, sibling_creator])
        # TrustedInstaller's own full-control ACE is owner-bound, not an
        # unrelated trustee merely because it is absent from the default set.
        self._inspect(path=volume, directory=True, ancestor=True,
                      owner=TRUSTED_INSTALLER,
                      aces=[own, ((0, 0), 0x001F01FF, TRUSTED_INSTALLER)])
        for path, ancestor in (
            (PureWindowsPath("X:/private"), True),
            (volume, False),
            (PureWindowsPath("X:relative"), True),
            (PureWindowsPath("//server/share/"), True),
        ):
            with self.subTest(path=str(path), ancestor=ancestor):
                with self.assertRaisesRegex(ValueError, "owned by another"):
                    self._inspect(path=path, directory=True, ancestor=ancestor,
                                  owner=TRUSTED_INSTALLER, aces=[own])
        with self.assertRaisesRegex(ValueError, "owned by another"):
            self._inspect(path=volume, directory=True, ancestor=True,
                          owner="S-1-5-80-123456", aces=[own])
        with self.assertRaisesRegex(ValueError, "owned by another"):
            self._inspect(path=volume, directory=True, ancestor=True,
                          owner=TRUSTED_INSTALLER, aces=[own],
                          native_volume=False)

    def test_trustedinstaller_root_does_not_hide_foreign_destructive_ace(self):
        volume = PureWindowsPath("X:/")
        for mask in (0x2, 0x40, 0x10000, 0x40000, 0x80000, 0x10000000):
            with self.subTest(mask=hex(mask)):
                with self.assertRaisesRegex(ValueError, "grants access"):
                    self._inspect(path=volume, directory=True, ancestor=True,
                                  owner=TRUSTED_INSTALLER,
                                  aces=[((0, 0), 0x001F01FF, SYSTEM),
                                        ((0, 0), mask, OTHER)])

    def test_owner_rights_ace_follows_trusted_owner_only(self):
        self._inspect(directory=True, ancestor=True,
                      aces=[((0, 0), 0x001F01FF, OWNER_RIGHTS),
                            ((0, 0), 0x001F01FF, CURRENT)])
        with self.assertRaisesRegex(ValueError, "owned by another"):
            self._inspect(directory=True, ancestor=True, owner=OTHER,
                          aces=[((0, 0), 0x001F01FF, OWNER_RIGHTS),
                                ((0, 0), 0x001F01FF, CURRENT)])

    def test_current_user_and_system_file_access_accepted(self):
        self._inspect(aces=[((0, 0), 0x001F01FF, CURRENT),
                            ((0, 0), 0x001F01FF, SYSTEM)])

    def test_other_user_file_read_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "grants access"):
            self._inspect(aces=[((0, 0), 0x1, OTHER),
                                ((0, 0), 0x1, CURRENT)])

    def test_directory_read_allowed_but_parent_mutations_rejected(self):
        self._inspect(directory=True, aces=[((0, 0), 0x00000001, OTHER),
                                              ((0, 0), 0x001F01FF, CURRENT)])
        for mutation_mask in (0x2, 0x4, 0x40, 0x10000, 0x40000, 0x80000,
                              0x40000000, 0x10000000):
            with self.subTest(mask=hex(mutation_mask)):
                with self.assertRaisesRegex(ValueError, "grants access"):
                    self._inspect(directory=True, aces=[
                        ((0, 0), mutation_mask, OTHER),
                        ((0, 0), 0x001F01FF, CURRENT),
                    ])

    def test_ancestor_allows_sibling_directory_creation_not_replacement(self):
        # FILE_ADD_SUBDIRECTORY (0x4) alone does not authorize renaming or
        # deleting the already-protected child; its immediate parent remains
        # deliberately stricter.
        own = ((0, 0), 0x001F01FF, CURRENT)
        sibling_create = ((0, 0), 0x00000004, OTHER)
        self._inspect(directory=True, ancestor=True, aces=[sibling_create, own])
        with self.assertRaisesRegex(ValueError, "grants access"):
            self._inspect(directory=True, ancestor=False, aces=[sibling_create, own])
        for dangerous in (0x2, 0x10, 0x40, 0x100, 0x10000, 0x40000, 0x80000,
                          0x40000000, 0x10000000, 0x02000000):
            with self.subTest(mask=hex(dangerous)):
                with self.assertRaisesRegex(ValueError, "grants access"):
                    self._inspect(directory=True, ancestor=True, aces=[
                        ((0, 0), dangerous, OTHER), own,
                    ])

    def test_inherit_only_ace_ignored_on_current_object_not_descendant(self):
        own = ((0, 0), 0x001F01FF, CURRENT)
        inherited_for_children = ((0, 0x08), 0x001F01FF, OTHER)
        self._inspect(directory=True, aces=[inherited_for_children, own])
        self._inspect(directory=True, ancestor=True,
                      aces=[inherited_for_children, own])
        self._inspect(aces=[inherited_for_children, own])
        with self.assertRaisesRegex(ValueError, "grants access"):
            self._inspect(directory=True, aces=[
                ((0, 0), 0x001F01FF, OTHER), own,
            ])

    def test_unknown_ace_type_foreign_owner_and_missing_dacl_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unverified ACE"):
            self._inspect(aces=[((5, 0), 0x1, CURRENT)])
        with self.assertRaisesRegex(ValueError, "owned by another"):
            self._inspect(owner=OTHER, aces=[((0, 0), 0x1, CURRENT)])
        with self.assertRaisesRegex(ValueError, "no trustworthy owner/DACL"):
            self._inspect(aces=[], has_dacl=False)

    def test_private_child_does_not_hide_writable_grandparent(self):
        with tempfile.TemporaryDirectory() as folder:
            nested = Path(folder) / "parent" / "child"
            nested.mkdir(parents=True)
            dangerous_ancestor = Path(folder)
            calls = []

            def inspect(path, *, directory, ancestor):
                self.assertTrue(directory)
                calls.append((path, ancestor))
                if path == dangerous_ancestor:
                    raise ValueError("Windows vault path grants access to another identity")

            with patch("interface.vault_acl._windows_private_dacl", side_effect=inspect), \
                    patch("interface.vault_acl._windows_is_reparse", return_value=False):
                with self.assertRaisesRegex(ValueError, "grants access"):
                    _windows_verify_directory_chain(nested, label="transcript DB")
            self.assertEqual(calls[:3], [(nested, False), (nested.parent, True),
                                        (dangerous_ancestor, True)])

    def test_private_chain_includes_anchor_and_refuses_reparse(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder) / "private"
            parent.mkdir()
            inspected = []

            def inspect(path, *, directory, ancestor):
                self.assertTrue(directory)
                inspected.append((path, ancestor))

            with patch("interface.vault_acl._windows_private_dacl", side_effect=inspect), \
                    patch("interface.vault_acl._windows_is_reparse", return_value=False):
                _windows_verify_directory_chain(parent, label="transcript DB")
            self.assertEqual(inspected[0], (parent, False))
            self.assertEqual(inspected[-1], (Path(parent.anchor), True))
            with patch("interface.vault_acl._windows_is_reparse", return_value=True):
                with self.assertRaisesRegex(ValueError, "ancestor reparse point refused"):
                    _windows_verify_directory_chain(parent, label="transcript DB")

    def test_native_reparse_attribute_is_checked_and_missing_api_fails_closed(self):
        security = SimpleNamespace()
        win32api = SimpleNamespace(GetFileAttributes=lambda *_: 0x400)
        win32con = SimpleNamespace(FILE_ATTRIBUTE_REPARSE_POINT=0x400)
        with patch.dict(sys.modules, {
            "win32security": security,
            "win32api": win32api,
            "win32con": win32con,
        }):
            self.assertTrue(_windows_is_reparse(Path("X:/private/ancestor")))
            win32api.GetFileAttributes = lambda *_: 0
            self.assertFalse(_windows_is_reparse(Path("X:/private/ancestor")))
            win32api.GetFileAttributes = lambda *_: (_ for _ in ()).throw(OSError("denied"))
            with self.assertRaisesRegex(ValueError, "failed closed"):
                _windows_is_reparse(Path("X:/private/ancestor"))

    def test_native_leaf_reparse_is_refused_before_file_acl(self):
        leaf = Path("X:/private/vault.sqlite3")
        with patch("interface.vault_acl._windows_is_reparse", return_value=True):
            with self.assertRaisesRegex(ValueError, "vault reparse point refused"):
                _windows_reject_reparse(leaf, label="vault")
        with patch("interface.vault_acl._windows_is_reparse", return_value=False):
            _windows_reject_reparse(leaf, label="vault")


if __name__ == "__main__":
    unittest.main()
