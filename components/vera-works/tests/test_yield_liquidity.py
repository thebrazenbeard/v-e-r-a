from __future__ import annotations

import unittest

from vera_works.yield_liquidity import PayoutProfile, PayoutState, assess_payout


def sample(**overrides):
    values = dict(
        mechanism_id="synthetic",
        accrued_usd="3",
        minimum_payout_usd="5",
        withdrawal_fee_usd="0",
        cash_equivalent_ratio="1",
        payout_rail_verified=True,
        payout_available=True,
    )
    values.update(overrides)
    return PayoutProfile(**values)


class YieldLiquidityTests(unittest.TestCase):
    def test_below_threshold_is_not_money(self):
        result = assess_payout(sample())
        self.assertEqual(result.state, PayoutState.BELOW_MINIMUM)
        self.assertEqual(result.withdrawable_now_usd, "0")

    def test_unverified_rail_fails_closed(self):
        result = assess_payout(sample(accrued_usd="20", payout_rail_verified=False))
        self.assertEqual(result.state, PayoutState.RAIL_UNVERIFIED)

    def test_fees_and_liquidity_apply(self):
        result = assess_payout(sample(accrued_usd="10", withdrawal_fee_usd="1", cash_equivalent_ratio="0.8"))
        self.assertEqual(result.state, PayoutState.WITHDRAWABLE)
        self.assertEqual(result.withdrawable_now_usd, "7.0")

    def test_zero_cash_equivalence_is_not_revenue(self):
        result = assess_payout(sample(accrued_usd="10", cash_equivalent_ratio="0"))
        self.assertEqual(result.state, PayoutState.NONCASH_OR_ILLIQUID)

    def test_invalid_ratio_fails(self):
        with self.assertRaises(ValueError):
            assess_payout(sample(cash_equivalent_ratio="1.1"))


if __name__ == "__main__":
    unittest.main()
