# Vera Cognition ↔ durable task: source-only Integration L2 gate

**Lane:** L2 Integration + Training (separate chats and source roles).
**Integration owner:** this branch; **Training reviewer:** model-training PR #106 (stacked on #104).
**Base:** V-E-R-A Integration draft PR #3 at db6c1fee06bf011f66b5ba9b490fc2f9e42cbdfb;
stacked on PORTAL runtime PR #1 at 7a9ebf5724dff962f5ffbd994678370c00592835.
**Training subject:** model-training@06995fd7c43230e1ccc33cab196dcd55ffc363d9.
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

Training #106 at `06995fd7c43230e1ccc33cab196dcd55ffc363d9` preserves Cricket BLOCK precedence over
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

Training PR #106 at `06995fd7c43230e1ccc33cab196dcd55ffc363d9` now rejects claimed PASS,
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

Training `06995fd7c43230e1ccc33cab196dcd55ffc363d9` requires all missing source capabilities to be
accounted for by exactly one typed rewrite or unresolved capability, and
the fidelity label to equal the worst applied rewrite severity.
Integration independently rejects forged EXACT receipts hiding missing
capabilities, but preserves a well-formed LOSSY source report as
`OBSERVED_UNATTESTED`. This is receipt coherence only, not semantic
equivalence, accepted cognition, resource qualification, identity
authentication, or authority. The bounded journal double-read still
detects some mid-binding races but is not atomic CAS.

## VeraOS PR31/32 provenance bridge (read-only, source-level)

The Integration-owned bridge `integration/veraos_evidence_bridge.py` is
a two-source readback classifier, not a runtime or model adapter. It verifies
an Intranel #12 **receiver-local** PR9 comment packet observation/staging
marker and compares two Vera Mono task-journal binding readbacks. It
references exact VeraOS PR32 `5ddac1459c3a7b06f251721a14048fc26e60bda0`
`veraos.native_cognition.admit_local_text_route` and
`execute_text_request` by **name**, without importing or invoking them.
The optional PR32 `virtio_guest_probe` constructs a diagnostic-only
self-declared PASS provider record for dev:virtio-qwen4b, and the bridge
records it as `TEST_ONLY_SELF_DECLARED`, never authenticated model identity
or normal-resident admission. The 2,497,293,803 byte digest-bearing model
inventory remains developer-reported, not a model blob authenticated here.

Synthetic negative tests forge sender authentication, provide incomplete
poll coverage, advance the actual task journal, and attempt to treat
diagnostic PASS as genuine provider qualification or protected effects.
All positive local packet/source/task evidence still produces HOLD:
`origin_authenticated=false`, `provider_authenticated=false`,
`normal_resident_route_admitted=false`, `accepted_as_task_result=false`,
`executed=false`. It is neither a cross-DB atomic transaction nor
end-to-end source authentication. Real installed runtime and QEMU developer
guest proofs belong to their respective exact VeraOS subjects, not this
classifier.

### Private VeraOS source access is separate from public Integration CI

VeraOS is a PRIVATE repository while v-e-r-a is PUBLIC. The first
cross-repo GitHub Actions run failed to fetch the VeraOS checkout
(`Repository not found`, git exit 128) because its public-repository
token cannot read that private dependency. This is a permission
boundary; no private source is copied into v-e-r-a, no credential or
trust grants have been changed, and this limitation is NOT converted
into a "source verified by public CI" claim.

The bridge tests in public GitHub Actions continue to exercise the
actual public Intranel receiver, Training source and Vera Mono SQLite
task state. A separate optional source-API test runs only when an
authorized checkout of VeraOS PR32 is supplied. The exact private Git
head `5ddac1459c3a7b06f251721a14048fc26e60bda0`, module names,
and blob subjects are recorded from read-only GitHub connector evidence
rather than installed/runtime facts. Public CI must report this optional
private-source check as SKIPPED, not silently substitute a fake module.

### L1 identity-collision revocation cross-check

The first `read_comment_packet_evidence` returned locally paired records
even after a later edited comment with the same `message_id` caused an
Intranel `IDENTITY_COLLISION`. A new L1 RED test reproduced this at
`9825a172`. Integration L1 corrects its read transaction at
`fb314b5e30f1ae0279e61e2c821306c3e77199a4` so collided message IDs can no longer yield clean evidence.
The bridge pins this exact receiver blob and includes a real SQLite
collision negative. Independently co-presented receiver-message and
Vera Mono-task evidence do NOT establish a causal message→task identity
link; `message_task_causal_link_attested=false` remains explicit.

## Training development-source cross-check

Training PR106 `06995fd7c43230e1ccc33cab196dcd55ffc363d9` adds
`veraos_development_evidence_v1.py` (Git blob
`3c8495f75e591b489bf6c8f54e85ecee34654c5f`).
The new pinned-source Integration test checks joint node/session/nonce
developer observations and a separate actual Training participation
receipt. A coherent synthetic cut remains `DEVELOPMENT_METADATA_ONLY`
and `HELD_NORMAL_RESIDENT`; a mismatched telemetry nonce becomes
`HELD_SOURCE_PROVENANCE`. Even a claimed provider PASS and matching
reported Ollama digest do not authenticate model bytes, allow normal
resident inference, accept a task, or authorize effects. These tests
do not invoke a model or boot VeraOS.

## New Intranel receiver byte-integrity revocation source

This successor pins Intranel #12 at `58714f5f6561b5e44e42dcdbca67e2cb59bfb87b`, receiver Git blob
`72e88e8d60516ec6655f010f469e936595fe15a6`.
The previous L1 local comment packet readback compared only staged/observed
hash fields, not stored message body/envelope bytes. Exact predecessor
test-only `56a4cc655d740fd23f6533671fbc8cf8ee157fcc` reproduced RED
by editing stored bytes without touching marker/digest columns.
Current L1 `58714f5f6561b5e44e42dcdbca67e2cb59bfb87b` rechecks persisted canonical observation
content and staged envelope in the same local read transaction,
rejecting either mismatch. The L2 bridge now includes a real SQLite
staged-envelope tamper negative. No remote attestation, sender verification,
global snapshot, atomic task acceptance, or route admission results.

## Training PR106 per-component VeraOS source observation freshness

Training's current source `06995fd7c43230e1ccc33cab196dcd55ffc363d9` updates
`veraos_development_evidence_v1.py` to Git blob
`bde78d71972f26c6e896b621fe1cd467d59e55ee`.
Integration now constructs four distinct self-declared
`SourceObservationStamp` fixtures in the source-only compatibility
test and asserts that missing artifact sample, stale telemetry timestamp,
or reused sample ID force `HELD_SOURCE_PROVENANCE`. An otherwise
coherent source tuple remains `DEVELOPMENT_METADATA_ONLY` rather
than normal resident admission. The four local sample labels are
NOT signer attestations, anti-replay protection or raw model artifact
authentication. Training's normal-resident requirements remain
source requirements owned by Training and PORTAL, not an installed grant.

## Actual Mono task → PORTAL advisory → VeraOS native route candidate (NO EFFECT)

`prepare_source_linked_veraos_route` resides inside the **existing**
`integration/veraos_evidence_bridge.py` and uses the **existing**
Vera Mono `TaskExecutionLedger`, Mono
`export_portal_route_request`/`verify_portal_route_assessment`,
PORTAL `assess_vera_task_route`, and V-E-R-A
`vera_portal_runtime.save_receipt`. Nothing is submitted to an
installed resident, no new task database is created, and no model runs.

The source link is a real durable Mono `TASK_OPENED` event whose
`lifecycle_evidence_digest` must match the exact locally paired
Intranel packet `semantic_sha256` recorded in the receiver's SQLite
journal. This is **a declared source link only** and is not a
signature, trusted origin, user acceptance, cross-DB transaction,
or permission. A task opened with an unrelated digest HOLDS.

The task must be OPEN at the exact verified journal head. The adapter
reserves the *existing* Mono SQLite task ledger with `BEGIN IMMEDIATE`
during packet/receipt revalidation, real Mono export, real PORTAL
NO_PROTECTED_EFFECT assessment, and one exclusively-created, fsynced
JSON advisory receipt. All `TaskExecutionLedger.append()` calls also
use `BEGIN IMMEDIATE`; the adversarial same-ledger writer test verifies
a competing real dependency append cannot cross this *source cut*.
This is **NOT an atomic acceptance CAS**: after release, another task
append can invalidate the proposal, and the revalidator holds it.

For PORTAL/normal resident integration the proposed call shape is
`veraos.native_cognition.execute_text_request(admitted,task,request_id,now)`.
The source adapter supplies only `task` from the immutable open task
packet and a deterministic `request_id` derived from the actual
Mono route-request digest and receiver semantic digest. `admitted`
and `now` are NOT supplied; `admit_local_text_route` is NEVER
called here. A syntactically matching caller-provided PORTAL
advertisement yields `ROUTE_PROPOSED_UNATTESTED`; unknown/wrong route
is `HELD_UNQUALIFIED_ROUTE`, never a default or fallback.

The durable receipt includes exact `portal_request`, authenticated-
**NOT** `portal_assessment` (advisory only), source packet/task head,
the **proposed** native call, SHA-256 of canonical receipt, and explicitly
`accepted_as_task_result=false`,
`origin_authenticated=false`,
`normal_resident_route_admitted=false`,
`executed=false`, `protected_effect_authority=false`.
`verify_source_linked_veraos_route` cold rereads and recomputes
it from current real ledgers and refuses stale/tampered/duplicated
changes. Source only, not a retained authoritative model result.

PORTAL handoff needs: externally verified sender/session/nonce,
provider-consistent source cursor, a trusted current model admission
attesting actual artifact and issuer, a **Mono-owner implemented**
expected-head task CAS/acceptance receipt under the same transaction
as the accepted decision, an independently authorized resident
invocation and persisted Pre-Active `event_id/run_id/final_text`
readback bound to that permit. Until then this adapter is a
verifiable no-effect vertical slice and not an accepted task result.

## Training PR106 controlled synthetic model trial source refresh

Training has advanced to `a242df78155ca20b36dbde8cbb7448dad43a5e55` (additive module
`controlled_resident_trial_v1.py` Git blob
`94e2b04063da37e30e7a2c515261d5444a60aa16`). A new
Integration real-source test checks Training's `ACCEPT_SYNTHETIC_DEV_PREFLIGHT`
under a synthetic fixture and explicitly verifies that model identity,
normal-resident admission and effects remain false. The SAME source
assessment under `REAL_HOST_UNATTESTED` remains `HOLD_SOURCE_PREFLIGHT`.
Neither result is an authorized Qwen trial or loaded-model result;
`prepare_source_linked_veraos_route` still generates only a revocable
Mono/PORTAL no-effect proposal.


## Real Pre-Active durable Store / Engine synthetic no-effect result

Integration's existing source-gate suite now checks out the exact Pre-Active
source staged by VeraOS PR31, head 1f23a809d7274df506e03e2d9052525538c3bcf6
(Store Git blob 4612d4c621e01ce4ee69ad5702c4ca37fa7e3402)
as a TEST dependency only. The test uses actual pre_active.Store, Engine,
ContextAssembler, and empty ToolRegistry with a literal in-memory stub
returning SYNTHETIC PRE-ACTIVE RESPONSE ONLY. It consumes the existing
Mono TASK_OPENED -> PORTAL route source proposal and mimics the exact PR31
event/request-id primitives: task.requested, veraos-text:<request_id>,
VERAOS_COGNITION_ROUTE_SELECTED, then bounded Engine.run_once. The actual
Pre-Active SQLite run must be COMPLETED, retain source_event_id/run_id,
survive cold Store reopen and preserve exactly one synthetic stub response.
Duplicate event/request ID does not create a second run, changed task with
same request token is rejected, and a later Vera Mono journal advance
invalidates the original advisory.

NO MODEL, NETWORK, QEMU, GUEST, OS, PROVIDER ADMISSION, OR EFFECT IS INVOKED.
This is NOT an execution of private veraos.native_cognition.execute_text_request.
Private VeraOS source is not copied into public CI; its optional source test
remains a declared SKIP. The stub result is explicitly not a Vera Mono
accepted task, a completed real cognition turn, or canonical memory.
The normal resident can only use a separately authorized admitted route,
Mono-owned expected-head acceptance transaction, and durable
event/run/result readback with identity and current-source checks.

## Canonical Mono task fixture acceptance — journal CAS (source-only)

Actual Vera Mono Draft #76 exact source `d95533abd5dce2fd86d66c0f70790f25f2e10cfd`,
`TaskExecutionLedger.append(expected_head=...)` and
`checkpoint(expected_head=...)`, Git blob
`aa06baf223993850dbaf8cabf44515b6b22720c2`,
compare the expected journal head **inside the canonical
BEGIN IMMEDIATE append transaction**. This is not a second SQLite store,
admission proxy or route resolver. Stale advice loses the CAS to a
competing Mono writer. Replayed IDs with stale heads cannot resurrect
fixture eligibility. Concurrent writers targeting one head permit
at most one checkpoint.

New `checkpoint_source_linked_fixture` in the EXISTING Integration
VeraOS source bridge first revalidates the fsynced source proposal.
It then CAS-appends a canonical `TASK_CHECKPOINT` whose
`lifecycle_evidence_digest` equals the source proposal's SHA-256.
The post-CAS receipt exposes exact task_id, immutable task packet
digest, receiver-local source digest, predecessor journal head, post-CAS
canonical event/head digest, request_id, PORTAL advisory route_id and
literal bounded task. It says fixture_only=true, dispatch_accepted=false,
model_admitted=false, accepted_as_task_result=false, effect_authority=false,
executed=false and requested_effect=NO_PROTECTED_EFFECT.
The source checkpoint records an eligible **synthetic** task fixture,
not a resident's authorization to invoke or accept an inference result.

Because Mono #76 task checkpoint and VeraOS Pre-Active Store are separate
transactions, NO atomic across-database dispatch/result acceptance or
identity signature follows. PORTAL/OS must perform current qualified
model admission with a new exact-head handoff permit under Mono ownership;
its independently authorized resident must record actual Pre-Active
event/run/result and Mono must separately accept a real result by
expected-head transaction. Training synthetic provider status HOLD
cannot become a model admission. No merge, real model or protected effect.

## Local message / Mono task / Pre-Active result correlation: source-only fixture

Added four functions inside the EXISTING integration/veraos_evidence_bridge.py:
open_local_cognition_fixture, accept_local_cognition_fixture,
record_local_cognition_result, read_local_cognition_response.
These are NOT installed in VeraOS, Mono or graphical Cog. No new conversation
database, task ledger, router, scheduler, or actual model endpoint.

Local conversation_id/message_id plus literal bounded text opens one real
Vera Mono TASK_OPENED with deterministic task ID and source digest. Replays
reuse the immutable opening event head, never a later head after checkpoint.
Different text at the same message identity is a collision and must HOLD.
Existing Mono export_portal_route_request, real PORTAL assessment and verifier
remain advisory. Mono checkpoint(expected_head=...) transactionally accepts
only a synthetic no-effect fixture, COGNITION_TURN still gated.

Actual Pre-Active Store/Engine and empty ToolRegistry tests send the exact
Mono task packet subject to a literal in-memory test response. Source readback
checks event dedup identity, event payload, run task/capabilities/status/final
text, route journal and source_event_id -> run_id linkage. A second Mono
expected-head checkpoint records only the result observation digest,
not task closeout, signed output or canonical memory.
Cold readback recomputes both Mono and Pre-Active results for an exact
conversation/message and refuses substituted output, terminal rewrites,
pending/cancelled runs, stale heads and changed dependencies.
The reply is a RESPONSE CANDIDATE: display_authorized=false,
accepted_as_task_result=false, effect_authority=false.

VeraOS PR36 source head 79b2562cb2b30fafae712e64a1d260bcaea2baaf
has only an in-process opt-in Python cognition_request+fixture verifier;
normal PID1 has NO authenticated graphical message intake and its resident
socket is read-only. PORTAL owns actual UI authority, resident provider
admission, and real guest/message result delivery. This source branch
does not invoke PR36, a model, QEMU, or external effects.
Pre-Active terminal low-level rows remain mutable; subsequent readback
detects mismatch but does not establish trusted terminal immutability.
