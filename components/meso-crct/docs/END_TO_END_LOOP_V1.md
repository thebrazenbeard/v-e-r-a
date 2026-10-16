# End-to-End Learned Salience Loop V1

The repository now executes the reference loop across module boundaries:

```text
experience
  -> canonical appraisal
  -> distinct verified event receipt
  -> signed bounded plasticity
  -> versioned association memory
  -> later cue event
  -> guarded recall
  -> current motivational salience
  -> target selection
  -> typed action tendency
```

The integration tests exercise both positive and negative learning.

A negative learned association can make a current cue highly motivational and win target selection while producing `LEARNED_WITHDRAW`, not approach. The same path does not manufacture hazard or negative pleasure.

A positive learned association can produce `APPROACH` under the same general priority machinery.

The tests also demonstrate the key semantic separation directly: two targets/states can have the same selection priority while learned direction produces opposite action tendencies.

This is a deterministic reference loop. It does not execute real-world actions or establish a trained policy.
