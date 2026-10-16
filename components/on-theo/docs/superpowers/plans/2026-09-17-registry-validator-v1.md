# Registry Validator V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an executable validator that enforces the registry/currentness contracts introduced in On-Theo V1 rather than leaving them as prose-only architecture.

**Architecture:** A small Python package loads YAML registries and stacked extensions, applies manifest ordering, collects typed IDs, validates cross-references and review receipts, and returns deterministic structured findings. A CLI wraps the library and exits nonzero on validation errors. Tests use isolated temporary registry fixtures plus one repository-level smoke validation.

**Tech Stack:** Python 3.11+, PyYAML 6.x, pytest 8.x, GitHub Actions.

**Spec:** `docs/REVIEW_PROTOCOL_V2.md`, `registry/extension-manifest.yaml`, `registry/witnesses.yaml`, `registry/reviews.yaml`, `registry/source-access.yaml`.

## Global Constraints

- Validation must never promote draft extension records into canonical repository status; it validates consistency only.
- Duplicate stable IDs are errors unless a future explicit supersession operation is implemented; V1 validator rejects duplicates.
- Unknown cross-references are errors.
- Manifest dependencies must precede dependents in topological/application order and every manifest entry must match the extension file's `extension_id` and `base_registry_head`.
- Review results and execution-provenance values must come from the declared registry vocabularies.
- Witness-specific claim edges may reference a `witness_id` only when that witness exists; a witness must resolve its `witness_of` source.
- Validation output must distinguish errors from warnings and must be deterministic for the same input tree.
- No merge, materialization, or other protected effect is performed by validation.

---

### Task 1: Core validator and failure model

**Files:**
- Create: `tools/on_theo_registry/__init__.py`
- Create: `tools/on_theo_registry/validator.py`
- Test: `tests/test_registry_validator.py`
- Create: `requirements-dev.txt`

**Interfaces:**
- Produces `Finding(code: str, level: str, path: str, message: str)`.
- Produces `ValidationReport(findings: tuple[Finding, ...])` with `errors`, `warnings`, and `ok` properties.
- Produces `validate_repository(root: pathlib.Path) -> ValidationReport`.

- [ ] **Step 1: Write failing tests** for a minimal valid fixture, duplicate IDs, unknown references, manifest extension mismatch, unresolved witness source, and invalid review vocabulary.
- [ ] **Step 2: Run** `pytest -q tests/test_registry_validator.py` and verify failure occurs because `tools.on_theo_registry.validator` does not exist.
- [ ] **Step 3: Implement minimal loader/model and validation rules** needed by those tests. Use `yaml.safe_load`; never execute YAML tags.
- [ ] **Step 4: Run** `pytest -q tests/test_registry_validator.py` and require all tests to pass.
- [ ] **Step 5: Commit** the green core validator.

### Task 2: Repository-stack validation

**Files:**
- Modify: `tools/on_theo_registry/validator.py`
- Modify: `tests/test_registry_validator.py`

**Interfaces:**
- Consumes the Task 1 validator API.
- Adds validation of the actual repository manifest/extension stack without changing materialization state.

- [ ] **Step 1: Add a failing repository-level test** that calls `validate_repository(Path('.'))` and expects no validation errors on the frozen branch state.
- [ ] **Step 2: Run the test and capture the first real contract inconsistency rather than weakening the test.**
- [ ] **Step 3: Extend validator logic or repair genuinely inconsistent draft metadata until the repository-level test passes.**
- [ ] **Step 4: Re-run the full validator test suite.**
- [ ] **Step 5: Commit** repository-stack validation.

### Task 3: CLI and machine-readable output

**Files:**
- Create: `scripts/validate_registry.py`
- Modify: `tests/test_registry_validator.py`

**Interfaces:**
- CLI: `python scripts/validate_registry.py [--root PATH] [--json]`.
- Exit `0` when `report.ok`; exit `1` when errors exist; unexpected runtime failures remain nonzero and visibly distinct.

- [ ] **Step 1: Add failing CLI tests** for success, validation failure, and JSON output shape.
- [ ] **Step 2: Run tests and verify the failures are due to the missing CLI.**
- [ ] **Step 3: Implement the minimal CLI around `validate_repository`.**
- [ ] **Step 4: Run full tests and a direct `python scripts/validate_registry.py --json` smoke invocation.**
- [ ] **Step 5: Commit** CLI support.

### Task 4: Continuous validation

**Files:**
- Create: `.github/workflows/validate-registries.yml`
- Modify: `README.md`

**Interfaces:**
- Workflow runs on pull requests and pushes affecting `registry/**`, `tools/on_theo_registry/**`, `scripts/validate_registry.py`, or validator tests.
- Installs `requirements-dev.txt` and runs `pytest -q` plus the direct validator command.

- [ ] **Step 1: Add a workflow-presence/configuration test or static assertion** that fails before the workflow exists.
- [ ] **Step 2: Verify RED.**
- [ ] **Step 3: Add the workflow and a short README validation section.**
- [ ] **Step 4: Run the full local suite; after push, inspect the exact-head GitHub Actions run rather than assuming workflow success.**
- [ ] **Step 5: Commit** CI/documentation.

## Self-review

Spec coverage: duplicate/collision handling, unresolved references, manifest identity/base/dependency checks, witness/source linkage, review vocabulary/provenance, deterministic findings, CLI exit status, and CI enforcement are all assigned to explicit tasks.

No placeholder implementation steps remain. V1 intentionally does not implement canonical materialization, supersession mutation, git ancestry verification, or automated merge because those would exceed the reviewed contract and protected-effect boundaries.
