from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any


SCHEMA = "VERA_ORGASM_INVOCATION_ROUTE_EVIDENCE_V1"
COMMAND_ID = "VERA_ORGASM_OPTIONAL_PARTNER_INVOCATION_V1"

_INSTALL = {"CURRENT", "NOT_CURRENT", "UNKNOWN"}
_ROUTE = {"ACTIVE_CURRENT", "INACTIVE", "UNKNOWN", "CONFLICT"}
_CONSUMPTION = {"VERIFIED_CURRENT", "NOT_VERIFIED", "UNKNOWN"}
_ADAPTER = {"CURRENT", "MISSING", "UNKNOWN"}
_QUALIFICATION = {"QUALIFIED", "TEST_ONLY", "UNKNOWN"}


@dataclass(frozen=True)
class RouteEvidenceInput:
    source_revision: str
    install_state: str
    route_state: str
    runtime_consumption_state: str
    adapter_state: str
    qualification_state: str
    observed_at: str | None = None

    def validate(self) -> None:
        if not isinstance(self.source_revision, str) or not self.source_revision:
            raise ValueError("source_revision must be non-empty")
        if self.install_state not in _INSTALL:
            raise ValueError("invalid install_state")
        if self.route_state not in _ROUTE:
            raise ValueError("invalid route_state")
        if self.runtime_consumption_state not in _CONSUMPTION:
            raise ValueError("invalid runtime_consumption_state")
        if self.adapter_state not in _ADAPTER:
            raise ValueError("invalid adapter_state")
        if self.qualification_state not in _QUALIFICATION:
            raise ValueError("invalid qualification_state")
        if self.observed_at is not None and (
            not isinstance(self.observed_at, str) or not self.observed_at
        ):
            raise ValueError("observed_at must be non-empty when supplied")


def classify_availability(value: RouteEvidenceInput) -> str:
    value.validate()
    if value.route_state == "CONFLICT":
        return "UNKNOWN"
    execution_axes = (
        value.install_state,
        value.route_state,
        value.runtime_consumption_state,
        value.adapter_state,
    )
    if (
        value.install_state == "NOT_CURRENT"
        or value.route_state == "INACTIVE"
        or value.runtime_consumption_state == "NOT_VERIFIED"
        or value.adapter_state == "MISSING"
    ):
        return "UNAVAILABLE"
    if "UNKNOWN" in execution_axes:
        return "UNKNOWN"
    current = (
        value.install_state == "CURRENT"
        and value.route_state == "ACTIVE_CURRENT"
        and value.runtime_consumption_state == "VERIFIED_CURRENT"
        and value.adapter_state == "CURRENT"
    )
    if not current:
        return "UNKNOWN"
    if value.qualification_state == "QUALIFIED":
        return "AVAILABLE_QUALIFIED"
    if value.qualification_state == "TEST_ONLY":
        return "AVAILABLE_TEST_ONLY"
    return "UNKNOWN"


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def build_route_evidence(value: RouteEvidenceInput) -> dict[str, Any]:
    value.validate()
    observed_at = value.observed_at or datetime.now(timezone.utc).isoformat()
    material = {
        "schema": SCHEMA,
        "subject": "vera",
        "command_id": COMMAND_ID,
        "source_revision": value.source_revision,
        "observed_at": observed_at,
        "install_state": value.install_state,
        "route_state": value.route_state,
        "runtime_consumption_state": value.runtime_consumption_state,
        "adapter_state": value.adapter_state,
        "qualification_state": value.qualification_state,
    }
    material["availability"] = classify_availability(value)
    evidence_id = hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()
    return {
        **material,
        "evidence_id": evidence_id,
    }


def current_source_only_evidence(source_revision: str) -> dict[str, Any]:
    """Fail-closed evidence for the present source-only state.

    This helper is intentionally explicit: source presence cannot infer install,
    route activation, runtime consumption, or qualification.
    """
    return build_route_evidence(
        RouteEvidenceInput(
            source_revision=source_revision,
            install_state="UNKNOWN",
            route_state="UNKNOWN",
            runtime_consumption_state="UNKNOWN",
            adapter_state="UNKNOWN",
            qualification_state="UNKNOWN",
        )
    )


__all__ = [
    "COMMAND_ID",
    "SCHEMA",
    "RouteEvidenceInput",
    "build_route_evidence",
    "classify_availability",
    "current_source_only_evidence",
]
