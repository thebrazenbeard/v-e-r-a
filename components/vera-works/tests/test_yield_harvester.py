from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from vera_works.yield_harvester import (
    AssessmentState,
    EconomicsState,
    ResourceAvailability,
    ResourceKind,
    ResourceOrigin,
    ResourceProfile,
    RewardModel,
    SourceClass,
    TermsState,
    YieldCandidate,
    YieldLedger,
    YieldPolicy,
    assess_candidate,
    broker_plan,
    harvest,
    load_resources_from_environment,
)


NOW = datetime(2026, 10, 5, 16, 30, tzinfo=timezone.utc)


def local_gpu(**overrides) -> ResourceProfile:
    base = dict(
        alias="local-gpu",
        kind=ResourceKind.GPU,
        origin=ResourceOrigin.LOCAL_OWNED,
        availability=ResourceAvailability.AVAILABLE,
        usage_terms_state=TermsState.NOT_APPLICABLE,
        electricity_usd_per_kwh="0.16",
        gpu_vram_gb="4",
        ram_gb="16",
        disk_free_gb="100",
        upload_mbps="100",
        cpu_threads=16,
    )
    base.update(overrides)
    return ResourceProfile(**base)


def candidate(**overrides) -> YieldCandidate:
    base = dict(
        yield_id="yield-1",
        title="Synthetic protocol GPU work",
        resource_alias="local-gpu",
        resource_kind=ResourceKind.GPU,
        reward_model=RewardModel.PROTOCOL_EMISSION,
        source_class=SourceClass.FIRST_PARTY_PROTOCOL,
        source_uri="https://protocol.example/rewards",
        source_digest="a" * 64,
        terms_uri="https://protocol.example/terms",
        terms_digest="b" * 64,
        terms_state=TermsState.VERIFIED_ALLOWED,
        observed_at="2026-10-05T16:00:00Z",
        quote_observed_at="2026-10-05T16:00:00Z",
        quote_digest="c" * 64,
        max_quote_age_seconds=7200,
        economics_state=EconomicsState.VERIFIED,
        gross_usd_per_hour="0.10",
        estimated_power_watts="75",
        platform_fee_usd_per_hour="0.005",
        network_cost_usd_per_hour="0",
        wear_reserve_usd_per_hour="0.005",
        other_cost_usd_per_hour="0",
        upfront_cost_usd="0",
        capital_locked_usd="0",
        customer_acquisition_required=False,
        human_communication_required=False,
        requires_account_creation=False,
        requires_terms_acceptance=False,
        requires_identity_verification=False,
        requires_wallet_signature=False,
        requires_installation=False,
        requires_network_exposure=False,
        minimum_vram_gb="4",
        evidence_refs=("source:synthetic", "terms:synthetic", "benchmark:synthetic"),
    )
    base.update(overrides)
    return YieldCandidate(**base)


class YieldHarvesterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.resources = [local_gpu()]

    def test_positive_protocol_yield_stops_at_effect_authorization(self):
        result = assess_candidate(candidate(), self.resources, now=NOW)
        self.assertEqual(result.state, AssessmentState.READY_FOR_EFFECT_AUTHORIZATION)
        self.assertEqual(result.net_usd_per_hour, "0.07800")
        self.assertEqual(result.boundary, "EXACT_EFFECT_AUTHORIZATION_REQUIRED")

    def test_useful_compute_reward_can_reach_authorization_gate(self):
        result = assess_candidate(
            candidate(reward_model=RewardModel.USEFUL_COMPUTE_REWARD),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.READY_FOR_EFFECT_AUTHORIZATION)

    def test_customer_sale_is_rejected(self):
        result = assess_candidate(
            candidate(reward_model=RewardModel.CUSTOMER_SALE, customer_acquisition_required=True),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.REJECT_CUSTOMER_DEPENDENT)

    def test_marketplace_can_be_disabled_by_policy(self):
        result = assess_candidate(
            candidate(
                reward_model=RewardModel.MARKETPLACE_DEMAND,
                source_class=SourceClass.OFFICIAL_MARKETPLACE,
            ),
            self.resources,
            YieldPolicy(allow_marketplace_demand=False),
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.REJECT_MARKETPLACE_DEPENDENT)

    def test_marketplace_is_disabled_by_default(self):
        result = assess_candidate(
            candidate(
                reward_model=RewardModel.MARKETPLACE_DEMAND,
                source_class=SourceClass.OFFICIAL_MARKETPLACE,
            ),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.REJECT_MARKETPLACE_DEPENDENT)

    def test_verified_economics_requires_benchmark_evidence(self):
        result = assess_candidate(
            candidate(evidence_refs=("source:synthetic", "terms:synthetic")),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.INVALID_CANDIDATE)

    def test_human_communication_is_rejected(self):
        result = assess_candidate(candidate(human_communication_required=True), self.resources, now=NOW)
        self.assertEqual(result.state, AssessmentState.REJECT_HUMAN_COMMUNICATION)

    def test_secondary_mechanism_source_is_research_only(self):
        result = assess_candidate(candidate(source_class=SourceClass.SECONDARY), self.resources, now=NOW)
        self.assertEqual(result.state, AssessmentState.RESEARCH_SOURCE_UNVERIFIED)

    def test_resource_kind_mismatch_is_rejected(self):
        result = assess_candidate(candidate(resource_kind=ResourceKind.CPU), self.resources, now=NOW)
        self.assertEqual(result.state, AssessmentState.REJECT_RESOURCE_INCOMPATIBLE)

    def test_employer_resource_is_rejected(self):
        result = assess_candidate(
            candidate(),
            [local_gpu(origin=ResourceOrigin.EMPLOYER)],
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.REJECT_RESOURCE_UNAUTHORIZED)

    def test_free_cloud_unknown_terms_do_not_execute(self):
        resource = local_gpu(
            origin=ResourceOrigin.CLOUD_FREE,
            usage_terms_state=TermsState.UNKNOWN,
        )
        result = assess_candidate(candidate(), [resource], now=NOW)
        self.assertEqual(result.state, AssessmentState.RESEARCH_TERMS_UNVERIFIED)

    def test_free_cloud_prohibited_terms_are_rejected(self):
        resource = local_gpu(
            origin=ResourceOrigin.CLOUD_FREE,
            usage_terms_state=TermsState.VERIFIED_PROHIBITED,
        )
        result = assess_candidate(candidate(), [resource], now=NOW)
        self.assertEqual(result.state, AssessmentState.REJECT_TERMS_PROHIBIT)

    def test_paid_cloud_is_rejected_by_bootstrap_policy(self):
        resource = local_gpu(
            origin=ResourceOrigin.CLOUD_PAID,
            usage_terms_state=TermsState.VERIFIED_ALLOWED,
        )
        result = assess_candidate(candidate(), [resource], now=NOW)
        self.assertEqual(result.state, AssessmentState.REJECT_PAID_INFRASTRUCTURE)

    def test_third_party_resource_is_rejected_without_authority_contract(self):
        resource = local_gpu(
            origin=ResourceOrigin.THIRD_PARTY,
            usage_terms_state=TermsState.VERIFIED_ALLOWED,
        )
        result = assess_candidate(candidate(), [resource], now=NOW)
        self.assertEqual(result.state, AssessmentState.REJECT_RESOURCE_UNAUTHORIZED)

    def test_resource_explicitly_prohibited_is_rejected(self):
        resource = local_gpu(usage_terms_state=TermsState.VERIFIED_PROHIBITED)
        result = assess_candidate(candidate(), [resource], now=NOW)
        self.assertEqual(result.state, AssessmentState.REJECT_TERMS_PROHIBIT)

    def test_staking_requires_capital_resource(self):
        result = assess_candidate(
            candidate(reward_model=RewardModel.STAKING_YIELD),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.REJECT_RESOURCE_INCOMPATIBLE)

    def test_mechanism_unknown_terms_do_not_execute(self):
        result = assess_candidate(
            candidate(
                terms_state=TermsState.UNKNOWN,
                evidence_refs=("source:synthetic", "benchmark:synthetic"),
            ),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.RESEARCH_TERMS_UNVERIFIED)

    def test_mechanism_prohibited_terms_are_rejected(self):
        result = assess_candidate(
            candidate(terms_state=TermsState.VERIFIED_PROHIBITED),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.REJECT_TERMS_PROHIBIT)

    def test_generic_estimate_requires_local_benchmark(self):
        result = assess_candidate(
            candidate(
                economics_state=EconomicsState.ESTIMATED,
                evidence_refs=("source:synthetic", "terms:synthetic", "quote:synthetic"),
            ),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.NEEDS_LOCAL_BENCHMARK)

    def test_estimate_cannot_be_promoted_to_effect_authorization(self):
        result = assess_candidate(
            candidate(
                economics_state=EconomicsState.ESTIMATED,
                evidence_refs=("source:synthetic", "terms:synthetic", "quote:synthetic"),
            ),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.NEEDS_LOCAL_BENCHMARK)
        self.assertIsNone(
            __import__("vera_works.yield_harvester", fromlist=["effect_packet_for_assessment"])
            .effect_packet_for_assessment(result)
        )

    def test_stale_quote_is_not_executable(self):
        result = assess_candidate(
            candidate(quote_observed_at="2026-10-05T12:00:00Z", max_quote_age_seconds=900),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.STALE_QUOTE)

    def test_incompatible_vram_is_rejected(self):
        result = assess_candidate(candidate(minimum_vram_gb="8"), self.resources, now=NOW)
        self.assertEqual(result.state, AssessmentState.REJECT_RESOURCE_INCOMPATIBLE)

    def test_nonpositive_net_is_rejected(self):
        result = assess_candidate(
            candidate(
                gross_usd_per_hour="0.01",
                estimated_power_watts="100",
                platform_fee_usd_per_hour="0",
                wear_reserve_usd_per_hour="0",
            ),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.REJECT_NONPOSITIVE_NET)

    def test_positive_but_tiny_net_can_be_rejected_by_threshold(self):
        result = assess_candidate(
            candidate(),
            self.resources,
            YieldPolicy(minimum_net_usd_per_hour="0.10"),
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.REJECT_BELOW_THRESHOLD)

    def test_capital_requirement_escalates_to_vera(self):
        result = assess_candidate(
            candidate(upfront_cost_usd="5"),
            self.resources,
            YieldPolicy(available_upfront_capital_usd="0"),
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.VERA_DECISION_REQUIRED)

    def test_busy_resource_waits(self):
        result = assess_candidate(
            candidate(),
            [local_gpu(availability=ResourceAvailability.BUSY)],
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.WAITING_RESOURCE_AVAILABLE)

    def test_network_exposure_is_patrick_decision(self):
        result = assess_candidate(candidate(requires_network_exposure=True), self.resources, now=NOW)
        self.assertEqual(result.state, AssessmentState.PATRICK_DECISION_REQUIRED)

    def test_account_terms_boundary_is_patrick_decision(self):
        result = assess_candidate(candidate(requires_account_creation=True), self.resources, now=NOW)
        self.assertEqual(result.state, AssessmentState.PATRICK_DECISION_REQUIRED)

    def test_installation_boundary_is_patrick_action(self):
        result = assess_candidate(candidate(requires_installation=True), self.resources, now=NOW)
        self.assertEqual(result.state, AssessmentState.PATRICK_ACTION_REQUIRED)

    def test_bad_quote_digest_fails_closed(self):
        result = assess_candidate(candidate(quote_digest="bad"), self.resources, now=NOW)
        self.assertEqual(result.state, AssessmentState.INVALID_CANDIDATE)

    def test_unknown_economics_are_research_only(self):
        result = assess_candidate(
            candidate(economics_state=EconomicsState.UNKNOWN, gross_usd_per_hour=None),
            self.resources,
            now=NOW,
        )
        self.assertEqual(result.state, AssessmentState.RESEARCH_ECONOMICS_UNVERIFIED)

    def test_broker_picks_highest_net_ready_workload_per_resource(self):
        results = harvest(
            [
                candidate(yield_id="lower", gross_usd_per_hour="0.08"),
                candidate(yield_id="higher", gross_usd_per_hour="0.12"),
            ],
            self.resources,
            now=NOW,
        )
        plan = broker_plan(results)
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0].yield_id, "higher")

    def test_broker_prefers_protocol_over_marketplace_on_equal_net(self):
        results = harvest(
            [
                candidate(
                    yield_id="market",
                    reward_model=RewardModel.MARKETPLACE_DEMAND,
                    source_class=SourceClass.OFFICIAL_MARKETPLACE,
                ),
                candidate(yield_id="protocol"),
            ],
            self.resources,
            YieldPolicy(allow_marketplace_demand=True),
            now=NOW,
        )
        plan = broker_plan(results)
        self.assertEqual(plan[0].yield_id, "protocol")

    def test_resources_load_cost_from_environment(self):
        config = {
            "resources": [
                {
                    "alias": "gpu",
                    "kind": "GPU",
                    "origin": "LOCAL_OWNED",
                    "availability": "AVAILABLE",
                    "usage_terms_state": "NOT_APPLICABLE",
                    "gpu_vram_gb": "4",
                    "env": {"electricity_usd_per_kwh": "VW_TEST_ELECTRICITY"},
                }
            ]
        }
        with patch.dict(os.environ, {"VW_TEST_ELECTRICITY": "0.17"}, clear=False):
            resources = load_resources_from_environment(config)
        self.assertEqual(resources[0].electricity_usd_per_kwh, "0.17")

    def test_yield_ledger_is_idempotent(self):
        result = assess_candidate(candidate(), self.resources, now=NOW)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "yield.jsonl"
            ledger = YieldLedger(path)
            self.assertTrue(ledger.append(result, recorded_at=NOW))
            self.assertFalse(ledger.append(result, recorded_at=NOW))
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["assessment"]["state"], "READY_FOR_EFFECT_AUTHORIZATION")


if __name__ == "__main__":
    unittest.main()
