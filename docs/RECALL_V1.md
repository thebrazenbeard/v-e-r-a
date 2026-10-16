# Guarded Association Recall V1

Persistent association strength is not self-activating.

The reference recall path requires both:

1. a current stored association revision;
2. a current constructor-gated transition receipt plus an explicit cue-match
   strength.

```text
stored association
    + current cue event
    -> bounded recall influence
    -> replay ledger
    -> current motivational support
```

A stored association with `cue_match = 0` contributes no current motivation.

## Event-bounded replay

Each `RecallInfluence` binds both the cue receipt and its event ID.

`RecallLedger` allows a cue event to affect a given association once. Reusing
the same event for the same association raises `RecallReplayError`.

A later distinct occurrence of the same cue has a different event identity and
may contribute again.

This prevents a caller from taking one valid old cue and repeatedly refreshing
motivation after transient state would otherwise decay.

## Direction stays separate

Association strength is signed.

Positive strength produces approach support. Negative strength produces learned
avoidance support. Both can make a cue motivationally salient, but learned
negative direction does **not** silently write the system's hazard or protective
avoidance channels.

Likewise recall does not rewrite pleasure.

## Current integration

`apply_recall_motivation()` raises current motivational salience to the recall
support magnitude if that exceeds current motivation. It never lowers stronger
current motivation and does not alter reward/protection state.

The function returns both updated circuit state and updated replay ledger.

This closes the first guarded reference loop:

```text
experience
  -> salience + prediction error
  -> bounded plasticity
  -> versioned association memory
  -> later distinct cue event
  -> guarded one-use recall
  -> current motivational salience
```
