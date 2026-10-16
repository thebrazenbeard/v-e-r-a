# Vera Cognition ↔ durable task: source-only Integration L2 gate

**Lane:** L2 Integration + Training (separate chats and source roles).
**Integration owner:** this branch; **Training reviewer:** model-training PR #104.
**Base:** V-E-R-A Integration draft PR #3 at db6c1fee06bf011f66b5ba9b490fc2f9e42cbdfb;
stacked on PORTAL runtime PR #1 at 7a9ebf5724dff962f5ffbd994678370c00592835.
**Training subject:** model-training@a271bf25bdbcd3731ac17588ef475ba1bf74f96f.
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

A Cricket BLOCK stays HELD_SOURCE_REVIEW; a Cricket PASS result containing
a BLOCK-severity finding is rejected. That contradiction was reproduced
against the current actual Training PR104 source; it creates a misleading
coherence label, not an effect grant or proof of malicious behavior.

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
