# Closed Allocation Control Loop V1

MESO-CRCT now has a closed reference loop connecting local selection,
long-horizon health, corrective rebalancing, and subsequent history.

```text
current targets
  -> typed local selection
  -> audit recent selected history
  -> protective-safe allocation guard
  -> final selected slot
  -> append to rolling allocation window
  -> re-audit
```

## Rolling selected window

The controller evaluates a bounded recent window of selected slots instead of
lifetime history.

This prevents a long period of old healthy behavior from permanently hiding a
new capture pattern.

Quiescent/no-selection cycles are tracked separately and do not consume the
selected-slot window.

## Corrective behavior

When a relevant goal falls below its explicit non-protective share obligation,
the guard may redirect one slot toward it.

Once the obligation recovers, normal local selection resumes.

The reference tests run this loop repeatedly to verify that correction does not
simply invert the monopoly and suppress the otherwise dominant target forever.

## Protection remains absolute

A protective selection bypasses ordinary rebalancing. Emergency attention is
recorded as protective and excluded from non-protective obligation shares.

## Ceiling

This controller is still deterministic reference machinery. It does not prove
optimal scheduling, strategic robustness, fairness across arbitrary goal
systems, or stability under a learned adversarial policy.
