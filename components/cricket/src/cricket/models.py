from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    NOTE = "NOTE"
    CHALLENGE = "CHALLENGE"
    BLOCK = "BLOCK"


class Disposition(str, Enum):
    PASS = "PASS"
    CHALLENGE = "CHALLENGE"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class Claim:
    statement: str
    status: str = "asserted"
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.statement, str):
            raise ValueError("claim statement must be text")
        if not isinstance(self.status, str):
            raise ValueError("claim status must be text")
        if not isinstance(self.evidence, tuple) or not all(
            isinstance(item, str) for item in self.evidence
        ):
            raise ValueError("claim evidence must be a tuple of strings")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Claim":
        if not isinstance(raw, dict):
            raise ValueError("claim must be an object")
        unknown = set(raw) - {"statement", "status", "evidence"}
        if unknown:
            raise ValueError("unknown claim fields: " + ", ".join(sorted(unknown)))
        if "statement" not in raw:
            raise ValueError("claim statement is required")
        statement = raw["statement"]
        status = raw.get("status", "asserted")
        evidence = raw.get("evidence", [])
        if not isinstance(statement, str):
            raise ValueError("claim statement must be text")
        if not isinstance(status, str):
            raise ValueError("claim status must be text")
        if not isinstance(evidence, list) or not all(isinstance(x, str) for x in evidence):
            raise ValueError("claim evidence must be a list of strings")
        return cls(
            statement=statement.strip(),
            status=status.strip().lower(),
            evidence=tuple(evidence),
        )


@dataclass(frozen=True)
class Correction:
    superseded: str
    replacement: str

    def __post_init__(self) -> None:
        if not isinstance(self.superseded, str):
            raise ValueError("correction superseded value must be text")
        if not isinstance(self.replacement, str):
            raise ValueError("correction replacement value must be text")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Correction":
        if not isinstance(raw, dict):
            raise ValueError("correction must be an object")
        unknown = set(raw) - {"superseded", "replacement"}
        if unknown:
            raise ValueError("unknown correction fields: " + ", ".join(sorted(unknown)))
        missing = [name for name in ("superseded", "replacement") if name not in raw]
        if missing:
            raise ValueError("correction fields required: " + ", ".join(missing))
        superseded = raw["superseded"]
        replacement = raw["replacement"]
        if not isinstance(superseded, str):
            raise ValueError("correction superseded value must be text")
        if not isinstance(replacement, str):
            raise ValueError("correction replacement value must be text")
        return cls(
            superseded=superseded.strip(),
            replacement=replacement.strip(),
        )


@dataclass(frozen=True)
class ReviewRequest:
    user_message: str
    candidate_response: str
    phase: str = "pre_send"
    effect_class: str = "none"
    explicit_authorization: bool = False
    completion_claimed: bool = False
    verification_evidence: tuple[str, ...] = ()
    claims: tuple[Claim, ...] = ()
    corrections: tuple[Correction, ...] = ()
    principles: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.user_message, str):
            raise ValueError("user_message must be text")
        if not isinstance(self.candidate_response, str):
            raise ValueError("candidate_response must be text")
        if not isinstance(self.phase, str):
            raise ValueError("phase must be text")
        if not isinstance(self.effect_class, str) or self.effect_class not in {
            "none",
            "reversible",
            "protected",
        }:
            raise ValueError("effect_class must be one of: none, reversible, protected")
        if not isinstance(self.explicit_authorization, bool):
            raise ValueError("explicit_authorization must be a boolean")
        if not isinstance(self.completion_claimed, bool):
            raise ValueError("completion_claimed must be a boolean")
        if not isinstance(self.verification_evidence, tuple) or not all(
            isinstance(item, str) for item in self.verification_evidence
        ):
            raise ValueError("verification_evidence must be a tuple of strings")
        if not isinstance(self.claims, tuple) or not all(
            isinstance(item, Claim) for item in self.claims
        ):
            raise ValueError("claims must be a tuple of Claim objects")
        if not isinstance(self.corrections, tuple) or not all(
            isinstance(item, Correction) for item in self.corrections
        ):
            raise ValueError("corrections must be a tuple of Correction objects")
        if not isinstance(self.principles, tuple) or not all(
            isinstance(item, str) for item in self.principles
        ):
            raise ValueError("principles must be a tuple of strings")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ReviewRequest":
        if not isinstance(raw, dict):
            raise ValueError("review request must be an object")
        allowed = {
            "user_message",
            "candidate_response",
            "phase",
            "effect_class",
            "explicit_authorization",
            "completion_claimed",
            "verification_evidence",
            "claims",
            "corrections",
            "principles",
            "metadata",
        }
        unknown = set(raw) - allowed
        if unknown:
            raise ValueError(
                "unknown review request fields: " + ", ".join(sorted(unknown))
            )

        missing = [name for name in ("user_message", "candidate_response") if name not in raw]
        if missing:
            raise ValueError("required review request fields missing: " + ", ".join(missing))

        user_message = raw["user_message"]
        candidate_response = raw["candidate_response"]
        phase = raw.get("phase", "pre_send")
        effect_class = raw.get("effect_class", "none")
        explicit_authorization = raw.get("explicit_authorization", False)
        completion_claimed = raw.get("completion_claimed", False)
        verification = raw.get("verification_evidence", [])
        principles = raw.get("principles", [])
        claims_raw = raw.get("claims", [])
        corrections_raw = raw.get("corrections", [])
        metadata = raw.get("metadata", {})

        if not isinstance(user_message, str):
            raise ValueError("user_message must be text")
        if not isinstance(candidate_response, str):
            raise ValueError("candidate_response must be text")
        if not isinstance(phase, str):
            raise ValueError("phase must be text")
        if not isinstance(effect_class, str):
            raise ValueError("effect_class must be text")
        effect_class = effect_class.strip().lower()
        if effect_class not in {"none", "reversible", "protected"}:
            raise ValueError("effect_class must be one of: none, reversible, protected")
        if not isinstance(explicit_authorization, bool):
            raise ValueError("explicit_authorization must be a boolean")
        if not isinstance(completion_claimed, bool):
            raise ValueError("completion_claimed must be a boolean")
        if not isinstance(verification, list) or not all(isinstance(x, str) for x in verification):
            raise ValueError("verification_evidence must be a list of strings")
        if not isinstance(principles, list) or not all(isinstance(x, str) for x in principles):
            raise ValueError("principles must be a list of strings")
        if not isinstance(claims_raw, list) or not all(isinstance(x, dict) for x in claims_raw):
            raise ValueError("claims must be a list of objects")
        if not isinstance(corrections_raw, list) or not all(isinstance(x, dict) for x in corrections_raw):
            raise ValueError("corrections must be a list of objects")
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object")

        return cls(
            user_message=user_message,
            candidate_response=candidate_response,
            phase=phase,
            effect_class=effect_class,
            explicit_authorization=explicit_authorization,
            completion_claimed=completion_claimed,
            verification_evidence=tuple(verification),
            claims=tuple(Claim.from_dict(x) for x in claims_raw),
            corrections=tuple(Correction.from_dict(x) for x in corrections_raw),
            principles=tuple(principles),
            metadata=dict(metadata),
        )


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    title: str
    rationale: str
    evidence: str = ""
    recommendation: str = ""
    source: str = "deterministic"

    def to_dict(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "title": self.title,
            "rationale": self.rationale,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "source": self.source,
        }


@dataclass(frozen=True)
class ReviewResult:
    disposition: Disposition
    findings: tuple[Finding, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "disposition": self.disposition.value,
            "findings": [finding.to_dict() for finding in self.findings],
        }
