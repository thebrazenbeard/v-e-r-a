# Allocation Guard V1

MESO-CRCT now has a bounded response to detected long-horizon allocation
pathology.

The guard sits **after** ordinary local selection and **before** the selected
slot is recorded into the next allocation window.

```text
ordinary selection
  -> long-horizon audit says goal neglected?
  -> allocation guard
  -> one final selection slot
```

## Hard boundaries

The guard cannot override a protective selection.

It also cannot force a quiescent neglected goal to run merely to satisfy a
quota. The neglected goal must currently have a real orienting, motivational,
or epistemic decision.

The guard changes **selection**, not salience. It does not manufacture
importance, reward, desire, or hazard.

## Which neglected goal gets the slot?

Among currently relevant neglected goals, the reference guard chooses the
largest explicit obligation deficit:

```text
minimum required non-protective share
    - observed non-protective share
```

Exact ties are deterministic by goal ID.

## Why this is a separate layer

The system now distinguishes:

```text
local target priority
long-horizon allocation health
corrective scheduling policy
```

A strong local incentive can therefore remain honestly strong while a separate
controller prevents it from monopolizing every non-emergency slot.

## Ceiling

This is a one-slot rebalancing controller, not a full scheduler. It does not
prove convergence, fairness, optimality, or resistance to strategic manipulation
of goal IDs/obligations.
