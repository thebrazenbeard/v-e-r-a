import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "protocol" / "VERARELAY_DSM_LIFECYCLE_TRANSITIONS_V1.json"


def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_running_current_requires_framework_process_listener_and_health_agreement():
    current = load()["classification"]["RUNNING_CURRENT"]
    assert set(current) >= {
        "PACKAGE_VERSION_EXPECTED",
        "DSM_STATUS_RUNNING",
        "START_STOP_STATUS_0",
        "EXACT_OWNED_RUNTIME_PRESENT",
        "OWNED_LISTENER_17443_PRESENT",
        "APPLICATION_HEALTH_PASS",
        "APPLICATION_VERSION_EXPECTED",
    }


def test_stop_never_succeeds_with_owned_runtime_alive():
    stop = load()["transitions"]["STOP"]
    assert stop["missing_pid"] == "RECONCILE_EXACT_PROCESS_OWNERSHIP_THEN_STOP_OR_FAIL"
    assert "RETURN_SUCCESS_WITH_OWNED_PROCESS_ALIVE" in stop["must_not"]
    assert "KILL_UNRELATED_PID" in stop["must_not"]
    assert "KILL_BY_PORT_ONLY" in stop["must_not"]


def test_upgrade_stops_and_proves_predecessor_absent_before_successor_install():
    gates = load()["transitions"]["UPGRADE"]["ordered_gates"]
    assert gates.index("STOP_PREDECESSOR_IF_RUNNING") < gates.index(
        "VERIFY_NO_PREDECESSOR_OWNED_PROCESS"
    )
    assert gates.index("VERIFY_NO_PREDECESSOR_OWNED_PROCESS") < gates.index(
        "INSTALL_SUCCESSOR"
    )
    assert gates.index("INSTALL_SUCCESSOR") < gates.index(
        "VERIFY_SUCCESSOR_PACKAGE_VERSION"
    )


def test_reboot_never_reuses_stale_pid_as_authority():
    reboot = load()["transitions"]["REBOOT"]["success_requires"]
    assert "NO_STALE_PREBOOT_PID_AUTHORITY" in reboot


def test_relay_running_does_not_equal_current_route():
    route = load()["route_gate"]
    assert route["relay_package_running_ne_durable_relay_current"] is True
    assert set(route["durable_relay_current_requires"]) >= {
        "RUNNING_CURRENT",
        "VERAMESH_V1_PROTOCOL_CONFORMANCE",
        "CURRENT_ROUTE_PROBE_PASS",
    }


def test_live_replacement_remains_exact_authority_gated():
    required = set(load()["deployment_gate"]["required_before_0005_replacement"])
    assert "PATRICK_EXACT_DEPLOY_AUTHORITY" in required
    assert "SECURITY_HOSTILE_PASS" in required
    assert "EXACT_0_4_ARTIFACT_SHA256" in required
    assert "PREDEPLOY_0005_STATE_CAPTURE" in required
    assert "ROLLBACK_ARTIFACT_AND_STATE_CAPTURE" in required
    assert "ROLLBACK_ARTIFACT_AND_DATA_PLAN" in required
