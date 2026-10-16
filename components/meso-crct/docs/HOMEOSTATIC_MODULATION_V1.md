# Homeostatic Modulation V1

MESO-CRCT needs a way for current internal state to change motivation without
rewriting learned value or manufacturing pleasure.

The reference model uses generic named need axes:

```text
need axis:
  setpoint
  current level
  sensitivity
  -> deficit
```

Targets may declare bounded corrective affordances for those needs.

The reference modulation is:

```text
boost = strongest(deficit * corrective_strength)
effective_incentive = base + (1 - base) * boost
```

The strongest matching need is used rather than summing unrelated deficits into
an artificial extreme.

Important semantic boundary:

```text
homeostatic need can increase wanting
    !=
homeostatic need increases pleasure
```

A target that does not address the current deficit receives no homeostatic
boost. A need at or above setpoint also provides no deficit boost.

This is a generic computational mechanism, not a claim that these exact
equations reproduce biological homeostasis.
