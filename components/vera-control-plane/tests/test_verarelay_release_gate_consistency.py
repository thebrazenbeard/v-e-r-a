import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE = ROOT / "protocol" / "VERARELAY_DSM_LIFECYCLE_CURRENTNESS_V1.json"
QUALIFICATION = ROOT / "protocol" / "VERARELAY_0_4_QUALIFICATION_V1.json"
TRANSITIONS = ROOT / "protocol" / "VERARELAY_DSM_LIFECYCLE_TRANSITIONS_V1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_beta_removal_gate_is_identical_across_relay_contracts():
    lifecycle = load(LIFECYCLE)
    qualification = load(QUALIFICATION)
    left = set(lifecycle["release"]["beta_removal_requires"])
    right = set(qualification["beta_removal"]["eligible_requires"])
    assert left == right == {
        "SOURCE_PASS",
        "BUILD_PASS",
        "CONFORMANCE_PASS",
        "DEVICE_LIFECYCLE_PASS",
        "SECURITY_HOSTILE_PASS",
    }


def test_security_hostile_pass_is_a_real_qualification_state():
    qualification = load(QUALIFICATION)
    assert "SECURITY_HOSTILE_PASS" in qualification["ordered_states"]
    assert qualification["current_observation"]["SECURITY_HOSTILE_PASS"] is False
    assert "SECURITY_HOSTILE_PASS" in qualification["deployed_requires"]


def test_live_replacement_gate_is_not_weaker_than_qualification_deployment():
    qualification = load(QUALIFICATION)
    transitions = load(TRANSITIONS)["deployment_gate"]
    pre = set(transitions["required_before_0005_replacement"])
    post = set(transitions["post_install_required"])
    qualification_required = set(qualification["deployed_requires"])
    assert qualification_required <= (pre | post)
    assert "SECURITY_HOSTILE_PASS" in pre
