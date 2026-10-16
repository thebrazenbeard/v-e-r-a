from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "SD1_SUPABASE_WITNESS_QUALIFICATION_CONTRACT_V1"
CURRENTNESS_PATHS = (
    ("current_frontier", "qualification_artifact"),
    ("current_frontier", "production_witness"),
    ("current_frontier", "causal_data_collection"),
    ("current_frontier", "control_causality"),
)
FRONTIER_DOMAINS = {
    "qualification_artifact": ("UNBOUND", "PINNED"),
    "production_witness": ("NOT_CONSTRUCTIBLE", "CONSTRUCTIBLE"),
    "causal_data_collection": ("HOLD", "READY"),
    "control_causality": ("UNRESOLVED", "PENDING_EXECUTION"),
}
EXPECTED_TOP_LEVEL = {
    "schema",
    "status",
    "artifact_schema",
    "required_evidence_gates",
    "artifact_gate_shape",
    "state_separation",
    "current_frontier",
    "current_frontier_allowed_values",
    "implementation_subject_binding",
    "non_effects",
}


class SD1AcceptanceIntegrityError(ValueError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def validate_acceptance_contract(value: dict[str, Any]) -> None:
    if type(value) is not dict or set(value) != EXPECTED_TOP_LEVEL:
        raise SD1AcceptanceIntegrityError("acceptance contract envelope mismatch")
    if value.get("schema") != SCHEMA:
        raise SD1AcceptanceIntegrityError("acceptance contract schema mismatch")
    if type(value.get("status")) is not str or not value["status"]:
        raise SD1AcceptanceIntegrityError("acceptance contract status must be a nonempty string")

    frontier = value.get("current_frontier")
    domains = value.get("current_frontier_allowed_values")
    if type(frontier) is not dict or set(frontier) != set(FRONTIER_DOMAINS):
        raise SD1AcceptanceIntegrityError("current_frontier shape mismatch")
    if type(domains) is not dict or set(domains) != set(FRONTIER_DOMAINS):
        raise SD1AcceptanceIntegrityError("current_frontier domain shape mismatch")

    expected_domains = {
        field: list(allowed)
        for field, allowed in FRONTIER_DOMAINS.items()
    }
    if domains != expected_domains:
        raise SD1AcceptanceIntegrityError("current_frontier domain definition mismatch")

    for field, allowed in FRONTIER_DOMAINS.items():
        current = frontier[field]
        if type(current) is not str or current not in allowed:
            raise SD1AcceptanceIntegrityError(
                f"current_frontier {field} value outside allowed domain"
            )

    binding = value.get("implementation_subject_binding")
    if type(binding) is not dict:
        raise SD1AcceptanceIntegrityError("implementation subject binding missing")
    if binding.get("digest_algorithm") != "SHA256_CANONICAL_JSON_SEMANTIC_PROJECTION_V1":
        raise SD1AcceptanceIntegrityError("semantic digest algorithm mismatch")
    expected_excludes = [".".join(parts) for parts in CURRENTNESS_PATHS]
    if binding.get("subject_projection_excludes") != expected_excludes:
        raise SD1AcceptanceIntegrityError("semantic projection exclusion mismatch")

    separation = value.get("state_separation")
    if type(separation) is not dict:
        raise SD1AcceptanceIntegrityError("state_separation must be an object")
    if separation.get("production_witness_constructible") != (
        "DOES_NOT_AUTHORIZE_FIRST_CAUSAL_MUTATION"
    ):
        raise SD1AcceptanceIntegrityError("production witness authority ceiling moved")
    if separation.get("causal_collection") != "SEPARATE_PROTECTED_EFFECT":
        raise SD1AcceptanceIntegrityError("causal collection effect ceiling moved")

    non_effects = value.get("non_effects")
    required_non_effects = {
        "NOT_PROVIDER_MUTATION",
        "NOT_CREDENTIAL_PROVISIONING",
        "NOT_CAUSAL_DATA_COLLECTION",
        "NOT_PROJECT_INSTALL",
        "NOT_CURRENT_ROUTE_QUALIFICATION",
        "NOT_CONTROL_CAUSALITY_PASS",
        "NOT_GLOBAL_QUALIFICATION",
        "NOT_MERGE_AUTHORITY",
    }
    if type(non_effects) is not list or not required_non_effects.issubset(set(non_effects)):
        raise SD1AcceptanceIntegrityError("acceptance non-effect ceiling is incomplete")


def semantic_subject_sha256(value: dict[str, Any]) -> str:
    validate_acceptance_contract(value)
    projected = json.loads(json.dumps(value))
    for key_path in CURRENTNESS_PATHS:
        cursor = projected
        for key in key_path[:-1]:
            cursor = cursor[key]
        del cursor[key_path[-1]]
    return hashlib.sha256(_canonical_bytes(projected)).hexdigest()


def load_and_validate(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SD1AcceptanceIntegrityError("acceptance contract unreadable") from exc
    validate_acceptance_contract(value)
    return value


__all__ = [
    "FRONTIER_DOMAINS",
    "SD1AcceptanceIntegrityError",
    "load_and_validate",
    "semantic_subject_sha256",
    "validate_acceptance_contract",
]
