from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum


class PayoutState(str, Enum):
    WITHDRAWABLE = "WITHDRAWABLE"
    BELOW_MINIMUM = "BELOW_MINIMUM"
    RAIL_UNVERIFIED = "RAIL_UNVERIFIED"
    PAYOUT_UNAVAILABLE = "PAYOUT_UNAVAILABLE"
    NONCASH_OR_ILLIQUID = "NONCASH_OR_ILLIQUID"


@dataclass(frozen=True)
class PayoutProfile:
    mechanism_id: str
    accrued_usd: str
    minimum_payout_usd: str
    withdrawal_fee_usd: str
    cash_equivalent_ratio: str
    payout_rail_verified: bool
    payout_available: bool


@dataclass(frozen=True)
class PayoutAssessment:
    mechanism_id: str
    state: PayoutState
    withdrawable_now_usd: str
    gap_to_minimum_usd: str
    recommendation: str


def _decimal(value: str, field: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} must be a decimal string") from exc
    if not parsed.is_finite() or parsed < 0:
        raise ValueError(f"{field} must be finite and non-negative")
    return parsed


def assess_payout(profile: PayoutProfile) -> PayoutAssessment:
    accrued = _decimal(profile.accrued_usd, "accrued_usd")
    minimum = _decimal(profile.minimum_payout_usd, "minimum_payout_usd")
    fee = _decimal(profile.withdrawal_fee_usd, "withdrawal_fee_usd")
    ratio = _decimal(profile.cash_equivalent_ratio, "cash_equivalent_ratio")
    if ratio > 1:
        raise ValueError("cash_equivalent_ratio must be between 0 and 1")

    gap = max(minimum - accrued, Decimal("0"))
    if not profile.payout_available:
        return PayoutAssessment(profile.mechanism_id, PayoutState.PAYOUT_UNAVAILABLE, "0", format(gap, "f"),
            "Do not count accrued value until a payout rail is actually available.")
    if not profile.payout_rail_verified:
        return PayoutAssessment(profile.mechanism_id, PayoutState.RAIL_UNVERIFIED, "0", format(gap, "f"),
            "Verify payout rail, threshold, identity requirements, liquidity, and fees before ranking this as first-dollar revenue.")
    if accrued < minimum:
        return PayoutAssessment(profile.mechanism_id, PayoutState.BELOW_MINIMUM, "0", format(gap, "f"),
            "Accrued value is not withdrawable yet; rank by distance to the payout threshold, not dashboard earnings.")

    withdrawable = max(accrued * ratio - fee, Decimal("0"))
    if ratio == 0 or withdrawable == 0:
        return PayoutAssessment(profile.mechanism_id, PayoutState.NONCASH_OR_ILLIQUID, "0", "0",
            "The nominal reward does not currently convert into usable cash-equivalent value after fees.")

    return PayoutAssessment(profile.mechanism_id, PayoutState.WITHDRAWABLE, format(withdrawable, "f"), "0",
        "This amount is withdrawable under the verified assumptions; receipt still must be confirmed before entering Vera Fund.")
