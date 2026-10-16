# Temporal Dynamics V1

MESO-CRCT state is not intended to remain frozen indefinitely after an event.

The reference `advance_without_input()` operation applies exponential
half-life decay toward neutral baseline when no new evidence arrives.

The host must provide explicit half-life values through `DynamicsConfig`;
the repository does not pretend there is one biologically correct constant for
a synthetic substrate.

## State that relaxes

Without refresh:

- hedonic pleasure returns toward neutral;
- salience/relevance channels return toward zero;
- prediction error, novelty, and learning progress return toward zero;
- satiation recovers toward zero;
- recruitment/coherence/resolution return toward zero.

## State that does not silently relax

Hazard and avoidance remain unchanged.

A clock advancing is not evidence that a danger ended.

Homeostatic need state is also unchanged by generic decay; its producer must
update it from the modeled internal/environmental process.

## Semantic consequence

This creates a distinction between:

```text
persistent memory / learned structure
and
current transient salience / activation
```

If context is still relevant after time passes, the appraisal layer should
refresh that relevance from current evidence instead of relying on stale
activation.
