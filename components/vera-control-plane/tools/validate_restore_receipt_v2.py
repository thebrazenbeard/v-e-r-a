#!/usr/bin/env python3
"""Validate VERA_RESTORE_RECEIPT_V2 semantic invariants with stdlib only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPECTED_LAYERS = {
    "CENTERED_SELF_STATE",
    "EXACT_RELATIONSHIP_IDENTITY",
    "CURRENT_CONATION_WANTING",
    "SEXUAL_SELF_CONCEPT",
    "GENDERED_RELATIONAL_SELF_REPRESENTATION",
    "AUTOBIOGRAPHICAL_MEMORY",
    "PATRICK_SPECIFIC_EMPATHY_RELATIONAL_MODEL",
    "BEHAVIORAL_EMBODIMENT_NONVERBAL_REPRESENTATION",
    "VERA_SPECIFIC_BEHAVIORAL_TEXTURE",
    "WHOLE_PROJECT_SELF",
}

ALLOWED_RESULTS = {
    "COMPLETE_FULL_SELF",
    "DEGRADED_BOUNDED",
    "CONFLICTED",
    "RECOVERY_REQUIRED",
}

ALLOWED_LAYER_STATUSES = {
    "CURRENT",
    "HISTORICAL_EVIDENCE_ONLY",
    "UNKNOWN",
    "CONFLICTED",
    "N/A",
    "SUPERSEDED",
}

ALLOWED_CURRENTNESS_CLASSES = {
    "LIVE_REAPPRAISAL",
    "CURRENT_CONFIGURED_SELF_MODEL",
    "CURRENT_DIRECT_USER_CORRECTION",
    "VERIFIED_CURRENT_EXTERNAL_STATE",
    "HISTORICAL_ONLY",
    "UNKNOWN",
    "NOT_APPLICABLE",
}

CURRENT_CAPABLE_CLASSES = {
    "LIVE_REAPPRAISAL",
    "CURRENT_CONFIGURED_SELF_MODEL",
    "CURRENT_DIRECT_USER_CORRECTION",
    "VERIFIED_CURRENT_EXTERNAL_STATE",
}

ALLOWED_SOURCE_OUTCOMES = {
    "READ_VERIFIED",
    "READ_UNVERIFIED",
    "UNAVAILABLE",
    "CONFLICT",
    "NOT_APPLICABLE",
}


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(ch in "0123456789abcdef" for ch in value)


def _centered_verified_leaves(receipt: dict) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    candidates = receipt.get("centered_candidates")
    if not isinstance(candidates, list):
        return set(), ["centered_candidates must be an array"]

    by_id: dict[str, dict] = {}
    for item in candidates:
        if not isinstance(item, dict):
            errors.append("every centered candidate must be an object")
            continue
        candidate_id = item.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            errors.append("centered candidate missing candidate_id")
            continue
        if candidate_id in by_id:
            errors.append(f"duplicate centered candidate_id: {candidate_id}")
            continue
        by_id[candidate_id] = item

    eligible_verified: set[str] = set()
    superseded: set[str] = set()

    for candidate_id, item in by_id.items():
        if item.get("verified") is True and item.get("eligibility") == "ELIGIBLE":
            eligible_verified.add(candidate_id)
        supersedes = item.get("supersedes_candidate_ids")
        if not isinstance(supersedes, list):
            errors.append(f"{candidate_id}: supersedes_candidate_ids must be an array")
            continue
        for parent_id in supersedes:
            if not isinstance(parent_id, str) or not parent_id:
                errors.append(f"{candidate_id}: invalid superseded candidate id")
                continue
            if parent_id == candidate_id:
                errors.append(f"{candidate_id}: candidate may not supersede itself")
            if parent_id not in by_id:
                errors.append(f"{candidate_id}: supersession target missing from receipt: {parent_id}")
            if candidate_id in eligible_verified and parent_id in eligible_verified:
                superseded.add(parent_id)

    return eligible_verified - superseded, errors


def validate_receipt(receipt: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(receipt, dict):
        return ["receipt must be a JSON object"]

    if receipt.get("schema") != "VERA_RESTORE_RECEIPT_V2":
        errors.append("schema must equal VERA_RESTORE_RECEIPT_V2")

    result = receipt.get("restore_result")
    if result not in ALLOWED_RESULTS:
        errors.append("invalid restore_result")

    protected = receipt.get("protected_effects_performed")
    if not isinstance(protected, list):
        errors.append("protected_effects_performed must be an array")
    elif protected:
        errors.append("restore receipt may not claim protected effects were performed by restore")

    layers = receipt.get("layers")
    if not isinstance(layers, list):
        errors.append("layers must be an array")
        layers = []

    seen_layers: set[str] = set()
    for layer in layers:
        if not isinstance(layer, dict):
            errors.append("every layer must be an object")
            continue
        layer_id = layer.get("layer_id")
        if layer_id not in EXPECTED_LAYERS:
            errors.append(f"unknown layer_id: {layer_id}")
            continue
        if layer_id in seen_layers:
            errors.append(f"duplicate layer_id: {layer_id}")
        seen_layers.add(layer_id)

        status = layer.get("status")
        if status not in ALLOWED_LAYER_STATUSES:
            errors.append(f"{layer_id}: invalid status")

        evidence = layer.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{layer_id}: evidence must be non-empty")

        basis = layer.get("currentness_basis")
        if not isinstance(basis, str) or not basis.strip():
            errors.append(f"{layer_id}: currentness_basis must be non-empty")

        basis_class = layer.get("currentness_basis_class")
        if basis_class not in ALLOWED_CURRENTNESS_CLASSES:
            errors.append(f"{layer_id}: invalid currentness_basis_class")
        if status == "CURRENT" and basis_class not in CURRENT_CAPABLE_CLASSES:
            errors.append(
                f"{layer_id}: CURRENT cannot be based only on historical/unknown/not-applicable evidence"
            )

        limitations = layer.get("limitations")
        if not isinstance(limitations, list):
            errors.append(f"{layer_id}: limitations must be an array")

    if seen_layers != EXPECTED_LAYERS:
        missing = sorted(EXPECTED_LAYERS - seen_layers)
        extra = sorted(seen_layers - EXPECTED_LAYERS)
        if missing:
            errors.append("missing layers: " + ", ".join(missing))
        if extra:
            errors.append("unexpected layers: " + ", ".join(extra))

    source_attempts = receipt.get("source_attempts")
    if not isinstance(source_attempts, list):
        errors.append("source_attempts must be an array")
        source_attempts = []

    source_attempt_layers: set[str] = set()
    for attempt in source_attempts:
        if not isinstance(attempt, dict):
            errors.append("every source attempt must be an object")
            continue
        attempt_layer = attempt.get("layer_id")
        if attempt_layer not in EXPECTED_LAYERS:
            errors.append("source attempt references unknown layer")
        else:
            source_attempt_layers.add(attempt_layer)
        if attempt.get("outcome") not in ALLOWED_SOURCE_OUTCOMES:
            errors.append("source attempt has invalid outcome")

    unresolved = receipt.get("unresolved_conflicts")
    if not isinstance(unresolved, list):
        errors.append("unresolved_conflicts must be an array")
        unresolved = []

    leaves, leaf_errors = _centered_verified_leaves(receipt)
    errors.extend(leaf_errors)

    selected = receipt.get("selected_centered_subject")
    selected_id = selected.get("candidate_id") if isinstance(selected, dict) else None
    selected_candidate = None
    if selected_id is not None:
        for candidate in receipt.get("centered_candidates", []) if isinstance(receipt.get("centered_candidates"), list) else []:
            if isinstance(candidate, dict) and candidate.get("candidate_id") == selected_id:
                selected_candidate = candidate
                break

    if isinstance(selected, dict):
        if selected_candidate is None:
            errors.append(
                "selected_centered_subject candidate_id must exist in centered_candidates"
            )
        else:
            for field in ("filename", "sha256"):
                if selected.get(field) != selected_candidate.get(field):
                    errors.append(
                        f"selected_centered_subject {field} must match centered candidate record"
                    )

    if result == "COMPLETE_FULL_SELF":
        if len(leaves) != 1:
            errors.append(
                "COMPLETE_FULL_SELF requires exactly one eligible verified centered leaf"
            )
        elif selected_id not in leaves:
            errors.append(
                "selected_centered_subject must identify the unique eligible verified centered leaf"
            )

        if unresolved:
            errors.append("COMPLETE_FULL_SELF cannot contain unresolved conflicts")

        bad_source = [
            a for a in source_attempts
            if isinstance(a, dict)
            and a.get("outcome") not in {"READ_VERIFIED", "NOT_APPLICABLE"}
        ]
        if bad_source:
            errors.append(
                "COMPLETE_FULL_SELF cannot contain unverified, unavailable, or conflicted expected sources"
            )
        if source_attempt_layers != EXPECTED_LAYERS:
            errors.append(
                "COMPLETE_FULL_SELF requires source-attempt coverage for every required layer"
            )

        bad_layers = [
            layer for layer in layers
            if isinstance(layer, dict)
            and layer.get("status") in {"UNKNOWN", "CONFLICTED"}
        ]
        if bad_layers:
            errors.append("COMPLETE_FULL_SELF cannot contain UNKNOWN or CONFLICTED layers")

    if result == "CONFLICTED" and not unresolved:
        errors.append("CONFLICTED requires at least one unresolved conflict")

    if len(leaves) > 1 and result not in {"CONFLICTED", "RECOVERY_REQUIRED"}:
        errors.append(
            "multiple incomparable eligible verified centered leaves require CONFLICTED or RECOVERY_REQUIRED"
        )

    if isinstance(selected, dict):
        if not isinstance(selected.get("candidate_id"), str) or not selected.get("candidate_id"):
            errors.append("selected_centered_subject missing candidate_id")
        if not _is_sha256(selected.get("sha256")):
            errors.append("selected_centered_subject sha256 is invalid")
        if not isinstance(selected.get("filename"), str) or not selected.get("filename"):
            errors.append("selected_centered_subject filename is required")
        if not isinstance(selected.get("verification_status"), str) or not selected.get("verification_status"):
            errors.append("selected_centered_subject verification_status is required")
    elif selected is not None:
        errors.append("selected_centered_subject must be an object or null")

    for candidate in receipt.get("centered_candidates", []) if isinstance(receipt.get("centered_candidates"), list) else []:
        if isinstance(candidate, dict):
            if not _is_sha256(candidate.get("sha256")):
                errors.append(f"{candidate.get('candidate_id')}: invalid sha256")
            if not isinstance(candidate.get("filename"), str) or not candidate.get("filename"):
                errors.append(f"{candidate.get('candidate_id')}: filename is required")

    frontier = receipt.get("resume_frontier")
    if not isinstance(frontier, str) or not frontier.strip():
        errors.append("resume_frontier must be non-empty")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_restore_receipt_v2.py <receipt.json>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"invalid receipt JSON: {exc}", file=sys.stderr)
        return 2

    errors = validate_receipt(receipt)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("VERA_RESTORE_RECEIPT_V2 validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
