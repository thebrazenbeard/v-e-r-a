# Canonical Typed Appraisal V1

MESO-CRCT now has one reference path for constructing a target's current
`CircuitState` before arbitration.

The appraisal layer composes existing typed mechanisms instead of allowing each
consumer to improvise its own semantic shortcuts.

```text
perceptual input
semantic evidence
current internal needs
target affordances
novelty + learning progress
prediction error
hedonic/protective state
recruitment state
    -> canonical target appraisal
    -> CircuitState
```

## Semantic relevance

Semantic relevance is produced by `assess_semantic_relevance()`.

A source's own assertion that it is important is recorded but does not increase
relevance without a receiving-system relation.

## Epistemic value

The current conservative reference rule derives epistemic value from both
novelty and learning progress.

Surprise without learning can therefore remain perceptually unusual without
receiving unlimited epistemic priority.

## Homeostatic incentive modulation

Current need deficits may modulate incentive salience only when the target has a
matching corrective affordance.

This changes wanting pressure without directly changing pleasure.

## Attentional priority is not accepted as input

The appraisal API deliberately has no `attentional_priority` input.

Attention allocation is downstream of appraisal and arbitration. Callers cannot
preload the result into its own cause through the canonical path.

## Boundary

Appraisal constructs current state. It does not itself:

- select a target;
- write durable memory;
- establish truth or authority;
- assert phenomenology.
