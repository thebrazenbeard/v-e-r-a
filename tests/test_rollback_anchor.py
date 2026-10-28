"""Bounded rollback witness regression; does NOT prove whole-host rollback safety."""

from __future__ import annotations

import os
from contextlib import closing
import hashlib
import hmac
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from interface.local_transcript import TranscriptStore
from interface.rollback_anchor import RollbackAnchor, _DOMAIN, _canonical


@unittest.skipIf(os.name == "nt", "Windows private DACL fixtures require real host qualification")
class RollbackAnchorTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        root = Path(self.root.name)
        self.dbdir = root / "vault"
        self.anchordir = root / "witness"
        self.dbdir.mkdir(mode=0o700)
        self.anchordir.mkdir(mode=0o700)
        self.db = self.dbdir / "vault.sqlite3"
        self.anchor = self.anchordir / "highwater.json"
        self.key = "operator-test-secret-0123456789abcdef"

    def _open(self):
        return TranscriptStore(self.db, self.key, rollback_anchor_path=self.anchor)

    def test_database_only_rollback_after_delete_is_refused(self):
        store = self._open()
        self.assertEqual(store.read()["status"], "empty")
        store.save([{"role": "user", "content": "sensitive snapshot"}], 0)
        backup = self.dbdir / "old-copy.sqlite3"
        shutil.copyfile(self.db, backup)
        store.delete(1)
        self.assertEqual(store.read()["status"], "empty")
        shutil.copyfile(backup, self.db)
        with patch.object(TranscriptStore, "_decrypt",
                          side_effect=AssertionError("stale ciphertext decrypted before custody")):
            with self.assertRaisesRegex(ValueError, "rollback|divergence"):
                self._open()
        with self.assertRaisesRegex(ValueError, "rollback|divergence"):
            store.read()

    def test_witness_mac_uses_scrypt_material_not_fast_raw_secret(self):
        self._open()
        with closing(sqlite3.connect(self.db)) as db:
            salt = db.execute("SELECT salt FROM vault_crypto WHERE slot=1").fetchone()[0]
        material = hashlib.scrypt(self.key.encode("ascii"), salt=salt,
                                  n=2 ** 14, r=8, p=1, dklen=32)
        witness = json.loads(self.anchor.read_text(encoding="ascii"))
        record = {field: value for field, value in witness.items() if field != "mac"}
        expected_derived_key = hmac.new(material, _DOMAIN, hashlib.sha256).digest()
        expected = hmac.new(expected_derived_key, _canonical(record), hashlib.sha256).hexdigest()
        fast_key = hmac.new(self.key.encode("ascii"), _DOMAIN, hashlib.sha256).digest()
        fast_oracle = hmac.new(fast_key, _canonical(record), hashlib.sha256).hexdigest()
        self.assertEqual(witness["mac"], expected)
        self.assertNotEqual(witness["mac"], fast_oracle,
                            "raw-secret HMAC would bypass the vault's scrypt work factor")
        # The same KDF-derived witness must remain verifiable after restart.
        self.assertEqual(self._open().read()["status"], "empty")

    def test_witness_missing_or_tampered_is_not_recreated_for_existing_db(self):
        store = self._open()
        store.save([{"role": "user", "content": "one"}], 0)
        self.anchor.write_text('{"version":1,"revision":999,"fingerprint":"x"}', encoding="ascii")
        with self.assertRaisesRegex(ValueError, "schema|contents|authentication"):
            self._open()
        self.anchor.unlink()
        with self.assertRaisesRegex(ValueError, "unavailable"):
            self._open()

    def test_oversized_witness_is_bounded_before_json_decode(self):
        store = self._open()
        self.anchor.write_bytes(b"x" * (10 * 1024 * 1024))
        with patch.object(Path, "read_bytes", side_effect=AssertionError("unbounded read")):
            with self.assertRaisesRegex(ValueError, "oversized"):
                store.read()

    def test_crash_between_witness_and_database_commit_fails_closed(self):
        store = self._open()
        actual = RollbackAnchor.advance

        def die_after_witness(anchor, revision, fingerprint):
            actual(anchor, revision, fingerprint)
            raise RuntimeError("injected precommit crash")

        with patch.object(RollbackAnchor, "advance", die_after_witness):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                store.save([{"role": "user", "content": "one"}], 0)
        with self.assertRaisesRegex(ValueError, "rollback|divergence"):
            store.read()

    def test_attacker_with_both_witness_and_db_backup_can_rollback(self):
        store = self._open()
        store.save([{"role": "user", "content": "FULL-ROOT-ROLLBACK-LIMIT"}], 0)
        db_backup = self.dbdir / "old-copy.sqlite3"
        anchor_backup = self.anchordir / "old-copy.json"
        shutil.copyfile(self.db, db_backup)
        shutil.copyfile(self.anchor, anchor_backup)
        store.delete(1)
        shutil.copyfile(db_backup, self.db)
        shutil.copyfile(anchor_backup, self.anchor)
        # Known limitation, not a success of forensic erasure.
        restored = self._open().read()
        self.assertIn("FULL-ROOT-ROLLBACK-LIMIT", restored["messages"][0]["content"])

    def test_anchor_must_be_separate_from_vault_dir(self):
        with self.assertRaisesRegex(ValueError, "separate protected directory"):
            TranscriptStore(self.db, self.key,
                            rollback_anchor_path=self.dbdir / "bad.json")
        self.assertFalse(self.db.exists(), "invalid anchor must not create an orphan DB")

    def test_existing_anchored_vault_refuses_restart_without_witness_option(self):
        store = self._open()
        store.save([{"role": "user", "content": "must remain anchored"}], 0)
        with self.assertRaisesRegex(ValueError, "requires its configured rollback witness"):
            TranscriptStore(self.db, self.key)
        self.assertEqual(self._open().read()["messages"][0]["content"],
                         "must remain anchored")

    def test_existing_unanchored_vault_cannot_silently_add_witness(self):
        normal = TranscriptStore(self.db, self.key)
        normal.save([{"role": "user", "content": "unanchored legacy"}], 0)
        with self.assertRaisesRegex(ValueError, "requires reviewed migration"):
            self._open()
        self.assertFalse(self.anchor.exists())

    def test_invalid_anchor_parent_does_not_create_orphan_db(self):
        missing = self.anchordir / "nonexistent" / "anchor.json"
        with self.assertRaisesRegex(ValueError, "parent directory unavailable"):
            TranscriptStore(self.db, self.key, rollback_anchor_path=missing)
        self.assertFalse(self.db.exists())
        # A corrected path should then initialize successfully without an
        # operator having to delete a stranded empty SQLite file.
        self.assertEqual(self._open().read()["status"], "empty")


if __name__ == "__main__":
    unittest.main()
