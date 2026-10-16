import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "protocol" / "VERARELAY_DSM_LIFECYCLE_CURRENTNESS_V1.json"


def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_application_health_never_proves_dsm_lifecycle_running():
    value = load()
    assert "APPLICATION_HEALTH_OK_NE_DSM_RUNNING" in value["observer_non_implications"]
    assert value["frozen_predecessor_observation"]["classification"] == "ORPHANED_RUNTIME"


def test_stop_cannot_succeed_on_missing_pid_without_reconciliation():
    stop = load()["lifecycle"]["stop"]
    assert stop["missing_pid_behavior"] == (
        "RECONCILE_OWNERSHIP_AND_STOP_OR_FAIL_NOT_SILENT_SUCCESS"
    )
    assert "NO_OWNED_RUNTIME_PROCESS" in stop["success_requires"]
    assert "NO_OWNED_CHILD_PROCESS" in stop["success_requires"]


def test_port_and_pid_are_not_process_ownership():
    ownership = load()["ownership"]
    assert ownership["port_only"] == "FORBIDDEN"
    assert ownership["pid_only"] == "INSUFFICIENT"
    assert ownership["unrelated_listener"] == "NEVER_ADOPT_OR_TERMINATE"
    assert "PROCESS_START_IDENTITY_OR_EQUIVALENT_REUSE_PROTECTION" in ownership["minimum_process_proof"]


def test_systemd_is_preferred_but_dsm_status_remains_required():
    value = load()
    assert value["ownership"]["preferred_supervision"] == "DSM_MANAGED_SYSTEMD_UNIT"
    assert value["ownership"]["systemd_control"] == "synosystemctl"
    assert "DSM_STATUS_RUNNING" in value["states"]["RUNNING_CURRENT"]["requires"]
    assert "START_STOP_STATUS_ZERO" in value["states"]["RUNNING_CURRENT"]["requires"]


def test_upgrade_and_uninstall_require_no_surviving_owned_processes():
    lifecycle = load()["lifecycle"]
    assert "NO_PREDECESSOR_OWNED_PROCESS_SURVIVES" in lifecycle["upgrade"]["preconditions"]
    assert "NO_OWNED_RUNTIME_PROCESS" in lifecycle["uninstall"]["success_requires"]
    assert "NO_OWNED_CHILD_PROCESS" in lifecycle["uninstall"]["success_requires"]


def test_orphaned_runtime_cannot_report_overall_health_ok():
    health = load()["health"]
    assert health["overall_ok_requires_supervisor_bound"] is True
    assert health["orphaned_runtime_health"] == "DEGRADED_LIFECYCLE_UNBOUND"


def test_beta_removal_is_evidence_gated():
    release = load()["release"]
    assert release["beta_field_is_not_release_authority"] is True
    assert set(release["beta_removal_requires"]) == {
        "SOURCE_PASS",
        "BUILD_PASS",
        "CONFORMANCE_PASS",
        "DEVICE_LIFECYCLE_PASS",
        "SECURITY_HOSTILE_PASS",
    }


def test_hostile_matrix_covers_lifecycle_ambiguity():
    attacks = set(load()["hostile_acceptance"])
    for required in {
        "MISSING_PID_LIVE_OWNED_RUNTIME",
        "PID_REUSE_UNRELATED_PROCESS",
        "UNRELATED_PROCESS_ON_17443",
        "STOP_WITH_MISSING_PID",
        "UNINSTALL_PROCESS_LEFTOVER",
        "HEALTH_OK_DSM_STOPPED",
        "SYSTEMD_UNIT_STALE",
    }:
        assert required in attacks


def test_frozen_predecessor_observation_is_not_current_device_state():
    value = load()
    frozen = value["frozen_predecessor_observation"]
    assert frozen["observed_at"] == "2026-09-20"
    assert frozen["evidence_source"] == "thebrazenbeard/vera-mesh#13"
    current = value["current_device_observation"]
    assert current["status"] == "UNKNOWN_FRESH_READBACK_REQUIRED"
    assert current["frozen_observation_is_not_current_device_state"] is True
    assert set(current["required_before_runtime_or_deployment_claim"]) >= {
        "FRESH_DSM_PACKAGE_STATUS",
        "FRESH_START_STOP_STATUS",
        "FRESH_EXACT_PROCESS_OWNERSHIP",
        "FRESH_APPLICATION_HEALTH",
        "FRESH_LISTENER_OWNERSHIP",
        "OBSERVED_AT",
    }
