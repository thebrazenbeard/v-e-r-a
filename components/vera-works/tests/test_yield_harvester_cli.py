from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from vera_works.yield_harvester_cli import main


class YieldHarvesterCliTests(unittest.TestCase):
    def test_cli_ranks_without_starting_workload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            feed = root / "feed.json"
            ledger = root / "ledger.jsonl"

            config.write_text(
                json.dumps(
                    {
                        "policy": {
                            "minimum_net_usd_per_hour": "0.01",
                            "available_upfront_capital_usd": "0"
                        },
                        "resources": [
                            {
                                "alias": "local-gpu",
                                "kind": "GPU",
                                "origin": "LOCAL_OWNED",
                                "availability": "AVAILABLE",
                                "usage_terms_state": "NOT_APPLICABLE",
                                "gpu_vram_gb": "4",
                                "env": {
                                    "electricity_usd_per_kwh": "VW_TEST_ELECTRICITY"
                                }
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            feed.write_text(
                json.dumps(
                    {
                        "candidates": [
                            {
                                "yield_id": "fixture-yield",
                                "title": "Synthetic protocol reward",
                                "resource_alias": "local-gpu",
                                "resource_kind": "GPU",
                                "reward_model": "PROTOCOL_EMISSION",
                                "source_class": "FIRST_PARTY_PROTOCOL",
                                "source_uri": "https://protocol.example/rewards",
                                "source_digest": "a" * 64,
                                "terms_uri": "https://protocol.example/terms",
                                "terms_digest": "b" * 64,
                                "terms_state": "VERIFIED_ALLOWED",
                                "observed_at": observed_at,
                                "quote_observed_at": observed_at,
                                "quote_digest": "c" * 64,
                                "max_quote_age_seconds": 86400,
                                "economics_state": "VERIFIED",
                                "gross_usd_per_hour": "0.10",
                                "estimated_power_watts": "75",
                                "platform_fee_usd_per_hour": "0.005",
                                "network_cost_usd_per_hour": "0",
                                "wear_reserve_usd_per_hour": "0.005",
                                "other_cost_usd_per_hour": "0",
                                "upfront_cost_usd": "0",
                                "capital_locked_usd": "0",
                                "minimum_vram_gb": "4",
                                "customer_acquisition_required": False,
                                "human_communication_required": False,
                                "requires_account_creation": False,
                                "requires_terms_acceptance": False,
                                "requires_identity_verification": False,
                                "requires_wallet_signature": False,
                                "requires_installation": False,
                                "requires_network_exposure": False,
                                "evidence_refs": [
                                    "source:synthetic",
                                    "terms:synthetic",
                                    "benchmark:synthetic"
                                ],
                                "notes": "Synthetic test only"
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            output = io.StringIO()
            with patch.dict(os.environ, {"VW_TEST_ELECTRICITY": "0.16"}, clear=False), redirect_stdout(output):
                code = main(
                    [
                        "--config",
                        str(config),
                        "--candidates",
                        str(feed),
                        "--ledger",
                        str(ledger),
                    ]
                )

            self.assertEqual(code, 0)
            result = json.loads(output.getvalue())
            self.assertFalse(result["external_effect_performed"])
            self.assertEqual(
                result["assessments"][0]["state"],
                "READY_FOR_EFFECT_AUTHORIZATION",
            )
            self.assertEqual(result["broker_plan"][0]["yield_id"], "fixture-yield")
            self.assertEqual(result["broker_plan"][0]["authorization_state"], "NOT_AUTHORIZED")
            self.assertTrue(ledger.exists())

    def test_cli_fails_closed_when_resource_cost_env_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            feed = root / "feed.json"
            config.write_text(
                json.dumps(
                    {
                        "resources": [
                            {
                                "alias": "local-gpu",
                                "kind": "GPU",
                                "origin": "LOCAL_OWNED",
                                "availability": "AVAILABLE",
                                "usage_terms_state": "NOT_APPLICABLE",
                                "env": {
                                    "electricity_usd_per_kwh": "VW_MISSING_ELECTRICITY"
                                }
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            feed.write_text(json.dumps({"candidates": []}), encoding="utf-8")

            output = io.StringIO()
            with patch.dict(os.environ, {}, clear=True), redirect_stdout(output):
                code = main(["--config", str(config), "--candidates", str(feed)])

            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output.getvalue())["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
