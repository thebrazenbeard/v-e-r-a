# Vera / Volition read-only goal view (isolated prototype)

**Source context, 2026-10-27:** Volition's `OperationalMotivation` already owns
typed persistent wants, admitted observation provenance, Choice/Goal lineage,
replay prevention, protection vetoes, and its own snapshot restoration.
Pre-Active already owns promptless cognition scheduling, state recovery, and
external effect admission. Conations supplies historical evidence **only**;
it cannot establish a present want by itself.

The local V-E-R-A interface on `main` remains response-only. Merely mounting
these components' source branches does not connect them at runtime.

This prototype adds `interface.goal_view` and an **opt-in, read-only**
`GET /api/goals/current` seam. It does **not** invent another durable want
register or write into Volition, Pre-Active, Conations, or a model.

## Host integration contract

The embedding host may call `make_server(goal_provider=..., goal_access_token=...)`
only after it has:

1. Read a live or durably saved Volition `OperationalMotivation` snapshot from a
   **separately authenticated and authorized local source**, not model text.
2. Independently checked its current observation and reappraisal custody,
   restored it using Volition's own `from_snapshot` verifier, and established a
   trusted UTC capture time.
3. Produced a short-lived `vera.volition-view-envelope.v1` projection with the
   exact `VOLITION_OPERATIONAL_MOTIVATION_V1` state and original Choice/Goal
   lineage. It must not assign `SELF_AUTHORED` to model proposals. **The
   current projector deliberately accepts only choices classified
   `MODEL_PROPOSED` with an explicit `model:` source claim.** It rejects
   `SELF_AUTHORED`, `USER_DIRECTED`, and `POLICY_DERIVED` without a separate
   source-authenticated adapter design; those labels in JSON cannot prove
   consent, identity, or origin.
4. Provided a separate private goal-read secret (at least 32 characters). The
   ordinary `/api/session` token is intentionally insufficient and must never
   grant access to private goals.

The view checks schema, capture age (five minutes), choice/goal/want identity,
eligible state, protection latches, bounded scores and explicit
`effect_authority=False`, and returns only a deterministic suggestion to
**review** the goal. It does not let model prose choose endpoint, role, action,
urgency, capability, or side effect. It offers no goal writes or tool calls.
The `model:` prefix is a restrictive consistency check, **not** a signature or
proof of who produced a choice. In particular, neither a claimed `source_ref`
nor a choice-class string permits promotion of model output to self-authored.
Malformed or stale states stay on HOLD; the goal route is absent without both
an explicit provider and private access token.

The goal-view module can reopen an externally persisted snapshot file after
process restart and reject malformed/duplicate JSON, but that file alone is
**not a trustworthy source of current goals**. The caller supplies genuine
observation admission and continuity; SHA hashes or a claimed source reference
do not authenticate reality. Read-only UI projection is not operational
motivation, autonomous scheduling, verified learning, or evidence of agency.

This implementation is isolated in scratch. No production service, GitHub
branch, system daemon, private goal store, or machine action was changed.
