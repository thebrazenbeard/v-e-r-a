from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


@dataclass(frozen=True, order=True)
class Finding:
    code: str
    level: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    findings: tuple[Finding, ...]

    @property
    def errors(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.level == "error")

    @property
    def warnings(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.level == "warning")

    @property
    def ok(self) -> bool:
        return not self.errors


class _Validator:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.findings: list[Finding] = []
        self.seen_ids: dict[str, str] = {}
        self.source_ids: set[str] = set()
        self.claim_ids: set[str] = set()
        self.concept_ids: set[str] = set()
        self.witness_ids: set[str] = set()
        self.extensions: list[tuple[dict[str, Any], dict[str, Any], str]] = []
        self.allowed_evidence_classes: set[str] = set()
        self.transmission_relation_types: set[str] = set()
        self.concept_relation_types: set[str] = set()
        self.source_access_states: set[str] = set()
        self.review_required_fields: tuple[str, ...] = ()
        self.witness_required_fields: tuple[str, ...] = ()
        self.concept_required_fields: tuple[str, ...] = ()
        self.extension_ids: set[str] = set()
        self.witness_extension_owner: dict[str, str] = {}

    def finding(self, code: str, path: str, message: str, level: str = "error") -> None:
        self.findings.append(Finding(code=code, level=level, path=path, message=message))

    def load(self, relative: str, *, required: bool = True) -> dict[str, Any]:
        path = self.root / relative
        if not path.exists():
            if required:
                self.finding("MISSING_FILE", relative, "required registry file is missing")
            return {}
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            self.finding("YAML_LOAD_ERROR", relative, str(exc))
            return {}
        if data is None:
            return {}
        if not isinstance(data, dict):
            self.finding("INVALID_YAML_ROOT", relative, "top-level YAML value must be a mapping")
            return {}
        return data

    def register_id(self, entity_id: Any, path: str, kind: str) -> None:
        if not isinstance(entity_id, str) or not entity_id:
            self.finding("MISSING_ID", path, f"{kind} record is missing a non-empty id")
            return
        previous = self.seen_ids.get(entity_id)
        if previous is not None:
            self.finding("DUPLICATE_ID", path, f"stable id {entity_id!r} already declared at {previous}")
            return
        self.seen_ids[entity_id] = path
        if kind == "source":
            self.source_ids.add(entity_id)
        elif kind == "claim":
            self.claim_ids.add(entity_id)
        elif kind == "concept":
            self.concept_ids.add(entity_id)
        elif kind == "witness":
            self.witness_ids.add(entity_id)

    @staticmethod
    def records(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
        value = data.get(key, [])
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    def validate_record_list_shape(self, data: dict[str, Any], key: str, path: str) -> None:
        if key not in data:
            return
        value = data.get(key)
        if not isinstance(value, list):
            self.finding(
                "INVALID_RECORD_LIST",
                f"{path}:{key}",
                f"{key!r} must be a list of mappings",
            )
            return
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                self.finding(
                    "INVALID_RECORD_TYPE",
                    f"{path}:{key}[{index}]",
                    f"{key!r} entries must be mappings, got {type(item).__name__}",
                )

    def register_base_ids(
        self,
        sources: dict[str, Any],
        claims: dict[str, Any],
        concepts: dict[str, Any],
        transmissions: dict[str, Any],
        witnesses: dict[str, Any],
        reviews: dict[str, Any],
    ) -> None:
        for index, item in enumerate(self.records(sources, "sources")):
            self.register_id(item.get("id"), f"registry/sources.yaml:sources[{index}]", "source")
        for index, item in enumerate(self.records(claims, "claims")):
            self.register_id(item.get("id"), f"registry/claims.yaml:claims[{index}]", "claim")
        for index, item in enumerate(self.records(concepts, "concepts")):
            self.register_id(item.get("id"), f"registry/concepts.yaml:concepts[{index}]", "concept")
        for index, item in enumerate(self.records(transmissions, "edges")):
            self.register_id(item.get("id"), f"registry/transmissions.yaml:edges[{index}]", "transmission")
        for index, item in enumerate(self.records(witnesses, "witnesses")):
            self.register_id(item.get("id"), f"registry/witnesses.yaml:witnesses[{index}]", "witness")
        for index, item in enumerate(self.records(reviews, "receipts")):
            self.register_id(item.get("id"), f"registry/reviews.yaml:receipts[{index}]", "review")

    def load_manifest_extensions(self, manifest: dict[str, Any]) -> None:
        entries = self.records(manifest, "extensions")
        positions: dict[str, int] = {}
        manifest_paths: dict[str, str] = {}
        for index, entry in enumerate(entries):
            extension_id = entry.get("extension_id")
            path = f"registry/extension-manifest.yaml:extensions[{index}]"
            if not isinstance(extension_id, str) or not extension_id:
                self.finding("MISSING_EXTENSION_ID", path, "manifest extension entry requires extension_id")
                continue
            if extension_id in positions:
                self.finding("DUPLICATE_EXTENSION_ID", path, f"extension {extension_id!r} is listed more than once")
            else:
                positions[extension_id] = index
                self.extension_ids.add(extension_id)

        for index, entry in enumerate(entries):
            extension_id = entry.get("extension_id")
            path = f"registry/extension-manifest.yaml:extensions[{index}]"
            if not isinstance(extension_id, str) or not extension_id:
                continue
            dependencies = entry.get("depends_on", []) or []
            if not isinstance(dependencies, list):
                self.finding(
                    "INVALID_EXTENSION_DEPENDENCY_LIST",
                    f"{path}:depends_on",
                    "depends_on must be a list of extension IDs",
                )
                dependencies = []
            for dependency_index, dependency in enumerate(dependencies):
                dependency_path = f"{path}:depends_on[{dependency_index}]"
                if not isinstance(dependency, str) or not dependency:
                    self.finding(
                        "INVALID_EXTENSION_DEPENDENCY",
                        dependency_path,
                        f"dependency must be a non-empty string, got {dependency!r}",
                    )
                elif dependency not in positions:
                    self.finding("UNKNOWN_EXTENSION_DEPENDENCY", dependency_path, f"dependency {dependency!r} is not in the manifest")
                elif positions[dependency] >= index:
                    self.finding("MANIFEST_DEPENDENCY_ORDER", dependency_path, f"dependency {dependency!r} must precede {extension_id!r}")

            relative = entry.get("path")
            if not isinstance(relative, str) or not relative:
                self.finding("MISSING_EXTENSION_PATH", path, "manifest extension entry requires path")
                continue
            relative_path = Path(relative)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                self.finding(
                    "INVALID_EXTENSION_PATH",
                    f"{path}:path",
                    f"extension path must stay inside the repository, got {relative!r}",
                )
                continue
            previous_path_owner = manifest_paths.get(relative)
            if previous_path_owner is not None:
                self.finding(
                    "DUPLICATE_EXTENSION_PATH",
                    path,
                    f"extension path {relative!r} is already owned by {previous_path_owner!r}",
                )
            else:
                manifest_paths[relative] = extension_id
            extension = self.load(relative)
            if not extension:
                continue
            for record_key in (
                "source_additions",
                "scholarly_context_additions",
                "claim_additions",
                "concept_additions",
                "witness_additions",
                "transmission_additions",
            ):
                self.validate_record_list_shape(extension, record_key, relative)
            expected_schema = manifest.get("extension_schema_version")
            actual_schema = extension.get("schema_version")
            if isinstance(expected_schema, str) and expected_schema and actual_schema != expected_schema:
                self.finding(
                    "EXTENSION_SCHEMA_VERSION_MISMATCH",
                    relative,
                    f"manifest requires schema {expected_schema!r} but file declares {actual_schema!r}",
                )
            actual_id = extension.get("extension_id")
            if actual_id != extension_id:
                self.finding(
                    "MANIFEST_EXTENSION_ID_MISMATCH",
                    relative,
                    f"manifest declares {extension_id!r} but file declares {actual_id!r}",
                )
            manifest_status = entry.get("status")
            actual_status = extension.get("status")
            if manifest_status != actual_status:
                self.finding(
                    "MANIFEST_EXTENSION_STATUS_MISMATCH",
                    relative,
                    f"manifest status {manifest_status!r} does not match file status {actual_status!r}",
                )
            declared_base = entry.get("declared_base")
            actual_base = extension.get("base_registry_head")
            if declared_base != actual_base:
                self.finding(
                    "MANIFEST_EXTENSION_BASE_MISMATCH",
                    relative,
                    f"manifest base {declared_base!r} does not match file base {actual_base!r}",
                )
            entity_key_by_type = {
                "source": "source_additions",
                "scholarly_context": "scholarly_context_additions",
                "claim": "claim_additions",
                "concept": "concept_additions",
                "witness": "witness_additions",
                "transmission": "transmission_additions",
            }
            declared_type_values = entry.get("adds_entity_types", []) or []
            if not isinstance(declared_type_values, list):
                self.finding(
                    "INVALID_EXTENSION_ENTITY_TYPE_LIST",
                    f"{path}:adds_entity_types",
                    "adds_entity_types must be a list",
                )
                declared_type_values = []
            declared_types: set[str] = set()
            for type_index, item in enumerate(declared_type_values):
                if not isinstance(item, str) or not item:
                    self.finding(
                        "INVALID_EXTENSION_ENTITY_TYPE",
                        f"{path}:adds_entity_types[{type_index}]",
                        f"entity type must be a non-empty string, got {item!r}",
                    )
                else:
                    declared_types.add(item)
            actual_types = {
                entity_type
                for entity_type, key in entity_key_by_type.items()
                if self.records(extension, key)
            }
            if declared_types != actual_types:
                self.finding(
                    "MANIFEST_ENTITY_TYPES_MISMATCH",
                    relative,
                    f"manifest declares {sorted(declared_types)!r} but extension adds {sorted(actual_types)!r}",
                )
            self.extensions.append((entry, extension, relative))

        extension_dir = self.root / "registry/extensions"
        if extension_dir.exists():
            for extension_path in sorted(extension_dir.glob("*.yaml")):
                relative = extension_path.relative_to(self.root).as_posix()
                if relative not in manifest_paths:
                    self.finding(
                        "ORPHAN_EXTENSION_FILE",
                        relative,
                        "extension file exists but is not listed in registry/extension-manifest.yaml",
                    )

    def register_extension_ids(self) -> None:
        key_kinds = (
            ("source_additions", "source"),
            ("scholarly_context_additions", "source"),
            ("claim_additions", "claim"),
            ("concept_additions", "concept"),
            ("witness_additions", "witness"),
            ("transmission_additions", "transmission"),
        )
        for entry, extension, relative in self.extensions:
            extension_id = entry.get("extension_id")
            for key, kind in key_kinds:
                for index, item in enumerate(self.records(extension, key)):
                    entity_id = item.get("id")
                    self.register_id(entity_id, f"{relative}:{key}[{index}]", kind)
                    if (
                        kind == "witness"
                        and isinstance(entity_id, str)
                        and entity_id
                        and isinstance(extension_id, str)
                        and extension_id
                    ):
                        self.witness_extension_owner[entity_id] = extension_id

    def validate_source_reference(self, source_id: Any, path: str, *, required: bool = False) -> None:
        if source_id is None:
            if required:
                self.finding("MISSING_SOURCE_REFERENCE", path, "required source_id is missing")
            return
        if not isinstance(source_id, str) or not source_id:
            self.finding("INVALID_SOURCE_REFERENCE", path, f"source_id must be a non-empty string, got {source_id!r}")
            return
        if source_id not in self.source_ids:
            self.finding("UNKNOWN_SOURCE_REFERENCE", path, f"source_id {source_id!r} does not resolve")

    def validate_witness_reference(self, witness_id: Any, path: str, *, required: bool = False) -> None:
        if witness_id is None:
            if required:
                self.finding("MISSING_WITNESS_REFERENCE", path, "required witness_id is missing")
            return
        if not isinstance(witness_id, str) or not witness_id:
            self.finding("INVALID_WITNESS_REFERENCE", path, f"witness_id must be a non-empty string, got {witness_id!r}")
            return
        if witness_id not in self.witness_ids:
            self.finding("UNKNOWN_WITNESS_REFERENCE", path, f"witness_id {witness_id!r} does not resolve")

    def validate_claims(self, claims: Iterable[tuple[dict[str, Any], str]]) -> None:
        for claim, path in claims:
            evidence_classes = claim.get("evidence_class", []) or []
            if isinstance(evidence_classes, str):
                evidence_classes = [evidence_classes]
            elif not isinstance(evidence_classes, list):
                self.finding(
                    "INVALID_EVIDENCE_CLASS_LIST",
                    f"{path}:evidence_class",
                    "evidence_class must be a string or list of strings",
                )
                evidence_classes = []
            if self.allowed_evidence_classes:
                for index, evidence_class in enumerate(evidence_classes):
                    if not isinstance(evidence_class, str) or not evidence_class:
                        self.finding(
                            "INVALID_EVIDENCE_CLASS",
                            f"{path}:evidence_class[{index}]",
                            f"evidence class must be a non-empty string, got {evidence_class!r}",
                        )
                    elif evidence_class not in self.allowed_evidence_classes:
                        self.finding(
                            "INVALID_EVIDENCE_CLASS",
                            f"{path}:evidence_class[{index}]",
                            f"evidence class {evidence_class!r} is not declared by registry/claims.yaml",
                        )
            for edge_key in ("supporting_sources", "opposing_sources"):
                self.validate_record_list_shape(claim, edge_key, path)
                for index, edge in enumerate(self.records(claim, edge_key)):
                    edge_path = f"{path}:{edge_key}[{index}]"
                    source_id = edge.get("source_id")
                    witness_id = edge.get("witness_id")
                    if source_id is None and witness_id is None:
                        self.finding(
                            "MISSING_CLAIM_EVIDENCE_REFERENCE",
                            edge_path,
                            "claim evidence edge requires source_id or witness_id",
                        )
                    self.validate_source_reference(source_id, f"{edge_path}:source_id")
                    self.validate_witness_reference(witness_id, f"{edge_path}:witness_id")

    def validate_witnesses(self, witnesses: Iterable[tuple[dict[str, Any], str]]) -> None:
        for witness, path in witnesses:
            for field in self.witness_required_fields:
                if field not in witness:
                    self.finding(
                        "MISSING_WITNESS_REQUIRED_FIELD",
                        path,
                        f"witness record is missing required field {field!r}",
                    )
            source_id = witness.get("witness_of")
            if not isinstance(source_id, str) or source_id not in self.source_ids:
                self.finding("UNKNOWN_WITNESS_SOURCE", path, f"witness_of {source_id!r} does not resolve to a source")

    def validate_transmissions(self, edges: Iterable[tuple[dict[str, Any], str]]) -> None:
        for edge, path in edges:
            relation = edge.get("relation")
            if self.transmission_relation_types and relation not in self.transmission_relation_types:
                self.finding(
                    "INVALID_TRANSMISSION_RELATION",
                    f"{path}:relation",
                    f"relation {relation!r} is not declared by registry/transmissions.yaml",
                )
            self.validate_source_reference(edge.get("from_source"), f"{path}:from_source", required=True)
            self.validate_source_reference(edge.get("to_source"), f"{path}:to_source", required=True)
            self.validate_record_list_shape(edge, "evidence", path)
            for index, evidence in enumerate(self.records(edge, "evidence")):
                self.validate_source_reference(
                    evidence.get("source_id"),
                    f"{path}:evidence[{index}]:source_id",
                    required=True,
                )

    def validate_concepts(self, concepts: Iterable[tuple[dict[str, Any], str]]) -> None:
        for concept, path in concepts:
            for field in self.concept_required_fields:
                if field not in concept:
                    self.finding(
                        "MISSING_CONCEPT_REQUIRED_FIELD",
                        path,
                        f"concept record is missing required field {field!r}",
                    )
            linked_claims = concept.get("linked_claims", []) or []
            if not isinstance(linked_claims, list):
                self.finding(
                    "INVALID_LINKED_CLAIMS_LIST",
                    f"{path}:linked_claims",
                    "linked_claims must be a list of claim IDs",
                )
                linked_claims = []
            for claim_index, claim_id in enumerate(linked_claims):
                claim_path = f"{path}:linked_claims[{claim_index}]"
                if not isinstance(claim_id, str) or not claim_id:
                    self.finding("INVALID_CONCEPT_CLAIM_REFERENCE", claim_path, f"claim ID must be a non-empty string, got {claim_id!r}")
                elif claim_id not in self.claim_ids:
                    self.finding("UNKNOWN_CONCEPT_CLAIM", claim_path, f"linked claim {claim_id!r} does not resolve")

            source_refs = concept.get("source_refs", []) or []
            if not isinstance(source_refs, list):
                self.finding(
                    "INVALID_SOURCE_REFS_LIST",
                    f"{path}:source_refs",
                    "source_refs must be a list",
                )
                source_refs = []
            for index, source_ref in enumerate(source_refs):
                source_path = f"{path}:source_refs[{index}]"
                if isinstance(source_ref, str):
                    self.validate_source_reference(source_ref, source_path, required=True)
                elif isinstance(source_ref, dict):
                    self.validate_source_reference(source_ref.get("source_id"), source_path, required=True)
                else:
                    self.finding("INVALID_SOURCE_REFERENCE_RECORD", source_path, f"source reference must be a string or mapping, got {type(source_ref).__name__}")

            self.validate_record_list_shape(concept, "relations", path)
            for index, relation in enumerate(self.records(concept, "relations")):
                relation_path = f"{path}:relations[{index}]"
                relation_type = relation.get("relation")
                if self.concept_relation_types and relation_type not in self.concept_relation_types:
                    self.finding(
                        "INVALID_CONCEPT_RELATION",
                        f"{relation_path}:relation",
                        f"relation {relation_type!r} is not declared by registry/concepts.yaml",
                    )
                relation_source_refs = relation.get("source_refs", []) or []
                if not isinstance(relation_source_refs, list):
                    self.finding(
                        "INVALID_SOURCE_REFS_LIST",
                        f"{relation_path}:source_refs",
                        "source_refs must be a list",
                    )
                    relation_source_refs = []
                for source_index, source_ref in enumerate(relation_source_refs):
                    source_path = f"{relation_path}:source_refs[{source_index}]"
                    if isinstance(source_ref, str):
                        self.validate_source_reference(source_ref, source_path, required=True)
                    elif isinstance(source_ref, dict):
                        self.validate_source_reference(source_ref.get("source_id"), source_path, required=True)
                    else:
                        self.finding("INVALID_SOURCE_REFERENCE_RECORD", source_path, f"source reference must be a string or mapping, got {type(source_ref).__name__}")
                target = relation.get("target_concept_id")
                if not isinstance(target, str) or not target:
                    self.finding(
                        "MISSING_CONCEPT_TARGET",
                        relation_path,
                        "concept relation requires non-empty target_concept_id",
                    )
                elif target not in self.concept_ids:
                    self.finding("UNKNOWN_CONCEPT_TARGET", relation_path, f"target concept {target!r} does not resolve")

    def validate_reviews(self, reviews: dict[str, Any]) -> None:
        allowed = set(reviews.get("allowed_results", []) or [])
        provenance = set(reviews.get("execution_provenance_types", []) or [])
        for index, receipt in enumerate(self.records(reviews, "receipts")):
            path = f"registry/reviews.yaml:receipts[{index}]"
            for field in self.review_required_fields:
                if field not in receipt:
                    self.finding(
                        "MISSING_REVIEW_REQUIRED_FIELD",
                        path,
                        f"review receipt is missing required field {field!r}",
                    )

            repository = receipt.get("repository")
            if not isinstance(repository, str) or "/" not in repository or repository.startswith("/") or repository.endswith("/"):
                self.finding(
                    "INVALID_REVIEW_REPOSITORY",
                    f"{path}:repository",
                    f"repository must be a non-empty owner/name string, got {repository!r}",
                )

            subject_sha = receipt.get("subject_sha")
            if (
                not isinstance(subject_sha, str)
                or len(subject_sha) != 40
                or any(char not in "0123456789abcdef" for char in subject_sha)
            ):
                self.finding(
                    "INVALID_REVIEW_SUBJECT_SHA",
                    f"{path}:subject_sha",
                    f"subject_sha must be a 40-character lowercase hexadecimal commit SHA, got {subject_sha!r}",
                )

            for field in ("review_type", "reviewer_role"):
                value = receipt.get(field)
                if not isinstance(value, str) or not value:
                    self.finding(
                        "INVALID_REVIEW_TEXT_FIELD",
                        f"{path}:{field}",
                        f"{field} must be a non-empty string",
                    )

            reviewed_artifacts = receipt.get("reviewed_artifacts")
            if not isinstance(reviewed_artifacts, list) or not reviewed_artifacts:
                self.finding(
                    "INVALID_REVIEWED_ARTIFACTS",
                    f"{path}:reviewed_artifacts",
                    "reviewed_artifacts must be a non-empty list of exact paths or stable IDs",
                )
            else:
                for artifact_index, artifact in enumerate(reviewed_artifacts):
                    if not isinstance(artifact, str) or not artifact:
                        self.finding(
                            "INVALID_REVIEWED_ARTIFACT",
                            f"{path}:reviewed_artifacts[{artifact_index}]",
                            f"reviewed artifact must be a non-empty string, got {artifact!r}",
                        )

            findings = receipt.get("findings")
            if not isinstance(findings, list):
                self.finding(
                    "INVALID_REVIEW_FINDINGS",
                    f"{path}:findings",
                    "findings must be a list of mappings",
                )
            else:
                for finding_index, finding in enumerate(findings):
                    if not isinstance(finding, dict):
                        self.finding(
                            "INVALID_REVIEW_FINDING",
                            f"{path}:findings[{finding_index}]",
                            f"review finding must be a mapping, got {type(finding).__name__}",
                        )

            if receipt.get("result") not in allowed:
                self.finding("INVALID_REVIEW_RESULT", path, f"result {receipt.get('result')!r} is not declared")
            if receipt.get("execution_provenance") not in provenance:
                self.finding(
                    "INVALID_EXECUTION_PROVENANCE",
                    path,
                    f"execution_provenance {receipt.get('execution_provenance')!r} is not declared",
                )

    def validate_pending_witness_extensions(self, witnesses: dict[str, Any]) -> None:
        pending_ids: set[str] = set()
        for index, record in enumerate(self.records(witnesses, "pending_extension_records")):
            path = f"registry/witnesses.yaml:pending_extension_records[{index}]"
            witness_id = record.get("id")
            declared_in = record.get("declared_in")
            if not isinstance(witness_id, str) or witness_id not in self.witness_ids:
                self.finding(
                    "UNKNOWN_PENDING_WITNESS",
                    path,
                    f"pending witness {witness_id!r} does not resolve to a registered witness",
                )
            else:
                if witness_id in pending_ids:
                    self.finding(
                        "DUPLICATE_PENDING_WITNESS",
                        path,
                        f"pending witness {witness_id!r} is listed more than once",
                    )
                pending_ids.add(witness_id)
                expected_owner = self.witness_extension_owner.get(witness_id)
                if expected_owner is not None and declared_in != expected_owner:
                    self.finding(
                        "PENDING_WITNESS_OWNER_MISMATCH",
                        path,
                        f"declared_in {declared_in!r} does not match owning extension {expected_owner!r}",
                    )
            if not isinstance(declared_in, str) or declared_in not in self.extension_ids:
                self.finding(
                    "UNKNOWN_PENDING_WITNESS_EXTENSION",
                    path,
                    f"declared_in {declared_in!r} does not resolve to a manifest extension",
                )

        if witnesses.get("materialization_state") == "EXTENSIONS_PENDING":
            for witness_id, owner in sorted(self.witness_extension_owner.items()):
                if witness_id not in pending_ids:
                    self.finding(
                        "MISSING_PENDING_WITNESS_INDEX",
                        "registry/witnesses.yaml:pending_extension_records",
                        f"extension witness {witness_id!r} from {owner!r} is not indexed as pending",
                    )

    def validate_source_access(self, source_access: dict[str, Any]) -> None:
        for index, record in enumerate(self.records(source_access, "records")):
            path = f"registry/source-access.yaml:records[{index}]"
            self.validate_source_reference(record.get("source_id"), f"{path}:source_id", required=True)
            state = record.get("state")
            if self.source_access_states and state not in self.source_access_states:
                self.finding(
                    "INVALID_SOURCE_ACCESS_STATE",
                    f"{path}:state",
                    f"state {state!r} is not declared by registry/source-access.yaml",
                )
            direct_access = record.get("direct_access")
            if direct_access is not None and not isinstance(direct_access, bool):
                self.finding(
                    "INVALID_DIRECT_ACCESS_FLAG",
                    f"{path}:direct_access",
                    "direct_access must be a boolean when present",
                )
            preserved_by = record.get("preserved_by", []) or []
            if not isinstance(preserved_by, list):
                self.finding(
                    "INVALID_PRESERVED_BY_LIST",
                    f"{path}:preserved_by",
                    "preserved_by must be a list of source IDs",
                )
                preserved_by = []
            for preserved_index, preserved_source in enumerate(preserved_by):
                self.validate_source_reference(
                    preserved_source,
                    f"{path}:preserved_by[{preserved_index}]",
                    required=True,
                )

    def run(self) -> ValidationReport:
        sources = self.load("registry/sources.yaml")
        claims = self.load("registry/claims.yaml")
        concepts = self.load("registry/concepts.yaml")
        transmissions = self.load("registry/transmissions.yaml")
        witnesses = self.load("registry/witnesses.yaml")
        reviews = self.load("registry/reviews.yaml")
        source_access = self.load("registry/source-access.yaml")
        manifest = self.load("registry/extension-manifest.yaml")

        for document, key, path in (
            (sources, "sources", "registry/sources.yaml"),
            (claims, "claims", "registry/claims.yaml"),
            (concepts, "concepts", "registry/concepts.yaml"),
            (transmissions, "edges", "registry/transmissions.yaml"),
            (witnesses, "witnesses", "registry/witnesses.yaml"),
            (witnesses, "pending_extension_records", "registry/witnesses.yaml"),
            (reviews, "receipts", "registry/reviews.yaml"),
            (source_access, "records", "registry/source-access.yaml"),
            (manifest, "extensions", "registry/extension-manifest.yaml"),
        ):
            self.validate_record_list_shape(document, key, path)

        self.allowed_evidence_classes = set(claims.get("allowed_evidence_classes", []) or [])
        self.transmission_relation_types = set(transmissions.get("relation_types", []) or [])
        self.concept_relation_types = set(concepts.get("relation_types", []) or [])
        access_states = source_access.get("access_states", {}) or {}
        self.source_access_states = set(access_states) if isinstance(access_states, dict) else set()
        required_review_fields = reviews.get("required_fields", []) or []
        self.review_required_fields = tuple(
            field for field in required_review_fields if isinstance(field, str) and field
        )
        required_witness_fields = witnesses.get("required_fields", []) or []
        self.witness_required_fields = tuple(
            field for field in required_witness_fields if isinstance(field, str) and field
        )
        concept_contract = concepts.get("concept_record_contract", {}) or {}
        required_concept_fields = (
            concept_contract.get("required_fields", [])
            if isinstance(concept_contract, dict)
            else []
        ) or []
        self.concept_required_fields = tuple(
            field for field in required_concept_fields if isinstance(field, str) and field
        )

        self.register_base_ids(sources, claims, concepts, transmissions, witnesses, reviews)
        self.load_manifest_extensions(manifest)
        self.register_extension_ids()

        claim_records: list[tuple[dict[str, Any], str]] = [
            (item, f"registry/claims.yaml:claims[{index}]")
            for index, item in enumerate(self.records(claims, "claims"))
        ]
        witness_records: list[tuple[dict[str, Any], str]] = [
            (item, f"registry/witnesses.yaml:witnesses[{index}]")
            for index, item in enumerate(self.records(witnesses, "witnesses"))
        ]
        transmission_records: list[tuple[dict[str, Any], str]] = [
            (item, f"registry/transmissions.yaml:edges[{index}]")
            for index, item in enumerate(self.records(transmissions, "edges"))
        ]
        concept_records: list[tuple[dict[str, Any], str]] = [
            (item, f"registry/concepts.yaml:concepts[{index}]")
            for index, item in enumerate(self.records(concepts, "concepts"))
        ]

        for _, extension, relative in self.extensions:
            claim_records.extend(
                (item, f"{relative}:claim_additions[{index}]")
                for index, item in enumerate(self.records(extension, "claim_additions"))
            )
            witness_records.extend(
                (item, f"{relative}:witness_additions[{index}]")
                for index, item in enumerate(self.records(extension, "witness_additions"))
            )
            transmission_records.extend(
                (item, f"{relative}:transmission_additions[{index}]")
                for index, item in enumerate(self.records(extension, "transmission_additions"))
            )
            concept_records.extend(
                (item, f"{relative}:concept_additions[{index}]")
                for index, item in enumerate(self.records(extension, "concept_additions"))
            )

        self.validate_claims(claim_records)
        self.validate_witnesses(witness_records)
        self.validate_transmissions(transmission_records)
        self.validate_concepts(concept_records)
        self.validate_reviews(reviews)
        self.validate_pending_witness_extensions(witnesses)
        self.validate_source_access(source_access)

        ordered = tuple(sorted(self.findings, key=lambda item: (item.level, item.code, item.path, item.message)))
        return ValidationReport(findings=ordered)


def validate_repository(root: Path) -> ValidationReport:
    return _Validator(Path(root)).run()
