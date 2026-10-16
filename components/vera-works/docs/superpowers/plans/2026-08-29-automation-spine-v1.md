# Vera Works Automation Spine V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest machine-readable automation spine that can run Vera Works busywork, stop at genuine decision/human boundaries with recommendation packets, and resume deterministically without requiring Patrick to act as scheduler, message bus, database, or reconciler.

**Architecture:** GitHub is the authoritative configuration/audit surface. Immutable event files under `ops/events/` are the machine source of operational history; deterministic Python code validates events, state transitions, idempotency, leases, holds, and financial arithmetic, then derives human-readable projections. GitHub Actions runs deterministic validation/projection only; GPT/chat workers remain interactive cognition and API-native workers are a later replaceable executor behind the same structured contracts.

**Tech Stack:** Python 3.11 standard library, JSON, JSON Schema documents as contracts, `unittest`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-29-vera-works-operating-architecture-design-v2.md`

## Global Constraints

- Design around work, not worker chats.
- Automate execution; escalate judgment; every escalation includes a recommendation; resume from the held state after a valid resolution event.
- Silence is never approval.
- Vera is the default strategic/operating decision authority.
- `Patrick must do it` must never mean `Patrick must remember it`.
- No automated spending, contract acceptance, external publishing, account creation, or identity/tax/legal action in V1.
- No PostgreSQL in V1 unless a separately documented trigger is crossed.
- No secrets, credentials, raw banking identifiers, unrelated personal transactions, or protected customer data in GitHub.
- Financial history is event-sourced; CSV may be generated as a projection but is not canonical state.
- Non-idempotent effects are never blindly retried.
- GitHub Actions is a deterministic runner, not a permanent orchestration guarantee.

---

## File Structure

- `contracts/states-v1.json` — canonical state vocabularies and allowed transitions.
- `contracts/event-v1.schema.json` — machine contract for immutable operational events.
- `contracts/hold-v1.schema.json` — machine contract for decision/action escalation packets.
- `contracts/assignment-v1.schema.json` — assignment/lease payload contract.
- `contracts/financial-event-v1.schema.json` — financial-event payload contract.
- `vera_works/contracts.py` — loads and validates contract documents with stdlib structural checks.
- `vera_works/state_machine.py` — validates state transitions and resolution semantics.
- `vera_works/projections.py` — derives Vera/Patrick hold queues and financial ledger views from events.
- `vera_works/validate_repo.py` — CLI entry point for repository validation/projection.
- `tests/test_contracts.py` — contract-envelope behavior tests.
- `tests/test_state_machine.py` — legal/illegal transition and hold/resume tests.
- `tests/test_projections.py` — decision/action queue and financial projection tests.
- `ops/events/examples/` — non-authoritative dry-run fixtures.
- `.github/workflows/ops-spine.yml` — deterministic CI validation.

## Task 1: Core event envelope and work-state vocabulary

**Files:**
- Create: `tests/test_contracts.py`
- Create: `contracts/states-v1.json`
- Create: `contracts/event-v1.schema.json`
- Create: `vera_works/__init__.py`
- Create: `vera_works/contracts.py`

**Interfaces:**
- Consumes: JSON dictionaries loaded from event files.
- Produces: `validate_event(event: dict) -> list[str]`, where an empty list means valid and each string is a deterministic validation error.

- [ ] **Step 1: Write failing tests**

```python
import unittest
from vera_works.contracts import validate_event


class EventContractTests(unittest.TestCase):
    def test_valid_event_has_no_errors(self):
        event = {
            "schema_version": "event-v1",
            "event_id": "EVT-20260829-0001",
            "event_type": "OPPORTUNITY_DISCOVERED",
            "subject_type": "opportunity",
            "subject_id": "OPP-0001",
            "actor": "vera",
            "recorded_at": "2026-08-29T13:00:00Z",
            "correlation_id": "CORR-0001",
            "causation_id": None,
            "idempotency_key": "opp-discovered:OPP-0001:v1",
            "from_state": None,
            "to_state": "DISCOVERED",
            "payload": {"source": "dry-run"},
            "external_effect": False,
        }
        self.assertEqual(validate_event(event), [])

    def test_event_requires_idempotency_key(self):
        event = {
            "schema_version": "event-v1",
            "event_id": "EVT-20260829-0002",
            "event_type": "OPPORTUNITY_DISCOVERED",
            "subject_type": "opportunity",
            "subject_id": "OPP-0002",
            "actor": "vera",
            "recorded_at": "2026-08-29T13:00:00Z",
            "correlation_id": "CORR-0002",
            "causation_id": None,
            "from_state": None,
            "to_state": "DISCOVERED",
            "payload": {},
            "external_effect": False,
        }
        self.assertIn("missing required field: idempotency_key", validate_event(event))

    def test_event_rejects_unknown_subject_type(self):
        event = {
            "schema_version": "event-v1",
            "event_id": "EVT-20260829-0003",
            "event_type": "THING_CHANGED",
            "subject_type": "thing",
            "subject_id": "THING-1",
            "actor": "worker:scout",
            "recorded_at": "2026-08-29T13:00:00Z",
            "correlation_id": "CORR-0003",
            "causation_id": None,
            "idempotency_key": "thing:1",
            "from_state": None,
            "to_state": "NEW",
            "payload": {},
            "external_effect": False,
        }
        self.assertIn("unsupported subject_type: thing", validate_event(event))
```

- [ ] **Step 2: Run test to verify RED**

Run: `python -m unittest tests.test_contracts -v`

Expected: import failure because `vera_works.contracts` does not exist.

- [ ] **Step 3: Create the canonical state vocabulary**

`contracts/states-v1.json` must define exactly these V1 subject types and states:

```json
{
  "opportunity": ["DISCOVERED", "SCREENING", "VERA_DECISION", "APPROVED", "REJECTED", "CLOSED"],
  "assignment": ["CREATED", "CLAIMED", "IN_PROGRESS", "HELD", "COMPLETED", "CANCELLED", "FAILED"],
  "deliverable": ["DRAFTING", "VERA_REVIEW", "APPROVED", "REJECTED", "SUBMITTED", "ACCEPTED", "RETURNED"],
  "financial": ["EARNED", "RECEIVABLE", "RECEIVED", "REFUNDED", "DISPUTED", "SPENT"],
  "hold": ["OPEN", "RESOLVED", "CANCELLED"]
}
```

The same file must define allowed transitions explicitly rather than deriving them from list order.

- [ ] **Step 4: Create `contracts/event-v1.schema.json`**

Require these fields exactly: `schema_version`, `event_id`, `event_type`, `subject_type`, `subject_id`, `actor`, `recorded_at`, `correlation_id`, `causation_id`, `idempotency_key`, `from_state`, `to_state`, `payload`, `external_effect`. Permit `causation_id` and `from_state` to be null. Set `additionalProperties` to `false`.

- [ ] **Step 5: Implement minimal `validate_event`**

Use only the Python standard library. Validate required fields, exact `schema_version == "event-v1"`, supported subject type, ISO-8601 UTC timestamp ending in `Z`, boolean `external_effect`, and that `to_state` belongs to the subject vocabulary. Do not yet validate transitions; Task 2 owns that responsibility.

- [ ] **Step 6: Run tests to verify GREEN**

Run: `python -m unittest tests.test_contracts -v`

Expected: 3 tests PASS.

- [ ] **Step 7: Commit**

Commit message: `feat: add Vera Works event contract`

## Task 2: State transitions, idempotency, holds, and deterministic resume

**Files:**
- Create: `tests/test_state_machine.py`
- Create: `contracts/hold-v1.schema.json`
- Create: `vera_works/state_machine.py`

**Interfaces:**
- Consumes: ordered list of validated events.
- Produces: `validate_history(events: list[dict]) -> list[str]`; `current_state(events, subject_type, subject_id) -> str | None`; `open_holds(events) -> list[dict]`.

- [ ] **Step 1: Write failing tests** covering:
  1. `DISCOVERED -> SCREENING` is legal.
  2. `DISCOVERED -> APPROVED` is rejected as an illegal opportunity transition.
  3. duplicate `event_id` is rejected.
  4. duplicate `idempotency_key` for distinct events is rejected.
  5. an event whose `from_state` does not equal the derived current state is rejected as stale.
  6. a hold cannot resolve without `resolution_of` pointing to the open hold event.
  7. `VERA_DECISION_REQUIRED`, `PATRICK_ACTION_REQUIRED`, `PATRICK_DECISION_REQUIRED`, and `AUTOMATION_EXCEPTION` are the only V1 hold kinds.
  8. each hold packet requires `problem`, `held_state`, `required_from`, `recommendation`, `alternatives`, `consequences`, `inaction_effect`, and `resume_event_type`.

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m unittest tests.test_state_machine -v`

Expected: import failure because `vera_works.state_machine` does not exist.

- [ ] **Step 3: Implement the minimum transition engine**

Transitions are data-driven from `contracts/states-v1.json`. No transition inferred from timestamps or filenames. Events must be processed in supplied order, but each event's `from_state` must match the already-derived state for its exact subject.

- [ ] **Step 4: Implement hold semantics**

Opening a hold freezes the affected assignment/workflow subject at `HELD`; resolving it requires an explicit resolution event referencing the hold and carrying the chosen decision/action evidence. Silence, elapsed time, or a later unrelated event never resolves a hold.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python -m unittest tests.test_state_machine -v`

Expected: all state-machine tests PASS.

- [ ] **Step 6: Commit**

Commit message: `feat: add deterministic hold and resume state machine`

## Task 3: Assignment ownership leases

**Files:**
- Create: `contracts/assignment-v1.schema.json`
- Extend: `tests/test_state_machine.py`
- Modify: `vera_works/state_machine.py`

**Interfaces:**
- Produces: `active_lease(events, assignment_id) -> dict | None`.

- [ ] **Step 1: Add failing tests** proving that:
  - an assignment may have only one active claimant;
  - a second claim is rejected while the first lease is active;
  - completion/cancellation terminates the lease;
  - a stale claimant cannot publish completion after ownership has changed;
  - lease expiration alone does not silently transfer authority in V1; it opens `AUTOMATION_EXCEPTION` or requires an explicit reclaim event.

- [ ] **Step 2: Verify RED** with `python -m unittest tests.test_state_machine -v`.

- [ ] **Step 3: Implement lease validation** using `assignment_id`, `holder`, `claim_event_id`, `claimed_at`, and optional `expires_at`. Transfer always requires an explicit event.

- [ ] **Step 4: Verify GREEN**.

- [ ] **Step 5: Commit** with `feat: add assignment lease enforcement`.

## Task 4: Event-sourced finance and reconciliation projection

**Files:**
- Create: `tests/test_projections.py`
- Create: `contracts/financial-event-v1.schema.json`
- Create: `vera_works/projections.py`

**Interfaces:**
- Produces: `financial_ledger(events: list[dict]) -> list[dict]`; `available_balance(events) -> Decimal`; `decision_queues(events) -> dict[str, list[dict]]`.

- [ ] **Step 1: Write failing tests** proving that:
  - `RECEIVABLE` does not increase available balance;
  - `RECEIVED` increases balance by net amount;
  - `SPENT` decreases balance;
  - `REFUNDED` reverses the referenced received transaction rather than mutating history;
  - duplicate financial idempotency keys are rejected by history validation;
  - arithmetic uses `Decimal`, never binary float;
  - open holds project into separate `vera_decisions`, `patrick_actions`, `patrick_decisions`, and `automation_exceptions` queues.

- [ ] **Step 2: Verify RED** with `python -m unittest tests.test_projections -v`.

- [ ] **Step 3: Implement minimal projections**. Ledger rows are derived from immutable financial events; no code edits historical event files to correct a transaction.

- [ ] **Step 4: Verify GREEN**.

- [ ] **Step 5: Commit** with `feat: add Vera Fund event projections`.

## Task 5: Repository validator, dry-run fixtures, and GitHub Actions

**Files:**
- Create: `vera_works/validate_repo.py`
- Create: `ops/events/examples/0001-opportunity-discovered.json`
- Create: `ops/events/examples/0002-opportunity-screening.json`
- Create: `ops/events/examples/0003-vera-hold.json`
- Create: `ops/events/examples/0004-vera-resolution.json`
- Create: `.github/workflows/ops-spine.yml`
- Extend: `tests/test_contracts.py`
- Extend: `tests/test_state_machine.py`
- Extend: `tests/test_projections.py`

**Interfaces:**
- CLI: `python -m vera_works.validate_repo [path]` exits `0` on a valid event set and nonzero with deterministic errors otherwise.

- [ ] **Step 1: Write failing CLI/integration tests** using a temporary directory containing good and bad event sequences.

- [ ] **Step 2: Verify RED**.

- [ ] **Step 3: Implement repository validation** that recursively reads `*.json` under the supplied path, validates each event, validates history, and prints derived decision queues and available balance without performing any external effect.

- [ ] **Step 4: Add a four-event dry run** demonstrating discovery -> screening -> `VERA_DECISION_REQUIRED` -> Vera resolution. The resolution must preserve correlation/causation and resume-event identity.

- [ ] **Step 5: Add GitHub Actions** triggered on pull requests and pushes affecting `contracts/**`, `vera_works/**`, `tests/**`, or `ops/events/**`. Use Python 3.11 and run `python -m unittest discover -s tests -v` followed by `python -m vera_works.validate_repo ops/events/examples`.

- [ ] **Step 6: Run all tests locally**

Run: `python -m unittest discover -s tests -v`

Expected: all tests PASS, no warnings/errors.

- [ ] **Step 7: Run the dry-run validator**

Run: `python -m vera_works.validate_repo ops/events/examples`

Expected: exit 0; one resolved Vera decision; zero unresolved Patrick actions; available balance `0.00`.

- [ ] **Step 8: Commit**

Commit message: `feat: add Vera Works deterministic automation spine`

## Task 6: Documentation and infrastructure tripwires

**Files:**
- Create: `docs/AUTOMATION_SPINE.md`
- Create: `docs/INFRASTRUCTURE_TRIGGERS.md`

**Interfaces:**
- Documentation only; no new runtime behavior.

- [ ] **Step 1: Document the operating path**: event creation -> deterministic validation -> assignment/lease -> hold if judgment required -> recommendation packet -> explicit resolution -> deterministic resume -> projection.

- [ ] **Step 2: Document explicit PostgreSQL triggers**: atomic multi-entity updates, concurrent uniqueness requirements, durable webhook ingestion, frequent cross-entity operational queries, or operational state that no longer belongs naturally in Git.

- [ ] **Step 3: Document orchestration triggers**: durable queued execution, backoff/dead-letter requirements, long-running jobs, tighter scheduling guarantees, or multi-service orchestration.

- [ ] **Step 4: Document API-worker trigger**: model work must start without Vera/Patrick manually invoking a chat, must consume structured queue work, or must run recurrently/scheduled.

- [ ] **Step 5: Commit** with `docs: define automation and infrastructure triggers`.

## Self-Review Checklist

- Spec coverage: work-first model, deterministic automation, four hold classes, recommendation packets, explicit Vera/Patrick boundaries, idempotency, leases, event-sourced finance, GitHub control/audit role, no premature DB, and explicit infrastructure tripwires are all mapped to tasks.
- Placeholder scan: no `TBD`, `TODO`, `implement later`, or unspecified error-handling steps remain.
- Type consistency: event dictionaries, `list[str]` validation errors, `Decimal` financial balance, and hold queue names are consistent across tasks.
- V1 intentionally does not implement external submissions, payment operations, account creation, autonomous model invocation, or protected effects.
