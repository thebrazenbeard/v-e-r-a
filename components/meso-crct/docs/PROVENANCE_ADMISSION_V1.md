# Provenance Admission V1

A source label supplied by a caller is an assertion, not evidence.

The reference runtime now separates:

1. `Provenance` — an unverified source assertion.
2. `ProvenanceVerifier` — an external exact-binding registry.
3. `VerifiedProvenance` — a source/kind/revision tuple accepted by that registry.
4. `TransitionReceipt` — emitted only after verified provenance is supplied.

The exact binding is:

```text
(source_kind, source_id, source_revision)
```

A different source identifier or revision fails verification.

The verifier refuses to register `DIRECT_REGISTER_WRITE` as a trusted source.
Authorized tests can instead receive their own explicit `TEST_STIMULATION`
binding, keeping test effects distinguishable from environmental effects.

The reference registry is intentionally simple. A production host can replace
its verification mechanism, but it should preserve the same semantic boundary:
the producer of a state change must not be the sole authority on where that
change supposedly came from.
