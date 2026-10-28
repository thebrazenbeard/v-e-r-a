"""Test-only Windows custody fixture helpers, never production ACL changes."""

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
