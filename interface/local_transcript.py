"""Explicit opt-in, single-operator transcript persistence (never implicit model memory).

This local SQLite store preserves only a bounded transcript the operator chose
to save. It neither extracts durable facts nor grants action authority.
"""

from __future__ import annotations

import hashlib
import base64
import binascii
import hmac
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
from threading import Lock

from .vault_acl import require_private_regular_file, require_protected_parent_directory


_ENCRYPTED_PREFIX = "v1.aes256gcm."
_ENCRYPTION_AAD = b"vera.local-transcript.slot-1.v1.revision."


class TranscriptConflict(Exception):
    """A write was based on a superseded vault revision."""


class TranscriptStore:
    def __init__(self, path: str | Path, secret: str):
        if (type(secret) is not str or len(secret) < 32 or len(secret) > 256
                or not secret.isascii() or not secret.isprintable()):
            raise ValueError("transcript encryption key must be 32..256 printable ASCII characters")
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError as exc:
            raise ValueError("authenticated transcript encryption requires cryptography") from exc
        supplied = Path(path).expanduser()
        if supplied.is_symlink():
            raise ValueError("transcript DB symlink refused")
        self.path = supplied.resolve(strict=False)
        if not self.path.parent.is_dir() or self.path.is_dir():
            raise ValueError("transcript DB parent must exist")
        require_protected_parent_directory(supplied, label="transcript DB")
        if self.path.exists() and not self.path.is_file():
            raise ValueError("transcript DB must be regular file")
        if not self.path.exists():
            flags = os.O_CREAT | os.O_EXCL | os.O_RDWR
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            try:
                descriptor = os.open(self.path, flags, 0o600)
            except FileExistsError as exc:
                raise ValueError("transcript DB changed during creation") from exc
            else:
                os.close(descriptor)
        require_private_regular_file(self.path, label="transcript DB")
        self._lock = Lock()
        with closing(self._connect()) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS transcript ("
                       "slot INTEGER PRIMARY KEY CHECK(slot=1), "
                       "body TEXT NOT NULL, sha256 TEXT NOT NULL, "
                       "saved_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS audit ("
                       "seq INTEGER PRIMARY KEY, action TEXT NOT NULL, "
                       "occurred_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS vault_revision ("
                       "slot INTEGER PRIMARY KEY CHECK(slot=1), "
                       "revision INTEGER NOT NULL CHECK(revision>=0))")
            db.execute("INSERT OR IGNORE INTO vault_revision (slot, revision) VALUES (1,0)")
            db.execute("CREATE TABLE IF NOT EXISTS vault_crypto ("
                       "slot INTEGER PRIMARY KEY CHECK(slot=1), "
                       "version INTEGER NOT NULL, salt BLOB NOT NULL, "
                       "key_check TEXT NOT NULL)")
            # Do not migrate old plaintext data implicitly or silently delete it.
            existing = db.execute("SELECT body FROM transcript WHERE slot=1").fetchone()
            if existing and (type(existing[0]) is not str
                             or not existing[0].startswith(_ENCRYPTED_PREFIX)):
                raise ValueError("legacy plaintext transcript refused; offline migration required")
            crypto = db.execute("SELECT version,salt,key_check FROM vault_crypto WHERE slot=1").fetchone()
            if crypto is None:
                salt = os.urandom(16)
            elif (crypto[0] == 1 and type(crypto[1]) is bytes and len(crypto[1]) == 16
                  and type(crypto[2]) is str and len(crypto[2]) == 64):
                salt = crypto[1]
            else:
                raise ValueError("invalid transcript encryption metadata")
            material = hashlib.scrypt(secret.encode("ascii"), salt=salt,
                                      n=2 ** 14, r=8, p=1, dklen=32)
            key_check = hmac.new(material, b"vera.local-transcript.key-check.v1",
                                 hashlib.sha256).hexdigest()
            if crypto is None:
                db.execute("INSERT INTO vault_crypto (slot,version,salt,key_check) VALUES (1,1,?,?)",
                           (salt, key_check))
            elif not hmac.compare_digest(key_check, crypto[2]):
                raise ValueError("transcript encryption key authentication failed")
            self._cipher = AESGCM(material)
            if existing:
                # A wrong key must not quietly open a vault that later appears
                # empty or corrupt. Authenticate active data before serving.
                self._decrypt(existing[0], self._revision(db))

    @staticmethod
    def _aad(revision: int) -> bytes:
        return _ENCRYPTION_AAD + str(revision).encode("ascii")

    def _encrypt(self, cleartext: bytes, revision: int) -> str:
        nonce = os.urandom(12)
        encrypted = self._cipher.encrypt(nonce, cleartext, self._aad(revision))
        return _ENCRYPTED_PREFIX + base64.urlsafe_b64encode(nonce + encrypted).decode("ascii")

    def _decrypt(self, wrapped: str, revision: int) -> bytes:
        if type(wrapped) is not str or not wrapped.startswith(_ENCRYPTED_PREFIX):
            raise ValueError("legacy or unrecognized plaintext transcript refused")
        try:
            packed = base64.b64decode(wrapped[len(_ENCRYPTED_PREFIX):], altchars=b"-_",
                                      validate=True)
            if len(packed) < 29:
                raise ValueError("encrypted transcript too short")
            return self._cipher.decrypt(packed[:12], packed[12:], self._aad(revision))
        except (ValueError, binascii.Error, UnicodeError) as exc:
            raise ValueError("encrypted transcript decryption failed") from exc
        except Exception as exc:
            # cryptography InvalidTag is intentionally not part of the public
            # error boundary: never reveal whether ciphertext or key was wrong.
            raise ValueError("encrypted transcript authentication failed") from exc

    def _connect(self):
        if self.path.is_symlink():
            raise ValueError("transcript DB symlink refused")
        # Recheck custody at each operation; a permission change after launch
        # must not turn an active vault into an implicitly shared file.
        require_private_regular_file(self.path, label="transcript DB")
        db = sqlite3.connect(self.path, timeout=5)
        db.execute("PRAGMA busy_timeout=5000")
        # Best-effort SQLite page-content cleanup, not filesystem/backup erasure.
        db.execute("PRAGMA secure_delete=ON")
        return db

    @staticmethod
    def _revision(db):
        return db.execute("SELECT revision FROM vault_revision WHERE slot=1").fetchone()[0]

    @staticmethod
    def _check_revision(db, expected_revision):
        if type(expected_revision) is not int or not 0 <= expected_revision <= 9223372036854775806:
            raise ValueError("invalid expected vault revision")
        current = TranscriptStore._revision(db)
        if expected_revision != current:
            raise TranscriptConflict("vault revision changed")
        return current + 1

    def save(self, messages: list[dict[str, str]], expected_revision: int) -> dict:
        raw = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
        if len(raw.encode("utf-8")) > 24 * 1024:
            raise ValueError("transcript exceeds byte budget")
        # The DB and audit contain ciphertext only, not a plaintext hash that
        # could be used for offline dictionary guesses about short messages.
        with self._lock, closing(self._connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            revision = self._check_revision(db, expected_revision)
            wrapped = self._encrypt(raw.encode("utf-8"), revision)
            digest = hashlib.sha256(wrapped.encode("ascii")).hexdigest()
            db.execute("INSERT OR REPLACE INTO transcript (slot,body,sha256,saved_at) "
                       "VALUES (1,?,?,strftime('%Y-%m-%dT%H:%M:%fZ','now'))",
                       (wrapped, digest))
            db.execute("UPDATE vault_revision SET revision=? WHERE slot=1", (revision,))
            db.execute("INSERT INTO audit (action, occurred_at) VALUES "
                       "('operator_save',strftime('%Y-%m-%dT%H:%M:%fZ','now'))")
        return {"sha256": digest, "status": "saved", "revision": revision}

    def read(self) -> dict:
        with self._lock, closing(self._connect()) as db:
            db.execute("BEGIN")
            revision = self._revision(db)
            row = db.execute("SELECT body,sha256,saved_at FROM transcript WHERE slot=1").fetchone()
        if row is None:
            return {"status": "empty", "messages": [], "revision": revision}
        body, digest, saved_at = row
        if hashlib.sha256(body.encode("utf-8")).hexdigest() != digest:
            raise ValueError("persisted transcript integrity failed")
        decoded = self._decrypt(body, revision).decode("utf-8")
        return {"status": "saved", "messages": json.loads(decoded), "revision": revision,
                "sha256": digest, "saved_at": saved_at,
                "provenance": "operator_saved_browser_transcript; unverified content"}

    def delete(self, expected_revision: int) -> dict:
        with self._lock, closing(self._connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            revision = self._check_revision(db, expected_revision)
            db.execute("DELETE FROM transcript WHERE slot=1")
            db.execute("UPDATE vault_revision SET revision=? WHERE slot=1", (revision,))
            db.execute("INSERT INTO audit (action, occurred_at) VALUES "
                       "('operator_delete',strftime('%Y-%m-%dT%H:%M:%fZ','now'))")
        # This removes the active row. SQLite freelists, journals/WAL, snapshots,
        # filesystem history, and backups may still retain bytes. NOT secure erase.
        return {"status": "removed_from_active_vault", "forensic_erasure": False,
                "revision": revision}
