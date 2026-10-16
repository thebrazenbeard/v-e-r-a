# Vera Cognition ↔ durable task: source-only Integration L2 gate

**Lane:** L2 Integration + Training (separate chats and source roles).
**Integration owner:** this branch; **Training reviewer:** model-training PR #106 (stacked on #104).
**Base:** V-E-R-A Integration draft PR #3 at db6c1fee06bf011f66b5ba9b490fc2f9e42cbdfb;
stacked on PORTAL runtime PR #1 at 7a9ebf5724dff962f5ffbd994678370c00592835.
**Training subject:** model-training@1390fbebbc5d1685a80610796e7ad8c2b955dac1.
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

Training #106 at `1390fbebbc5d1685a80610796e7ad8c2b955dac1` preserves Cricket BLOCK precedence over
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

Training PR #106 at `1390fbebbc5d1685a80610796e7ad8c2b955dac1` now rejects claimed PASS,
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

Training `1390fbebbc5d1685a80610796e7ad8c2b955dac1` requires all missing source capabilities to be
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

Training PR106 `1390fbebbc5d1685a80610796e7ad8c2b955dac1` adds
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
