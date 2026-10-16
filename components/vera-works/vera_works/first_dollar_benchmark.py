from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from enum import Enum
from typing import Iterable, Mapping
from urllib.parse import urlparse


class EvidenceQuality(str, Enum):
    SOURCE_ESTIMATE = "SOURCE_ESTIMATE"
    EXACT_RESOURCE_MEASURED = "EXACT_RESOURCE_MEASURED"
    REALIZED_REWARD = "REALIZED_REWARD"


class BenchmarkState(str, Enum):
    INVALID = "INVALID"
    STALE_QUOTE = "STALE_QUOTE"
    NO_REWARD = "NO_REWARD"
    NONPOSITIVE_NET = "NONPOSITIVE_NET"
    POSITIVE_ESTIMATE = "POSITIVE_ESTIMATE"
    POSITIVE_MEASURED = "POSITIVE_MEASURED"
    POSITIVE_REALIZED = "POSITIVE_REALIZED"


@dataclass(frozen=True)
class BenchmarkObservation:
    mechanism_id: str
    resource_alias: str
    evidence_quality: EvidenceQuality
    source_uri: str
    quote_observed_at: str
    max_quote_age_seconds: int
    benchmark_duration_hours: str
    hours_per_day: str
    baseline_watts: str
    workload_watts: str
    performance_metric_name: str
    performance_metric_value: str
    performance_metric_unit: str
    reward_units_per_day: str
    reward_unit_symbol: str
    reward_unit_usd: str
    minimum_payout_units: str
    payout_fee_units: str
    liquidity_ratio: str
    platform_fee_usd_per_day: str
    other_cost_usd_per_day: str
    electricity_usd_per_kwh: str
    warmup_days: str
    payout_lag_days: str
    evidence_refs: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "BenchmarkObservation":
        data = dict(value)
        data["evidence_quality"] = EvidenceQuality(str(data["evidence_quality"]))
        data["evidence_refs"] = tuple(data.get("evidence_refs", ()))
        return cls(**data)  # type: ignore[arg-type]


@dataclass(frozen=True)
class BenchmarkAssessment:
    mechanism_id: str
    resource_alias: str
    evidence_quality: EvidenceQuality
    state: BenchmarkState
    reason: str
    incremental_watts: str | None = None
    incremental_kwh_per_day: str | None = None
    gross_usd_per_day: str | None = None
    power_cost_usd_per_day: str | None = None
    payout_fee_usd_per_cycle: str | None = None
    payout_cycle_days: int | None = None
    payout_fee_usd_per_day: str | None = None
    net_usd_per_day: str | None = None
    net_usd_per_30d: str | None = None
    days_to_first_payout: int | None = None
    first_payout_cash_usd: str | None = None
    first_payout_net_profit_usd: str | None = None
    break_even_electricity_usd_per_kwh: str | None = None
    authorization_state: str = "NOT_AUTHORIZED"

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["evidence_quality"] = self.evidence_quality.value
        data["state"] = self.state.value
        return data


def _decimal(value: str, field: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"{field} must be a decimal string") from exc
    if not parsed.is_finite():
        raise ValueError(f"{field} must be finite")
    return parsed


def _nonnegative(value: str, field: str) -> Decimal:
    parsed = _decimal(value, field)
    if parsed < 0:
        raise ValueError(f"{field} must be non-negative")
    return parsed


def _parse_time(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include timezone")
    return parsed.astimezone(timezone.utc)


def _fmt(value: Decimal) -> str:
    return format(value.normalize() if value != 0 else Decimal("0"), "f")


def _ceil_int(value: Decimal) -> int:
    return int(value.to_integral_value(rounding=ROUND_CEILING))


def validate_observation(
    observation: BenchmarkObservation,
    *,
    now: datetime | None = None,
) -> list[str]:
    errors: list[str] = []
    moment = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    for field in (
        "mechanism_id",
        "resource_alias",
        "source_uri",
        "quote_observed_at",
        "performance_metric_name",
        "performance_metric_value",
        "performance_metric_unit",
        "reward_unit_symbol",
    ):
        if not isinstance(getattr(observation, field), str) or not getattr(observation, field).strip():
            errors.append(f"{field} is required")

    parsed_uri = urlparse(observation.source_uri)
    if parsed_uri.scheme != "https" or not parsed_uri.netloc:
        errors.append("source_uri must be an HTTPS URL")

    if not isinstance(observation.max_quote_age_seconds, int) or observation.max_quote_age_seconds <= 0:
        errors.append("max_quote_age_seconds must be a positive integer")

    try:
        observed_at = _parse_time(observation.quote_observed_at, "quote_observed_at")
        if observed_at > moment:
            errors.append("quote_observed_at must not be in the future")
    except ValueError as exc:
        errors.append(str(exc))

    decimal_fields = (
        "benchmark_duration_hours",
        "hours_per_day",
        "performance_metric_value",
        "baseline_watts",
        "workload_watts",
        "reward_units_per_day",
        "reward_unit_usd",
        "minimum_payout_units",
        "payout_fee_units",
        "liquidity_ratio",
        "platform_fee_usd_per_day",
        "other_cost_usd_per_day",
        "electricity_usd_per_kwh",
        "warmup_days",
        "payout_lag_days",
    )
    values: dict[str, Decimal] = {}
    for field in decimal_fields:
        try:
            values[field] = _nonnegative(str(getattr(observation, field)), field)
        except ValueError as exc:
            errors.append(str(exc))

    hours = values.get("hours_per_day")
    if hours is not None and (hours <= 0 or hours > 24):
        errors.append("hours_per_day must be greater than 0 and at most 24")

    liquidity = values.get("liquidity_ratio")
    if liquidity is not None and liquidity > 1:
        errors.append("liquidity_ratio must be between 0 and 1")

    baseline = values.get("baseline_watts")
    workload = values.get("workload_watts")
    if baseline is not None and workload is not None and workload < baseline:
        errors.append("workload_watts must be at least baseline_watts")

    duration = values.get("benchmark_duration_hours")
    if observation.evidence_quality in {
        EvidenceQuality.EXACT_RESOURCE_MEASURED,
        EvidenceQuality.REALIZED_REWARD,
    }:
        if duration is not None and duration <= 0:
            errors.append("measured evidence requires benchmark_duration_hours > 0")
        if not any(ref.startswith("benchmark:") for ref in observation.evidence_refs):
            errors.append("measured evidence requires benchmark: evidence")

    if observation.evidence_quality == EvidenceQuality.SOURCE_ESTIMATE:
        if not any(ref.startswith("estimate:") for ref in observation.evidence_refs):
            errors.append("source estimates require estimate: evidence")

    if observation.evidence_quality == EvidenceQuality.REALIZED_REWARD:
        if not any(ref.startswith("receipt:") for ref in observation.evidence_refs):
            errors.append("realized reward evidence requires receipt: evidence")

    if not observation.evidence_refs:
        errors.append("at least one evidence reference is required")

    return errors


def assess_observation(
    observation: BenchmarkObservation,
    *,
    now: datetime | None = None,
) -> BenchmarkAssessment:
    moment = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    errors = validate_observation(observation, now=moment)
    if errors:
        return BenchmarkAssessment(
            mechanism_id=observation.mechanism_id,
            resource_alias=observation.resource_alias,
            evidence_quality=observation.evidence_quality,
            state=BenchmarkState.INVALID,
            reason="; ".join(errors),
        )

    observed_at = _parse_time(observation.quote_observed_at, "quote_observed_at")
    age_seconds = (moment - observed_at).total_seconds()
    if age_seconds > observation.max_quote_age_seconds:
        return BenchmarkAssessment(
            mechanism_id=observation.mechanism_id,
            resource_alias=observation.resource_alias,
            evidence_quality=observation.evidence_quality,
            state=BenchmarkState.STALE_QUOTE,
            reason="Reward/liquidity quote is older than the permitted age.",
        )

    duration = _nonnegative(observation.benchmark_duration_hours, "benchmark_duration_hours")
    hours_per_day = _nonnegative(observation.hours_per_day, "hours_per_day")
    baseline = _nonnegative(observation.baseline_watts, "baseline_watts")
    workload = _nonnegative(observation.workload_watts, "workload_watts")
    units_per_day = _nonnegative(observation.reward_units_per_day, "reward_units_per_day")
    unit_usd = _nonnegative(observation.reward_unit_usd, "reward_unit_usd")
    minimum = _nonnegative(observation.minimum_payout_units, "minimum_payout_units")
    payout_fee_units = _nonnegative(observation.payout_fee_units, "payout_fee_units")
    liquidity = _nonnegative(observation.liquidity_ratio, "liquidity_ratio")
    platform_fee = _nonnegative(observation.platform_fee_usd_per_day, "platform_fee_usd_per_day")
    other_cost = _nonnegative(observation.other_cost_usd_per_day, "other_cost_usd_per_day")
    electricity = _nonnegative(observation.electricity_usd_per_kwh, "electricity_usd_per_kwh")
    warmup_days = _nonnegative(observation.warmup_days, "warmup_days")
    payout_lag_days = _nonnegative(observation.payout_lag_days, "payout_lag_days")

    incremental_watts = workload - baseline
    incremental_kwh = incremental_watts * hours_per_day / Decimal("1000")
    power_cost = incremental_kwh * electricity
    gross_usd = units_per_day * unit_usd * liquidity

    if units_per_day <= 0 or gross_usd <= 0:
        return BenchmarkAssessment(
            mechanism_id=observation.mechanism_id,
            resource_alias=observation.resource_alias,
            evidence_quality=observation.evidence_quality,
            state=BenchmarkState.NO_REWARD,
            reason="No positive liquid reward rate is established.",
            incremental_watts=_fmt(incremental_watts),
            incremental_kwh_per_day=_fmt(incremental_kwh),
            gross_usd_per_day=_fmt(gross_usd),
            power_cost_usd_per_day=_fmt(power_cost),
        )

    threshold = minimum if minimum > 0 else units_per_day
    cycle_days = max(1, _ceil_int(threshold / units_per_day))
    payout_fee_usd = payout_fee_units * unit_usd * liquidity
    payout_fee_daily = payout_fee_usd / Decimal(cycle_days)
    net_daily = gross_usd - power_cost - platform_fee - other_cost - payout_fee_daily

    production_days = Decimal(cycle_days)
    first_units = units_per_day * production_days
    first_payout_cash = max(first_units * unit_usd * liquidity - payout_fee_usd, Decimal("0"))
    warmup_operating_days = warmup_days
    first_operating_cost = (
        (power_cost + platform_fee + other_cost)
        * (production_days + warmup_operating_days)
    )
    first_net_profit = first_payout_cash - first_operating_cost

    days_to_first = _ceil_int(warmup_days) + cycle_days + _ceil_int(payout_lag_days)

    non_power_net = gross_usd - platform_fee - other_cost - payout_fee_daily
    if incremental_kwh > 0:
        break_even = max(non_power_net / incremental_kwh, Decimal("0"))
        break_even_text: str | None = _fmt(break_even)
    else:
        break_even_text = None

    if net_daily <= 0:
        state = BenchmarkState.NONPOSITIVE_NET
        reason = "Reward is positive, but measured/estimated operating economics are non-positive after power and explicit costs."
    elif observation.evidence_quality == EvidenceQuality.REALIZED_REWARD:
        state = BenchmarkState.POSITIVE_REALIZED
        reason = "Positive economics are backed by an exact-resource realized reward observation; this still does not authorize a workload."
    elif observation.evidence_quality == EvidenceQuality.EXACT_RESOURCE_MEASURED:
        state = BenchmarkState.POSITIVE_MEASURED
        reason = "Positive economics are backed by an exact-resource benchmark; this still does not authorize a workload."
    else:
        state = BenchmarkState.POSITIVE_ESTIMATE
        reason = "Positive economics are only source-estimated. Run an exact-resource benchmark before any workload authorization."

    return BenchmarkAssessment(
        mechanism_id=observation.mechanism_id,
        resource_alias=observation.resource_alias,
        evidence_quality=observation.evidence_quality,
        state=state,
        reason=reason,
        incremental_watts=_fmt(incremental_watts),
        incremental_kwh_per_day=_fmt(incremental_kwh),
        gross_usd_per_day=_fmt(gross_usd),
        power_cost_usd_per_day=_fmt(power_cost),
        payout_fee_usd_per_cycle=_fmt(payout_fee_usd),
        payout_cycle_days=cycle_days,
        payout_fee_usd_per_day=_fmt(payout_fee_daily),
        net_usd_per_day=_fmt(net_daily),
        net_usd_per_30d=_fmt(net_daily * Decimal("30")),
        days_to_first_payout=days_to_first,
        first_payout_cash_usd=_fmt(first_payout_cash),
        first_payout_net_profit_usd=_fmt(first_net_profit),
        break_even_electricity_usd_per_kwh=break_even_text,
    )


def rank_first_dollar(
    assessments: Iterable[BenchmarkAssessment],
) -> list[BenchmarkAssessment]:
    quality_rank = {
        EvidenceQuality.REALIZED_REWARD: 0,
        EvidenceQuality.EXACT_RESOURCE_MEASURED: 1,
        EvidenceQuality.SOURCE_ESTIMATE: 2,
    }
    eligible = [
        item for item in assessments
        if item.state in {
            BenchmarkState.POSITIVE_REALIZED,
            BenchmarkState.POSITIVE_MEASURED,
            BenchmarkState.POSITIVE_ESTIMATE,
        }
    ]

    def key(item: BenchmarkAssessment) -> tuple[int, int, Decimal, str]:
        days = item.days_to_first_payout if item.days_to_first_payout is not None else 10**9
        net = Decimal(item.net_usd_per_day or "0")
        return (
            quality_rank[item.evidence_quality],
            days,
            -net,
            item.mechanism_id,
        )

    return sorted(eligible, key=key)
