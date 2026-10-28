"""Emulated Windows DACL logic tests; NOT a real Win32 ACL qualification.

Keep the distinction explicit: these verify deny/allow decisions given pywin32
return values. They cannot establish filesystem custody on Lappy.
"""

from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from interface.vault_acl import _windows_private_dacl


CURRENT = "S-1-5-21-12345-67890-13579-1001"
OTHER = "S-1-5-21-12345-67890-13579-1002"
SYSTEM = "S-1-5-18"


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
    def _inspect(self, *, aces, owner=CURRENT, directory=False, has_dacl=True):
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
        }):
            _windows_private_dacl(Path("X:/private/vault"), directory=directory)

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

    def test_unknown_ace_type_foreign_owner_and_missing_dacl_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unverified ACE"):
            self._inspect(aces=[((5, 0), 0x1, CURRENT)])
        with self.assertRaisesRegex(ValueError, "owned by another"):
            self._inspect(owner=OTHER, aces=[((0, 0), 0x1, CURRENT)])
        with self.assertRaisesRegex(ValueError, "no trustworthy owner/DACL"):
            self._inspect(aces=[], has_dacl=False)


if __name__ == "__main__":
    unittest.main()
