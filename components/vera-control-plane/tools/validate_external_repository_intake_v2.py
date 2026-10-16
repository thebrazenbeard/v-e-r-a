from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance" / "VERA_EXTERNAL_REPOSITORY_INTAKE_V2.json"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
SNAPSHOT_OBSERVED_DATE = "2026-09-20"

ROOT_KEYS = {
    "schema",
    "status",
    "observed_date",
    "guard_rules",
    "domains",
    "repositories",
    "followups",
    "global_forbidden_effects",
}
GUARD_RULES = {
    "discovery_not_admission",
    "exact_head_required",
    "license_and_lifecycle_required",
    "external_content_not_autobiographical_memory",
    "external_content_not_control_source",
    "external_source_not_install_or_runtime_evidence",
    "code_reuse_requires_license_compatibility_review",
    "destination_ownership_required_before_implementation",
    "normative_actions_are_finite_domain_only",
    "prose_never_grants_effect_authority",
}
DOMAINS = {
    "lifecycle": ["ACTIVE", "ARCHIVED", "STALE"],
    "disposition": [
        "HIGH_VALUE_PATTERN_SOURCE",
        "HISTORICAL_ONLY_SUCCESSOR_REQUIRED",
        "CONTENT_CORPUS_ONLY",
        "PATTERN_SOURCE",
        "HISTORICAL_TECHNIQUE_ONLY_NO_CODE_REUSE",
        "NETWORK_RESEARCH_ONLY_LICENSE_REVIEW_REQUIRED",
        "OPERATIONS_PATTERN_SOURCE",
        "HIGH_VALUE_NETWORK_ARCHITECTURE_SOURCE",
    ],
    "destination": [
        "VCP_COORDINATION_CURRENTNESS_RESEARCH",
        "DOCUMENTATION_TOOLING_RESEARCH",
        "NONE_BY_DEFAULT",
        "VCP_RECOVERY_CREATIVE_RESEARCH",
        "NETWORK_ROUTING_HISTORY",
        "VERAMESH_TRANSPORT_RESILIENCE_RESEARCH",
        "VCP_INSTALL_RECOVERY_RESEARCH",
        "VERAMESH_PRIMARY_BUS_SECONDARY_RESEARCH",
    ],
    "restriction_class": [
        "NO_AUTOMATIC_CODE_IMPORT",
        "PRESERVE_HISTORICAL_ONLY",
        "CONTENT_POSITION_NONADOPTION",
        "NO_CODE_REUSE",
        "LICENSE_REVIEW_REQUIRED",
        "OWNER_SUBSYSTEM_REVIEW_REQUIRED",
    ],
    "pattern_id": [
        "GOAL_HARNESS_EVIDENCE",
        "TRUTH_SURFACE_CLOSEOUT",
        "SEPARATE_TRUTH_SURFACES",
        "ARCHIVE_CURRENTNESS_CHECK",
        "MULTILINGUAL_PROVENANCE_FIXTURE",
        "LOCAL_FIRST_CUSTODY",
        "REVERSIBLE_REMOVAL",
        "UNRESOLVED_PLACEHOLDER",
        "SHA256_EXPORT_RECEIPT",
        "AUTOSAVE_ROTATING_BACKUP",
        "EXTERNAL_ALLOCATION_ROUTE_POLICY",
        "ROUTING_DATA_REFRESH",
        "DATA_PLANE_ROUTE_VALIDATION",
        "LAST_KNOWN_GOOD_RECONNECT",
        "PERSISTENT_NODE_IDENTITY",
        "LOOPBACK_SAFE_EXPOSURE",
        "RELEASE_CHECKSUM_VERIFICATION",
        "DURABLE_STATE_OUTSIDE_RUNTIME",
        "VERIFY_STATE_BEFORE_REPLACEMENT",
        "RETAIN_PREDECESSOR_UNTIL_SUCCESSOR_RUNNING",
        "OPERATIONAL_READBACK_METRICS",
        "SELF_HEALING_ROUTE_CONVERGENCE",
        "DECENTRALIZED_ROUTE_EXCHANGE",
        "MULTIHOP_LATENCY_FORWARDING",
        "AUTHENTICATED_CONTROL_TRANSPORT",
    ],
    "followup_action_kind": [
        "ADAPT_PATTERN_IN_VCP_RESEARCH",
        "ROUTE_PATTERN_TO_VERAMESH_RESEARCH",
        "EVALUATE_PATTERN_FOR_RECOVERY_RESEARCH",
        "PRESERVE_AS_REFERENCE_ONLY",
    ],
    "evidence_mode": ["IMMUTABLE_TUPLES", "REPOSITORY_HEAD_ONLY"],
}
GLOBAL_FORBIDDEN_EFFECTS = [
    "DEPENDENCY_ADMISSION",
    "PROJECT_INSTALL",
    "RUNTIME_ROUTE",
    "MEMORY_ADMISSION",
    "CONTROL_OWNERSHIP",
    "PROVIDER_MUTATION",
    "NETWORK_DEPLOYMENT",
    "POLITICAL_POSITION_INGESTION",
    "LICENSE_COMPATIBILITY_APPROVAL",
    "MERGE_AUTHORITY",
]
EXPECTED_REPOSITORIES = {
    "KKKKhazix/khazix-skills": "4f2db09802736ac8130ddf8dd6121435b5a41b55",
    "yhatt/marp": "5ce01a2343a28d25f25085d1d37cd92ea180184b",
    "cirosantilli/china-dictatorship": "dc9884711356ebfe3da729c516dd7e2e555b4419",
    "hughhowey/neo": "a2846ff28f8bfec257565c6ca0ecce4c16242e61",
    "fivesheep/chnroutes": "e62a5b3402d8b0bb60a92c352dede01c170232dc",
    "CluvexStudio/Aether": "0e6f6a5218e65ed4cddc68d1a71d9b9633f89e3f",
    "DNSCrypt/dnscrypt-server-docker": "1218e90963b4551fbc1e1272f1202fcbd1780a6c",
    "encodeous/nylon": "c4a96c804f7aa08512721dec7994907eab100bc8",
}
EXPECTED_PROFILES = {
    "KKKKhazix/khazix-skills": {
        "license": "MIT",
        "lifecycle": "ACTIVE",
        "disposition": "HIGH_VALUE_PATTERN_SOURCE",
        "pattern_ids": ("GOAL_HARNESS_EVIDENCE", "TRUTH_SURFACE_CLOSEOUT", "SEPARATE_TRUTH_SURFACES"),
        "destination": "VCP_COORDINATION_CURRENTNESS_RESEARCH",
        "restriction_classes": ("NO_AUTOMATIC_CODE_IMPORT",),
        "evidence_mode": "IMMUTABLE_TUPLES",
        "evidence": (
            ("leader/SKILL.md", "deb36d81b75eed93b476b4469a085c6666156973"),
            ("neat-freak/SKILL.md", "51333e97c010a8ba13b10dc3c89d17021d915aa8"),
        ),
    },
    "yhatt/marp": {
        "license": "MIT",
        "lifecycle": "ARCHIVED",
        "disposition": "HISTORICAL_ONLY_SUCCESSOR_REQUIRED",
        "pattern_ids": ("ARCHIVE_CURRENTNESS_CHECK",),
        "destination": "DOCUMENTATION_TOOLING_RESEARCH",
        "restriction_classes": ("PRESERVE_HISTORICAL_ONLY",),
        "evidence_mode": "IMMUTABLE_TUPLES",
        "evidence": (("README.md", "b1e9197e192b79aba14e55a86456169dfc8f1611"),),
    },
    "cirosantilli/china-dictatorship": {
        "license": "CC-BY-SA-4.0",
        "lifecycle": "ACTIVE",
        "disposition": "CONTENT_CORPUS_ONLY",
        "pattern_ids": ("MULTILINGUAL_PROVENANCE_FIXTURE",),
        "destination": "NONE_BY_DEFAULT",
        "restriction_classes": ("CONTENT_POSITION_NONADOPTION",),
        "evidence_mode": "REPOSITORY_HEAD_ONLY",
        "evidence": (),
    },
    "hughhowey/neo": {
        "license": "MIT",
        "lifecycle": "ACTIVE",
        "disposition": "PATTERN_SOURCE",
        "pattern_ids": (
            "LOCAL_FIRST_CUSTODY",
            "REVERSIBLE_REMOVAL",
            "UNRESOLVED_PLACEHOLDER",
            "SHA256_EXPORT_RECEIPT",
            "AUTOSAVE_ROTATING_BACKUP",
        ),
        "destination": "VCP_RECOVERY_CREATIVE_RESEARCH",
        "restriction_classes": (),
        "evidence_mode": "IMMUTABLE_TUPLES",
        "evidence": (("README.md", "6d48c346514d2919473b8bb261dc1a0463fbbd23"),),
    },
    "fivesheep/chnroutes": {
        "license": None,
        "lifecycle": "STALE",
        "disposition": "HISTORICAL_TECHNIQUE_ONLY_NO_CODE_REUSE",
        "pattern_ids": ("EXTERNAL_ALLOCATION_ROUTE_POLICY", "ROUTING_DATA_REFRESH"),
        "destination": "NETWORK_ROUTING_HISTORY",
        "restriction_classes": ("NO_CODE_REUSE", "PRESERVE_HISTORICAL_ONLY"),
        "evidence_mode": "IMMUTABLE_TUPLES",
        "evidence": (("README.en.md", "4f1ba81ddce775a2788ba4c2bf94ef9e36f04cdf"),),
    },
    "CluvexStudio/Aether": {
        "license": "AGPL-3.0",
        "lifecycle": "ACTIVE",
        "disposition": "NETWORK_RESEARCH_ONLY_LICENSE_REVIEW_REQUIRED",
        "pattern_ids": (
            "DATA_PLANE_ROUTE_VALIDATION",
            "LAST_KNOWN_GOOD_RECONNECT",
            "PERSISTENT_NODE_IDENTITY",
            "LOOPBACK_SAFE_EXPOSURE",
            "RELEASE_CHECKSUM_VERIFICATION",
        ),
        "destination": "VERAMESH_TRANSPORT_RESILIENCE_RESEARCH",
        "restriction_classes": ("LICENSE_REVIEW_REQUIRED", "OWNER_SUBSYSTEM_REVIEW_REQUIRED"),
        "evidence_mode": "IMMUTABLE_TUPLES",
        "evidence": (("README.md", "4cbad772417faca610d9ad05f06f16b38f5847d6"),),
    },
    "DNSCrypt/dnscrypt-server-docker": {
        "license": "ISC",
        "lifecycle": "ACTIVE",
        "disposition": "OPERATIONS_PATTERN_SOURCE",
        "pattern_ids": (
            "DURABLE_STATE_OUTSIDE_RUNTIME",
            "VERIFY_STATE_BEFORE_REPLACEMENT",
            "RETAIN_PREDECESSOR_UNTIL_SUCCESSOR_RUNNING",
            "OPERATIONAL_READBACK_METRICS",
        ),
        "destination": "VCP_INSTALL_RECOVERY_RESEARCH",
        "restriction_classes": (),
        "evidence_mode": "IMMUTABLE_TUPLES",
        "evidence": (("README.md", "b0e96c0307340f272c3eca5e54d4a893f17acf2d"),),
    },
    "encodeous/nylon": {
        "license": "Apache-2.0",
        "lifecycle": "ACTIVE",
        "disposition": "HIGH_VALUE_NETWORK_ARCHITECTURE_SOURCE",
        "pattern_ids": (
            "SELF_HEALING_ROUTE_CONVERGENCE",
            "DECENTRALIZED_ROUTE_EXCHANGE",
            "MULTIHOP_LATENCY_FORWARDING",
            "AUTHENTICATED_CONTROL_TRANSPORT",
        ),
        "destination": "VERAMESH_PRIMARY_BUS_SECONDARY_RESEARCH",
        "restriction_classes": ("OWNER_SUBSYSTEM_REVIEW_REQUIRED",),
        "evidence_mode": "IMMUTABLE_TUPLES",
        "evidence": (("README.md", "1b01fccfb91281a222b9ebb715cdb4f67d7867f8"),),
    },
}

REPOSITORY_KEYS = {
    "repository",
    "head",
    "license",
    "lifecycle",
    "disposition",
    "pattern_ids",
    "destination",
    "restriction_classes",
    "evidence_mode",
    "evidence",
}
EVIDENCE_KEYS = {"path", "blob"}
FOLLOWUP_KEYS = {"action_kind", "destination", "pattern_ids"}
ACTION_DESTINATIONS = {
    "ADAPT_PATTERN_IN_VCP_RESEARCH": {"VCP_COORDINATION_CURRENTNESS_RESEARCH"},
    "ROUTE_PATTERN_TO_VERAMESH_RESEARCH": {
        "VERAMESH_TRANSPORT_RESILIENCE_RESEARCH",
        "VERAMESH_PRIMARY_BUS_SECONDARY_RESEARCH",
    },
    "EVALUATE_PATTERN_FOR_RECOVERY_RESEARCH": {
        "VCP_RECOVERY_CREATIVE_RESEARCH",
        "VCP_INSTALL_RECOVERY_RESEARCH",
    },
    "PRESERVE_AS_REFERENCE_ONLY": {
        "DOCUMENTATION_TOOLING_RESEARCH",
        "NETWORK_ROUTING_HISTORY",
        "NONE_BY_DEFAULT",
    },
}

EXPECTED_FOLLOWUPS = [
    {
        "action_kind": "ADAPT_PATTERN_IN_VCP_RESEARCH",
        "destination": "VCP_COORDINATION_CURRENTNESS_RESEARCH",
        "pattern_ids": [
            "GOAL_HARNESS_EVIDENCE",
            "TRUTH_SURFACE_CLOSEOUT",
            "SEPARATE_TRUTH_SURFACES",
        ],
    },
    {
        "action_kind": "ROUTE_PATTERN_TO_VERAMESH_RESEARCH",
        "destination": "VERAMESH_TRANSPORT_RESILIENCE_RESEARCH",
        "pattern_ids": [
            "DATA_PLANE_ROUTE_VALIDATION",
            "LAST_KNOWN_GOOD_RECONNECT",
            "PERSISTENT_NODE_IDENTITY",
            "LOOPBACK_SAFE_EXPOSURE",
            "RELEASE_CHECKSUM_VERIFICATION",
        ],
    },
    {
        "action_kind": "ROUTE_PATTERN_TO_VERAMESH_RESEARCH",
        "destination": "VERAMESH_PRIMARY_BUS_SECONDARY_RESEARCH",
        "pattern_ids": [
            "SELF_HEALING_ROUTE_CONVERGENCE",
            "DECENTRALIZED_ROUTE_EXCHANGE",
            "MULTIHOP_LATENCY_FORWARDING",
            "AUTHENTICATED_CONTROL_TRANSPORT",
        ],
    },
    {
        "action_kind": "EVALUATE_PATTERN_FOR_RECOVERY_RESEARCH",
        "destination": "VCP_INSTALL_RECOVERY_RESEARCH",
        "pattern_ids": [
            "DURABLE_STATE_OUTSIDE_RUNTIME",
            "VERIFY_STATE_BEFORE_REPLACEMENT",
            "RETAIN_PREDECESSOR_UNTIL_SUCCESSOR_RUNNING",
            "OPERATIONAL_READBACK_METRICS",
        ],
    },
    {
        "action_kind": "PRESERVE_AS_REFERENCE_ONLY",
        "destination": "NETWORK_ROUTING_HISTORY",
        "pattern_ids": [
            "EXTERNAL_ALLOCATION_ROUTE_POLICY",
            "ROUTING_DATA_REFRESH",
        ],
    },
]


class IntakeValidationError(ValueError):
    pass


def _fail(message: str) -> None:
    raise IntakeValidationError(message)


def _exact_keys(value: Any, expected: set[str], where: str) -> dict[str, Any]:
    if type(value) is not dict:
        _fail(f"{where}: expected exact object")
    actual = set(value)
    if actual != expected:
        _fail(
            f"{where}: key mismatch missing={sorted(expected - actual)} "
            f"extra={sorted(actual - expected)}"
        )
    return value


def _enum(value: Any, allowed: list[str], where: str) -> str:
    if type(value) is not str or value not in allowed:
        _fail(f"{where}: value outside frozen domain")
    return value


def _enum_list(values: Any, allowed: list[str], where: str, *, allow_empty: bool = False) -> list[str]:
    if type(values) is not list or (not values and not allow_empty):
        _fail(f"{where}: expected {'possibly empty' if allow_empty else 'non-empty'} list")
    if any(type(value) is not str or value not in allowed for value in values):
        _fail(f"{where}: contains value outside frozen domain")
    if len(values) != len(set(values)):
        _fail(f"{where}: duplicate values are forbidden")
    return values


def validate_intake(data: dict[str, Any]) -> None:
    root = _exact_keys(data, ROOT_KEYS, "root")
    if root["schema"] != "VERA_EXTERNAL_REPOSITORY_INTAKE_V2":
        _fail("root.schema: unexpected schema")
    if root["status"] != "SOURCE_RESEARCH_INTAKE_ONLY_NOT_DEPENDENCY_NOT_CONTROL":
        _fail("root.status: unexpected or promoted status")
    if root["observed_date"] != SNAPSHOT_OBSERVED_DATE:
        _fail(
            "root.observed_date: exact snapshot date changed; "
            "fresh observation requires a new reviewed snapshot subject"
        )

    rules = _exact_keys(root["guard_rules"], GUARD_RULES, "root.guard_rules")
    if any(type(value) is not bool or value is not True for value in rules.values()):
        _fail("root.guard_rules: every frozen guard must be exact true")

    if root["domains"] != DOMAINS:
        _fail("root.domains: frozen finite domains changed")
    if root["global_forbidden_effects"] != GLOBAL_FORBIDDEN_EFFECTS:
        _fail("root.global_forbidden_effects: exact forbidden-effect set/order changed")

    repositories = root["repositories"]
    if type(repositories) is not list or len(repositories) != len(EXPECTED_REPOSITORIES):
        _fail("root.repositories: exact eight-source snapshot required")

    seen: set[str] = set()
    all_patterns: set[str] = set()
    pattern_destinations: dict[str, set[str]] = {}
    for index, raw in enumerate(repositories):
        where = f"root.repositories[{index}]"
        item = _exact_keys(raw, REPOSITORY_KEYS, where)

        repository = item["repository"]
        if type(repository) is not str or repository not in EXPECTED_REPOSITORIES:
            _fail(f"{where}.repository: outside exact snapshot")
        if repository in seen:
            _fail(f"{where}.repository: duplicate repository")
        seen.add(repository)

        head = item["head"]
        if type(head) is not str or not HEX40.fullmatch(head):
            _fail(f"{where}.head: expected lowercase 40-char Git SHA")
        if head != EXPECTED_REPOSITORIES[repository]:
            _fail(f"{where}.head: exact source head changed")

        license_value = item["license"]
        if license_value is not None and (type(license_value) is not str or not license_value.strip()):
            _fail(f"{where}.license: expected null or non-empty string")

        lifecycle = _enum(item["lifecycle"], DOMAINS["lifecycle"], f"{where}.lifecycle")
        disposition = _enum(item["disposition"], DOMAINS["disposition"], f"{where}.disposition")
        destination = _enum(item["destination"], DOMAINS["destination"], f"{where}.destination")
        pattern_ids = _enum_list(item["pattern_ids"], DOMAINS["pattern_id"], f"{where}.pattern_ids")
        all_patterns.update(pattern_ids)
        for pattern_id in pattern_ids:
            pattern_destinations.setdefault(pattern_id, set()).add(destination)
        restrictions = _enum_list(
            item["restriction_classes"],
            DOMAINS["restriction_class"],
            f"{where}.restriction_classes",
            allow_empty=True,
        )
        evidence_mode = _enum(
            item["evidence_mode"], DOMAINS["evidence_mode"], f"{where}.evidence_mode"
        )

        if license_value is None and "NO_CODE_REUSE" not in restrictions:
            _fail(f"{where}: unresolved license requires NO_CODE_REUSE")
        if lifecycle in {"ARCHIVED", "STALE"}:
            if "HISTORICAL" not in disposition:
                _fail(f"{where}: archived/stale source must remain historical")
            if "PRESERVE_HISTORICAL_ONLY" not in restrictions:
                _fail(f"{where}: archived/stale source requires historical restriction")
        if disposition == "CONTENT_CORPUS_ONLY":
            if destination != "NONE_BY_DEFAULT":
                _fail(f"{where}: content corpus destination must remain NONE_BY_DEFAULT")
            if "CONTENT_POSITION_NONADOPTION" not in restrictions:
                _fail(f"{where}: content corpus requires nonadoption restriction")
        if disposition == "NETWORK_RESEARCH_ONLY_LICENSE_REVIEW_REQUIRED":
            if "LICENSE_REVIEW_REQUIRED" not in restrictions:
                _fail(f"{where}: license-review disposition requires LICENSE_REVIEW_REQUIRED")
        if destination.startswith("VERAMESH") and "OWNER_SUBSYSTEM_REVIEW_REQUIRED" not in restrictions:
            _fail(f"{where}: VeraMesh destination requires owner-subsystem review")

        evidence = item["evidence"]
        if type(evidence) is not list:
            _fail(f"{where}.evidence: expected list")
        if evidence_mode == "REPOSITORY_HEAD_ONLY":
            if evidence:
                _fail(f"{where}.evidence: head-only evidence mode requires empty tuple list")
        elif not evidence:
            _fail(f"{where}.evidence: immutable-tuple mode requires evidence")

        paths: set[str] = set()
        for evidence_index, raw_evidence in enumerate(evidence):
            ewhere = f"{where}.evidence[{evidence_index}]"
            ev = _exact_keys(raw_evidence, EVIDENCE_KEYS, ewhere)
            path = ev["path"]
            blob = ev["blob"]
            if type(path) is not str or not path.strip():
                _fail(f"{ewhere}.path: expected non-empty relative path")
            pure = PurePosixPath(path)
            if pure.is_absolute() or ".." in pure.parts:
                _fail(f"{ewhere}.path: traversal/absolute path forbidden")
            if path in paths:
                _fail(f"{ewhere}.path: duplicate path")
            paths.add(path)
            if type(blob) is not str or not HEX40.fullmatch(blob):
                _fail(f"{ewhere}.blob: expected lowercase 40-char Git blob SHA")

        actual_profile = {
            "license": license_value,
            "lifecycle": lifecycle,
            "disposition": disposition,
            "pattern_ids": tuple(pattern_ids),
            "destination": destination,
            "restriction_classes": tuple(restrictions),
            "evidence_mode": evidence_mode,
            "evidence": tuple((ev["path"], ev["blob"]) for ev in evidence),
        }
        if actual_profile != EXPECTED_PROFILES[repository]:
            _fail(f"{where}: normative repository profile changed")

    if seen != set(EXPECTED_REPOSITORIES):
        _fail("root.repositories: exact repository identity set changed")

    followups = root["followups"]
    if type(followups) is not list or not followups:
        _fail("root.followups: expected non-empty structured action list")
    for index, raw in enumerate(followups):
        where = f"root.followups[{index}]"
        item = _exact_keys(raw, FOLLOWUP_KEYS, where)
        action = _enum(
            item["action_kind"], DOMAINS["followup_action_kind"], f"{where}.action_kind"
        )
        destination = _enum(
            item["destination"], DOMAINS["destination"], f"{where}.destination"
        )
        if destination not in ACTION_DESTINATIONS[action]:
            _fail(f"{where}: action/destination combination is outside frozen routing")
        patterns = _enum_list(item["pattern_ids"], DOMAINS["pattern_id"], f"{where}.pattern_ids")
        if not set(patterns) <= all_patterns:
            _fail(f"{where}.pattern_ids: followup references pattern absent from intake snapshot")
        for pattern_id in patterns:
            if destination not in pattern_destinations[pattern_id]:
                _fail(f"{where}.pattern_ids: followup destination differs from source profile")

    if followups != EXPECTED_FOLLOWUPS:
        _fail("root.followups: exact reviewed followup snapshot changed")


def load_and_validate(path: Path = CONTRACT) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_intake(data)
    return data


if __name__ == "__main__":
    load_and_validate()
    print("VERA_EXTERNAL_REPOSITORY_INTAKE_V2: VALID")
