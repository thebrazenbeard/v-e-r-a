import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance" / "VERA_RELATIONAL_REACTION_ARTIFACTS_V1.json"
SELECTOR = ROOT / "tools" / "relational_reaction_selector.py"
PATCH = (
    ROOT
    / "project-instructions"
    / "r10a0"
    / "relational-reactions"
    / "VERA_RELATIONAL_REACTION_BEHAVIOR_PATCH_V1.md"
)

spec = importlib.util.spec_from_file_location("relational_reaction_selector", SELECTOR)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def _contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_grounded_asset_bytes_are_exact():
    data = _contract()
    for item in data["grounded_artifacts"].values():
        raw = (ROOT / item["repository_path"]).read_bytes()
        assert len(raw) == item["bytes"]
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]


def test_ambiguous_repository_artifact_is_exact_but_not_routeable():
    item = _contract()["unresolved_artifacts"]["BAD_NOT_A_GIRL"]
    raw = (ROOT / item["repository_path"]).read_bytes()
    assert len(raw) == item["bytes"]
    assert hashlib.sha256(raw).hexdigest() == item["sha256"]
    assert item["routeable"] is False


def test_serious_repair_fails_closed_without_exact_artifact_binding():
    d = module.select_reaction(
        {"event_class": "SERIOUS_REPAIR", "severity": "MAJOR", "timing_fresh": True}
    )
    assert d.status == "UNRESOLVED"
    assert d.artifact_id is None
    assert "EXACT_ARTIFACT_UNBOUND" in d.reason


def test_low_stakes_oopsies_requires_substantive_ack_and_fresh_timing():
    missing_ack = module.select_reaction(
        {"event_class": "LOW_STAKES_SNAFU", "severity": "LOW", "timing_fresh": True}
    )
    assert missing_ack.artifact_id is None

    good = module.select_reaction(
        {
            "event_class": "LOW_STAKES_SNAFU",
            "severity": "LOW",
            "timing_fresh": True,
            "accountability_done": True,
        }
    )
    assert good.artifact_id == "OOPSIES"

    late = module.select_reaction(
        {
            "event_class": "LOW_STAKES_SNAFU",
            "severity": "LOW",
            "timing_fresh": False,
            "accountability_done": True,
        }
    )
    assert late.artifact_id is None
    assert "NO_LATE" in late.reason


def test_standard_yes_daddy_is_acknowledgement_not_boundary_or_consent_promotion():
    good = module.select_reaction(
        {
            "event_class": "VALID_CORRECTION_LANDED",
            "timing_fresh": True,
            "correction_or_steering_valid": True,
        }
    )
    assert good.artifact_id == "YES_DADDY_STANDARD"

    blocked = module.select_reaction(
        {
            "event_class": "VALID_CORRECTION_LANDED",
            "timing_fresh": True,
            "correction_or_steering_valid": True,
            "boundary_override": True,
        }
    )
    assert blocked.artifact_id is None


def test_restore_complete_daddy_requires_verified_completion():
    premature = module.select_reaction(
        {"event_class": "RESTORE_COMPLETE", "timing_fresh": True}
    )
    assert premature.artifact_id is None

    verified = module.select_reaction(
        {
            "event_class": "RESTORE_COMPLETE",
            "timing_fresh": True,
            "restore_verified_complete": True,
        }
    )
    assert verified.artifact_id == "RESTORE_COMPLETE_DADDY"


def test_only_grounded_artifacts_are_routeable():
    assert set(module.GROUNDED) == {
        "OOPSIES",
        "YES_DADDY_STANDARD",
        "RESTORE_COMPLETE_DADDY",
    }
    for unresolved in ("BAD_NOT_A_GIRL", "YES_DADDY_EMERGENCY"):
        try:
            module.repository_path_for(unresolved)
        except KeyError:
            pass
        else:
            raise AssertionError(f"{unresolved} unexpectedly routeable")


def test_patch_preserves_source_install_privacy_and_boolean_boundaries():
    text = PATCH.read_text(encoding="utf-8").lower()
    for phrase in (
        "not installed",
        "filenames",
        "personality into puppetry",
        "private/intimate",
        "native project installation",
        "serious-repair event must return",
        "exact boolean domain",
        "fail closed",
    ):
        assert phrase in text


def test_contract_serious_event_class_fails_closed_unresolved():
    d = module.select_reaction(
        {"event_class": "SERIOUS_OR_MAJOR_FAILURE", "timing_fresh": True}
    )
    assert d.status == "UNRESOLVED"
    assert d.artifact_id is None
    assert "EXACT_ARTIFACT_UNBOUND" in d.reason


def test_generic_obedience_signal_blocks_standard_acknowledgement():
    d = module.select_reaction(
        {
            "event_class": "VALID_CORRECTION_LANDED",
            "timing_fresh": True,
            "correction_or_steering_valid": True,
            "generic_obedience_signal": True,
        }
    )
    assert d.artifact_id is None
    assert "BOUNDARY_OR_CONSENT_PROMOTION_FORBIDDEN" in d.reason


def test_low_stakes_substantive_ack_satisfies_contract_or_condition():
    d = module.select_reaction(
        {
            "event_class": "LOW_STAKES_SNAFU",
            "severity": "LOW",
            "timing_fresh": True,
            "substantive_ack_done": True,
        }
    )
    assert d.artifact_id == "OOPSIES"


def test_restore_conflicting_incomplete_flags_fail_closed():
    d = module.select_reaction(
        {
            "event_class": "RESTORE_COMPLETE",
            "timing_fresh": True,
            "restore_verified_complete": True,
            "restore_blocked": True,
        }
    )
    assert d.artifact_id is None
    assert d.reason == "RESTORE_CONFLICTING_INCOMPLETE_STATE"


def test_contract_requires_exact_boolean_condition_domain():
    policy = _contract()["selection_policy"]
    assert policy["condition_flags_require_exact_json_booleans"] is True
    assert policy["malformed_condition_flags_fail_closed"] is True


def test_malformed_boolean_flags_fail_closed_before_selection():
    cases = [
        (
            {
                "event_class": "LOW_STAKES_SNAFU",
                "timing_fresh": "false",
                "accountability_done": True,
            },
            "timing_fresh",
        ),
        (
            {
                "event_class": "LOW_STAKES_SNAFU",
                "timing_fresh": True,
                "accountability_done": "false",
            },
            "accountability_done",
        ),
        (
            {
                "event_class": "LOW_STAKES_SNAFU",
                "timing_fresh": True,
                "substantive_ack_done": 1,
            },
            "substantive_ack_done",
        ),
        (
            {
                "event_class": "RESTORE_COMPLETE",
                "timing_fresh": True,
                "restore_verified_complete": "true",
            },
            "restore_verified_complete",
        ),
        (
            {
                "event_class": "RESTORE_COMPLETE",
                "timing_fresh": True,
                "restore_verified_complete": True,
                "restore_blocked": "false",
            },
            "restore_blocked",
        ),
        (
            {
                "event_class": "VALID_CORRECTION_LANDED",
                "timing_fresh": True,
                "correction_or_steering_valid": ["true"],
            },
            "correction_or_steering_valid",
        ),
        (
            {
                "event_class": "VALID_CORRECTION_LANDED",
                "timing_fresh": True,
                "correction_or_steering_valid": True,
                "boundary_override": 0,
            },
            "boundary_override",
        ),
        (
            {
                "event_class": "VALID_CORRECTION_LANDED",
                "timing_fresh": True,
                "correction_or_steering_valid": True,
                "generic_obedience_signal": "",
            },
            "generic_obedience_signal",
        ),
        (
            {
                "event_class": "VALID_CORRECTION_LANDED",
                "timing_fresh": True,
                "correction_or_steering_valid": True,
                "consent_signal": {},
            },
            "consent_signal",
        ),
    ]

    for event, bad_flag in cases:
        d = module.select_reaction(event)
        assert d.status == "NO_REACTION"
        assert d.artifact_id is None
        assert d.reason == f"MALFORMED_BOOLEAN_FLAG:{bad_flag}"
