import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "protocol" / "VERARELAY_0_4_QUALIFICATION_V1.json"


def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_snapshot_custody_is_not_release_qualification():
    value = load()
    assert value["source_snapshot"]["captured_status"] == (
        "SOURCE_SNAPSHOT_PERSISTED_NOT_RUNTIME_QUALIFIED"
    )
    assert value["source_snapshot"]["non_implication"] == (
        "CAPTURED_TEST_PASS_NE_0_4_RELEASE_PASS"
    )
    assert value["current_observation"]["SOURCE_CUSTODY"] is True
    assert value["current_observation"]["SOURCE_RECONSTRUCTED"] is False


def test_qualification_states_do_not_collapse():
    value = load()
    assert value["ordered_states"] == [
        "SOURCE_CUSTODY",
        "SOURCE_RECONSTRUCTED",
        "SOURCE_PASS",
        "BUILD_PASS",
        "CONFORMANCE_PASS",
        "DEVICE_LIFECYCLE_PASS",
        "SECURITY_HOSTILE_PASS",
        "DEPLOYED",
        "DURABLE_RELAY_ROUTE_CURRENT",
        "END_TO_END_ACCEPTED",
        "BETA_REMOVAL_ELIGIBLE",
    ]
    assert "DEVICE_LIFECYCLE_PASS_NE_SECURITY_HOSTILE_PASS" in value["non_implications"]
    assert "SECURITY_HOSTILE_PASS_NE_DEPLOYED" in value["non_implications"]
    assert "DEPLOYED_NE_DURABLE_RELAY_ROUTE_CURRENT" in value["non_implications"]


def test_source_pass_closes_known_0005_defect_classes():
    required = set(load()["source_pass_requires"])
    for item in {
        "STRICT_P256_ALGORITHM_AND_KEY_TYPE",
        "REAL_ROLE_SCOPE_RECIPIENT_AUTHORIZATION",
        "IMMUTABLE_MESSAGE_IDEMPOTENCY_CONFLICT",
        "MONOTONIC_RECEIPT_PROJECTION",
        "AUDIT_FAILURE_BLOCKS_SECURITY_MUTATION",
        "CORRUPT_RECORD_QUARANTINE",
        "RATE_LIMITING_PRESENT",
        "STRUCTURED_HEALTH",
    }:
        assert item in required


def test_device_lifecycle_gate_covers_orphan_and_cleanup_failures():
    required = set(load()["device_lifecycle_pass_requires"])
    assert "MISSING_PID_ORPHAN_RECONCILIATION" in required
    assert "STALE_PID_REJECTION" in required
    assert "PID_REUSE_REJECTION" in required
    assert "NO_PROCESS_LEFT_AFTER_UNINSTALL" in required
    assert "NAS_REBOOT_WITH_PENDING_MAIL" in required


def test_security_hostile_gate_is_explicit_and_independent():
    value = load()
    required = set(value["security_hostile_pass_requires"])
    assert {
        "INDEPENDENT_REVIEW_EXACT_HEAD",
        "AUTHENTICATION_HOSTILE_PASS",
        "AUTHORIZATION_HOSTILE_PASS",
        "IDEMPOTENCY_AND_REPLAY_HOSTILE_PASS",
        "AUDIT_INTEGRITY_HOSTILE_PASS",
        "LIFECYCLE_OWNERSHIP_HOSTILE_PASS",
        "RESOURCE_EXHAUSTION_HOSTILE_PASS",
        "AMBIGUOUS_DELIVERY_HOSTILE_PASS",
    }.issubset(required)
    assert value["current_observation"]["SECURITY_HOSTILE_PASS"] is False


def test_deploy_and_route_current_are_separate():
    value = load()
    assert "SECURITY_HOSTILE_PASS" in value["deployed_requires"]
    assert "PATRICK_EXACT_DEPLOY_AUTHORITY" in value["deployed_requires"]
    route = set(value["durable_relay_route_current_requires"])
    assert "DEPLOYED" in route
    assert "FRESH_DATA_PLANE_PROBE_PASS" in route
    assert "APPLICATION_AUTHORIZATION_PASS" in route


def test_beta_removal_is_not_cosmetic_flag_flip():
    beta = load()["beta_removal"]
    assert beta["beta_flag_false_ne_release_qualified"] is True
    assert set(beta["eligible_requires"]) == {
        "SOURCE_PASS",
        "BUILD_PASS",
        "CONFORMANCE_PASS",
        "DEVICE_LIFECYCLE_PASS",
        "SECURITY_HOSTILE_PASS",
    }
