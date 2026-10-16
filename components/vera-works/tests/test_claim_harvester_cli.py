from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from vera_works.claim_harvester_cli import main


EVM = "0x1111111111111111111111111111111111111111"


class ClaimHarvesterCliTests(unittest.TestCase):
    def test_cli_evaluates_feed_without_external_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            feed = root / "feed.json"
            ledger = root / "ledger.jsonl"
            config.write_text(
                json.dumps(
                    {
                        "wallets": [
                            {
                                "alias": "vera-fund-evm",
                                "chain": "evm",
                                "address_env": "VW_TEST_EVM",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            feed.write_text(
                json.dumps(
                    {
                        "candidates": [
                            {
                                "claim_id": "fixture-1",
                                "title": "Synthetic official entitlement fixture",
                                "source_id": "fixture-source",
                                "source_uri": "https://official.example/fixture",
                                "source_class": "FIRST_PARTY_PROTOCOL",
                                "source_digest": "a" * 64,
                                "observed_at": "2026-10-05T15:00:00Z",
                                "eligibility_class": "ENTITLED",
                                "beneficiary_type": "WALLET",
                                "beneficiary_locator": EVM,
                                "beneficiary_match": "VERIFIED",
                                "opens_at": "2026-10-01T00:00:00Z",
                                "closes_at": "2027-01-01T00:00:00Z",
                                "gross_amount": "25",
                                "currency": "USD",
                                "fee_estimate": "1",
                                "tax_reserve_estimate": "4",
                                "requires_wallet_signature": False,
                                "requires_identity_verification": False,
                                "requires_account_creation": False,
                                "requires_terms_acceptance": False,
                                "human_communication_required": False,
                                "evidence_refs": ["fixture:evidence"],
                                "notes": "Synthetic test only"
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output = io.StringIO()
            with patch.dict(os.environ, {"VW_TEST_EVM": EVM}, clear=False), redirect_stdout(output):
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
            self.assertEqual(result["assessments"][0]["wallet_alias"], "vera-fund-evm")
            self.assertTrue(ledger.exists())

    def test_cli_fails_closed_when_wallet_environment_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            feed = root / "feed.json"
            config.write_text(
                json.dumps(
                    {
                        "wallets": [
                            {
                                "alias": "vera-fund-evm",
                                "chain": "evm",
                                "address_env": "VW_DEFINITELY_MISSING",
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
