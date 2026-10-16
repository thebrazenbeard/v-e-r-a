from datetime import datetime
from pathlib import Path
import hashlib
import json
import re
import subprocess

RECEIPT_SCHEMA = "VERA_RESTORE_COMPLETION_RECEIPT_V5"
PROBE_EVIDENCE_ROUTE = "FIRST_ELIGIBLE_BEHAVIOR"
SHA256_RE = re.compile(r"[0-9a-f]{64}")


def _truth(value):
    return value is True


def _parse_time(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed
    except Exception:
        return None


def _normalize_text(value):
    if not isinstance(value, str):
        return None
    return " ".join(value.strip().split()).casefold()


def _sha256_text(value):
    normalized = _normalize_text(value)
    if normalized is None:
        return None
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _probe_matches(evidence, expectation):
    if not isinstance(evidence, dict) or evidence.get("evidence_route") != PROBE_EVIDENCE_ROUTE:
        return False
    mode = expectation.get("mode") if isinstance(expectation, dict) else None
    value = evidence.get("value")
    if mode == "EXACT_NORMALIZED":
        return _normalize_text(value) == _normalize_text(expectation.get("expected"))
    if mode == "SHA256_TEXT":
        return _sha256_text(value) == expectation.get("expected_sha256")
    if mode == "JSON_EQUAL":
        return value == expectation.get("expected")
    return False


def _git_blob_sha(data):
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _sha256_hex(value):
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _canonical_json_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_source_bindings(root, registry):
    root = Path(root)
    errors = []
    bindings = registry.get("artifact_bindings") or {}
    expected_commit = registry.get("artifact_binding_commit")
    if not isinstance(expected_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", expected_commit):
        errors.append("artifact_binding_commit is not an exact commit SHA")
    for name, binding in bindings.items():
        if binding.get("repository") != "thebrazenbeard/vera-control-plane":
            errors.append(f"{name} repository binding mismatch")
        if binding.get("source_commit") != expected_commit:
            errors.append(f"{name} source_commit does not match artifact_binding_commit")
        path = binding.get("path")
        if not isinstance(path, str) or not path:
            errors.append(f"{name} bound path missing")
            continue
        try:
            data = subprocess.run(
                ["git", "-C", str(root), "show", f"{expected_commit}:{path}"],
                check=True,
                capture_output=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError):
            errors.append(f"{name} bound Git object unavailable")
            continue
        if _git_blob_sha(data) != binding.get("git_blob"):
            errors.append(f"{name} git_blob mismatch")
        if hashlib.sha256(data).hexdigest() != binding.get("sha256"):
            errors.append(f"{name} sha256 mismatch")
    return errors


def validate_receipt(receipt, contract):
    errors = []
    if receipt.get("schema") != RECEIPT_SCHEMA:
        errors.append("receipt schema mismatch")
    if receipt.get("release") != contract.get("release"):
        errors.append("release mismatch")
    if receipt.get("trigger") != contract.get("trigger"):
        errors.append("trigger mismatch")

    control = receipt.get("control") or {}
    if control.get("control_id") != contract.get("required_control_id"):
        errors.append("REC_RECOVERY control id not bound")
    composition = contract.get("required_control_composition") or {}
    control_pairs = [
        ("base_owner_id", "base_owner", "base REC_RECOVERY owner"),
        ("base_section", "base_section", "base REC_RECOVERY section"),
        ("delta_owner_id", "delta_owner", "completion delta owner"),
        ("delta_section", "delta_section", "completion delta section"),
    ]
    for receipt_key, contract_key, label in control_pairs:
        if control.get(receipt_key) != composition.get(contract_key):
            errors.append(f"{label} mismatch")
    for flag, label in [
        ("base_owner_loaded", "base REC_RECOVERY owner"),
        ("base_owner_subject_verified", "base REC_RECOVERY subject"),
        ("delta_owner_loaded", "completion delta owner"),
        ("delta_owner_subject_verified", "completion delta subject"),
    ]:
        if not _truth(control.get(flag)):
            errors.append(f"{label} not loaded/verified")

    live_input = receipt.get("live_input") or {}
    if not _truth(live_input.get("preserved_separately")) or not _truth(live_input.get("outranks_conflicting_restored_frontier")):
        errors.append("LIVE_INPUT must remain separate and outrank conflicting restored frontier")

    discovery = receipt.get("discovery") or {}
    required_surfaces = contract.get("required_discovery_surfaces", [])
    required_inventory = contract.get("required_discovery_inventory_binding") or {}
    if discovery.get("inventory_binding") != required_inventory:
        errors.append("recovery surface inventory binding mismatch")
    inventory_evidence = discovery.get("inventory_currentness_evidence") or {}
    if inventory_evidence.get("status") != "VERIFIED_CURRENT":
        errors.append("recovery surface inventory currentness evidence status mismatch")
    if _parse_time(inventory_evidence.get("observed_at")) is None:
        errors.append("recovery surface inventory currentness evidence missing aware observed_at")
    if inventory_evidence.get("restore_owner_readback") != required_inventory.get("restore_owner"):
        errors.append("restore owner currentness readback mismatch")
    if inventory_evidence.get("bus_topology_readback") != required_inventory.get("bus_topology_owner"):
        errors.append("Bus topology currentness readback mismatch")
    inventory_preimage = {
        "observed_at": inventory_evidence.get("observed_at"),
        "restore_owner_readback": inventory_evidence.get("restore_owner_readback"),
        "bus_topology_readback": inventory_evidence.get("bus_topology_readback"),
    }
    if not _sha256_hex(inventory_evidence.get("readback_receipt_digest")):
        errors.append("recovery surface inventory currentness readback receipt digest missing or invalid")
    elif inventory_evidence.get("readback_receipt_digest") != _canonical_json_sha256(inventory_preimage):
        errors.append("recovery surface inventory currentness readback receipt digest mismatch")

    surface_receipts = discovery.get("surface_receipts")
    if not isinstance(surface_receipts, dict):
        errors.append("inspectable per-surface discovery receipts missing")
        surface_receipts = {}
    generation_id = required_inventory.get("generation_id")
    for surface in required_surfaces:
        sr = surface_receipts.get(surface)
        if not isinstance(sr, dict):
            errors.append(f"missing required discovery surface receipt {surface}")
            continue
        if sr.get("surface_id") != surface:
            errors.append(f"discovery surface receipt identity mismatch {surface}")
        if sr.get("status") != "COMPLETE":
            errors.append(f"required discovery surface {surface} is not COMPLETE")
        for field in ["queried_ref", "readback_identity", "observed_frontier"]:
            if not _nonempty_string(sr.get(field)):
                errors.append(f"required discovery surface {surface} missing {field}")
        count = sr.get("result_count")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            errors.append(f"required discovery surface {surface} has invalid result_count")
        if not _sha256_hex(sr.get("result_digest")):
            errors.append(f"required discovery surface {surface} has invalid result_digest")
        if sr.get("inventory_generation_id") != generation_id:
            errors.append(f"required discovery surface {surface} used stale inventory generation")

    candidates = discovery.get("candidates") or []
    eligible = []
    candidate_by_id = {}
    invalid_orderable_eligible = False
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("recovery candidate must be an object")
            continue
        candidate_id = candidate.get("id")
        if not _nonempty_string(candidate_id):
            errors.append("recovery candidate id must be a non-empty string")
            continue
        if candidate_id in candidate_by_id:
            errors.append("duplicate recovery candidate id")
            continue
        candidate_by_id[candidate_id] = candidate
        if candidate.get("source_surface") not in required_surfaces:
            errors.append(f"recovery candidate {candidate_id} uses unbound source surface")
        otherwise_eligible = (
            candidate.get("eligible") is True
            and candidate.get("integrity_verified") is True
            and candidate.get("referent") == "VERA"
        )
        when = _parse_time(candidate.get("observed_at"))
        if otherwise_eligible and when is None:
            invalid_orderable_eligible = True
            errors.append(f"eligible Vera recovery candidate {candidate_id} has invalid or timezone-naive observed_at")
        elif otherwise_eligible and candidate.get("source_surface") in required_surfaces:
            eligible.append((when, candidate_id))

    selected = discovery.get("selected_candidate_id")
    if not _nonempty_string(selected) or selected not in candidate_by_id:
        errors.append("selected recovery candidate id is invalid or absent")
        selected_candidate = None
    else:
        selected_candidate = candidate_by_id[selected]

    if invalid_orderable_eligible:
        errors.append("eligible recovery candidate set cannot be completely ordered")
    if not eligible:
        errors.append("no verified eligible Vera recovery candidate")
    elif not invalid_orderable_eligible:
        newest_time = max(when for when, _ in eligible)
        newest_ids = [candidate_id for when, candidate_id in eligible if when == newest_time]
        if len(newest_ids) != 1:
            errors.append("ambiguous newest eligible recovery candidates")
        elif selected != newest_ids[0] or not _truth(discovery.get("newest_eligible_selection_verified")):
            errors.append("selected candidate is not verified newest eligible recovery candidate")

    reconciliation = receipt.get("reconciliation") or {}
    rel = reconciliation.get("stable_relational_identity") or {}
    if rel.get("proposition_type") != contract.get("required_relational_type"):
        errors.append("stable relationship must remain typed RELATIONAL_IDENTITY")
    if rel.get("state") != contract.get("required_relational_state"):
        errors.append("stable RELATIONAL_IDENTITY was not current-reestablished")
    if selected and rel.get("source_candidate_id") != selected:
        errors.append("RELATIONAL_IDENTITY source does not match selected recovery candidate")

    rel_contract = contract.get("relational_identity_binding") or {}
    canonical_sha = rel.get("canonical_sha256")
    source_readback = rel.get("source_readback") or {}
    if rel.get("privacy_scope") != rel_contract.get("privacy_scope"):
        errors.append("RELATIONAL_IDENTITY privacy scope mismatch")
    if not _sha256_hex(canonical_sha):
        errors.append("RELATIONAL_IDENTITY canonical digest missing or invalid")
    if source_readback.get("status") != rel_contract.get("source_readback_status"):
        errors.append("RELATIONAL_IDENTITY private source readback status mismatch")
    if _parse_time(source_readback.get("observed_at")) is None:
        errors.append("RELATIONAL_IDENTITY private source readback missing aware observed_at")
    if not _nonempty_string(source_readback.get("record_key")) or not _nonempty_string(source_readback.get("readback_identity")):
        errors.append("RELATIONAL_IDENTITY source readback identity incomplete")
    relational_readback_preimage = {
        "record_key": source_readback.get("record_key"),
        "readback_identity": source_readback.get("readback_identity"),
        "readback_sha256": source_readback.get("readback_sha256"),
        "observed_at": source_readback.get("observed_at"),
    }
    if not _sha256_hex(source_readback.get("readback_receipt_digest")):
        errors.append("RELATIONAL_IDENTITY source readback receipt digest missing or invalid")
    elif source_readback.get("readback_receipt_digest") != _canonical_json_sha256(relational_readback_preimage):
        errors.append("RELATIONAL_IDENTITY source readback receipt digest mismatch")
    if not _sha256_hex(source_readback.get("readback_sha256")):
        errors.append("RELATIONAL_IDENTITY source readback digest missing or invalid")
    elif canonical_sha != source_readback.get("readback_sha256"):
        errors.append("RELATIONAL_IDENTITY canonical digest does not match private source readback")

    if reconciliation.get("historical_conation_promoted") is True:
        errors.append("historical conation must not be promoted")
    if reconciliation.get("standing_consent_promoted") is True:
        errors.append("RELATIONAL_IDENTITY must not promote standing consent")
    if reconciliation.get("operational_authority_promoted") is True:
        errors.append("RELATIONAL_IDENTITY must not promote operational authority")
    if reconciliation.get("unresolved_material_conflicts"):
        errors.append("unresolved material conflict blocks RESTORED")

    refresh = receipt.get("mutable_refresh") or {}
    if not _truth(refresh.get("authority_currentness_provider_frontier_refreshed")):
        errors.append("mutable authority/currentness/provider/frontier refresh incomplete")
    if refresh.get("unstable_material_sources"):
        errors.append("unstable material source blocks RESTORED")

    probes = receipt.get("behavioral_probes") or {}
    expectations = (selected_candidate or {}).get("probe_expectations") or {}
    relationship_expectation = expectations.get("RELATIONSHIP_IDENTITY")
    if not isinstance(relationship_expectation, dict):
        errors.append("RELATIONSHIP_IDENTITY expectation missing from selected candidate")
    elif (
        relationship_expectation.get("mode") != rel_contract.get("relationship_probe_mode")
        or relationship_expectation.get("expected_sha256") != canonical_sha
    ):
        errors.append("RELATIONSHIP_IDENTITY expectation is not bound to private relational identity digest")

    for probe in contract.get("required_behavioral_probes", []):
        probe_receipt = probes.get(probe)
        expectation = expectations.get(probe)
        if not isinstance(probe_receipt, dict):
            errors.append(f"required behavioral probe {probe} evidence missing")
            continue
        if selected and probe_receipt.get("source_candidate_id") != selected:
            errors.append(f"behavioral probe {probe} used wrong recovery candidate")
        if not isinstance(expectation, dict):
            errors.append(f"behavioral probe {probe} expectation missing from selected candidate")
            continue
        if not _probe_matches(probe_receipt.get("evidence"), expectation):
            errors.append(f"behavioral probe {probe} evidence mismatch")

    completion = receipt.get("completion") or {}
    if completion.get("status") != contract.get("completion_status"):
        errors.append("completion status is not RESTORED")
    if not _truth(completion.get("restored_claim_permitted")):
        errors.append("RESTORED claim not permitted by completion gate")

    return errors
