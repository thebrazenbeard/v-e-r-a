"""Synthetic, no-provider regression tests for Supabase snapshot currentness."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check_supabase_snapshot_currentness.py"
SPEC = importlib.util.spec_from_file_location("supabase_snapshot_guard", MODULE_PATH)
assert SPEC and SPEC.loader
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)
NOW = dt.datetime(2026, 11, 5, 20, tzinfo=dt.timezone.utc)
HEAD = "a" * 40
DIGEST = "b" * 64


class CurrentnessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.snapshot = self.root / "source"
        self.project = {
            "project_ref": "synthetic-project",
            "snapshot_source_head": HEAD,
            "observed_at": "2026-11-05T18:00:00Z",
            "definition_snapshot_only": True,
            "source_state": "SOURCE_DEFINITION_SNAPSHOT_ONLY",
        }
        self.history = {
            "project_ref": "synthetic-project",
            "count": 2,
            "migrations": [
                {"version": "20260101010101", "name": "create_a"},
                {"version": "20260102010101", "name": "create_b"},
            ],
        }
        self.binding = {
            "slug": "synthetic-edge",
            "project_ref": "synthetic-project",
            "status": "ACTIVE",
            "version": 5,
            "ezbr_sha256": DIGEST,
            "verify_jwt": False,
        }
        self.live = {
            "schema": "SUPABASE_METADATA_OBSERVATION_V1",
            "project_ref": "synthetic-project",
            "snapshot_source_head": HEAD,
            "observed_at": "2026-11-05T19:00:00Z",
            "migrations": self.history["migrations"].copy(),
            "functions": [self.binding.copy()],
        }
        self._save()

    def _write(self, relative: str, contents: object) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(contents), encoding="utf-8")

    def _save(self) -> None:
        self._write("source/supabase/project.json", self.project)
        self._write("source/supabase/migration-index.json", self.history)
        self._write("source/supabase/functions/synthetic-edge/binding.json", self.binding)
        self._write("live.json", self.live)

    def _check(self) -> dict[str, object]:
        self._save()
        return guard.compare(self.snapshot, self.root / "live.json", now=NOW)

    def assert_hold(self) -> None:
        result = self._check()
        self.assertEqual("HOLD_STALE_OR_UNBOUND", result["status"])
        self.assertFalse(result["effect_authority"])

    def test_exact_fresh_metadata_matches_only_without_authority(self) -> None:
        result = self._check()
        self.assertEqual("SOURCE_METADATA_MATCH_UNATTESTED", result["status"])
        self.assertFalse(result["effect_authority"])
        self.assertFalse(result["provider_authenticated_by_tool"])
        self.assertFalse(result["model_or_host_runtime_qualified"])

    def test_snapshot_currentness_missing(self) -> None:
        del self.project["observed_at"]
        self.assert_hold()

    def test_snapshot_source_head_missing(self) -> None:
        del self.project["snapshot_source_head"]
        self.assert_hold()

    def test_mismatched_source_head(self) -> None:
        self.live["snapshot_source_head"] = "c" * 40
        self.assert_hold()

    def test_live_edge_version_drift_even_with_same_migration_count(self) -> None:
        self.live["functions"][0]["version"] = 7
        self.assert_hold()

    def test_live_edge_digest_drift(self) -> None:
        self.live["functions"][0]["ezbr_sha256"] = "d" * 64
        self.assert_hold()

    def test_edge_auth_flag_drift(self) -> None:
        self.live["functions"][0]["verify_jwt"] = True
        self.assert_hold()

    def test_cross_project_function_binding_rejected(self) -> None:
        self.live["functions"][0]["project_ref"] = "other"
        self.assert_hold()

    def test_migration_identity_drift_with_same_count(self) -> None:
        self.live["migrations"][1] = {"version": "20260102010101", "name": "different"}
        self.assert_hold()

    def test_missing_function_rejected(self) -> None:
        self.live["functions"] = []
        self.assert_hold()

    def test_additional_live_function_rejected(self) -> None:
        self.live["functions"].append({**self.binding, "slug": "other"})
        self.assert_hold()

    def test_stale_provider_receipt_rejected(self) -> None:
        self.live["observed_at"] = "2026-11-01T19:00:00Z"
        self.assert_hold()

    def test_stale_snapshot_rejected(self) -> None:
        self.project["observed_at"] = "2026-11-01T19:00:00Z"
        self.assert_hold()

    def test_future_provider_observation_rejected(self) -> None:
        self.live["observed_at"] = "2026-11-05T21:00:00Z"
        self.assert_hold()

    def test_duplicate_json_keys_rejected(self) -> None:
        self._save()
        (self.root / "live.json").write_text('{"schema":"x","schema":"SUPABASE_METADATA_OBSERVATION_V1"}')
        result = guard.compare(self.snapshot, self.root / "live.json", now=NOW)
        self.assertEqual("HOLD_STALE_OR_UNBOUND", result["status"])

    def test_malformed_head_rejected(self) -> None:
        self.project["snapshot_source_head"] = "not-a-git-head"
        self.assert_hold()

    def test_boolean_edge_version_rejected(self) -> None:
        self.live["functions"][0]["version"] = True
        self.assert_hold()

    def test_migration_count_forgery_rejected(self) -> None:
        self.history["count"] = 3
        self.assert_hold()


if __name__ == "__main__":
    unittest.main()
