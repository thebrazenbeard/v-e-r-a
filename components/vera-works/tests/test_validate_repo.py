import json
import tempfile
import unittest
from pathlib import Path

from vera_works.validate_repo import validate_path


class RepositoryValidatorTests(unittest.TestCase):
    def _event(self, event_id, subject_id, idempotency_key):
        return {
            "schema_version": "event-v1",
            "event_id": event_id,
            "event_type": "OPPORTUNITY_DISCOVERED",
            "subject_type": "opportunity",
            "subject_id": subject_id,
            "actor": "vera",
            "recorded_at": "2026-08-29T13:00:00Z",
            "correlation_id": "C1",
            "causation_id": None,
            "idempotency_key": idempotency_key,
            "from_state": None,
            "to_state": "DISCOVERED",
            "payload": {},
            "external_effect": False,
        }

    def test_validate_repo_returns_zero_error_report_for_valid_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "0001.json").write_text(json.dumps(self._event("E1", "O1", "idem-1")), encoding="utf-8")
            report = validate_path(Path(tmp))
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["available_balance"], "0.00")

    def test_validate_repo_detects_duplicate_idempotency_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "0001.json").write_text(json.dumps(self._event("E1", "O1", "same")), encoding="utf-8")
            Path(tmp, "0002.json").write_text(json.dumps(self._event("E2", "O2", "same")), encoding="utf-8")
            report = validate_path(Path(tmp))
            self.assertIn("duplicate idempotency_key: same", report["errors"])


if __name__ == "__main__":
    unittest.main()
