"""Read owner-provisioned local bearer keys without accepting shared files.

These file checks do not protect against processes running as the same owner
or against privileged code. Native process/port ownership is a separate gate.
"""

from __future__ import annotations

from pathlib import Path

from .vault_acl import require_private_regular_file


def load_private_bearer_file(path: str | Path, *, label: str) -> str:
    """Load exactly one printable key from an owner-private, non-reparse file.

    No file content or path is placed into exception messages or HTTP status.
    File ACL verification is inherited from the existing transcript custody
    verifier, including native Windows DACL checks when pywin32 is present.
    """
    target = require_private_regular_file(path, label=label)
    if not 32 <= target.stat().st_size <= 258:
        raise ValueError(f"{label} must contain one 32..256-byte key")
    try:
        raw = target.read_bytes()
        if raw.endswith(b"\r\n"):
            raw = raw[:-2]
        elif raw.endswith(b"\n"):
            raw = raw[:-1]
        key = raw.decode("ascii")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"{label} unreadable") from exc
    if not 32 <= len(key) <= 256 or any(ord(char) < 33 or ord(char) > 126 for char in key):
        raise ValueError(f"{label} must be one printable non-whitespace ASCII key")
    return key
