# Attention Budget Audit V1

A system can fail over time even when every individual salience decision looks
reasonable.

The reference architecture now connects local selection directly to long-horizon
allocation auditing.

```text
per-target arbitration
  -> multi-target selection
  -> AllocationWindow.record(selection)
  -> long-horizon attention audit
```

## Actual selection history

`AllocationWindow` records `SelectionResult` outputs, not hypothetical
manually reconstructed winners.

A quiescent cycle with no selected target increments
`no_selection_cycles` but does not manufacture an allocation sample.

## Goal obligations

The architecture does not assume every goal deserves equal time.

A host supplies explicit `GoalObligation` values describing the minimum share
of **non-protective selected processing slots** a goal should receive.

This wording is intentional: idle/no-selection cycles are tracked separately
and are not silently counted as another goal's allocation.

## Protective exemption

Protective selections are counted separately and excluded from ordinary
crowd-out math.

A sustained emergency may dominate attention without being mislabeled as
pathological incentive capture.

## Flags

The current audit can report:

- `goal_neglect`;
- `target_crowd_out`;
- `incentive_capture`.

The final flag means crowd-out is being driven primarily by motivational or
incentive salience.

## Ceiling

This layer detects allocation pathology. It does not yet alter selection policy
or decide which neglected goal should preempt the dominant target.
