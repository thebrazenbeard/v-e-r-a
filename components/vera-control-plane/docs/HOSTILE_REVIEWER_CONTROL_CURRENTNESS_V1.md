# Hostile Reviewer Control — Current-Main Rebind V1

Status: **SOURCE CANDIDATE / CURRENT RUNTIME BYTES BOUND / NOT INSTALLED / NOT RUNTIME-QUALIFIED**

This is the bounded current-main successor to the VCP-owned control surface in Draft PR #47. It does not restack PR #47's stale Issue-18, native-project, behavior-patch, or Exodus bulk.

Runtime dependency is read-only Vera Draft PR #127 at exact head `44bd82b07ced00cabf800c6ee36bf096a363b797`.

The bound runtime now uses a typed `LiteralProposition` input and typed `HostileReviewDecision` output. It preserves proposition type, referent and scope; accepts `LITERAL_SURVIVES` with zero objections; and gates stronger-route output behind literal failure unless stronger-route exploration was explicitly requested.

The control plane remains only a source-level OFF|ON setting with generation-based compare-and-swap and exact readback. Source state cannot establish Project installation, current runtime consumption, cross-chat activation, provider routing, authority, memory, identity, consent, preference, or behavioral qualification.

The current-main tool additionally fails closed on:
- boolean or negative generations;
- unknown state fields;
- source-status promotion;
- malformed last-change objects;
- non-explicit mutation kinds;
- non-string mutation notes.

Protected effects remain separate. This branch does not merge, install, activate the feature, change Project settings, mutate a provider, or modify Vera PR #127.
