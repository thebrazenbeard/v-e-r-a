from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from vera_works.claim_harvester import (
    AssessmentState,
    CandidateObservation,
    ClaimLedger,
    EligibilityClass,
    MatchState,
    SourceClass,
    WalletTarget,
    assess_candidate,
    harvest,
    load_wallets_from_environment,
)


NOW = datetime(2026, 10, 5, 15, 30, tzinfo=timezone.utc)
EVM = "0x1111111111111111111111111111111111111111"
OTHER_EVM = "0x2222222222222222222222222222222222222222"


def candidate(**overrides) -> CandidateObservation:
    base = dict(
        claim_id="claim-1",
        title="Example official wallet distribution",
        source_id="official-example",
        source_uri="https://official.example/claim",
        source_class=SourceClass.FIRST_PARTY_PROTOCOL,
        source_digest="a" * 64,
        observed_at="2026-10-05T15:00:00Z",
        eligibility_class=EligibilityClass.ENTITLED,
        beneficiary_type="WALLET",
        beneficiary_locator=EVM,
        beneficiary_match=MatchState.VERIFIED,
        opens_at="2026-10-01T00:00:00Z",
        closes_at="2026-12-01T00:00:00Z",
        gross_amount="100",
        currency="USD",
        fee_estimate="3",
        tax_reserve_estimate="20",
        evidence_refs=("source:official-example",),
    )
    base.update(overrides)
    return CandidateObservation(**base)


class ClaimHarvesterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.wallets = [WalletTarget(alias="vera-fund-evm", chain="evm", address=EVM)]

    def test_entitled_wallet_candidate_stops_at_effect_authorization(self):
        result = assess_candidate(candidate(), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.READY_FOR_EFFECT_AUTHORIZATION)
        self.assertEqual(result.wallet_alias, "vera-fund-evm")
        self.assertEqual(result.expected_net, "77")
        self.assertEqual(result.boundary, "EXACT_EFFECT_AUTHORIZATION_REQUIRED")

    def test_not_ours_is_rejected(self):
        result = assess_candidate(candidate(eligibility_class=EligibilityClass.NOT_OURS), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.REJECT_NOT_OURS)

    def test_ambiguous_is_research_only(self):
        result = assess_candidate(candidate(eligibility_class=EligibilityClass.AMBIGUOUS), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.RESEARCH_ONLY_AMBIGUOUS)

    def test_secondary_source_cannot_authorize_claim(self):
        result = assess_candidate(candidate(source_class=SourceClass.SECONDARY), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.RESEARCH_ONLY_SOURCE_NOT_AUTHORITATIVE)

    def test_wallet_mismatch_is_rejected(self):
        result = assess_candidate(candidate(beneficiary_locator=OTHER_EVM), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.REJECT_WALLET_MISMATCH)

    def test_wallet_signature_requires_patrick_action(self):
        result = assess_candidate(candidate(requires_wallet_signature=True), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.PATRICK_ACTION_REQUIRED)
        self.assertEqual(result.boundary, "PATRICK_ACTION_REQUIRED")

    def test_terms_acceptance_requires_patrick_decision(self):
        result = assess_candidate(candidate(requires_terms_acceptance=True), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.PATRICK_DECISION_REQUIRED)

    def test_person_to_person_communication_is_out_of_scope(self):
        result = assess_candidate(candidate(human_communication_required=True), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.OUT_OF_SCOPE_COMMUNICATION)

    def test_expired_claim_closes(self):
        result = assess_candidate(candidate(closes_at="2026-10-04T00:00:00Z"), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.CLOSED_EXPIRED)

    def test_future_claim_waits_for_window(self):
        result = assess_candidate(candidate(opens_at="2026-10-06T00:00:00Z"), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.WAITING_CLAIM_WINDOW)

    def test_invalid_digest_fails_closed(self):
        result = assess_candidate(candidate(source_digest="not-a-digest"), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.INVALID_CANDIDATE)

    def test_missing_evidence_fails_closed(self):
        result = assess_candidate(candidate(evidence_refs=()), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.INVALID_CANDIDATE)

    def test_negative_fee_fails_closed(self):
        result = assess_candidate(candidate(fee_estimate="-1"), self.wallets, now=NOW)
        self.assertEqual(result.state, AssessmentState.INVALID_CANDIDATE)

    def test_identity_claim_requires_verified_beneficiary(self):
        result = assess_candidate(
            candidate(
                beneficiary_type="IDENTITY",
                beneficiary_locator=None,
                beneficiary_match=MatchState.UNVERIFIED,
            ),
            self.wallets,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.NEEDS_BENEFICIARY_VERIFICATION)

    def test_open_class_can_pass_when_verified(self):
        result = assess_candidate(
            candidate(
                beneficiary_type="OPEN_CLASS",
                beneficiary_locator=None,
                beneficiary_match=MatchState.VERIFIED,
            ),
            self.wallets,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.READY_FOR_EFFECT_AUTHORIZATION)

    def test_harvest_prioritizes_actionable_then_value(self):
        results = harvest(
            [
                candidate(claim_id="ambiguous", eligibility_class=EligibilityClass.AMBIGUOUS),
                candidate(claim_id="small", gross_amount="10", fee_estimate="0", tax_reserve_estimate="0"),
                candidate(claim_id="large", gross_amount="25", fee_estimate="0", tax_reserve_estimate="0"),
            ],
            self.wallets,
            now=NOW,
        )
        self.assertEqual([item.claim_id for item in results], ["large", "small", "ambiguous"])

    def test_wallets_load_from_environment_without_persisting_secret_material(self):
        config = {"wallets": [{"alias": "vera-fund-evm", "chain": "evm", "address_env": "VW_EVM_ADDRESS"}]}
        with patch.dict(os.environ, {"VW_EVM_ADDRESS": EVM}, clear=False):
            wallets = load_wallets_from_environment(config)
        self.assertEqual(wallets[0].normalized_address, EVM)
        self.assertNotIn(EVM, wallets[0].fingerprint)

    def test_claim_ledger_is_idempotent(self):
        result = assess_candidate(candidate(), self.wallets, now=NOW)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claims.jsonl"
            ledger = ClaimLedger(path)
            self.assertTrue(ledger.append(result, recorded_at=NOW))
            self.assertFalse(ledger.append(result, recorded_at=NOW))
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["assessment"]["state"], "READY_FOR_EFFECT_AUTHORIZATION")


if __name__ == "__main__":
    unittest.main()
