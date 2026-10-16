# Versioned Association Memory V1

This layer is the first durable owner for MESO-CRCT learning output.

It owns only bounded numeric **association strengths**. It does not accept free
text, autobiographical episodes, identity claims, relationship state, consent,
or other semantic authority.

## Admission path

```text
verified transition
  -> verifier-bound transition receipt
  -> proposal-only plasticity gate
  -> non-zero bounded plasticity candidate
  -> association-memory version check
  -> append-only parent-bound revision
```

Callers cannot directly construct a valid `PlasticityCandidate` through the
public reference API. The candidate must come through `propose_plasticity()`.

A zero-delta candidate is not a learning event and is rejected by durable
memory instead of creating meaningless versions.

## Optimistic versioning

Every association has a monotonically increasing version.

An update must name the current expected version. Stale writers fail instead of
silently overwriting newer learning.

## Parent-bound revision chain

Every revision after version 1 records the prior revision ID. The revision ID is
a deterministic digest over the association, version, strengths, receipt,
operation, and parent revision.

`AssociationMemory` validates this chain whenever a memory snapshot is
constructed. This detects accidental or unsanctioned structural alteration of
the reference history. It is an integrity check, not a cryptographic proof of
who authored a valid-looking snapshot.

## Replay protection

For a given association, a verified transition receipt may contribute at most
one applied persistent update in a memory snapshot.

This prevents replaying the same event against the same association while still
allowing one event to legitimately update more than one distinct association.

## Reversal

`revert_last()` appends a new parent-bound revision returning the association
to its prior strength. It does not delete history.

That makes negative-transfer repair auditable:

```text
bad learned update
  -> review
  -> explicit reversal revision
  -> history preserved
```

## Bounds

Association strengths remain in `[-1, 1]` even under repeated updates.

## Claim ceiling

This module implements versioned learned associations and structural lineage.

It does not establish:
- autobiographical memory;
- permanent personal preference;
- identity;
- belief truth;
- phenomenology.

Those remain distinct admission problems.
