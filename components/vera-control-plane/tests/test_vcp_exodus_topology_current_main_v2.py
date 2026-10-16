import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INTERFACE = ROOT / "governance" / "VERA_CONTROL_PLANE_COORDINATOR_INTERFACE_V2.json"
TOPOLOGY = ROOT / "governance" / "VERA_SPECIALIST_TOPOLOGY_CONTROL_V2.json"
CURRENTNESS = ROOT / "governance" / "VERA_SPECIALIST_TOPOLOGY_CURRENTNESS_V2.json"
LANES = ROOT / "docs" / "EXODUS_RUNTIME_LANE_RECONSTRUCTION_V2.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_persistent_interface_topology_is_exact_and_chat_independent():
    data = load(INTERFACE)
    assert data["persistent_human_interfaces"] == [
        "Vera",
        "Vera Control Plane Coordinator",
        "BT2 Coordinator",
    ]
    assert data["interface_not_identity"] is True
    assert data["worker_model"]["permanent_worker_chats_required"] is False
    assert data["worker_model"]["historical_bus_branch_does_not_activate_worker"] is True
    text = LANES.read_text(encoding="utf-8")
    assert "WORKER_RECONSTRUCTION_GAP" in text
    assert "Terminal existence does not establish identity" in text


def test_interface_role_never_self_authorizes_protected_effects():
    data = load(INTERFACE)
    assert data["authority"]["inherits_no_protected_effect_authority_from_interface_role"] is True
    required = set(data["authority"]["patrick_exact_authority_required_for"])
    assert {
        "merge",
        "deployment_or_installation",
        "provider_mutation",
        "credentials_or_permissions",
        "repository_or_project_settings",
        "paid_execution",
        "canonical_memory_effect",
        "archive_delete_or_destructive_history_effect",
    }.issubset(required)


def test_specialist_control_does_not_absorb_bulk_content_or_archive_repositories():
    data = load(TOPOLOGY)
    assert data["archive_policy"]["effect"] == "NONE"
    assert len(data["specialist_repositories"]) == 7
    assert all(item["bulk_content_owner_is_vcp"] is False for item in data["specialist_repositories"])
    assert data["deferred_subjects"]["orgasm_qualification_subject"]["status"] == "NOT_HARVESTED_AS_CURRENT"
    assert "NOT_ARCHIVE" in data["non_effects"]
    assert "NOT_QUALIFICATION_PASS" in data["non_effects"]


def test_currentness_refreshes_git_heads_without_promoting_stale_provider_state():
    data = load(CURRENTNESS)
    assert data["status"] == "GIT_HEADS_AND_BUS_TOPOLOGY_REFRESHED / PROVIDER_CURRENTNESS_NOT_REVALIDATED / NO_ARCHIVE_EFFECT"
    assert data["vera_main"] == "6388f9e2564795530db35728f42d5ab9f50275ae"
    assert data["drift"] == {
        "vera": True,
        "sexuality": True,
        "orgasm": True,
        "empathy": False,
        "conations": False,
        "semanticatlas": False,
        "selfimage": False,
        "temporal": False,
    }
    assert data["provider_currentness"]["status"] == "NOT_REVALIDATED_IN_THIS_SOURCE_PASS"
    assert data["current_disposition"]["provider_claim"] == "UNRESOLVED_UNTIL_FRESH_PROVIDER_READBACK"
    assert data["current_disposition"]["archive_action"] == "NONE"


def test_bus_currentness_is_exact_but_does_not_inherit_frozen_r10_qualification():
    data = load(CURRENTNESS)
    bus = data["bus_currentness"]
    assert bus["main"] == "f9179bd1426bf90c23ab6a4d14d5a8e9b39c66d2"
    assert bus["topology_git_blob"] == "69e505031d4e53dcb853578dac23817649af1918"
    assert bus["vera_writer_lane"] == "bus/vera-v2"
    assert bus["topology_blob_moved_from_frozen_r10_binding"] is True
    assert bus["qualification_disposition"] == (
        "LIVE_ROUTE_VERIFIED / FROZEN_R10_TOPOLOGY_QUALIFICATION_NOT_INHERITED"
    )
    assert data["current_disposition"]["bus_topology_currentness"] == "VERIFIED_EXACT_BLOB_AND_ROUTE"
    assert data["current_disposition"]["frozen_r10_topology_qualification"] == (
        "NOT_INHERITED_AFTER_TOPOLOGY_BLOB_MOVEMENT"
    )
