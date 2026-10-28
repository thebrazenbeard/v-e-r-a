"""Read-only, fail-closed bridge from a *host-sealed* Volition state.

The host, not the model or browser, owns the HMAC key and is responsible for
verifying observations before sealing a snapshot. This module verifies exact
key custody, owner/source, freshness, monotonic publication and restoration
through Volition's real OperationalMotivation class. None grants effects.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import importlib
import json
import os
from pathlib import Path
import sqlite3
import stat
from threading import Lock
from typing import Any

from .goal_view import (GoalViewError, MAX_CURRENT_AGE, MAX_FUTURE_SKEW,
                        MAX_ENVELOPE_BYTES, project_volition_goal)


SCHEMA = "vera.host-sealed-volition.v1"
MAC_PREFIX = b"vera.host-sealed-volition.v1\x00"


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _pairs_once(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    found: dict[str, Any] = {}
    for key, value in pairs:
        if key in found:
            raise GoalViewError("duplicate sealed state key")
        found[key] = value
    return found


def _ident(value: object) -> bool:
    return (type(value) is str and 0 < len(value) <= 128 and value.strip() == value
            and all(33 <= ord(c) <= 126 for c in value))


def _private_regular(path: Path, *, allow_missing: bool = False) -> Path:
    """Refuse ambiguous and shared POSIX custody; Windows ACLs are not qualified."""
    if os.name == "nt":
        raise GoalViewError("Windows source/key ACL verification not implemented; refuse host adapter")
    if path.is_symlink():
        raise GoalViewError("host evidence symlink refused")
    resolved = path.resolve(strict=not allow_missing)
    parent_info = resolved.parent.stat()
    if (not stat.S_ISDIR(parent_info.st_mode) or parent_info.st_mode & 0o077
            or parent_info.st_uid != os.geteuid()):
        raise GoalViewError("host evidence directory must be same-owner private")
    if resolved.exists():
        info = resolved.stat()
        if (not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077
                or info.st_uid != os.geteuid()):
            raise GoalViewError("host evidence must be same-owner private regular file")
    elif not allow_missing:
        raise GoalViewError("missing host evidence")
    return resolved


def _read_private(path: Path, *, max_bytes: int) -> bytes:
    """Open once with NOFOLLOW and fstat, never read through a raced path."""
    _private_regular(path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if (not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077
                    or info.st_uid != os.geteuid()):
                raise GoalViewError("host evidence file ownership changed")
            if not 0 < info.st_size <= max_bytes:
                raise GoalViewError("host evidence file exceeds budget")
            raw = stream.read(max_bytes + 1)
    except OSError as exc:
        raise GoalViewError("host evidence unavailable") from exc
    if len(raw) > max_bytes:
        raise GoalViewError("host evidence exceeded byte budget")
    return raw


def _runtime_fingerprint() -> tuple[type, str]:
    """Import real Volition restoration; pin package source files as a set."""
    try:
        mod = importlib.import_module("volition.operational_drive")
        eng = importlib.import_module("volition.engine")
        model = getattr(mod, "OperationalMotivation")
        if not isinstance(model, type) or not callable(model.from_snapshot):
            raise AttributeError("Volition operational restore unavailable")
        root = Path(mod.__file__).resolve(strict=True).parent
        if root != Path(eng.__file__).resolve(strict=True).parent:
            raise GoalViewError("Volition modules are from different source roots")
        paths = sorted(root.rglob("*.py"))
        if not paths or any(path.is_symlink() for path in paths):
            raise GoalViewError("Volition source file missing or symlinked")
        digests = [(path.relative_to(root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
                   for path in paths]
        return model, hashlib.sha256(_canonical({
            "source_root_package": "volition",
            "source_files_sha256": digests,
        })).hexdigest()
    except (ImportError, AttributeError, OSError, TypeError) as exc:
        raise GoalViewError("pinned Volition restoration is unavailable") from exc


def fingerprint_installed_volition() -> str:
    """Read-only installer aid; the operator must pin the resulting digest."""
    return _runtime_fingerprint()[1]


def seal_host_state(*, snapshot: dict[str, Any], owner_id: str,
                    source_id: str, publication: int, captured_at: datetime,
                    key: bytes) -> dict[str, Any]:
    """Trusted host helper; NOT an observation attestation or model tool."""
    if (not _ident(owner_id) or not _ident(source_id)
            or type(publication) is not int or not 1 <= publication < 2 ** 63
            or not isinstance(captured_at, datetime) or captured_at.tzinfo is None
            or type(key) is not bytes or len(key) < 32):
        raise GoalViewError("invalid host sealing parameters")
    record = {"schema": SCHEMA, "owner_id": owner_id, "source_id": source_id,
              "publication": publication,
              "captured_at_utc": captured_at.astimezone(timezone.utc).isoformat(),
              "snapshot": snapshot}
    raw = _canonical(record)
    record["mac"] = "sha256:" + hmac.new(key, MAC_PREFIX + raw, hashlib.sha256).hexdigest()
    return record


class VerifiedVolitionGoalProvider:
    """Exact owner/source + HMAC + restored Volition + durable replay gate."""

    def __init__(self, *, record_path: str | Path, ledger_path: str | Path,
                 key: bytes, owner_id: str, source_id: str,
                 expected_runtime_sha256: str):
        if (type(key) is not bytes or len(key) < 32
                or not _ident(owner_id) or not _ident(source_id)
                or type(expected_runtime_sha256) is not str
                or len(expected_runtime_sha256) != 64
                or any(c not in "0123456789abcdef" for c in expected_runtime_sha256)):
            raise GoalViewError("invalid trusted provider configuration")
        self.record_path = _private_regular(Path(record_path).expanduser())
        self.ledger_path = _private_regular(Path(ledger_path).expanduser(), allow_missing=True)
        if self.record_path == self.ledger_path:
            raise GoalViewError("host record and replay ledger must be separate")
        self._key = key
        self._owner = owner_id
        self._source = source_id
        self._runtime_sha = expected_runtime_sha256
        self._lock = Lock()
        if not self.ledger_path.exists():
            flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(self.ledger_path, flags, 0o600)
            os.close(fd)
        with sqlite3.connect(self.ledger_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS seen ("
                       "owner TEXT NOT NULL, source TEXT NOT NULL, "
                       "publication INTEGER NOT NULL, digest TEXT NOT NULL, "
                       "PRIMARY KEY(owner,source))")

    def read_projection(self, *, now: datetime | None = None) -> dict[str, Any]:
        now = datetime.now(timezone.utc) if now is None else now
        if not isinstance(now, datetime) or now.tzinfo is None:
            raise GoalViewError("aware host clock required")
        now = now.astimezone(timezone.utc)
        raw = _read_private(self.record_path, max_bytes=MAX_ENVELOPE_BYTES)
        try:
            record = json.loads(raw, object_pairs_hook=_pairs_once,
                                parse_constant=lambda _: (_ for _ in ()).throw(GoalViewError("nonfinite JSON")))
        except GoalViewError:
            raise
        except (UnicodeError, ValueError) as exc:
            raise GoalViewError("malformed host-sealed state") from exc
        if (not isinstance(record, dict) or set(record) != {
                "schema", "owner_id", "source_id", "publication", "captured_at_utc", "snapshot", "mac"}
                or record["schema"] != SCHEMA
                or record["owner_id"] != self._owner or record["source_id"] != self._source
                or type(record["publication"]) is not int or not 1 <= record["publication"] < 2 ** 63
                or not isinstance(record["snapshot"], dict)):
            raise GoalViewError("host owner/source/publication mismatch")
        claimed_mac = record.pop("mac")
        if (type(claimed_mac) is not str or not claimed_mac.startswith("sha256:")
                or len(claimed_mac) != 71 or any(c not in "0123456789abcdef" for c in claimed_mac[7:])
                or not hmac.compare_digest(claimed_mac[7:],
                    hmac.new(self._key, MAC_PREFIX + _canonical(record), hashlib.sha256).hexdigest())):
            raise GoalViewError("untrusted host signature")
        try:
            captured = datetime.fromisoformat(record["captured_at_utc"].replace("Z", "+00:00"))
            if captured.tzinfo is None:
                raise ValueError("naive time")
            captured = captured.astimezone(timezone.utc)
        except (TypeError, ValueError) as exc:
            raise GoalViewError("invalid signed host time") from exc
        if captured - now > MAX_FUTURE_SKEW or now - captured > MAX_CURRENT_AGE:
            raise GoalViewError("signed host state is stale")
        restorer, runtime_sha = _runtime_fingerprint()
        if runtime_sha != self._runtime_sha:
            raise GoalViewError("unexpected Volition module revision")
        try:
            restored = restorer.from_snapshot(record["snapshot"])
            verified = restored.snapshot()
            if _canonical(verified) != _canonical(record["snapshot"]):
                raise ValueError("Volition restore changed snapshot content")
        except (TypeError, ValueError, KeyError) as exc:
            raise GoalViewError("Volition state restoration rejected") from exc
        envelope = {"schema": "vera.volition-view-envelope.v1",
                    "captured_at_utc": record["captured_at_utc"],
                    "source_ref": "host-sealed:" + self._source,
                    "snapshot": verified}
        projection = project_volition_goal(envelope, now=now)
        digest = hashlib.sha256(raw).hexdigest()
        publication = record["publication"]
        # A separate owner-only high-water mark survives restarts. Replaying an
        # older sealed publication after a later one is rejected even inside TTL.
        with self._lock:
            _private_regular(self.ledger_path)
            with sqlite3.connect(self.ledger_path, timeout=5) as db:
                db.execute("BEGIN IMMEDIATE")
                old = db.execute("SELECT publication,digest FROM seen WHERE owner=? AND source=?",
                                 (self._owner, self._source)).fetchone()
                if old is not None and (publication < old[0]
                                        or (publication == old[0] and digest != old[1])):
                    raise GoalViewError("host publication rolled back or equivocated")
                if old is None or publication > old[0]:
                    db.execute("INSERT INTO seen(owner,source,publication,digest) VALUES(?,?,?,?) "
                               "ON CONFLICT(owner,source) DO UPDATE SET "
                               "publication=excluded.publication,digest=excluded.digest",
                               (self._owner, self._source, publication, digest))
        return projection
