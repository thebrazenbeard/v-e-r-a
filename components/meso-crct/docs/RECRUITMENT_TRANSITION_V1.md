# Recruitment Transition V1

Status: executable synthetic reference mechanism.

MESO-CRCT previously represented recruitment as bounded state but did not define
how typed salience advances that state. This slice adds one deterministic,
auditable transition.

## Inputs

The transition consumes the five upstream appraisal channels:

- perceptual salience
- semantic relevance
- motivational salience
- incentive salience
- epistemic value

It deliberately excludes `attentional_priority` because the canonical appraisal
contract treats attention allocation as downstream of appraisal/arbitration.
Feeding it back into recruitment would create a self-amplifying shortcut.

## Reference transition

For one update:

- activation = strongest upstream driver;
- coherence = weakest/strongest driver ratio;
- persistence = max(repeated activation, retained prior persistence);
- resolution = normalized strongest-vs-second-strongest margin.

A single strong channel can therefore recruit strongly while remaining
cross-channel incoherent. Repeated activation is required to create persistence.
Equal strong drivers can be highly coherent while remaining unresolved as to
which driver dominates.

The strongest-driver label and all intermediate values are retained in the
returned `RecruitmentTransition`.

## Semantic boundaries

This mechanism does not equate or collapse:

```text
recruitment != pleasure
recruitment != truth
recruitment != authority
activation != attentional allocation
persistence != memory truth
resolution != permission
salience != executable intent
```

The transition does not modify reward, protective state, memory, authorization,
or execution state.

## Claim ceiling

The equations are a deterministic synthetic reference policy for testing system
composition. They are not asserted to be a biological model of neural
recruitment, consciousness, subjective experience, pleasure, suffering, or
human motivation.

Passing tests establishes only the implemented invariants and deterministic
behavior of this source slice.
