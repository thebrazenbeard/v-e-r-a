# Vera Cognition ↔ durable task: source-only Integration L2 gate

**Lane:** L2 Integration + Training (separate chats and source roles).
**Integration owner:** this branch; **Training reviewer:** model-training PR #106 (stacked on #104).
**Base:** V-E-R-A Integration draft PR #3 at db6c1fee06bf011f66b5ba9b490fc2f9e42cbdfb;
stacked on PORTAL runtime PR #1 at 7a9ebf5724dff962f5ffbd994678370c00592835.
**Training subject:** model-training@e1fe1bbe3d530f4db3d31b2009a1c109ce3a52f8.
**Vera Mono source:** PR #76 at dec5c029e51c4fd436435cbda7e02e501822ee85.

## Executable, limited behavior

The read-only integration/cognition_task_gate.py reads an actual current Vera
Mono TaskExecutionLedger task and Training ParticipationReceipt.as_dict().
It checks two attributed participant/claim bindings, claim SHA-256,
distinct logical participants, one task, retained dissent, no-effect ceilings
and semantic transfer boundaries. Its output binds task packet digest,
journal head, exact Training source subject and episode snapshot digest.
Re-verification re-reads the SQLite task chain. Changing task, episode,
source subject, digest or effect flags holds rather than accepting.

Cricket's BLOCK > CHALLENGE > PASS disposition rule must match nested finding
severity. Training PR106 adds CRICKET_BLOCKED/CRICKET_CHALLENGED statuses;
this consumer retains both as HELD_SOURCE_REVIEW, rejects inconsistent status
or disposition, and rejects duplicate globally scoped agent IDs after node
migration. Digest consistency is never independence or effect permission.

## Source qualification and limits

Tests require VERA_MONO_SOURCE_ROOT, PORTAL_SOURCE_ROOT and
VERA_TRAINING_SOURCE_ROOT pointing at independently pinned checkouts.
They reject incorrect Git HEADs and changed source blobs, run actual
Training composition and Vera Mono task ledger methods, restart SQLite,
and invalidate prior bindings after real task-journal advancement.

> Hostile objection: A digest over self-supplied JSON proves its own bytes,
> not authenticated sender, source signer, participant, model, or observation.

> Hostile objection: A task-journal binding is not atomic joint cognition,
> memory, accepted task completion, remote message delivery, or execution.
> Current untrusted receipt is never an authorization or installed runtime.

Integration owns this additional bridge only; Training owns its PR104
cognitive model. Production use, model skill, Training peer review, live host
consumption, schedules, merges and deployment all remain unqualified.

## Exact Training #106 successor compatibility

Training #106 at `e1fe1bbe3d530f4db3d31b2009a1c109ce3a52f8` preserves Cricket BLOCK precedence over
semantic unrepresentability and exposes correlated runtime identity claims.
The consumer retains this BLOCK, forbids a correlated-runtime dissent from
being treated as an independent evidence conflict, and keeps duplicate-runtime
observations HELD without claiming model/agent independence. Its stricter
Cricket disposition/finding consistency guard still rejects a synthetic
BLOCK with no BLOCK-severity finding, unlike Training's current permissive
source fixture; independent upstream review is requested.

## Dissent-field coherence and correlated evidence hold

The exact Training #106 dissent receipt carries `classification`,
`source_digests`, `challenge_for_review`, `accepted_as_fact` and
`independence_proven`. The consumer checks this exact shape and Training's
source enumeration, including that only `EVIDENCE_CONFLICT_FOR_REVIEW`
has a true review challenge flag. It refuses invented states and flag
contradictions, and retains reviewable conflict, mixed claim types, and
correlated evidence as `HELD_SOURCE_REVIEW`. Two distinct runtime IDs do
not cancel a shared evidence-group correlation. This is coherence of
untrusted source receipts, not independent evidence attestation. No claim
can become an accepted task result or effect.

## Upstream Cricket exact-precedence correction

Training PR #106 at `e1fe1bbe3d530f4db3d31b2009a1c109ce3a52f8` now rejects claimed PASS,
CHALLENGE or BLOCK dispositions that disagree with the strongest nested
finding, and uses a real BLOCK finding in its unrepresentable Core fixture.
This closes Integration's upstream challenge #6221273923 at the source
level. The L2 consumer still holds dissent/effect claims and rechecks
the current Vera Mono task journal. Not an installed model or effect grant.

## Bounded current-journal advance falsifier

A real Vera Mono task can advance between `verify_chain()` and
`read(task_id)`. An adversarial test mutates the real SQLite journal
after returning its old first task snapshot. The earlier consumer
returned a no-effect binding for that old head. This source-only guard
now compares two global verified chain cuts and two per-task readbacks,
holding on changed global/task/packet/closed state. **This is bounded
race detection, not SQLite snapshot isolation or compare-and-swap**:
an advance after the last read can still occur. Any future accepted
task-result event must be guarded by the Vera Mono owner's own
transaction and an explicitly authorized compare-and-swap of the
journal head. No authorized task-result transition is added here.

## Semantic plan inventory / newest Training cut

Training `e1fe1bbe3d530f4db3d31b2009a1c109ce3a52f8` requires all missing source capabilities to be
accounted for by exactly one typed rewrite or unresolved capability, and
the fidelity label to equal the worst applied rewrite severity.
Integration independently rejects forged EXACT receipts hiding missing
capabilities, but preserves a well-formed LOSSY source report as
`OBSERVED_UNATTESTED`. This is receipt coherence only, not semantic
equivalence, accepted cognition, resource qualification, identity
authentication, or authority. The bounded journal double-read still
detects some mid-binding races but is not atomic CAS.
