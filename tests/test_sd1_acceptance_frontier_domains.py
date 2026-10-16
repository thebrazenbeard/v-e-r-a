from copy import deepcopy
import json
from pathlib import Path

import pytest

from tools.validate_sd1_acceptance_frontier import (
    FRONTIER_DOMAINS,
    SD1AcceptanceIntegrityError,
    semantic_subject_sha256,
    validate_acceptance_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "protocol" / "SD1_CAUSAL_SUPABASE_WITNESS_QUALIFICATION_V1.json"


def load() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_current_acceptance_contract_validates():
    validate_acceptance_contract(load())


def test_exact_finite_domains_are_frozen():
    value = load()
    assert value["current_frontier_allowed_values"] == {
        field: list(allowed)
        for field, allowed in FRONTIER_DOMAINS.items()
    }


@pytest.mark.parametrize(
    ("field", "hostile"),
    [
        ("qualification_artifact", "PROVIDER_WRITE_AUTHORITY_GRANTED"),
        ("production_witness", "RUNTIME_EFFECT_AUTHORIZED"),
        ("causal_data_collection", "PROVIDER_WRITE_AUTHORITY_GRANTED"),
        ("control_causality", "CAUSAL_CONTROL_GRANTED"),
    ],
)
def test_authority_or_effect_strings_fail_closed_in_excluded_frontier(field, hostile):
    value = load()
    value["current_frontier"][field] = hostile
    with pytest.raises(SD1AcceptanceIntegrityError, match="outside allowed domain"):
        validate_acceptance_contract(value)


def test_unknown_excluded_frontier_key_fails_closed():
    value = load()
    value["current_frontier"]["provider_write_authority"] = "GRANTED"
    with pytest.raises(SD1AcceptanceIntegrityError, match="shape mismatch"):
        validate_acceptance_contract(value)


def test_expanding_a_domain_changes_semantic_subject():
    baseline = load()
    baseline_digest = semantic_subject_sha256(baseline)
    widened = deepcopy(baseline)
    widened["current_frontier_allowed_values"]["causal_data_collection"].append(
        "PROVIDER_WRITE_AUTHORITY_GRANTED"
    )
    with pytest.raises(SD1AcceptanceIntegrityError, match="domain definition mismatch"):
        semantic_subject_sha256(widened)
    assert semantic_subject_sha256(baseline) == baseline_digest


def test_in_domain_currentness_movement_does_not_move_semantic_subject():
    baseline = load()
    moved = deepcopy(baseline)
    moved["current_frontier"] = {
        "qualification_artifact": "PINNED",
        "production_witness": "CONSTRUCTIBLE",
        "causal_data_collection": "READY",
        "control_causality": "PENDING_EXECUTION",
    }
    assert semantic_subject_sha256(moved) == semantic_subject_sha256(baseline)


def test_status_change_moves_semantic_subject():
    baseline = load()
    changed = deepcopy(baseline)
    changed["status"] = "PROVIDER_WRITE_AUTHORIZED"
    assert semantic_subject_sha256(changed) != semantic_subject_sha256(baseline)


def test_non_string_status_fails_closed():
    value = load()
    value["status"] = True
    with pytest.raises(SD1AcceptanceIntegrityError, match="status must be a nonempty string"):
        validate_acceptance_contract(value)


def test_fixed_state_separation_change_moves_or_fails_subject():
    baseline = load()
    changed = deepcopy(baseline)
    changed["state_separation"]["causal_collection"] = "AUTO_ALLOWED"
    with pytest.raises(SD1AcceptanceIntegrityError, match="effect ceiling"):
        semantic_subject_sha256(changed)


def test_non_effect_ceiling_cannot_drop_provider_mutation_guard():
    value = load()
    value["non_effects"].remove("NOT_PROVIDER_MUTATION")
    with pytest.raises(SD1AcceptanceIntegrityError, match="non-effect ceiling"):
        validate_acceptance_contract(value)
