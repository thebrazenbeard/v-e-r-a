from __future__ import annotations

import unittest
from datetime import datetime, timezone

from vera_works.first_dollar_benchmark import (
    BenchmarkObservation,
    BenchmarkState,
    EvidenceQuality,
    assess_observation,
    rank_first_dollar,
)


NOW = datetime(2026, 10, 5, 18, 30, tzinfo=timezone.utc)


def observation(**overrides) -> BenchmarkObservation:
    values = dict(
        mechanism_id="synthetic",
        resource_alias="owned-compute",
        evidence_quality=EvidenceQuality.SOURCE_ESTIMATE,
        source_uri="https://example.invalid/reward",
        quote_observed_at="2026-10-05T18:00:00Z",
        max_quote_age_seconds=7200,
        benchmark_duration_hours="0",
        hours_per_day="8",
        baseline_watts="20",
        workload_watts="100",
        performance_metric_name="points_per_day",
        performance_metric_value="1000000",
        performance_metric_unit="PPD",
        reward_units_per_day="10",
        reward_unit_symbol="UNIT",
        reward_unit_usd="0.05",
        minimum_payout_units="10",
        payout_fee_units="0",
        liquidity_ratio="1",
        platform_fee_usd_per_day="0",
        other_cost_usd_per_day="0",
        electricity_usd_per_kwh="0.16",
        warmup_days="0",
        payout_lag_days="0",
        evidence_refs=("estimate:synthetic",),
    )
    values.update(overrides)
    return BenchmarkObservation(**values)


class FirstDollarBenchmarkTests(unittest.TestCase):
    def test_positive_source_estimate_never_authorizes(self):
        result = assess_observation(observation(), now=NOW)
        self.assertEqual(result.state, BenchmarkState.POSITIVE_ESTIMATE)
        self.assertEqual(result.authorization_state, "NOT_AUTHORIZED")
        self.assertEqual(result.incremental_kwh_per_day, "0.64")
        self.assertEqual(result.power_cost_usd_per_day, "0.1024")
        self.assertEqual(result.gross_usd_per_day, "0.5")
        self.assertEqual(result.net_usd_per_day, "0.3976")
        self.assertEqual(result.net_usd_per_30d, "11.928")
        self.assertEqual(result.days_to_first_payout, 1)
        self.assertEqual(result.first_payout_cash_usd, "0.5")
        self.assertEqual(result.first_payout_net_profit_usd, "0.3976")
        self.assertEqual(result.break_even_electricity_usd_per_kwh, "0.78125")

    def test_measured_result_requires_exact_benchmark_evidence(self):
        result = assess_observation(
            observation(
                evidence_quality=EvidenceQuality.EXACT_RESOURCE_MEASURED,
                benchmark_duration_hours="2",
            ),
            now=NOW,
        )
        self.assertEqual(result.state, BenchmarkState.INVALID)

    def test_measured_positive_result(self):
        result = assess_observation(
            observation(
                evidence_quality=EvidenceQuality.EXACT_RESOURCE_MEASURED,
                benchmark_duration_hours="2",
                evidence_refs=("benchmark:owned-compute-20261005",),
            ),
            now=NOW,
        )
        self.assertEqual(result.state, BenchmarkState.POSITIVE_MEASURED)
        self.assertEqual(result.authorization_state, "NOT_AUTHORIZED")

    def test_realized_reward_requires_receipt_evidence(self):
        result = assess_observation(
            observation(
                evidence_quality=EvidenceQuality.REALIZED_REWARD,
                benchmark_duration_hours="8",
                evidence_refs=("benchmark:run-1",),
            ),
            now=NOW,
        )
        self.assertEqual(result.state, BenchmarkState.INVALID)

    def test_realized_reward_is_strongest_evidence_state(self):
        result = assess_observation(
            observation(
                evidence_quality=EvidenceQuality.REALIZED_REWARD,
                benchmark_duration_hours="8",
                evidence_refs=("benchmark:run-1", "receipt:payout-1"),
            ),
            now=NOW,
        )
        self.assertEqual(result.state, BenchmarkState.POSITIVE_REALIZED)

    def test_stale_quote_fails_closed(self):
        result = assess_observation(
            observation(quote_observed_at="2026-10-01T18:00:00Z", max_quote_age_seconds=60),
            now=NOW,
        )
        self.assertEqual(result.state, BenchmarkState.STALE_QUOTE)

    def test_zero_reward_is_not_a_candidate(self):
        result = assess_observation(observation(reward_units_per_day="0"), now=NOW)
        self.assertEqual(result.state, BenchmarkState.NO_REWARD)

    def test_negative_net_is_rejected(self):
        result = assess_observation(
            observation(reward_units_per_day="0.1", reward_unit_usd="0.01"),
            now=NOW,
        )
        self.assertEqual(result.state, BenchmarkState.NONPOSITIVE_NET)

    def test_payout_threshold_fee_warmup_and_lag_are_explicit(self):
        result = assess_observation(
            observation(
                minimum_payout_units="50",
                payout_fee_units="1",
                warmup_days="1",
                payout_lag_days="2",
            ),
            now=NOW,
        )
        self.assertEqual(result.payout_cycle_days, 5)
        self.assertEqual(result.days_to_first_payout, 8)
        self.assertEqual(result.payout_fee_usd_per_cycle, "0.05")
        self.assertEqual(result.payout_fee_usd_per_day, "0.01")
        self.assertEqual(result.first_payout_cash_usd, "2.45")
        self.assertEqual(result.first_payout_net_profit_usd, "1.8356")

    def test_liquidity_discount_reduces_cash_value(self):
        result = assess_observation(observation(liquidity_ratio="0.5"), now=NOW)
        self.assertEqual(result.gross_usd_per_day, "0.25")
        self.assertEqual(result.net_usd_per_day, "0.1476")

    def test_non_numeric_performance_metric_is_invalid(self):
        result = assess_observation(
            observation(performance_metric_value="fast"),
            now=NOW,
        )
        self.assertEqual(result.state, BenchmarkState.INVALID)

    def test_warmup_days_incurring_workload_cost_reduce_first_payout_profit(self):
        without_warmup = assess_observation(observation(), now=NOW)
        with_warmup = assess_observation(observation(warmup_days="2"), now=NOW)
        self.assertEqual(without_warmup.first_payout_net_profit_usd, "0.3976")
        self.assertEqual(with_warmup.first_payout_net_profit_usd, "0.1928")

    def test_workload_below_baseline_is_invalid(self):
        result = assess_observation(
            observation(baseline_watts="100", workload_watts="80"),
            now=NOW,
        )
        self.assertEqual(result.state, BenchmarkState.INVALID)

    def test_ranking_prefers_stronger_evidence_before_estimates(self):
        estimate = assess_observation(
            observation(mechanism_id="estimate-fast"),
            now=NOW,
        )
        measured = assess_observation(
            observation(
                mechanism_id="measured",
                evidence_quality=EvidenceQuality.EXACT_RESOURCE_MEASURED,
                benchmark_duration_hours="2",
                minimum_payout_units="100",
                evidence_refs=("benchmark:measured",),
            ),
            now=NOW,
        )
        realized = assess_observation(
            observation(
                mechanism_id="realized",
                evidence_quality=EvidenceQuality.REALIZED_REWARD,
                benchmark_duration_hours="8",
                minimum_payout_units="200",
                evidence_refs=("benchmark:realized", "receipt:realized"),
            ),
            now=NOW,
        )
        ranked = rank_first_dollar([estimate, measured, realized])
        self.assertEqual(
            [item.mechanism_id for item in ranked],
            ["realized", "measured", "estimate-fast"],
        )


if __name__ == "__main__":
    unittest.main()
