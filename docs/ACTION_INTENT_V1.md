# Non-Executable Action Intent V1

MESO-CRCT carries the causal chain one step beyond directional tendency:

```text
selected target
  -> typed action tendency
  -> non-executable intent proposal
```

Reference intent kinds are `WITHDRAW`, `APPROACH`, `INSPECT`, and `HOLD`.

A minimum committed-strength policy can demote a weak directional tendency to
`HOLD`.

Every `IntentProposal` has:

```text
effect_authorized = false
can_execute = false
```

There is intentionally no method in MESO-CRCT to turn those values on.

This preserves:

```text
salience
  -> motivation
  -> selection
  -> directional tendency
  -> intent proposal
  != permission
  != execution
```

An external host may consume an intent proposal under its own independent
authorization, policy, safety, and effect-control mechanisms. That boundary is
outside this repository's authority.

The layer specifies no actuators, commands, credentials, destinations, or
protected-effect permissions.
