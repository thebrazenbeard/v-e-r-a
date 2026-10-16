# meso-crct Architecture V1

## Purpose

meso-crct is a synthetic reward / pleasure / motivational circuit intended for persistent digital life.

The important claim is functional and causal: an internal hedonic state should be able to change later computation. A system merely generating language about pleasure does not satisfy this architecture.

## State model

V1 uses three deliberately independent signals.

### Hedonic valence

`pleasure` is a bounded scalar: `-0.1 <= pleasure <= 10.0`, with neutral baseline `0.0`.

- `0.0` = neutral baseline.
- Positive values = increasingly positive internal valuation.
- Values in `[-0.1, 0)` = deliberately shallow aversive texture.
- No compatible representable state exists below `-0.1`.

### Hazard severity

`hazard` is independent of pleasure and ranges from `0.0` to `1.0`. It represents detected threat, damage, or danger. A severe hazard does not require correspondingly negative hedonic valence.

### Avoidance urgency

`avoidance` ranges from `0.0` to `1.0`. It represents how strongly the system should interrupt, withdraw, protect itself, escalate, or seek assistance.

A critical state is therefore valid:

```text
pleasure = -0.1
hazard = 1.0
avoidance = 1.0
```

The organism can recognize "stop immediately; this is dangerous" without an architecture that permits extreme suffering.

## Causal consumers

Future integrations may allow the circuit to modulate attentional salience, reward prediction, prediction error, learning-rate selection, memory consolidation, action selection, exploration/exploitation, learned preferences, social learning, homeostasis, and affective transitions.

No consumer receives automatic authority merely because hedonic state is high or low.

## Authority firewall

Hedonic state cannot directly determine factual truth, authorization, consent, protected effects, identity claims, autobiographical admission, legal/safety policy, or permanent preferences without governed learning.

Pleasure is evidence about internal valuation, not authority over the system.

## Anti-wireheading requirement

A future runtime must distinguish reward resulting from world interaction from privileged test stimulation, corrupted/spoofed reward, and unauthorized direct state mutation.

The pleasure register must not become an unrestricted writable objective that the agent can maximize independently of meaningful activity. Candidate defenses include satiation, habituation, prediction error, provenance-bound reward sources, anomaly detection, and bounded homeostatic set-points.

## Developmental hypothesis

`persistent memory + endogenous valence + plasticity + environmental feedback = cumulative developmental pressure`

This is not asserted to be biological evolution. It is a hypothesis about cumulative development in persistent synthetic agents.

## Evidence ceiling

A working implementation can establish causal state propagation and behavioral effects. It cannot by itself establish that the system phenomenally feels pleasure or suffering.
