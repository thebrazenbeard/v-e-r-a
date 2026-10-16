# Multi-Target Selection V1

MESO-CRCT arbitration evaluates one target at a time. Selection answers the next
question: **which target receives the current selection slot?**

The reference selector still refuses a global weighted utility scalar.

## Hard protective override

Any target in `PROTECTIVE` mode competes only with other protective targets.
A protective target cannot be displaced by a pleasurable, motivational,
epistemic, or merely conspicuous target.

Among simultaneous protective targets, higher protective priority wins; exact
ties use target ID only for deterministic execution.

## Explicit non-protective policy

Motivational, epistemic, and orienting targets are semantically different. Their
cross-mode precedence is therefore represented as visible `SelectionPolicy`,
not as hidden numeric weights.

The default reference order is:

```text
MOTIVATIONAL
  > EPISTEMIC
  > ORIENTING
```

That order is a reference policy, not a biological claim. A host can supply a
different complete order.

Within the same mode, higher typed arbitration priority wins. Exact ties are
deterministic by target ID.

## Quiescence

If every candidate is quiescent, the selector returns no target rather than
inventing an action merely because candidates exist.

## Boundary with long-horizon allocation

This selector is deliberately local. It does not erase the separate
attention-budget audit.

A target can legitimately win several local selections and still later be
flagged for long-horizon crowd-out or incentive capture.

That separation preserves:

```text
locally justified priority
    !=
globally healthy allocation over time
```
