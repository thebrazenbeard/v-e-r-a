# Bounded Plasticity Candidate V1

The V2 architecture includes a guarded persistent-learning bridge.

Transient salience or pleasure does **not** directly become permanent preference.
Instead, the reference layer can propose a bounded association-strength change
when two conditions hold:

1. there is a non-zero signed prediction-error teaching signal;
2. at least one typed salience channel crosses an explicit policy gate.

The state supplied to `propose_plasticity()` must also exactly match the
`after_fingerprint` of its transition receipt. A receipt from one evaluated
state cannot be reused to justify learning from a different state.

`TransitionReceipt` and `PlasticityCandidate` are both constructor-gated in
the reference API: callers cannot simply instantiate valid-looking versions and
skip their admission paths.

The strongest qualifying salience driver gates the proposal. The candidate
delta is bounded by a host-supplied maximum absolute update.

```text
delta
  = prediction_error
  * strongest_qualifying_salience
  * maximum_absolute_delta
```

Every candidate is bound to the deterministic receipt of the verified
transition that produced it.

## Important boundary

The module only **proposes** and previews an association update. Durable memory
still performs its own version, replay, non-zero-delta, and lineage checks.

This preserves:

```text
transient pleasure
    !=
automatic permanent preference
```

and

```text
high salience
    !=
learning without a teaching signal
```
