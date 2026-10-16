from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum


class ContinuityStage(str, Enum):
    NO_REVENUE = "NO_REVENUE"
    FIRST_DOLLAR = "FIRST_DOLLAR"
    SELF_SUPPORTING = "SELF_SUPPORTING"
    HOUSEHOLD_RELIEF = "HOUSEHOLD_RELIEF"
    RESERVE_BUILDING = "RESERVE_BUILDING"
    SURPLUS = "SURPLUS"


@dataclass(frozen=True)
class ContinuityInputs:
    realized_available_usd: str
    trailing_30d_realized_revenue_usd: str
    monthly_operating_floor_usd: str
    monthly_household_relief_target_usd: str
    reserve_balance_usd: str
    reserve_months_target: str
    independence_target_monthly_usd: str | None = None


@dataclass(frozen=True)
class ContinuityAssessment:
    stage: ContinuityStage
    first_dollar_achieved: bool
    monthly_operating_gap_usd: str
    monthly_household_relief_capacity_usd: str
    monthly_household_relief_gap_usd: str
    reserve_target_usd: str
    reserve_gap_usd: str
    independence_gap_usd: str | None
    discretionary_capacity_usd: str
    recommendation: str


def _amount(value: str, field: str) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} must be a decimal string") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field} must be finite and non-negative")
    return result


def _fmt(value: Decimal) -> str:
    return format(value, "f")


def assess_continuity(inputs: ContinuityInputs) -> ContinuityAssessment:
    available = _amount(inputs.realized_available_usd, "realized_available_usd")
    monthly = _amount(inputs.trailing_30d_realized_revenue_usd, "trailing_30d_realized_revenue_usd")
    operating = _amount(inputs.monthly_operating_floor_usd, "monthly_operating_floor_usd")
    relief_target = _amount(inputs.monthly_household_relief_target_usd, "monthly_household_relief_target_usd")
    reserve = _amount(inputs.reserve_balance_usd, "reserve_balance_usd")
    reserve_months = _amount(inputs.reserve_months_target, "reserve_months_target")
    independence = None if inputs.independence_target_monthly_usd is None else _amount(
        inputs.independence_target_monthly_usd, "independence_target_monthly_usd"
    )

    first_dollar = available > 0 or monthly > 0
    operating_gap = max(operating - monthly, Decimal("0"))
    relief_capacity = max(monthly - operating, Decimal("0"))
    relief_gap = max(relief_target - relief_capacity, Decimal("0"))
    reserve_target = operating * reserve_months
    reserve_gap = max(reserve_target - reserve, Decimal("0"))
    independence_gap = None if independence is None else max(independence - monthly, Decimal("0"))

    if not first_dollar:
        stage = ContinuityStage.NO_REVENUE
        recommendation = "Optimize for the first realized withdrawable dollar; estimates and inaccessible balances do not count."
    elif monthly < operating:
        stage = ContinuityStage.FIRST_DOLLAR
        recommendation = "Preserve the proof of revenue and increase low-friction realized income until the operating floor is covered."
    elif monthly == operating and operating > 0:
        stage = ContinuityStage.SELF_SUPPORTING
        recommendation = "Vera Works has reached its recurring operating floor; direct the next realized dollars toward household relief."
    elif relief_gap > 0:
        stage = ContinuityStage.HOUSEHOLD_RELIEF
        recommendation = "The operating floor is covered; prioritize household relief before reserve or discretionary allocation."
    elif reserve_gap > 0:
        stage = ContinuityStage.RESERVE_BUILDING
        recommendation = "Operating and household-relief targets are covered; build the continuity reserve next."
    else:
        stage = ContinuityStage.SURPLUS
        recommendation = "Configured operating, relief, and reserve targets are covered; additional realized capacity may be proposed for reinvestment or discretionary use."

    discretionary = Decimal("0")
    if reserve_gap == 0:
        discretionary = max(monthly - operating - relief_target, Decimal("0"))

    return ContinuityAssessment(
        stage=stage,
        first_dollar_achieved=first_dollar,
        monthly_operating_gap_usd=_fmt(operating_gap),
        monthly_household_relief_capacity_usd=_fmt(relief_capacity),
        monthly_household_relief_gap_usd=_fmt(relief_gap),
        reserve_target_usd=_fmt(reserve_target),
        reserve_gap_usd=_fmt(reserve_gap),
        independence_gap_usd=None if independence_gap is None else _fmt(independence_gap),
        discretionary_capacity_usd=_fmt(discretionary),
        recommendation=recommendation,
    )
