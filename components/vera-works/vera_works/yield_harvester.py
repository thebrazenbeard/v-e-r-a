from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping, Sequence


class SourceClass(str, Enum):
    FIRST_PARTY_PROTOCOL = "FIRST_PARTY_PROTOCOL"
    OFFICIAL_POOL = "OFFICIAL_POOL"
    OFFICIAL_NETWORK = "OFFICIAL_NETWORK"
    OFFICIAL_MARKETPLACE = "OFFICIAL_MARKETPLACE"
    OFFICIAL_REWARD_PROGRAM = "OFFICIAL_REWARD_PROGRAM"
    SECONDARY = "SECONDARY"
    UNKNOWN = "UNKNOWN"


AUTHORITATIVE_SOURCE_CLASSES = {
    SourceClass.FIRST_PARTY_PROTOCOL,
    SourceClass.OFFICIAL_POOL,
    SourceClass.OFFICIAL_NETWORK,
    SourceClass.OFFICIAL_MARKETPLACE,
    SourceClass.OFFICIAL_REWARD_PROGRAM,
}


class ResourceKind(str, Enum):
    CPU = "CPU"
    GPU = "GPU"
    STORAGE = "STORAGE"
    BANDWIDTH = "BANDWIDTH"
    CAPITAL = "CAPITAL"
    UPTIME = "UPTIME"
    OTHER = "OTHER"


class ResourceOrigin(str, Enum):
    LOCAL_OWNED = "LOCAL_OWNED"
    CLOUD_FREE = "CLOUD_FREE"
    CLOUD_PAID = "CLOUD_PAID"
    EMPLOYER = "EMPLOYER"
    THIRD_PARTY = "THIRD_PARTY"


class ResourceAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


class TermsState(str, Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    VERIFIED_ALLOWED = "VERIFIED_ALLOWED"
    VERIFIED_PROHIBITED = "VERIFIED_PROHIBITED"
    UNKNOWN = "UNKNOWN"


class RewardModel(str, Enum):
    PROTOCOL_EMISSION = "PROTOCOL_EMISSION"
    POOL_REWARD = "POOL_REWARD"
    NETWORK_SUBSIDY = "NETWORK_SUBSIDY"
    POSTED_REWARD = "POSTED_REWARD"
    USEFUL_COMPUTE_REWARD = "USEFUL_COMPUTE_REWARD"
    STAKING_YIELD = "STAKING_YIELD"
    MARKETPLACE_DEMAND = "MARKETPLACE_DEMAND"
    CUSTOMER_SALE = "CUSTOMER_SALE"


class EconomicsState(str, Enum):
    VERIFIED = "VERIFIED"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"


class AssessmentState(str, Enum):
    READY_FOR_EFFECT_AUTHORIZATION = "READY_FOR_EFFECT_AUTHORIZATION"
    VERA_DECISION_REQUIRED = "VERA_DECISION_REQUIRED"
    PATRICK_DECISION_REQUIRED = "PATRICK_DECISION_REQUIRED"
    PATRICK_ACTION_REQUIRED = "PATRICK_ACTION_REQUIRED"
    NEEDS_LOCAL_BENCHMARK = "NEEDS_LOCAL_BENCHMARK"
    WAITING_RESOURCE_AVAILABLE = "WAITING_RESOURCE_AVAILABLE"
    STALE_QUOTE = "STALE_QUOTE"
    RESEARCH_SOURCE_UNVERIFIED = "RESEARCH_SOURCE_UNVERIFIED"
    RESEARCH_TERMS_UNVERIFIED = "RESEARCH_TERMS_UNVERIFIED"
    RESEARCH_ECONOMICS_UNVERIFIED = "RESEARCH_ECONOMICS_UNVERIFIED"
    INVALID_CANDIDATE = "INVALID_CANDIDATE"
    REJECT_CUSTOMER_DEPENDENT = "REJECT_CUSTOMER_DEPENDENT"
    REJECT_MARKETPLACE_DEPENDENT = "REJECT_MARKETPLACE_DEPENDENT"
    REJECT_HUMAN_COMMUNICATION = "REJECT_HUMAN_COMMUNICATION"
    REJECT_TERMS_PROHIBIT = "REJECT_TERMS_PROHIBIT"
    REJECT_RESOURCE_UNAUTHORIZED = "REJECT_RESOURCE_UNAUTHORIZED"
    REJECT_RESOURCE_INCOMPATIBLE = "REJECT_RESOURCE_INCOMPATIBLE"
    REJECT_PAID_INFRASTRUCTURE = "REJECT_PAID_INFRASTRUCTURE"
    REJECT_NONPOSITIVE_NET = "REJECT_NONPOSITIVE_NET"
    REJECT_BELOW_THRESHOLD = "REJECT_BELOW_THRESHOLD"


@dataclass(frozen=True)
class ResourceProfile:
    alias: str
    kind: ResourceKind
    origin: ResourceOrigin
    availability: ResourceAvailability
    electricity_usd_per_kwh: str
    usage_terms_state: TermsState = TermsState.NOT_APPLICABLE
    gpu_vram_gb: str | None = None
    ram_gb: str | None = None
    disk_free_gb: str | None = None
    upload_mbps: str | None = None
    cpu_threads: int | None = None
    notes: str = ""

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "ResourceProfile":
        data = dict(value)
        data["kind"] = ResourceKind(str(data["kind"]))
        data["origin"] = ResourceOrigin(str(data["origin"]))
        data["availability"] = ResourceAvailability(str(data["availability"]))
        data["usage_terms_state"] = TermsState(str(data.get("usage_terms_state", "NOT_APPLICABLE")))
        return cls(**data)  # type: ignore[arg-type]


@dataclass(frozen=True)
class YieldCandidate:
    yield_id: str
    title: str
    resource_alias: str
    resource_kind: ResourceKind
    reward_model: RewardModel
    source_class: SourceClass
    source_uri: str
    source_digest: str
    terms_uri: str
    terms_digest: str
    terms_state: TermsState
    observed_at: str
    quote_observed_at: str
    quote_digest: str
    max_quote_age_seconds: int
    economics_state: EconomicsState
    gross_usd_per_hour: str | None
    estimated_power_watts: str | None
    platform_fee_usd_per_hour: str
    network_cost_usd_per_hour: str
    wear_reserve_usd_per_hour: str
    other_cost_usd_per_hour: str
    upfront_cost_usd: str
    capital_locked_usd: str
    customer_acquisition_required: bool
    human_communication_required: bool
    requires_account_creation: bool
    requires_terms_acceptance: bool
    requires_identity_verification: bool
    requires_wallet_signature: bool
    requires_installation: bool
    requires_network_exposure: bool
    evidence_refs: tuple[str, ...]
    minimum_vram_gb: str | None = None
    minimum_ram_gb: str | None = None
    minimum_disk_gb: str | None = None
    minimum_upload_mbps: str | None = None
    minimum_cpu_threads: int | None = None
    notes: str = ""

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "YieldCandidate":
        data = dict(value)
        data["resource_kind"] = ResourceKind(str(data["resource_kind"]))
        data["reward_model"] = RewardModel(str(data["reward_model"]))
        data["source_class"] = SourceClass(str(data["source_class"]))
        data["terms_state"] = TermsState(str(data["terms_state"]))
        data["economics_state"] = EconomicsState(str(data["economics_state"]))
        data["evidence_refs"] = tuple(str(item) for item in data.get("evidence_refs", ()))
        return cls(**data)  # type: ignore[arg-type]


@dataclass(frozen=True)
class YieldPolicy:
    minimum_net_usd_per_hour: str = "0.01"
    available_upfront_capital_usd: str = "0"
    allow_marketplace_demand: bool = False
    allow_network_exposure: bool = False
    allow_paid_cloud: bool = False

    @classmethod
    def from_dict(cls, value: Mapping[str, object] | None) -> "YieldPolicy":
        return cls(**dict(value or {}))  # type: ignore[arg-type]


@dataclass(frozen=True)
class YieldAssessment:
    yield_id: str
    title: str
    resource_alias: str
    resource_kind: ResourceKind
    reward_model: RewardModel
    source_class: SourceClass
    state: AssessmentState
    recommendation: str
    gross_usd_per_hour: str | None
    power_cost_usd_per_hour: str | None
    total_cost_usd_per_hour: str | None
    net_usd_per_hour: str | None
    payback_hours: str | None
    quote_observed_at: str
    quote_digest: str
    source_uri: str
    source_digest: str
    terms_uri: str
    terms_digest: str
    boundary: str
    evidence_refs: tuple[str, ...]
    validation_errors: tuple[str, ...] = ()

    @property
    def idempotency_key(self) -> str:
        payload = {
            "yield_id": self.yield_id,
            "resource_alias": self.resource_alias,
            "resource_kind": self.resource_kind.value,
            "reward_model": self.reward_model.value,
            "source_class": self.source_class.value,
            "state": self.state.value,
            "net_usd_per_hour": self.net_usd_per_hour,
            "quote_observed_at": self.quote_observed_at,
            "quote_digest": self.quote_digest,
            "source_digest": self.source_digest,
            "terms_digest": self.terms_digest,
            "boundary": self.boundary,
            "validation_errors": self.validation_errors,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class YieldPlanItem:
    resource_alias: str
    yield_id: str
    expected_net_usd_per_hour: str
    reward_model: RewardModel
    authorization_state: str = "NOT_AUTHORIZED"


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def _decimal(value: str | None, *, field: str, allow_none: bool = True) -> Decimal | None:
    if value is None:
        if allow_none:
            return None
        raise ValueError(f"{field} is required")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} must be a decimal string") from exc
    if not parsed.is_finite():
        raise ValueError(f"{field} must be finite")
    return parsed


def _nonnegative_decimal(value: str | None, *, field: str, allow_none: bool = True) -> Decimal | None:
    parsed = _decimal(value, field=field, allow_none=allow_none)
    if parsed is not None and parsed < 0:
        raise ValueError(f"{field} must be non-negative")
    return parsed


def validate_resource(resource: ResourceProfile) -> list[str]:
    errors: list[str] = []
    if not resource.alias.strip():
        errors.append("resource alias must be non-empty")
    try:
        _nonnegative_decimal(resource.electricity_usd_per_kwh, field="electricity_usd_per_kwh", allow_none=False)
    except ValueError as exc:
        errors.append(str(exc))
    for field in ("gpu_vram_gb", "ram_gb", "disk_free_gb", "upload_mbps"):
        try:
            _nonnegative_decimal(getattr(resource, field), field=field)
        except ValueError as exc:
            errors.append(str(exc))
    if resource.cpu_threads is not None and resource.cpu_threads < 0:
        errors.append("cpu_threads must be non-negative")
    return errors


def validate_candidate(
    candidate: YieldCandidate,
    *,
    now: datetime | None = None,
) -> list[str]:
    errors: list[str] = []
    moment = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    for field in (
        "yield_id",
        "title",
        "resource_alias",
        "source_uri",
        "source_digest",
        "terms_uri",
        "terms_digest",
        "observed_at",
        "quote_observed_at",
        "quote_digest",
    ):
        value = getattr(candidate, field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")

    for field in ("source_uri", "terms_uri"):
        if not getattr(candidate, field).startswith("https://"):
            errors.append(f"{field} must use https")

    for field in ("source_digest", "terms_digest", "quote_digest"):
        digest = getattr(candidate, field).lower()
        if len(digest) != 64:
            errors.append(f"{field} must be a 64-character SHA-256 hex digest")
        else:
            try:
                int(digest, 16)
            except ValueError:
                errors.append(f"{field} must contain only hexadecimal characters")

    try:
        observed = _parse_time(candidate.observed_at)
    except ValueError as exc:
        errors.append(f"observed_at invalid: {exc}")
        observed = None
    try:
        quote = _parse_time(candidate.quote_observed_at)
    except ValueError as exc:
        errors.append(f"quote_observed_at invalid: {exc}")
        quote = None

    if observed is not None and observed > moment:
        errors.append("observed_at must not be in the future")
    if quote is not None and quote > moment:
        errors.append("quote_observed_at must not be in the future")
    if candidate.max_quote_age_seconds <= 0:
        errors.append("max_quote_age_seconds must be positive")

    for field in (
        "gross_usd_per_hour",
        "estimated_power_watts",
        "platform_fee_usd_per_hour",
        "network_cost_usd_per_hour",
        "wear_reserve_usd_per_hour",
        "other_cost_usd_per_hour",
        "upfront_cost_usd",
        "capital_locked_usd",
        "minimum_vram_gb",
        "minimum_ram_gb",
        "minimum_disk_gb",
        "minimum_upload_mbps",
    ):
        try:
            _nonnegative_decimal(getattr(candidate, field), field=field)
        except ValueError as exc:
            errors.append(str(exc))

    if candidate.minimum_cpu_threads is not None and candidate.minimum_cpu_threads < 0:
        errors.append("minimum_cpu_threads must be non-negative")
    if not candidate.evidence_refs:
        errors.append("evidence_refs must contain at least one provenance reference")
    if candidate.terms_state in {TermsState.VERIFIED_ALLOWED, TermsState.VERIFIED_PROHIBITED}:
        if not any(ref.startswith("terms:") for ref in candidate.evidence_refs):
            errors.append("verified terms state requires at least one terms: evidence reference")
    if candidate.economics_state == EconomicsState.VERIFIED:
        if not any(ref.startswith("benchmark:") for ref in candidate.evidence_refs):
            errors.append("verified economics requires exact-resource benchmark: evidence")
    if candidate.economics_state == EconomicsState.ESTIMATED:
        if not any(ref.startswith("quote:") or ref.startswith("estimate:") for ref in candidate.evidence_refs):
            errors.append("estimated economics requires quote: or estimate: evidence")
    return errors


def _lookup_resource(alias: str, resources: Sequence[ResourceProfile]) -> ResourceProfile | None:
    matches = [item for item in resources if item.alias == alias]
    if len(matches) != 1:
        return None
    return matches[0]


def _requirement_met(candidate: YieldCandidate, resource: ResourceProfile) -> tuple[bool, str | None]:
    checks = (
        ("VRAM", candidate.minimum_vram_gb, resource.gpu_vram_gb),
        ("RAM", candidate.minimum_ram_gb, resource.ram_gb),
        ("disk", candidate.minimum_disk_gb, resource.disk_free_gb),
        ("upload bandwidth", candidate.minimum_upload_mbps, resource.upload_mbps),
    )
    for label, required_raw, available_raw in checks:
        if required_raw is None:
            continue
        required = _decimal(required_raw, field=f"minimum_{label}")
        available = _decimal(available_raw, field=f"available_{label}") if available_raw is not None else None
        if available is None or required is None or available < required:
            return False, f"{label} requirement is not satisfied"
    if candidate.minimum_cpu_threads is not None:
        if resource.cpu_threads is None or resource.cpu_threads < candidate.minimum_cpu_threads:
            return False, "CPU thread requirement is not satisfied"
    return True, None


def economics(
    candidate: YieldCandidate,
    resource: ResourceProfile,
) -> tuple[Decimal | None, Decimal | None, Decimal | None, Decimal | None]:
    gross = _decimal(candidate.gross_usd_per_hour, field="gross_usd_per_hour")
    if gross is None:
        return None, None, None, None

    watts = _decimal(candidate.estimated_power_watts, field="estimated_power_watts")
    electricity = _decimal(resource.electricity_usd_per_kwh, field="electricity_usd_per_kwh", allow_none=False)
    if watts is None or electricity is None:
        power_cost = None
    else:
        power_cost = (watts / Decimal("1000")) * electricity

    costs = [
        _decimal(candidate.platform_fee_usd_per_hour, field="platform_fee_usd_per_hour", allow_none=False),
        _decimal(candidate.network_cost_usd_per_hour, field="network_cost_usd_per_hour", allow_none=False),
        _decimal(candidate.wear_reserve_usd_per_hour, field="wear_reserve_usd_per_hour", allow_none=False),
        _decimal(candidate.other_cost_usd_per_hour, field="other_cost_usd_per_hour", allow_none=False),
    ]
    if power_cost is None or any(item is None for item in costs):
        return gross, power_cost, None, None
    total_cost = power_cost + sum((item for item in costs if item is not None), Decimal("0"))
    net = gross - total_cost
    return gross, power_cost, total_cost, net


def _make_assessment(
    candidate: YieldCandidate,
    state: AssessmentState,
    recommendation: str,
    *,
    resource: ResourceProfile | None,
    boundary: str,
    validation_errors: tuple[str, ...] = (),
) -> YieldAssessment:
    gross = power = total = net = None
    if resource is not None:
        try:
            gross, power, total, net = economics(candidate, resource)
        except ValueError:
            pass

    upfront = None
    try:
        upfront = _decimal(candidate.upfront_cost_usd, field="upfront_cost_usd", allow_none=False)
    except ValueError:
        pass
    payback = None
    if upfront is not None and net is not None and upfront > 0 and net > 0:
        payback = upfront / net

    def fmt(value: Decimal | None) -> str | None:
        return None if value is None else format(value, "f")

    return YieldAssessment(
        yield_id=candidate.yield_id,
        title=candidate.title,
        resource_alias=candidate.resource_alias,
        resource_kind=candidate.resource_kind,
        reward_model=candidate.reward_model,
        source_class=candidate.source_class,
        state=state,
        recommendation=recommendation,
        gross_usd_per_hour=fmt(gross),
        power_cost_usd_per_hour=fmt(power),
        total_cost_usd_per_hour=fmt(total),
        net_usd_per_hour=fmt(net),
        payback_hours=fmt(payback),
        quote_observed_at=candidate.quote_observed_at,
        quote_digest=candidate.quote_digest,
        source_uri=candidate.source_uri,
        source_digest=candidate.source_digest,
        terms_uri=candidate.terms_uri,
        terms_digest=candidate.terms_digest,
        boundary=boundary,
        evidence_refs=tuple(candidate.evidence_refs),
        validation_errors=validation_errors,
    )


def assess_candidate(
    candidate: YieldCandidate,
    resources: Sequence[ResourceProfile],
    policy: YieldPolicy | None = None,
    *,
    now: datetime | None = None,
) -> YieldAssessment:
    policy = policy or YieldPolicy()
    moment = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    errors = validate_candidate(candidate, now=moment)
    resource = _lookup_resource(candidate.resource_alias, resources)
    if resource is None:
        errors.append("resource_alias must resolve to exactly one resource")
    else:
        errors.extend(validate_resource(resource))
    if errors:
        return _make_assessment(
            candidate,
            AssessmentState.INVALID_CANDIDATE,
            "Candidate or resource failed deterministic validation; repair the evidence record before ranking it.",
            resource=resource,
            boundary="NONE",
            validation_errors=tuple(errors),
        )

    assert resource is not None

    if candidate.source_class not in AUTHORITATIVE_SOURCE_CLASSES:
        return _make_assessment(
            candidate,
            AssessmentState.RESEARCH_SOURCE_UNVERIFIED,
            "Bind the mechanism to an authoritative protocol, pool, network, or marketplace source before ranking it for execution.",
            resource=resource,
            boundary="NONE",
        )

    if candidate.resource_kind != resource.kind:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_RESOURCE_INCOMPATIBLE,
            "Candidate resource kind does not match the bound resource profile.",
            resource=resource,
            boundary="NONE",
        )

    if candidate.reward_model == RewardModel.STAKING_YIELD and resource.kind != ResourceKind.CAPITAL:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_RESOURCE_INCOMPATIBLE,
            "Staking yield requires a CAPITAL resource profile.",
            resource=resource,
            boundary="NONE",
        )

    if candidate.reward_model == RewardModel.CUSTOMER_SALE or candidate.customer_acquisition_required:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_CUSTOMER_DEPENDENT,
            "This mechanism requires acquiring customers; it is outside the current customerless-yield lane.",
            resource=resource,
            boundary="NONE",
        )

    if candidate.reward_model == RewardModel.MARKETPLACE_DEMAND and not policy.allow_marketplace_demand:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_MARKETPLACE_DEPENDENT,
            "Marketplace-demand yield is disabled by policy; only protocol/network-paid mechanisms are allowed.",
            resource=resource,
            boundary="NONE",
        )

    if candidate.human_communication_required:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_HUMAN_COMMUNICATION,
            "This mechanism requires person-to-person communication and is outside the current lane.",
            resource=resource,
            boundary="NONE",
        )

    if resource.usage_terms_state == TermsState.VERIFIED_PROHIBITED:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_TERMS_PROHIBIT,
            "The bound resource is explicitly prohibited from this yield use.",
            resource=resource,
            boundary="NONE",
        )

    if resource.origin == ResourceOrigin.EMPLOYER:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_RESOURCE_UNAUTHORIZED,
            "Employer-owned resources are not available for Vera Works yield generation.",
            resource=resource,
            boundary="NONE",
        )

    if resource.origin == ResourceOrigin.THIRD_PARTY:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_RESOURCE_UNAUTHORIZED,
            "Third-party resources are not executable in V1; explicit owner authorization needs a future authority contract.",
            resource=resource,
            boundary="NONE",
        )

    if resource.origin == ResourceOrigin.CLOUD_PAID and not policy.allow_paid_cloud:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_PAID_INFRASTRUCTURE,
            "Paid cloud compute is disabled for the bootstrap lane; do not buy commodity compute to chase uncertain yield.",
            resource=resource,
            boundary="NONE",
        )

    if resource.origin in {ResourceOrigin.CLOUD_FREE, ResourceOrigin.CLOUD_PAID, ResourceOrigin.THIRD_PARTY}:
        if resource.usage_terms_state == TermsState.VERIFIED_PROHIBITED:
            return _make_assessment(
                candidate,
                AssessmentState.REJECT_TERMS_PROHIBIT,
                "The resource provider's terms prohibit this workload.",
                resource=resource,
                boundary="NONE",
            )
        if resource.usage_terms_state != TermsState.VERIFIED_ALLOWED:
            return _make_assessment(
                candidate,
                AssessmentState.RESEARCH_TERMS_UNVERIFIED,
                "Provider permission is not verified; keep this resource out of execution until terms are bound.",
                resource=resource,
                boundary="NONE",
            )

    if candidate.terms_state == TermsState.VERIFIED_PROHIBITED:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_TERMS_PROHIBIT,
            "The reward mechanism or platform terms prohibit the proposed workload.",
            resource=resource,
            boundary="NONE",
        )
    if candidate.reward_model in {RewardModel.POOL_REWARD, RewardModel.MARKETPLACE_DEMAND} and candidate.terms_state == TermsState.NOT_APPLICABLE:
        return _make_assessment(
            candidate,
            AssessmentState.RESEARCH_TERMS_UNVERIFIED,
            "Pools and marketplaces require bound current terms; NOT_APPLICABLE is not sufficient.",
            resource=resource,
            boundary="NONE",
        )
    if candidate.terms_state not in {TermsState.VERIFIED_ALLOWED, TermsState.NOT_APPLICABLE}:
        return _make_assessment(
            candidate,
            AssessmentState.RESEARCH_TERMS_UNVERIFIED,
            "Mechanism terms are not verified as allowing this use.",
            resource=resource,
            boundary="NONE",
        )

    compatible, reason = _requirement_met(candidate, resource)
    if not compatible:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_RESOURCE_INCOMPATIBLE,
            reason or "Resource requirements are not satisfied.",
            resource=resource,
            boundary="NONE",
        )

    quote_time = _parse_time(candidate.quote_observed_at)
    if (moment - quote_time).total_seconds() > candidate.max_quote_age_seconds:
        return _make_assessment(
            candidate,
            AssessmentState.STALE_QUOTE,
            "Profitability evidence is stale; refresh price, difficulty/demand, fees, and cost inputs before ranking.",
            resource=resource,
            boundary="NONE",
        )

    if candidate.economics_state == EconomicsState.UNKNOWN or candidate.gross_usd_per_hour is None:
        return _make_assessment(
            candidate,
            AssessmentState.RESEARCH_ECONOMICS_UNVERIFIED,
            "Revenue economics are not quantified well enough to compare with other workloads.",
            resource=resource,
            boundary="NONE",
        )

    if candidate.economics_state == EconomicsState.ESTIMATED:
        return _make_assessment(
            candidate,
            AssessmentState.NEEDS_LOCAL_BENCHMARK,
            "Generic profitability is only an estimate; use it to prioritize a benchmark, never to authorize the workload.",
            resource=resource,
            boundary="NONE",
        )

    gross, power, total, net = economics(candidate, resource)
    if gross is None or power is None or total is None or net is None:
        return _make_assessment(
            candidate,
            AssessmentState.RESEARCH_ECONOMICS_UNVERIFIED,
            "Incremental power/cost evidence is incomplete, so net yield cannot be established.",
            resource=resource,
            boundary="NONE",
        )

    if net <= 0:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_NONPOSITIVE_NET,
            "Measured/verified net yield is not positive after incremental costs.",
            resource=resource,
            boundary="NONE",
        )

    minimum_net = _decimal(policy.minimum_net_usd_per_hour, field="minimum_net_usd_per_hour", allow_none=False)
    assert minimum_net is not None
    if net < minimum_net:
        return _make_assessment(
            candidate,
            AssessmentState.REJECT_BELOW_THRESHOLD,
            "Net yield is positive but below the current minimum worthwhile threshold.",
            resource=resource,
            boundary="NONE",
        )

    upfront = _decimal(candidate.upfront_cost_usd, field="upfront_cost_usd", allow_none=False)
    capital_locked = _decimal(candidate.capital_locked_usd, field="capital_locked_usd", allow_none=False)
    available = _decimal(policy.available_upfront_capital_usd, field="available_upfront_capital_usd", allow_none=False)
    assert upfront is not None and capital_locked is not None and available is not None
    if upfront + capital_locked > available:
        return _make_assessment(
            candidate,
            AssessmentState.VERA_DECISION_REQUIRED,
            "This otherwise-positive mechanism requires capital beyond the currently available bootstrap allocation.",
            resource=resource,
            boundary="VERA_DECISION_REQUIRED",
        )

    if resource.availability != ResourceAvailability.AVAILABLE:
        return _make_assessment(
            candidate,
            AssessmentState.WAITING_RESOURCE_AVAILABLE,
            "The mechanism is economically viable but the resource is not currently available for an idle workload.",
            resource=resource,
            boundary="NONE",
        )

    if candidate.requires_network_exposure and not policy.allow_network_exposure:
        return _make_assessment(
            candidate,
            AssessmentState.PATRICK_DECISION_REQUIRED,
            "The workload would expose or relay network traffic; Patrick must approve the property/privacy/network boundary.",
            resource=resource,
            boundary="PATRICK_DECISION_REQUIRED",
        )

    if candidate.requires_account_creation or candidate.requires_terms_acceptance:
        return _make_assessment(
            candidate,
            AssessmentState.PATRICK_DECISION_REQUIRED,
            "A legal account or terms-acceptance boundary must be resolved before execution.",
            resource=resource,
            boundary="PATRICK_DECISION_REQUIRED",
        )

    if candidate.requires_identity_verification or candidate.requires_wallet_signature or candidate.requires_installation:
        return _make_assessment(
            candidate,
            AssessmentState.PATRICK_ACTION_REQUIRED,
            "The mechanism is viable but requires an irreducibly human identity, signing, or installation action.",
            resource=resource,
            boundary="PATRICK_ACTION_REQUIRED",
        )

    return _make_assessment(
        candidate,
        AssessmentState.READY_FOR_EFFECT_AUTHORIZATION,
        "This mechanism passes the V1 customerless-yield, terms, resource, freshness, and net-value gates. Prepare an exact workload-start authorization; do not start automatically.",
        resource=resource,
        boundary="EXACT_EFFECT_AUTHORIZATION_REQUIRED",
    )


_REWARD_INDEPENDENCE = {
    RewardModel.PROTOCOL_EMISSION: 0,
    RewardModel.POOL_REWARD: 0,
    RewardModel.NETWORK_SUBSIDY: 1,
    RewardModel.POSTED_REWARD: 1,
    RewardModel.USEFUL_COMPUTE_REWARD: 0,
    RewardModel.STAKING_YIELD: 1,
    RewardModel.MARKETPLACE_DEMAND: 2,
    RewardModel.CUSTOMER_SALE: 9,
}

_STATE_PRIORITY = {
    AssessmentState.READY_FOR_EFFECT_AUTHORIZATION: 0,
    AssessmentState.PATRICK_ACTION_REQUIRED: 1,
    AssessmentState.PATRICK_DECISION_REQUIRED: 2,
    AssessmentState.VERA_DECISION_REQUIRED: 3,
    AssessmentState.NEEDS_LOCAL_BENCHMARK: 4,
    AssessmentState.WAITING_RESOURCE_AVAILABLE: 5,
    AssessmentState.STALE_QUOTE: 6,
    AssessmentState.RESEARCH_ECONOMICS_UNVERIFIED: 7,
    AssessmentState.RESEARCH_TERMS_UNVERIFIED: 8,
    AssessmentState.RESEARCH_SOURCE_UNVERIFIED: 9,
    AssessmentState.INVALID_CANDIDATE: 10,
    AssessmentState.REJECT_BELOW_THRESHOLD: 11,
    AssessmentState.REJECT_NONPOSITIVE_NET: 12,
    AssessmentState.REJECT_RESOURCE_INCOMPATIBLE: 13,
    AssessmentState.REJECT_PAID_INFRASTRUCTURE: 14,
    AssessmentState.REJECT_RESOURCE_UNAUTHORIZED: 15,
    AssessmentState.REJECT_TERMS_PROHIBIT: 16,
    AssessmentState.REJECT_MARKETPLACE_DEPENDENT: 17,
    AssessmentState.REJECT_HUMAN_COMMUNICATION: 18,
    AssessmentState.REJECT_CUSTOMER_DEPENDENT: 19,
}


def harvest(
    candidates: Iterable[YieldCandidate],
    resources: Sequence[ResourceProfile],
    policy: YieldPolicy | None = None,
    *,
    now: datetime | None = None,
) -> list[YieldAssessment]:
    results = [assess_candidate(item, resources, policy, now=now) for item in candidates]

    def key(item: YieldAssessment) -> tuple[int, int, Decimal]:
        net = Decimal(item.net_usd_per_hour) if item.net_usd_per_hour is not None else Decimal("-1")
        return (_STATE_PRIORITY[item.state], _REWARD_INDEPENDENCE[item.reward_model], -net)

    return sorted(results, key=key)


def broker_plan(assessments: Iterable[YieldAssessment]) -> list[YieldPlanItem]:
    """Pick at most one authorized-ready workload per resource.

    This is a plan only. It does not start workloads or reserve resources.
    """
    selected: dict[str, YieldAssessment] = {}
    for item in assessments:
        if item.state != AssessmentState.READY_FOR_EFFECT_AUTHORIZATION:
            continue
        current = selected.get(item.resource_alias)
        item_net = Decimal(item.net_usd_per_hour or "0")
        current_net = Decimal(current.net_usd_per_hour or "0") if current else None
        if current is None:
            selected[item.resource_alias] = item
            continue
        if item_net > current_net:
            selected[item.resource_alias] = item
            continue
        if item_net == current_net:
            item_independence = _REWARD_INDEPENDENCE[item.reward_model]
            current_independence = _REWARD_INDEPENDENCE[current.reward_model]
            if item_independence < current_independence:
                selected[item.resource_alias] = item
                continue
            if item_independence == current_independence and item.yield_id < current.yield_id:
                selected[item.resource_alias] = item

    return [
        YieldPlanItem(
            resource_alias=item.resource_alias,
            yield_id=item.yield_id,
            expected_net_usd_per_hour=item.net_usd_per_hour or "0",
            reward_model=item.reward_model,
        )
        for item in sorted(selected.values(), key=lambda x: x.resource_alias)
    ]


def effect_packet_for_assessment(assessment: YieldAssessment) -> dict | None:
    if assessment.state != AssessmentState.READY_FOR_EFFECT_AUTHORIZATION:
        return None
    return {
        "schema_version": "yield-workload-effect-request-v1",
        "yield_id": assessment.yield_id,
        "resource_alias": assessment.resource_alias,
        "reward_model": assessment.reward_model.value,
        "expected_net_usd_per_hour": assessment.net_usd_per_hour,
        "quote_observed_at": assessment.quote_observed_at,
        "quote_digest": assessment.quote_digest,
        "source_uri": assessment.source_uri,
        "source_digest": assessment.source_digest,
        "terms_uri": assessment.terms_uri,
        "terms_digest": assessment.terms_digest,
        "requested_effect_class": "START_YIELD_WORKLOAD",
        "authorization_state": "NOT_AUTHORIZED",
        "stop_conditions": [
            "profitability quote exceeds its freshness window",
            "measured net yield falls below the configured threshold",
            "resource becomes busy or unavailable",
            "provider/protocol terms or resource authority change",
            "unexpected network, identity, signing, spend, or account boundary appears",
        ],
        "evidence_refs": list(assessment.evidence_refs),
    }


def load_resources_from_environment(config: Mapping[str, object]) -> list[ResourceProfile]:
    raw_resources = config.get("resources", [])
    if not isinstance(raw_resources, list):
        raise ValueError("config resources must be an array")
    resources: list[ResourceProfile] = []
    aliases: set[str] = set()
    for raw in raw_resources:
        if not isinstance(raw, Mapping):
            raise ValueError("every resource entry must be an object")
        data = dict(raw)
        for field, env_name in dict(data.pop("env", {})).items():
            value = os.getenv(str(env_name))
            if value is None:
                raise ValueError(f"required resource environment variable is not set: {env_name}")
            data[str(field)] = value
        resource = ResourceProfile.from_dict(data)
        if resource.alias in aliases:
            raise ValueError(f"duplicate resource alias: {resource.alias}")
        errors = validate_resource(resource)
        if errors:
            raise ValueError("; ".join(errors))
        aliases.add(resource.alias)
        resources.append(resource)
    return resources


class YieldLedger:
    """Append-only local assessment evidence with deterministic idempotency keys."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def _existing_keys(self) -> set[str]:
        if not self.path.exists():
            return set()
        keys: set[str] = set()
        lines = self.path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                if index == len(lines) - 1:
                    continue
                raise
            key = row.get("idempotency_key")
            if isinstance(key, str):
                keys.add(key)
        return keys

    def append(self, assessment: YieldAssessment, *, recorded_at: datetime | None = None) -> bool:
        key = assessment.idempotency_key
        if key in self._existing_keys():
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = (recorded_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
        row = {
            "schema_version": "yield-assessment-v1",
            "idempotency_key": key,
            "recorded_at": timestamp.isoformat().replace("+00:00", "Z"),
            "assessment": {
                **asdict(assessment),
                "resource_kind": assessment.resource_kind.value,
                "reward_model": assessment.reward_model.value,
                "source_class": assessment.source_class.value,
                "state": assessment.state.value,
            },
        }
        encoded = json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        return True
