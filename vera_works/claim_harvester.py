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
    GOVERNMENT = "GOVERNMENT"
    REGULATOR = "REGULATOR"
    COURT_ADMIN = "COURT_ADMIN"
    FIRST_PARTY_PROTOCOL = "FIRST_PARTY_PROTOCOL"
    OFFICIAL = "OFFICIAL"
    SECONDARY = "SECONDARY"
    UNKNOWN = "UNKNOWN"


class EligibilityClass(str, Enum):
    ENTITLED = "ENTITLED"
    OPEN_CLAIM = "OPEN_CLAIM"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_OURS = "NOT_OURS"
    UNKNOWN = "UNKNOWN"


class MatchState(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    NO_MATCH = "NO_MATCH"


class AssessmentState(str, Enum):
    READY_FOR_EFFECT_AUTHORIZATION = "READY_FOR_EFFECT_AUTHORIZATION"
    PATRICK_ACTION_REQUIRED = "PATRICK_ACTION_REQUIRED"
    PATRICK_DECISION_REQUIRED = "PATRICK_DECISION_REQUIRED"
    WAITING_CLAIM_WINDOW = "WAITING_CLAIM_WINDOW"
    INVALID_CANDIDATE = "INVALID_CANDIDATE"
    NEEDS_BENEFICIARY_VERIFICATION = "NEEDS_BENEFICIARY_VERIFICATION"
    RESEARCH_ONLY_SOURCE_NOT_AUTHORITATIVE = "RESEARCH_ONLY_SOURCE_NOT_AUTHORITATIVE"
    RESEARCH_ONLY_AMBIGUOUS = "RESEARCH_ONLY_AMBIGUOUS"
    REJECT_NOT_OURS = "REJECT_NOT_OURS"
    REJECT_WALLET_MISMATCH = "REJECT_WALLET_MISMATCH"
    REJECT_NONPOSITIVE_VALUE = "REJECT_NONPOSITIVE_VALUE"
    OUT_OF_SCOPE_COMMUNICATION = "OUT_OF_SCOPE_COMMUNICATION"
    CLOSED_EXPIRED = "CLOSED_EXPIRED"


AUTHORITATIVE_SOURCE_CLASSES = {
    SourceClass.GOVERNMENT,
    SourceClass.REGULATOR,
    SourceClass.COURT_ADMIN,
    SourceClass.FIRST_PARTY_PROTOCOL,
    SourceClass.OFFICIAL,
}


@dataclass(frozen=True)
class WalletTarget:
    alias: str
    chain: str
    address: str

    @property
    def normalized_address(self) -> str:
        return normalize_wallet_address(self.chain, self.address)

    @property
    def fingerprint(self) -> str:
        material = f"{self.chain.lower()}:{self.normalized_address}".encode("utf-8")
        return hashlib.sha256(material).hexdigest()


@dataclass(frozen=True)
class CandidateObservation:
    claim_id: str
    title: str
    source_id: str
    source_uri: str
    source_class: SourceClass
    source_digest: str
    observed_at: str
    eligibility_class: EligibilityClass
    beneficiary_type: str
    beneficiary_locator: str | None = None
    beneficiary_match: MatchState = MatchState.UNVERIFIED
    opens_at: str | None = None
    closes_at: str | None = None
    gross_amount: str | None = None
    currency: str | None = None
    fee_estimate: str = "0"
    tax_reserve_estimate: str = "0"
    requires_wallet_signature: bool = False
    requires_identity_verification: bool = False
    requires_account_creation: bool = False
    requires_terms_acceptance: bool = False
    human_communication_required: bool = False
    evidence_refs: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "CandidateObservation":
        data = dict(value)
        data["source_class"] = SourceClass(str(data["source_class"]))
        data["eligibility_class"] = EligibilityClass(str(data["eligibility_class"]))
        data["beneficiary_match"] = MatchState(str(data.get("beneficiary_match", "UNVERIFIED")))
        data["evidence_refs"] = tuple(str(item) for item in data.get("evidence_refs", ()))
        return cls(**data)  # type: ignore[arg-type]


@dataclass(frozen=True)
class Assessment:
    claim_id: str
    state: AssessmentState
    recommendation: str
    source_uri: str
    source_digest: str
    wallet_alias: str | None
    expected_net: str | None
    currency: str | None
    boundary: str
    evidence_refs: tuple[str, ...]

    @property
    def idempotency_key(self) -> str:
        payload = {
            "claim_id": self.claim_id,
            "state": self.state.value,
            "source_digest": self.source_digest,
            "wallet_alias": self.wallet_alias,
            "expected_net": self.expected_net,
            "currency": self.currency,
            "boundary": self.boundary,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


def normalize_wallet_address(chain: str, address: str) -> str:
    chain_key = chain.strip().lower()
    value = address.strip()
    if not value:
        raise ValueError("wallet address must not be empty")
    if chain_key in {"ethereum", "evm", "base", "optimism", "arbitrum", "polygon"}:
        if not value.startswith("0x") or len(value) != 42:
            raise ValueError("EVM address must be a 20-byte 0x-prefixed address")
        try:
            int(value[2:], 16)
        except ValueError as exc:
            raise ValueError("EVM address contains non-hex characters") from exc
        return value.lower()
    if chain_key in {"bitcoin", "btc"}:
        lowered = value.lower()
        if not (lowered.startswith("bc1") and 14 <= len(lowered) <= 90):
            raise ValueError("Bitcoin target must be a mainnet bech32/bech32m address")
        if lowered != value and value.upper() != value:
            raise ValueError("mixed-case bech32 address is invalid")
        return lowered
    return value


def load_wallets_from_environment(config: Mapping[str, object]) -> list[WalletTarget]:
    result: list[WalletTarget] = []
    for raw in config.get("wallets", []):  # type: ignore[union-attr]
        item = dict(raw)  # type: ignore[arg-type]
        env_name = str(item["address_env"])
        address = os.getenv(env_name)
        if not address:
            raise ValueError(f"required wallet environment variable is not set: {env_name}")
        result.append(WalletTarget(alias=str(item["alias"]), chain=str(item["chain"]), address=address))
    return result


def _parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("claim timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def _decimal(value: str | None, *, field: str) -> Decimal | None:
    if value is None:
        return None
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} must be a decimal string") from exc
    if not parsed.is_finite():
        raise ValueError(f"{field} must be finite")
    return parsed


def validate_candidate(candidate: CandidateObservation) -> list[str]:
    errors: list[str] = []

    for field in ("claim_id", "title", "source_id", "source_uri", "source_digest", "observed_at", "beneficiary_type"):
        value = getattr(candidate, field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")

    digest = candidate.source_digest.lower()
    if len(digest) != 64:
        errors.append("source_digest must be a 64-character SHA-256 hex digest")
    else:
        try:
            int(digest, 16)
        except ValueError:
            errors.append("source_digest must contain only hexadecimal characters")

    try:
        observed = _parse_time(candidate.observed_at)
    except ValueError as exc:
        errors.append(f"observed_at invalid: {exc}")
        observed = None
    if observed is not None and observed > datetime.now(timezone.utc):
        errors.append("observed_at must not be in the future")

    try:
        opens = _parse_time(candidate.opens_at)
    except ValueError as exc:
        errors.append(f"opens_at invalid: {exc}")
        opens = None
    try:
        closes = _parse_time(candidate.closes_at)
    except ValueError as exc:
        errors.append(f"closes_at invalid: {exc}")
        closes = None
    if opens is not None and closes is not None and closes < opens:
        errors.append("closes_at must not precede opens_at")

    for field in ("gross_amount", "fee_estimate", "tax_reserve_estimate"):
        try:
            amount = _decimal(getattr(candidate, field), field=field)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if amount is not None and amount < 0:
            errors.append(f"{field} must be non-negative")

    if candidate.currency is not None:
        if len(candidate.currency) != 3 or not candidate.currency.isalpha() or candidate.currency != candidate.currency.upper():
            errors.append("currency must be a three-letter uppercase code")

    if not candidate.evidence_refs:
        errors.append("evidence_refs must contain at least one provenance reference")

    if candidate.beneficiary_type.upper() == "WALLET" and not candidate.beneficiary_locator:
        errors.append("wallet beneficiary requires beneficiary_locator")

    if candidate.source_class in AUTHORITATIVE_SOURCE_CLASSES:
        if not candidate.source_uri.startswith("https://"):
            errors.append("authoritative source_uri must use https")

    return errors


def expected_net(candidate: CandidateObservation) -> Decimal | None:
    gross = _decimal(candidate.gross_amount, field="gross_amount")
    if gross is None:
        return None
    fee = _decimal(candidate.fee_estimate, field="fee_estimate") or Decimal("0")
    reserve = _decimal(candidate.tax_reserve_estimate, field="tax_reserve_estimate") or Decimal("0")
    return gross - fee - reserve


def _wallet_match(candidate: CandidateObservation, wallets: Sequence[WalletTarget]) -> WalletTarget | None:
    if candidate.beneficiary_type.upper() != "WALLET" or not candidate.beneficiary_locator:
        return None
    locator = candidate.beneficiary_locator.strip()
    for wallet in wallets:
        try:
            if normalize_wallet_address(wallet.chain, locator) == wallet.normalized_address:
                return wallet
        except ValueError:
            continue
    return None


def assess_candidate(
    candidate: CandidateObservation,
    wallets: Sequence[WalletTarget],
    *,
    now: datetime | None = None,
) -> Assessment:
    moment = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    evidence = tuple(candidate.evidence_refs)
    validation_errors = validate_candidate(candidate)
    if validation_errors:
        return Assessment(
            claim_id=candidate.claim_id,
            state=AssessmentState.INVALID_CANDIDATE,
            recommendation="Candidate failed deterministic input validation: " + "; ".join(validation_errors),
            source_uri=candidate.source_uri,
            source_digest=candidate.source_digest,
            wallet_alias=None,
            expected_net=None,
            currency=candidate.currency,
            boundary="NONE",
            evidence_refs=evidence,
        )

    if candidate.eligibility_class == EligibilityClass.NOT_OURS:
        return _assessment(candidate, AssessmentState.REJECT_NOT_OURS, "Ownership or eligibility is assigned elsewhere; do not claim.", None, "NONE", evidence)

    if candidate.eligibility_class in {EligibilityClass.AMBIGUOUS, EligibilityClass.UNKNOWN}:
        return _assessment(candidate, AssessmentState.RESEARCH_ONLY_AMBIGUOUS, "Keep as research only until authoritative eligibility language resolves ownership.", None, "NONE", evidence)

    if candidate.source_class not in AUTHORITATIVE_SOURCE_CLASSES:
        return _assessment(candidate, AssessmentState.RESEARCH_ONLY_SOURCE_NOT_AUTHORITATIVE, "Find and bind an authoritative first-party, court, regulator, or government source before acting.", None, "NONE", evidence)

    closes = _parse_time(candidate.closes_at)
    if closes is not None and moment > closes:
        return _assessment(candidate, AssessmentState.CLOSED_EXPIRED, "Claim window is closed; retain provenance but take no effect.", None, "NONE", evidence)

    opens = _parse_time(candidate.opens_at)
    if opens is not None and moment < opens:
        return _assessment(candidate, AssessmentState.WAITING_CLAIM_WINDOW, "Claim window has not opened yet; re-evaluate when it opens.", None, "NONE", evidence)

    if candidate.human_communication_required:
        return _assessment(candidate, AssessmentState.OUT_OF_SCOPE_COMMUNICATION, "Reject for the current passive/no-human-communication revenue lane.", None, "NONE", evidence)

    wallet = _wallet_match(candidate, wallets)
    beneficiary_type = candidate.beneficiary_type.upper()
    if beneficiary_type == "WALLET":
        if wallet is None:
            return _assessment(candidate, AssessmentState.REJECT_WALLET_MISMATCH, "The designated beneficiary wallet is not one of the configured Vera Fund targets.", None, "NONE", evidence)
    elif beneficiary_type in {"IDENTITY", "OPEN_CLASS"}:
        if candidate.beneficiary_match != MatchState.VERIFIED:
            return _assessment(candidate, AssessmentState.NEEDS_BENEFICIARY_VERIFICATION, "Verify the identity or open-class condition against authoritative evidence before treating this as claimable.", None, "NONE", evidence)
    else:
        return _assessment(candidate, AssessmentState.NEEDS_BENEFICIARY_VERIFICATION, "Beneficiary semantics are not specific enough to authorize a claim.", None, "NONE", evidence)

    net = expected_net(candidate)
    if net is not None and net <= 0:
        return _assessment(candidate, AssessmentState.REJECT_NONPOSITIVE_VALUE, "Expected value after stated fees/reserve is not positive.", wallet, "NONE", evidence)

    if candidate.requires_terms_acceptance or candidate.requires_account_creation:
        return _assessment(
            candidate,
            AssessmentState.PATRICK_DECISION_REQUIRED,
            "A legal/account boundary is required before any claim effect. Present the exact terms/account requirement to Patrick with a recommendation.",
            wallet,
            "PATRICK_DECISION_REQUIRED",
            evidence,
        )

    if candidate.requires_identity_verification or candidate.requires_wallet_signature:
        return _assessment(
            candidate,
            AssessmentState.PATRICK_ACTION_REQUIRED,
            "Eligibility is supportable, but Patrick must perform the irreducibly human identity/signature step. Do not store secrets or sign automatically.",
            wallet,
            "PATRICK_ACTION_REQUIRED",
            evidence,
        )

    return _assessment(
        candidate,
        AssessmentState.READY_FOR_EFFECT_AUTHORIZATION,
        "Candidate passes V1 evidence and eligibility gates. Prepare an exact external-effect authorization packet; do not submit or claim automatically.",
        wallet,
        "EXACT_EFFECT_AUTHORIZATION_REQUIRED",
        evidence,
    )


def _assessment(
    candidate: CandidateObservation,
    state: AssessmentState,
    recommendation: str,
    wallet: WalletTarget | None,
    boundary: str,
    evidence_refs: tuple[str, ...],
) -> Assessment:
    try:
        net = expected_net(candidate)
    except ValueError:
        net = None
    return Assessment(
        claim_id=candidate.claim_id,
        state=state,
        recommendation=recommendation,
        source_uri=candidate.source_uri,
        source_digest=candidate.source_digest,
        wallet_alias=wallet.alias if wallet else None,
        expected_net=None if net is None else format(net, "f"),
        currency=candidate.currency,
        boundary=boundary,
        evidence_refs=evidence_refs,
    )


def harvest(
    candidates: Iterable[CandidateObservation],
    wallets: Sequence[WalletTarget],
    *,
    now: datetime | None = None,
) -> list[Assessment]:
    results = [assess_candidate(candidate, wallets, now=now) for candidate in candidates]
    priority = {
        AssessmentState.READY_FOR_EFFECT_AUTHORIZATION: 0,
        AssessmentState.PATRICK_ACTION_REQUIRED: 1,
        AssessmentState.PATRICK_DECISION_REQUIRED: 2,
        AssessmentState.WAITING_CLAIM_WINDOW: 3,
        AssessmentState.NEEDS_BENEFICIARY_VERIFICATION: 4,
        AssessmentState.RESEARCH_ONLY_AMBIGUOUS: 5,
        AssessmentState.RESEARCH_ONLY_SOURCE_NOT_AUTHORITATIVE: 6,
        AssessmentState.INVALID_CANDIDATE: 7,
        AssessmentState.OUT_OF_SCOPE_COMMUNICATION: 8,
        AssessmentState.REJECT_NONPOSITIVE_VALUE: 9,
        AssessmentState.REJECT_WALLET_MISMATCH: 10,
        AssessmentState.REJECT_NOT_OURS: 11,
        AssessmentState.CLOSED_EXPIRED: 12,
    }

    def sort_key(item: Assessment) -> tuple[int, Decimal]:
        value = Decimal(item.expected_net) if item.expected_net is not None else Decimal("-1")
        return (priority[item.state], -value)

    return sorted(results, key=sort_key)


class ClaimLedger:
    """Append-only assessment ledger with deterministic idempotency keys."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def _existing_keys(self) -> set[str]:
        if not self.path.exists():
            return set()
        keys: set[str] = set()
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            key = row.get("idempotency_key")
            if isinstance(key, str):
                keys.add(key)
        return keys

    def append(self, assessment: Assessment, *, recorded_at: datetime | None = None) -> bool:
        key = assessment.idempotency_key
        if key in self._existing_keys():
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = (recorded_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
        row = {
            "schema_version": "claim-assessment-v1",
            "idempotency_key": key,
            "recorded_at": timestamp.isoformat().replace("+00:00", "Z"),
            "assessment": {
                **asdict(assessment),
                "state": assessment.state.value,
            },
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        return True
