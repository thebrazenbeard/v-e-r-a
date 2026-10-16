# Event Identity V1

MESO-CRCT now separates **what happened** from **which occurrence this was**.

A state fingerprint describes content/state. An event identity describes a
particular occurrence.

Two events may therefore have identical before/after state fingerprints while
still receiving different transition receipts.

## Reference event stream

`EventSequencer` issues immutable `EventIdentity` values containing:

- stream ID;
- monotonically increasing sequence;
- deterministic event ID derived from stream + sequence.

`EventIdentity` is constructor-gated in the reference API.

## Receipt binding

Every transition receipt now binds:

- event identity;
- before/after state fingerprints;
- verified source provenance;
- arbitration/runtime result.

This gives the system two different equalities:

```text
same event + same state/provenance
    -> same deterministic receipt

different event + identical state/provenance
    -> different receipt
```

That distinction matters for learning. Replaying one event should not create
additional learning, but two genuinely separate repeated experiences may each
contribute evidence.

## Trust ceiling

The immutable sequencer is a reference mechanism, not a distributed clock or
tamper-proof hardware counter. A production host must preserve stream
currentness and prevent sequence rollback at its own trust boundary.
