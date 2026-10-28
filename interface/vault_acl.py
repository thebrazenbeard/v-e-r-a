"""Fail-closed private file checks for opt-in transcript vault custody.

Windows checks use the DACL of the *actual file*, not POSIX mode emulation.
No ACLs are rewritten automatically. A missing Windows ACL inspection runtime
refuses vault activation rather than treating file existence as protection.
"""

from __future__ import annotations

import os
from pathlib import Path
import stat


def _windows_private_dacl(path: Path, *, directory: bool = False) -> None:
    try:
        import win32api
        import win32con
        import win32security
    except ImportError as exc:
        raise ValueError("Windows vault ACL verification requires pywin32") from exc
    try:
        sd = win32security.GetFileSecurity(str(path),
            win32security.OWNER_SECURITY_INFORMATION |
            win32security.DACL_SECURITY_INFORMATION)
        dacl = sd.GetSecurityDescriptorDacl()
        owner = sd.GetSecurityDescriptorOwner()
        current = win32security.GetTokenInformation(
            win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_QUERY),
            win32security.TokenUser)[0]
        if dacl is None or owner is None or current is None:
            raise ValueError("Windows vault path has no trustworthy owner/DACL")
        sid_text = win32security.ConvertSidToStringSid
        current_sid = sid_text(current)
        trusted_owners = {current_sid, "S-1-5-18", "S-1-5-32-544"}
        if sid_text(owner) not in trusted_owners:
            raise ValueError("Windows vault path is owned by another identity")
        allowed = trusted_owners | {"S-1-3-0"}
        has_trusted_allow = False
        # A directory can allow other identities to list/traverse, but never
        # to replace this vault's files, rename them, or rewrite its ACL.
        directory_write_mask = (0x40000000 | 0x10000000 | 0x02000000 |
                                0x00010000 | 0x00040000 | 0x00080000 |
                                0x00000002 | 0x00000004 | 0x00000010 |
                                0x00000040 | 0x00000100)
        for idx in range(dacl.GetAceCount()):
            ace = dacl.GetAce(idx)
            ace_type = ace[0][0]
            if ace_type == win32security.ACCESS_DENIED_ACE_TYPE:
                continue
            if ace_type != win32security.ACCESS_ALLOWED_ACE_TYPE:
                raise ValueError("Windows vault path uses unverified ACE type")
            principal = sid_text(ace[2])
            if (principal not in allowed
                    and (not directory or ace[1] & directory_write_mask)):
                raise ValueError("Windows vault path grants access to another identity")
            if principal in allowed:
                has_trusted_allow = True
        if not has_trusted_allow:
            raise ValueError("Windows vault path lacks a trustworthy allow rule")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Windows vault ACL verification failed closed") from exc


def require_private_regular_file(path: str | Path, *, label: str) -> Path:
    """Require a regular, non-symlink owner-private file; never change its ACL."""
    supplied = Path(path).expanduser()
    require_protected_parent_directory(supplied, label=label)
    if supplied.is_symlink():
        raise ValueError(f"{label} symlink refused")
    try:
        resolved = supplied.resolve(strict=True)
        mode = resolved.stat().st_mode
    except OSError as exc:
        raise ValueError(f"{label} unavailable") from exc
    if not stat.S_ISREG(mode):
        raise ValueError(f"{label} must be regular file")
    if os.name == "nt":
        _windows_private_dacl(resolved)
    else:
        if mode & 0o077:
            raise ValueError(f"{label} must have owner-only file permissions")
        if resolved.stat().st_uid != os.geteuid():
            raise ValueError(f"{label} must belong to the current user")
    return resolved


def require_protected_parent_directory(path: str | Path, *, label: str) -> None:
    """Deny shared-write parent directories where other users can swap files."""
    supplied = Path(path).expanduser()
    parent = supplied.parent
    if parent.is_symlink():
        raise ValueError(f"{label} parent directory symlink refused")
    try:
        resolved = parent.resolve(strict=True)
        mode = resolved.stat().st_mode
    except OSError as exc:
        raise ValueError(f"{label} parent directory unavailable") from exc
    if not stat.S_ISDIR(mode):
        raise ValueError(f"{label} parent must be a directory")
    if os.name == "nt":
        _windows_private_dacl(resolved, directory=True)
    elif mode & 0o022:
        raise ValueError(f"{label} parent must not be group/world writable")
