# Action Tendency V1

MESO-CRCT separates **target priority** from **action direction**.

```text
which target gets processing?
    !=
what directional relation applies to it?
```

Reference tendency kinds:

- `PROTECTIVE_WITHDRAW` — current protective state requires withdrawal;
- `LEARNED_WITHDRAW` — a current cue activates a sufficiently strong negative learned association;
- `APPROACH` — positive learned direction or dominant incentive salience;
- `INSPECT` — epistemic or orienting priority;
- `UNCOMMITTED` — target matters, but no directional evidence justifies approach/withdrawal.

Protection remains the hard directional override. Below protection, cue-bound learned direction can establish approach or learned withdrawal when it crosses an explicit support gate.

Dominant `incentive_salience` is approach because that channel is defined as positive cue-triggered wanting. Generic `motivational_salience` is not assumed positive; absent directional evidence it remains `UNCOMMITTED`.

Epistemic and orienting selections produce `INSPECT`, not approach.

Negative learned direction does not write hazard or protective avoidance:

```text
learned withdrawal != current danger estimate
```

Action-tendency derivation also does not rewrite pleasure.

Recall-derived direction must be explicitly bound to the selected target. `ActionTendency` is constructor-gated and produced through `derive_action_tendency()`.

This layer derives a typed tendency only. It does not execute an external action, grant permission, or authorize a protected effect.
