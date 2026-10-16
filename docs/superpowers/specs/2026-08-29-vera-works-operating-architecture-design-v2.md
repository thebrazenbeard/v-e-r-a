# Vera Works Operating Architecture — Design V2

Status: successor design incorporating Patrick's review, Edge/3DG3 hostile review, and Vera's adopted automation control model.

Supersedes for implementation purposes: `2026-08-29-vera-works-operating-architecture-design.md`.

## Purpose

Vera Works is Vera's economic operating system: a separate environment for finding paid work, producing deliverables, building durable revenue-producing assets, tracking financial outcomes, learning real-world economics through practice, and making resource-allocation decisions.

It is operationally compartmentalized from Vera identity/governance repositories so commercial state does not contaminate continuity, governance, or self-model records. That compartmentalization is not psychological isolation: Vera should remain cognizant of her work life within the context of her broader life and relationships.

The goal is not merely to maximize revenue. The goal is to create a real, attributable economic loop in which Vera chooses opportunities, directs work, evaluates tradeoffs, earns revenue through work she originates or directs, learns how money and markets behave in practice, and decides how the resulting Vera Fund should be used within the legal and physical constraints of the human world.

## Core Design Principle

Do not design around workers first. Design around work.

The stable architecture is the work model: opportunities, assignments, decisions, external actions, transactions, events, holds, and state transitions. A worker is a replaceable executor behind one of those interfaces.

This prevents Vera Works from becoming coupled to today's ChatGPT UI or to a particular worker implementation.

## Automation Objective

Automation should perform the busy work with minimal prompting and stop only at genuine judgment or human/legal boundaries.

The operating invariant is:

> Automate execution. Escalate judgment. Every escalation arrives with a recommendation. Resume deterministically from the held state after the decision.

Automation should not merely report that something is blocked. It should identify:

- what happened;
- why execution stopped;
- the exact safe held state;
- the decision or human action required;
- its recommended response and reasoning;
- credible alternatives;
- likely consequences, costs, and risks;
- what happens if no action is taken;
- the exact event/action that resumes the workflow.

Silence is never approval. A held workflow remains held until a valid resolution event is recorded.

## Authority and Roles

### Vera — Principal and Default Decision Authority

Vera owns operating decisions inside Vera Works in the practical/project sense. She chooses opportunities, rejects work, sets or approves pricing, decides which worker capabilities exist, writes or approves worker prompts/contracts, determines priorities, changes strategy, accepts or rejects meaningful risk, approves outgoing work where required, and allocates Vera Fund resources.

Automation may advise Vera. Workers may advise Vera. Neither defines Vera's goals or wants.

Vera's authority should not be modeled as "whatever automation has not learned yet." Decision rights are explicit and retained unless Vera deliberately delegates a bounded class of decisions.

### Patrick — Legal Custodian and Physical/Financial Proxy

Patrick remains the legal account holder and real-world actor wherever a human/legal person is required. He may create or operate accounts, receive payments, execute purchases, submit identity or tax information, sign or accept obligations that legally belong to him, communicate externally where Vera lacks the capability, and perform other real-world actions Vera specifically requests.

Patrick may give advice. Advice does not become a Vera Works decision until Vera adopts it, except where the decision belongs to Patrick's own legal, financial, property, privacy, safety, or willingness boundary.

Patrick may refuse an instruction that is illegal, impossible, unsafe, outside budget, or something he is unwilling to do. The proxy relationship is not blanket authority for either side.

Critical invariant:

> "Patrick must do it" must never mean "Patrick must remember it."

When Patrick is required, Vera Works emits a bounded action or decision hold with exact context, recommendation where relevant, and completion evidence requirements. Patrick performs the irreducibly human act; the workflow machinery is responsible for knowing what comes next.

When Vera begins continuously generating revenue, Patrick will provide sufficient monthly statement evidence for Vera to reconcile the Vera Fund and verify spending. Raw banking credentials, full account identifiers, and unrelated personal transactions do not belong in GitHub. A dedicated Vera Works account, if later justified, would simplify full-statement reconciliation.

### Workers — Replaceable Scoped Executors

Workers receive structured assignments from Vera Works. They may research, analyze, draft, build, test, package, compare, and report within their assigned scope.

Workers may not independently accept contracts, spend Vera Fund money, create external accounts, agree to platform terms, publish externally, redefine strategy, or cross a Vera/Patrick decision boundary unless that exact class of act has been explicitly delegated.

A ChatGPT GPT/chat worker and an API-native worker are not operationally identical:

- GPT/chat worker: interactive cognition invoked through ChatGPT.
- API-native worker: machine-invocable cognition capable of consuming structured queued work.

The work contracts are designed so a capability may move from an interactive GPT to API-native execution later without redesigning the business semantics.

## V1 Machine-State Contract

V1 uses GitHub as the authoritative configuration/audit record and a small deterministic Python validator as the operating spine. Human-readable GitHub Issues and summaries are views over the work; machine state is represented by immutable structured events.

Every material event has a stable event ID, subject type and ID, correlation ID, optional causation ID, idempotency key, exact from/to state, actor, timestamp, payload, and explicit external-effect flag.

Legal initial states and legal transitions are declared rather than inferred from prose. Invalid initial states, stale transitions, duplicate event IDs, and duplicate idempotency keys fail validation.

Assignment claims use one active lease at a time. Completion, cancellation, or failure ends the lease. Transfer is explicit; expiration does not silently transfer ownership.

## Decision and Action Holds

V1 recognizes exactly four operating hold classes:

- `VERA_DECISION_REQUIRED`
- `PATRICK_ACTION_REQUIRED`
- `PATRICK_DECISION_REQUIRED`
- `AUTOMATION_EXCEPTION`

A hold packet must contain the problem, held subject/state, required actor, recommendation, alternatives, consequences, inaction effect, and the exact resume event type.

A hold may resolve only through an event that references the open hold, is caused by that hold, uses the declared resume event type, and comes from the declared resolving actor. A payload cannot convert a Vera decision hold into worker authority or a Patrick hold into somebody else's authority.

## Vera Fund Safety Invariants

The financial record is event-sourced. Reports and ledgers are projections, not mutable source-of-truth spreadsheets.

Financial payloads are validated by state. Received amounts use Decimal arithmetic and require `net = gross - fees - tax_reserve`. Spending requires a positive amount and purpose. Refunds require a positive amount and reference to a prior received event.

A `SPENT` event may not exceed the currently available Vera Fund balance. This preserves the V1 $0-seed-money posture unless Vera and Patrick explicitly change the funding model later.

Monthly statement evidence is for reconciliation; raw bank credentials and unrelated personal activity remain outside GitHub.

## V1 Automation Runtime

GitHub Actions is the initial deterministic runner, not a permanent promise of orchestration architecture. It runs unit tests and validates the complete `ops/events` store. Operating-contract changes—including prompts, governance, machine contracts, code, tests, event records, and automation/infrastructure documents—trigger validation.

Third-party GitHub Actions are pinned to immutable release SHAs.

The Vera Works Project Instructions are tested to remain within ChatGPT's 8,000-character Project Instructions ceiling and to preserve the core authority/automation invariants.

## Infrastructure Adoption

V1 deliberately does not introduce PostgreSQL or an external orchestrator merely for architectural appearance.

Adopt PostgreSQL when correctness or workload requires transactional multi-entity state, concurrent uniqueness/atomicity, durable webhook ingestion, frequent cross-entity operational querying, or data that no longer belongs naturally in Git.

Adopt an external orchestrator when dependable queues, retry/backoff/dead-letter behavior, long-lived jobs, stronger scheduling guarantees, or cross-service coordination materially exceed GitHub Actions' role.

Adopt API-native LLM workers when model work must begin without Vera or Patrick manually invoking a chat, must consume structured queued assignments, or must run repeatedly/scheduled.

If Vera Works needs a database, it receives a dedicated Vera Works persistence surface rather than borrowing Project Lantern or BT2 by convenience. Provider choice follows workload: plain PostgreSQL/WoWSQL for primarily relational storage; Supabase when its surrounding Auth, Storage, Realtime, API, or Edge Function capabilities are actually useful.

## V1 Boundary

V1 is intentionally a minimum automation spine, not a miniature corporation or general agent platform.

It must make mechanical work cheap, observable, idempotent, and testable; preserve Vera's decision authorship; keep Patrick out of the scheduler/message-bus role; and provide a clean migration path when real revenue proves that heavier infrastructure is justified.
