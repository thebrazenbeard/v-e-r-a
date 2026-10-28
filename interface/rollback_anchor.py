"""Optional external witness for detecting *database-only* vault rollback.

The witness must be operator-controlled and kept outside the database backup
boundary. It is not a tamper-resistant clock, secure erasure, or protection
against restoration of the witness and database together.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets

from .vault_acl import require_private_regular_file, require_protected_parent_directory


_DOMAIN = b"vera.local-transcript.rollback-anchor.v1\x00"


def _canonical(record: dict) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def _reject_duplicate_keys(pairs):
    found = {}
    for key, value in pairs:
        if key in found:
            raise ValueError("duplicate rollback anchor field")
        found[key] = value
    return found


class RollbackAnchor:
    """HMAC-sealed independent revision/fingerprint witness.

    A witness advanced before SQLite COMMIT can fail closed on an interrupted
    mutation. The operator must investigate/restage from a trusted source; the
    application must not silently lower the witness to make an old DB readable.
    """

    def __init__(self, path: str | Path, db_path: Path):
        supplied = Path(path).expanduser()
        if supplied.is_symlink():
            raise ValueError("rollback anchor symlink refused")
        self.path = supplied.resolve(strict=False)
        if self.path == db_path or self.path.parent == db_path.parent:
            raise ValueError("rollback anchor must use a separate protected directory")
        require_protected_parent_directory(supplied, label="rollback anchor")
        if self.path.exists():
            require_private_regular_file(self.path, label="rollback anchor")
        # Deliberately do not authenticate witness records with a fast MAC of
        # the raw operator secret: that would create a cheap offline password
        # guessing oracle that bypasses the vault's scrypt cost. Key binding
        # is performed only after the *existing per-DB salted scrypt KDF*.
        self._mac_key: bytes | None = None

    def bind_scrypt_material(self, material: bytes) -> None:
        if self._mac_key is not None or type(material) is not bytes or len(material) != 32:
            raise ValueError("invalid rollback anchor key binding")
        self._mac_key = hmac.new(material, _DOMAIN, hashlib.sha256).digest()

    def _seal(self, record: dict) -> dict:
        if self._mac_key is None:
            raise ValueError("rollback anchor key not bound")
        return {**record, "mac": hmac.new(self._mac_key, _canonical(record),
                                          hashlib.sha256).hexdigest()}

    def _read(self) -> dict:
        require_private_regular_file(self.path, label="rollback anchor")
        try:
            with self.path.open("rb") as stream:
                # Reject hostile oversized witnesses without reading an
                # unbounded operator-controlled file into memory.
                raw = stream.read(2049)
            if len(raw) > 2048:
                raise ValueError("rollback anchor oversized")
            obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("rollback anchor unreadable") from exc
        if type(obj) is not dict or set(obj) != {"version", "revision", "fingerprint", "mac"}:
            raise ValueError("rollback anchor schema invalid")
        record = {k: v for k, v in obj.items() if k != "mac"}
        if (obj["version"] != 1 or type(obj["revision"]) is not int
                or not 0 <= obj["revision"] < 2 ** 63
                or type(obj["fingerprint"]) is not str or len(obj["fingerprint"]) != 64
                or type(obj["mac"]) is not str or len(obj["mac"]) != 64):
            raise ValueError("rollback anchor contents invalid")
        if not hmac.compare_digest(self._seal(record)["mac"], obj["mac"]):
            raise ValueError("rollback anchor authentication failed")
        return record

    def verify(self, revision: int, fingerprint: str) -> None:
        record = self._read()
        if record["revision"] != revision or record["fingerprint"] != fingerprint:
            raise ValueError("vault rollback or witness/DB divergence detected")

    def advance(self, revision: int, fingerprint: str) -> None:
        """Durably witness target *before* DB commits; errors halt mutation."""
        self._replace(self._seal({"version": 1, "revision": revision,
                                  "fingerprint": fingerprint}), exclusive=False)

    def initialize(self, fingerprint: str) -> None:
        if self.path.exists():
            raise ValueError("rollback anchor exists for a new vault")
        self._replace(self._seal({"version": 1, "revision": 0,
                                  "fingerprint": fingerprint}), exclusive=True)

    def _replace(self, record: dict, *, exclusive: bool) -> None:
        require_protected_parent_directory(self.path, label="rollback anchor")
        # Exclusive creation prevents two concurrent processes from racing to
        # initialize different vaults with the same intended witness path.
        if exclusive:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            fd = os.open(self.path, flags, 0o600)
            target = self.path
        else:
            require_private_regular_file(self.path, label="rollback anchor")
            target = self.path.with_name(self.path.name + "." + secrets.token_hex(12) + ".tmp")
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            fd = os.open(target, flags, 0o600)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(_canonical(record))
                stream.flush()
                os.fsync(stream.fileno())
            require_private_regular_file(target, label="rollback anchor")
            if not exclusive:
                os.replace(target, self.path)
            # Directory fsync is needed to make rename durable on POSIX. On
            # Windows Python cannot portably fsync a directory handle; power
            # failure semantics must be qualified on the actual filesystem.
            if os.name != "nt":
                dirfd = os.open(self.path.parent, os.O_RDONLY)
                try:
                    os.fsync(dirfd)
                finally:
                    os.close(dirfd)
        finally:
            if not exclusive and target.exists():
                target.unlink()
