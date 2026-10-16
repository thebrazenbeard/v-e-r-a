# Canonical Decision Cycle V1

The current decision path is composed by `run_decision_cycle()`.

```text
canonical appraised targets
  + current cue-bound recalls
  + memory/review snapshots that authorized those recalls
  + prior recall ledger
  + rolling allocation-control state
    -> verify recall belongs to current appraised state
    -> resolve same-event recall direction
    -> apply recall motivational support
    -> multi-target selection
    -> long-horizon allocation guard
    -> final selected target
    -> typed action tendency
    -> non-executable intent proposal
    -> updated recall/control state
```

Durable learning is intentionally **not** performed in this cycle. New learning
belongs to the separate appraised-experience transaction.

## Recall/current-state binding

Each `RecallInfluence` carries the after-state fingerprint of the cue receipt
that produced it.

Before applying recall, the decision cycle requires that fingerprint to match
the current canonical appraised state for that target.

An old valid recall cannot therefore be attached to a different current
appraisal merely because the target ID is convenient.

The binding also carries the current `AssociationMemory` snapshot. Before
applying a precomputed recall, the cycle verifies that:

- the influence still names the current learned revision;
- that revision is not quarantined or review-stale;
- the influence's review-record ID still matches the current review record.

A recall computed before quarantine/release or before a later learning revision
is therefore rejected as stale rather than being allowed to bypass the newer
memory governance state.

## Replay state

The cycle carries `RecallLedger` forward. Reusing the same cue event against
the same association in a later cycle fails instead of refreshing motivation
again.

## Allocation state

The cycle also carries the rolling `ControlState`, so long-horizon capture
detection and corrective selection use actual prior final selections.

## Output boundary

The final output is an `IntentProposal`, which remains non-executable and
unauthorized.

The decision cycle has no actuator/effect API.
