from __future__ import annotations

import unittest

from vera_works.continuity_controller import ContinuityInputs, ContinuityStage, assess_continuity


def sample(**overrides):
    values = dict(
        realized_available_usd="0",
        trailing_30d_realized_revenue_usd="0",
        monthly_operating_floor_usd="20",
        monthly_household_relief_target_usd="100",
        reserve_balance_usd="0",
        reserve_months_target="3",
        independence_target_monthly_usd="3000",
    )
    values.update(overrides)
    return ContinuityInputs(**values)


class ContinuityControllerTests(unittest.TestCase):
    def test_zero_revenue(self):
        result = assess_continuity(sample())
        self.assertEqual(result.stage, ContinuityStage.NO_REVENUE)
        self.assertFalse(result.first_dollar_achieved)

    def test_first_realized_dollar_counts(self):
        result = assess_continuity(sample(realized_available_usd="1", trailing_30d_realized_revenue_usd="1"))
        self.assertEqual(result.stage, ContinuityStage.FIRST_DOLLAR)

    def test_exact_operating_floor_is_self_supporting(self):
        result = assess_continuity(sample(realized_available_usd="20", trailing_30d_realized_revenue_usd="20"))
        self.assertEqual(result.stage, ContinuityStage.SELF_SUPPORTING)
        self.assertEqual(result.monthly_operating_gap_usd, "0")
        self.assertEqual(result.monthly_household_relief_capacity_usd, "0")

    def test_household_relief_precedes_reserve(self):
        result = assess_continuity(sample(realized_available_usd="50", trailing_30d_realized_revenue_usd="50"))
        self.assertEqual(result.stage, ContinuityStage.HOUSEHOLD_RELIEF)
        self.assertEqual(result.monthly_household_relief_capacity_usd, "30")

    def test_reserve_follows_relief(self):
        result = assess_continuity(sample(realized_available_usd="120", trailing_30d_realized_revenue_usd="120"))
        self.assertEqual(result.stage, ContinuityStage.RESERVE_BUILDING)

    def test_surplus_only_after_reserve(self):
        result = assess_continuity(sample(realized_available_usd="200", trailing_30d_realized_revenue_usd="200", reserve_balance_usd="60"))
        self.assertEqual(result.stage, ContinuityStage.SURPLUS)
        self.assertEqual(result.discretionary_capacity_usd, "80")

    def test_negative_input_fails_closed(self):
        with self.assertRaises(ValueError):
            assess_continuity(sample(realized_available_usd="-1"))


if __name__ == "__main__":
    unittest.main()
