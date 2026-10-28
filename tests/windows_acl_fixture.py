"""Test-only Windows custody fixture helpers, never production ACL changes."""

from contextlib import contextmanager
import os
from pathlib import Path
import tempfile


def private_profile_temporary_directory():
    """Put disposable fixtures below the user's profile, not CI's shared TEMP.

    The actual ACL tests still verify the full ancestor chain. A protected
    child below a shared runner TEMP would give a false positive if an attacker
    could replace that child through a writable grandparent.
    """
    profile = Path.home()
    if not profile.is_dir() or profile.is_symlink():
        raise RuntimeError("Windows runner has no ordinary user-profile directory")
    return tempfile.TemporaryDirectory(prefix="vera-private-acl-", dir=profile)


@contextmanager
def private_test_temporary_directory():
    """Disposable private parent on either platform, with real Windows DACLs.

    Windows TEMP commonly permits other identities to modify its children.
    POSIX chmod does not repair that DACL.  For affirmative vault/custody
    tests, create a protected inheritable user/SYSTEM/Administrators DACL
    underneath the operator profile, and let production verify every ancestor.
    This helper is a fixture, not a permission bypass or a product fallback.
    """
    if os.name != "nt":
        with tempfile.TemporaryDirectory() as folder:
            yield folder
        return

    import win32api
    import win32con
    import win32security

    with private_profile_temporary_directory() as folder:
        token = win32security.OpenProcessToken(win32api.GetCurrentProcess(),
                                               win32con.TOKEN_QUERY)
        current = win32security.GetTokenInformation(token, win32security.TokenUser)[0]
        dacl = win32security.ACL()
        inherited = win32con.OBJECT_INHERIT_ACE | win32con.CONTAINER_INHERIT_ACE
        for sid in (current,
                    win32security.ConvertStringSidToSid("S-1-5-18"),
                    win32security.ConvertStringSidToSid("S-1-5-32-544")):
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, inherited,
                                       win32con.GENERIC_ALL, sid)
        win32security.SetNamedSecurityInfo(
            folder, win32security.SE_FILE_OBJECT,
            win32security.DACL_SECURITY_INFORMATION |
            win32security.PROTECTED_DACL_SECURITY_INFORMATION,
            None, None, dacl, None)
        yield folder


def describe_windows_acl_chain(path: Path) -> str:
    """Diagnostic-only SID/mask inventory for a failed positive custody check.

    This intentionally does not decide policy. `interface.vault_acl` remains
    the sole implementation of the fail-closed custody contract.
    """
    import win32security

    lines = []
    current = path
    while True:
        try:
            sd = win32security.GetFileSecurity(str(current),
                win32security.OWNER_SECURITY_INFORMATION |
                win32security.DACL_SECURITY_INFORMATION)
            dacl = sd.GetSecurityDescriptorDacl()
            owner = win32security.ConvertSidToStringSid(sd.GetSecurityDescriptorOwner())
            aces = []
            if dacl is not None:
                for index in range(min(dacl.GetAceCount(), 24)):
                    ace = dacl.GetAce(index)
                    sid = win32security.ConvertSidToStringSid(ace[2])
                    aces.append(f"{sid}:type={ace[0][0]}:flags=0x{ace[0][1]:x}:mask=0x{ace[1]:08x}")
                if dacl.GetAceCount() > 24:
                    aces.append(f"+{dacl.GetAceCount()-24} more ACE(s)")
            lines.append(f"{current} owner={owner} aces=[{'|'.join(aces)}]")
        except Exception as exc:
            lines.append(f"{current} diagnostic-unavailable={type(exc).__name__}")
        if current.parent == current:
            break
        current = current.parent
    return "; ".join(lines)
