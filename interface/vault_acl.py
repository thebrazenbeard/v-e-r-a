"""Fail-closed private file checks for opt-in transcript vault custody.

Windows checks use the DACL of the *actual file*, not POSIX mode emulation.
No ACLs are rewritten automatically. A missing Windows ACL inspection runtime
refuses vault activation rather than treating file existence as protection.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import stat


def _windows_is_local_fixed_volume_root(path: Path) -> bool:
    """Refuse mapped or SUBST roots as a shortcut past actual ancestors.

    A drive-letter spelling alone does not establish a volume anchor: SUBST
    can map X: to an ordinary (potentially replaceable) directory.  Accept
    only a fixed drive whose DOS device target is a native volume device.
    Unknown mappings fail closed; this is not a race-free handle binding.
    """
    if (not path.is_absolute() or len(path.drive) != 2
            or path.drive[1] != ":" or path != type(path)(path.anchor)):
        return False
    try:
        import ctypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        drive_type = kernel.GetDriveTypeW
        drive_type.argtypes = [ctypes.c_wchar_p]
        drive_type.restype = ctypes.c_uint
        if drive_type(str(path.anchor)) != 3:  # DRIVE_FIXED
            return False
        query = kernel.QueryDosDeviceW
        query.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
        query.restype = ctypes.c_uint
        buffer = ctypes.create_unicode_buffer(4096)
        size = query(str(path.drive), buffer, len(buffer))
        if not size:
            return False
        targets = [target for target in buffer[:size].split("\0") if target]
        return bool(targets) and all(
            re.fullmatch(r"\\Device\\HarddiskVolume\d+", target, re.IGNORECASE)
            for target in targets
        )
    except Exception:
        return False


def _windows_private_dacl(path: Path, *, directory: bool = False,
                          ancestor: bool = False) -> None:
    if ancestor and not directory:
        raise ValueError("Windows vault ancestor must be a directory")
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
        # Windows can assign its system-volume root to TrustedInstaller.  Its
        # service SID is a fixed, documented operating-system principal; this
        # exception applies to that *exact* SID on a local drive root only,
        # never to an arbitrary service SID or a lower directory/file.  The
        # DACL is still checked for all foreign replacement/write rights.
        trustedinstaller_sid = (
            "S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464"
        )
        local_volume_root = (directory and ancestor and path.is_absolute()
                             and len(path.drive) == 2 and path.drive[1] == ":"
                             and path == type(path)(path.anchor)
                             and _windows_is_local_fixed_volume_root(path))
        owner_sid = sid_text(owner)
        trusted_owner = owner_sid in trusted_owners or (
            local_volume_root and owner_sid == trustedinstaller_sid)
        if not trusted_owner:
            raise ValueError("Windows vault path is owned by another identity")
        # OWNER RIGHTS (S-1-3-4) is the rights-bearing SID for this object's
        # already-checked owner.  It is not an additional foreign identity.
        allowed = trusted_owners | {owner_sid, "S-1-3-0", "S-1-3-4"}
        has_trusted_allow = False
        # The immediate parent must not permit another identity to create,
        # delete, or replace entries in the vault's directory. For higher
        # ancestors, merely creating a sibling subdirectory (0x00000004)
        # does not allow replacing the existing protected child. Mutation of
        # the ancestor itself (including setting a reparse point) or deleting
        # its protected child remains forbidden.
        ancestor_mutation_mask = (0x40000000 | 0x10000000 | 0x02000000 |
                                  0x00010000 | 0x00040000 | 0x00080000 |
                                  0x00000002 | 0x00000010 | 0x00000040 |
                                  0x00000100)
        immediate_parent_mask = ancestor_mutation_mask | 0x00000004
        directory_write_mask = (ancestor_mutation_mask if ancestor else
                                immediate_parent_mask)
        for idx in range(dacl.GetAceCount()):
            ace = dacl.GetAce(idx)
            # INHERIT_ONLY_ACE applies to descendants, not this object. The
            # descendant is checked separately as the chain is traversed.
            if ace[0][1] & 0x08:
                continue
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


def _windows_is_reparse(path: Path) -> bool:
    """Inspect the native file attributes; symlink/junction checks alone miss tags."""
    try:
        import win32api
        import win32con
    except ImportError as exc:
        raise ValueError("Windows vault reparse inspection requires pywin32") from exc
    try:
        return bool(win32api.GetFileAttributes(str(path)) &
                    win32con.FILE_ATTRIBUTE_REPARSE_POINT)
    except Exception as exc:
        raise ValueError("Windows vault reparse inspection failed closed") from exc


def _windows_reject_reparse(path: Path, *, label: str) -> None:
    if _windows_is_reparse(path):
        raise ValueError(f"{label} reparse point refused")


def _windows_verify_directory_chain(parent: Path, *, label: str) -> None:
    """Guard every ancestor against hostile replacement of a protected child.

    Checking only the immediate parent is insufficient on Windows: a principal
    with DELETE_CHILD or ACL-write rights on a grandparent may replace the
    *entire* protected directory. Stop at the filesystem anchor, including it.
    """
    current = parent
    immediate = True
    while True:
        if current.is_symlink() or _windows_is_reparse(current):
            raise ValueError(f"{label} ancestor reparse point refused")
        _windows_private_dacl(current, directory=True, ancestor=not immediate)
        immediate = False
        ancestor = current.parent
        if ancestor == current:
            break
        current = ancestor


def _posix_verify_directory_chain(parent: Path, *, label: str) -> None:
    """Check each lexical ancestor before trusting a private vault parent.

    A writable, non-sticky grandparent can replace an otherwise private child
    directory. A *higher* sticky directory (such as /tmp) is acceptable only
    when each child in the path is owned by this process or root: the sticky
    rule then prevents a different user from removing that child's entry.
    The immediate parent stays owner-private, even when it is sticky.

    This is a path-state check, not a claim of race-free directory-handle
    pinning or protection from the same UID / privileged adversaries.
    """
    if ".." in parent.parts:
        raise ValueError(f"{label} ancestor traversal refused")
    absolute_parent = parent.absolute()
    trusted_owners = {0, os.geteuid()}
    for directory in (*reversed(absolute_parent.parents), absolute_parent):
        try:
            metadata = directory.lstat()
        except OSError as exc:
            raise ValueError(f"{label} ancestor directory unavailable") from exc
        mode = metadata.st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f"{label} ancestor symlink refused")
        if not stat.S_ISDIR(mode):
            raise ValueError(f"{label} ancestor must be a directory")
        if metadata.st_uid not in trusted_owners:
            raise ValueError(f"{label} ancestor owned by another identity")
        if mode & 0o022:
            if directory == absolute_parent:
                raise ValueError(f"{label} parent must not be group/world writable")
            if not mode & stat.S_ISVTX:
                raise ValueError(f"{label} ancestor must not be non-sticky writable")


def require_private_regular_file(path: str | Path, *, label: str) -> Path:
    """Require a regular, non-symlink owner-private file; never change its ACL."""
    supplied = Path(path).expanduser()
    require_protected_parent_directory(supplied, label=label)
    if supplied.is_symlink():
        raise ValueError(f"{label} symlink refused")
    if os.name == "nt":
        # Native attributes cover junctions and other reparse tags that are
        # not necessarily reported by Path.is_symlink(). Check the supplied
        # name before resolving it and the resulting file before trusting it.
        _windows_reject_reparse(supplied, label=label)
    try:
        resolved = supplied.resolve(strict=True)
        mode = resolved.stat().st_mode
    except OSError as exc:
        raise ValueError(f"{label} unavailable") from exc
    if not stat.S_ISREG(mode):
        raise ValueError(f"{label} must be regular file")
    if os.name == "nt":
        _windows_reject_reparse(resolved, label=label)
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
        # Check the operator-supplied path (including ancestor reparse points)
        # as well as the resolved path. A writable grandparent can otherwise
        # replace the private directory after its immediate DACL was checked.
        _windows_verify_directory_chain(parent, label=label)
        if resolved != parent:
            _windows_verify_directory_chain(resolved, label=label)
    else:
        _posix_verify_directory_chain(parent, label=label)
