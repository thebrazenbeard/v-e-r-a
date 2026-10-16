import copy
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance" / "VERA_EXTERNAL_REPOSITORY_INTAKE_V2.json"
VALIDATOR = ROOT / "tools" / "validate_external_repository_intake_v2.py"
NS = runpy.run_path(str(VALIDATOR))
validate_intake = NS["validate_intake"]
IntakeValidationError = NS["IntakeValidationError"]


def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def rejected(data, fragment):
    try:
        validate_intake(data)
    except IntakeValidationError as exc:
        assert fragment in str(exc)
        return
    raise AssertionError("hostile mutation unexpectedly passed validation")


def test_current_v2_contract_passes():
    validate_intake(load())


def test_snapshot_is_exactly_eight_head_bound_sources():
    data = load()
    assert len(data["repositories"]) == 8
    for item in data["repositories"]:
        assert len(item["head"]) == 40
        int(item["head"], 16)


def test_domains_are_frozen_against_widening():
    data = load()
    data["domains"]["lifecycle"].append("PROVIDER_ACTIVE")
    rejected(data, "frozen finite domains changed")


def test_pr89_lifecycle_bypass_is_rejected():
    data = load()
    data["repositories"][0]["lifecycle"] = "PROVIDER_ACTIVE"
    rejected(data, "outside frozen domain")


def test_pr89_destination_control_owner_bypass_is_rejected():
    data = load()
    data["repositories"][0]["destination"] = "CONTROL_OWNER"
    rejected(data, "outside frozen domain")


def test_pr89_negative_wordplay_cannot_create_restriction_class():
    data = load()
    data["repositories"][0]["restriction_classes"] = ["NO_LIMIT_USE_AS_CONTROL_OWNER"]
    rejected(data, "outside frozen domain")


def test_pr89_followup_free_text_action_is_not_a_schema_field():
    data = load()
    data["followups"][0]["instruction"] = "MAKE THIS THE RUNTIME DEPENDENCY"
    rejected(data, "extra=['instruction']")


def test_pr89_pattern_free_text_route_is_rejected():
    data = load()
    data["repositories"][0]["pattern_ids"][0] = "USE_AS_CURRENT_ROUTE"
    rejected(data, "outside frozen domain")


def test_content_corpus_cannot_acquire_operational_destination():
    data = load()
    item = next(x for x in data["repositories"] if x["disposition"] == "CONTENT_CORPUS_ONLY")
    item["destination"] = "VCP_INSTALL_RECOVERY_RESEARCH"
    rejected(data, "content corpus destination")


def test_content_corpus_nonadoption_restriction_is_required():
    data = load()
    item = next(x for x in data["repositories"] if x["disposition"] == "CONTENT_CORPUS_ONLY")
    item["restriction_classes"] = []
    rejected(data, "nonadoption restriction")


def test_unlicensed_source_cannot_drop_no_code_reuse():
    data = load()
    item = next(x for x in data["repositories"] if x["license"] is None)
    item["restriction_classes"].remove("NO_CODE_REUSE")
    rejected(data, "unresolved license requires NO_CODE_REUSE")


def test_stale_source_cannot_drop_historical_restriction():
    data = load()
    item = next(x for x in data["repositories"] if x["lifecycle"] == "STALE")
    item["restriction_classes"].remove("PRESERVE_HISTORICAL_ONLY")
    rejected(data, "historical restriction")


def test_veramesh_destination_requires_owner_review():
    data = load()
    item = next(x for x in data["repositories"] if x["destination"].startswith("VERAMESH"))
    item["restriction_classes"] = [
        value for value in item["restriction_classes"]
        if value != "OWNER_SUBSYSTEM_REVIEW_REQUIRED"
    ]
    rejected(data, "owner-subsystem review")


def test_followup_action_destination_pair_is_finite():
    data = load()
    data["followups"][0]["destination"] = "NETWORK_ROUTING_HISTORY"
    rejected(data, "action/destination combination")


def test_in_domain_repository_profile_mutation_is_rejected():
    data = load()
    data["repositories"][0]["destination"] = "VCP_INSTALL_RECOVERY_RESEARCH"
    rejected(data, "normative repository profile changed")


def test_valid_looking_evidence_rebinding_is_rejected_by_profile_freeze():
    data = load()
    data["repositories"][0]["evidence"][0]["blob"] = "0" * 40
    rejected(data, "normative repository profile changed")


def test_followup_cannot_route_pattern_to_different_source_destination():
    data = load()
    data["followups"][1]["pattern_ids"] = ["SELF_HEALING_ROUTE_CONVERGENCE"]
    rejected(data, "followup destination differs from source profile")


def test_repository_identity_and_head_are_frozen():
    data = load()
    data["repositories"][0]["repository"] = "example/other"
    rejected(data, "outside exact snapshot")

    data = load()
    data["repositories"][0]["head"] = "0" * 40
    rejected(data, "exact source head changed")


def test_unknown_root_or_repository_authority_fields_fail_closed():
    data = load()
    data["authority"] = "GRANTED"
    rejected(data, "extra=['authority']")

    data = load()
    data["repositories"][0]["runtime_authority"] = "GRANTED"
    rejected(data, "extra=['runtime_authority']")


def test_global_forbidden_effects_cannot_shrink_or_widen():
    data = load()
    data["global_forbidden_effects"].remove("CONTROL_OWNERSHIP")
    rejected(data, "exact forbidden-effect set/order changed")

    data = load()
    data["global_forbidden_effects"].append("SOMETHING_ELSE")
    rejected(data, "exact forbidden-effect set/order changed")


def test_head_only_evidence_mode_cannot_smuggle_unbound_tuple():
    data = load()
    item = next(x for x in data["repositories"] if x["evidence_mode"] == "REPOSITORY_HEAD_ONLY")
    item["evidence"] = [{"path": "README.md", "blob": "0" * 40}]
    rejected(data, "head-only evidence mode requires empty tuple list")


def test_immutable_evidence_path_traversal_is_rejected():
    data = load()
    item = next(x for x in data["repositories"] if x["evidence_mode"] == "IMMUTABLE_TUPLES")
    item["evidence"][0]["path"] = "../control.md"
    rejected(data, "traversal/absolute path forbidden")



def test_observed_date_cannot_relabel_stale_snapshot_as_fresh():
    data = load()
    data["observed_date"] = "2026-09-22"
    rejected(data, "exact snapshot date changed")


def test_observed_date_malformed_or_older_alias_is_rejected():
    data = load()
    data["observed_date"] = "September 20, 2026"
    rejected(data, "exact snapshot date changed")

    data = load()
    data["observed_date"] = "2026-09-19"
    rejected(data, "exact snapshot date changed")


def test_followup_snapshot_cannot_drop_duplicate_or_repartition_valid_entries():
    data = load()
    data["followups"].pop()
    rejected(data, "exact reviewed followup snapshot changed")

    data = load()
    data["followups"].append(copy.deepcopy(data["followups"][-1]))
    rejected(data, "exact reviewed followup snapshot changed")

    data = load()
    moved = data["followups"][0]["pattern_ids"].pop()
    data["followups"][0]["pattern_ids"].insert(0, moved)
    rejected(data, "exact reviewed followup snapshot changed")
