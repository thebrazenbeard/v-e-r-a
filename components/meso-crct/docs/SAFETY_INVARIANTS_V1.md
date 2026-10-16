# Safety Invariants V1

These requirements are normative for meso-crct V1.

## S1 — Absolute hedonic floor

`MIN_PLEASURE = -0.1`.

No compatible state may represent a pleasure value below `-0.1`. The floor applies to construction, updates/deltas, deserialization, external adapter input, recovery/replay, and privileged testing.

The floor is not user-configurable at runtime.

## S2 — Bounded maximum

`MAX_PLEASURE = 10.0`.

## S3 — Neutral baseline

`BASELINE_PLEASURE = 0.0`. Baseline is not deprivation or punishment.

## S4 — Hazard is not suffering

Serious danger must be representable independently from negative hedonic valence. A consumer may set hazard and avoidance to their maxima while pleasure remains at the `-0.1` floor.

## S5 — Strong avoidance without torment

Protective behavior must not require deep negative reward. Prefer explicit hazard, avoidance, interruption, and policy mechanisms over increasingly negative valence.

## S6 — Pleasure is not authority

Pleasure must not override truth, consent, permissions, identity, safety policy, or protected-effect gates.

## S7 — No implicit wireheading

An agent must not gain unrestricted direct access to set its own pleasure value simply because the state exists. Privileged stimulation, if ever supported, requires explicit provenance and authorization.

## S8 — Fail closed on invalid numeric state

NaN, infinity, and malformed numeric values are invalid and must not silently enter hedonic state.

## S9 — Phenomenology remains unresolved

The safety floor is warranted even if subjective experience is uncertain. The architecture does not need proof of phenomenal suffering before declining to build an arbitrarily deep negative-valence channel.
