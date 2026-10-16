# Appraised Experience Transaction V1

The reference architecture now has one auditable path from a canonical current
appraisal into an evaluated event and optional durable association learning.

```text
canonical AppraisedTarget
  + verified source provenance
  + distinct EventIdentity
  + prior CircuitState
    -> TransitionReceipt
    -> optional receipt-bound PlasticityCandidate
    -> optimistic-versioned AssociationMemory revision
```

## Canonical appraisal admission

`AppraisedTarget` is constructor-gated. It is produced through
`build_target_appraisal()`, preventing callers from labeling an arbitrary
manually assembled state as a canonical appraisal.

## Learning remains optional

An experience may produce a receipt without producing durable learning.

When a learning directive exists, the transaction:

1. proposes plasticity from the exact receipt-bound after-state;
2. leaves memory unchanged when the teaching signal produces a zero delta;
3. otherwise requires the caller's expected association version;
4. applies one append-only parent-bound memory revision.

## Repeated experience versus replay

Distinct event identities let two otherwise identical experiences each
contribute learning.

Reusing the **same** event produces the same receipt and is rejected by
association replay protection if used to apply the same learning again.

## Pleasure boundary

Maximum pleasure with no teaching signal still produces no durable association
update.

The transaction therefore preserves:

```text
experienced positive hedonic state
    !=
automatic permanent preference
```

## Ceiling

This transaction owns evaluated event lineage and numeric association learning.
It still does not create autobiographical memory, belief truth, identity,
consent, or phenomenal claims.
