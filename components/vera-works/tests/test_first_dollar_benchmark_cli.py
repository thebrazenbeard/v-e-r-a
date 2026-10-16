from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from vera_works.first_dollar_benchmark_cli import main


class FirstDollarBenchmarkCliTests(unittest.TestCase):
    def test_cli_is_analysis_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": "first-dollar-benchmark-v1",
                        "observations": [
                            {
                                "mechanism_id": "fixture",
                                "resource_alias": "owned-compute",
                                "evidence_quality": "SOURCE_ESTIMATE",
                                "source_uri": "https://example.invalid/reward",
                                "quote_observed_at": "2026-10-05T18:00:00Z",
                                "max_quote_age_seconds": 7200,
                                "benchmark_duration_hours": "0",
                                "hours_per_day": "8",
                                "baseline_watts": "20",
                                "workload_watts": "100",
                                "performance_metric_name": "points_per_day",
                                "performance_metric_value": "1000000",
                                "performance_metric_unit": "PPD",
                                "reward_units_per_day": "10",
                                "reward_unit_symbol": "UNIT",
                                "reward_unit_usd": "0.05",
                                "minimum_payout_units": "10",
                                "payout_fee_units": "0",
                                "liquidity_ratio": "1",
                                "platform_fee_usd_per_day": "0",
                                "other_cost_usd_per_day": "0",
                                "electricity_usd_per_kwh": "0.16",
                                "warmup_days": "0",
                                "payout_lag_days": "0",
                                "evidence_refs": ["estimate:fixture"]
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output = io.StringIO()
            with redirect_stdout(output):
                code = main([
                    "--input",
                    str(path),
                    "--now",
                    "2026-10-05T18:30:00Z",
                ])

            self.assertEqual(code, 0)
            payload = json.loads(output.getvalue())
            self.assertFalse(payload["external_effect_performed"])
            self.assertEqual(payload["authorization_state"], "NOT_AUTHORIZED")
            self.assertEqual(payload["assessments"][0]["state"], "POSITIVE_ESTIMATE")

    def test_cli_rejects_malformed_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text("{not-json", encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["--input", str(path)])

            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output.getvalue())["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
