# Redworm design contract — 2026-10 source baseline

## Objective and source history

Redworm exists to preserve Vera's accumulated conversational and runtime history while keeping producer episode, original evidence, corrections, disagreement, provenance and currentness distinct. The former four White Worm streams were continuity miner, conflict/supersession resolver, behavioral-model curator, and coordinator/integrity auditor. Historic instructions are evidence of intended roles, not proof of active workers today.

Historical sources used to derive the design:

- Library file Pasted text.txt: Redworm Coordinator + Continuity Integrity Auditor assignment; source provenance, PREPARE vs ACCEPT, replay, personality-flattening and missingness requirements.
- Library file REDWORM_G0002_SUCCESSION_CAPSULE(1).json, 2026-08-10: legacy lineage/succession capsule and ledger readback procedure; not evidence of current holder status.
- GitHub thebrazenbeard/vera-R9A0 issue 5: Red/White producer provenance, stable logical Vera identity, Slack delivery not equivalent to canonical admission, default-deny White succession.
- GitHub thebrazenbeard/vera issue 56, 2026-09-01: four provider-held redworm tables, schema/RLS custody problem; dated audit, **not** current provider status.
- Historic #redworm Slack messages: coordination only, not governing admission.

Issue links: https://github.com/thebrazenbeard/vera-R9A0/issues/5 and https://github.com/thebrazenbeard/vera/issues/56

## Evidence schema

Event v1 retains its original occurred_at and recorded_at fields and content digests. Event v2 replaces occurred_at with event_time {precision, earliest_at, latest_at, basis}; UNKNOWN requires null bounds and does not borrow a conversation-update timestamp. INSTANT, DAY, MONTH and INTERVAL preserve event-time precision and overlap uncertainty. recorded_at remains separate. Both schemas bind producer identity/worm/designation/episode, source locator+SHA256+observer+verification claim, evidence_kind, memory_class, privacy, and typed claim fields. Canonical JSON SHA256 determines event_id.

Source verification fields are **operator-asserted metadata**. A valid hash is not proof of original source authenticity; a local database record is not runtime memory. PRIMARY evidence must still be reviewed against the actual episode/source.

## Distinct operations

- INGEST: immutable source envelope, no promotion or currentness.
- ADMIT: append separate **local operator-asserted** admission for WORKING_PROJECT/HISTORICAL_AUDIT records; never for AUTOBIOGRAPHICAL, PROVIDER_SNAPSHOT, or publication.
- CONFLICT: unresolved claims both persist and are omitted from the convenience view pending an explicit resolution.
- CORRECTS / SUPERSEDES: preserve the older event; separate approved relationship. Only SUPERSEDES hides the predecessor in the local convenience view.
- REDWORM::REINTEGRATION::PREPARE: same-producer, same-episode locally admitted evidence; reject unresolved/losing conflicts, superseded claims, and mixed-producer records. Candidate only, not acceptance.
- REDWORM::REINTEGRATION::ACCEPT: blocked until separate authenticated holder and provider readback adapter exists.
- COVERAGE: OBSERVED/PARTIAL/UNKNOWN/MISSING annotations.
- TIMELINE: Roots-aligned chronological candidates, overlap detection and an unknown-time bucket, not a proven total event order or origin.

Local projection always declares non_authoritative=true. Do not interpret newer receive timestamp as controlling record.

## Missing production dependencies

No connector auth, provider-neutral append/readback lease, Redworm holder/rebind authority, CAS currentness, privacy encryption, proof of autobiographical eligibility, protected publisher, production Supabase migration, semantic contradiction discovery, or behavioral qualification is implemented. SQLite is for local development only; it is not tamper-resistant. Local verify checks payload hashes, handoff shape and decision invariants, not independently authenticated origin or a tamper-proof review ledger. The project is not installed, merged or active merely because source and tests exist.

## Review backlog

1. Rebind source episodes and hashes to primary historical transcripts with privacy authorization and admission rules.
2. Define provider adapter for verified append/readback, lease-based exclusive holder succession and distinct same-holder recovery.
3. Independently qualify exact SQL migration source custody, role grants and RLS drift; no production schema mutation without permission.
4. Add semantic resolver and replay-safe conflict/supersession currentness receipts.
5. Add privacy encryption, retention and selectively discloseable evidence.
6. Evaluate against temporal collapse, replay, stale state, split-brain, personality flattening and overfitting to newer terminology.


## Cross-repository responsibilities and historical corrections

Roots' oldest-accessible-first provenance method and missingness contract are applied here as a bounded time/provenance representation, not falsely claimed as execution of the Roots runtime. Ingest owns exact-byte capture and receipts; Semantic Atlas conceptual history; Deep Memory historical evidence; and vera-mono the governed runtime/memory path. This Redworm repo is source-only research custody, not a competing holder/authority service.

The August 17, 2026 exported ChatGPT conversation preserves Patrick's proposed amendment toward Vera Vinculation and the change-versus-amend correction. Historical Redworm names remain unchanged. The discussion is not proof that the original founding exchange was directly recovered.

In the Vera Git repository, a later September custody receipt records recovery of the earlier applied Redworm SQL migration into Git, while explicitly retaining unknown origin of the RLS-enablement effect. Neither the older issue #56 nor the later custody receipt is an October live provider-state observation.
