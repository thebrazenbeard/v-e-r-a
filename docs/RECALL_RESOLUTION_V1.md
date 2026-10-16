# Multi-Recall Resolution V1

A current target may activate more than one learned association. MESO-CRCT does
not allow caller ordering or simple summation to decide direction.

`resolve_recall_influences()` requires all influences in one resolution to
come from the same cue event.

For each direction it keeps the **strongest** support rather than summing every
memory:

```text
approach_support = max(all approach supports)
avoid_support = max(all learned-avoid supports)
```

This prevents many individually weak memories from manufacturing an extreme
direction merely by count.

The reference disposition is one of:

- `APPROACH`
- `AVOID`
- `CONFLICT`
- `NEUTRAL`

When both directions clear the minimum support gate and remain within the
configured conflict margin, the result is `CONFLICT` rather than an arbitrary
tie-break.

Action tendency preserves that conflict as `UNCOMMITTED`. It does not force a
direction simply because the target itself remains highly motivational.

Recall influences from different cue event IDs cannot be combined as if they
described one current moment.
