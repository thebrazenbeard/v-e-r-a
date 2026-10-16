# Review Action Proposal V1

Evidence classification and review mutation are separate steps.

```text
evidence
  -> exact-revision assessment
  -> non-mutating review proposal
  -> separately governed memory mutation
```

`propose_review_action()` emits one of:

- `QUARANTINE`
- `RELEASE`
- `HOLD`

Reference mapping:

- `CONTRADICTED` or `SUSPECTED_OVERGENERALIZATION` -> propose quarantine unless already quarantined;
- `CLEAR` -> propose release only when currently quarantined;
- `INSUFFICIENT` -> hold.

A proposal never changes `AssociationMemory`.

Every `ReviewActionProposal` has:

```text
mutation_authorized = false
can_mutate = false
```

The actual mutation still requires `quarantine_association()` or
`release_association()` with the exact evidence assessment.

This mirrors the larger MESO-CRCT authority boundary:

```text
evidence conclusion != permission != effect
```


## Proposal currentness

Each proposal also snapshots the exact review-evidence ledger fingerprint and
current review disposition used to derive it.

`validate_review_action_proposal()` rejects a proposal if, before action:

- the learned association revision changes;
- the evidence ledger changes;
- the current review disposition changes;
- the supplied assessment no longer matches;
- the derived recommendation would now differ.

This makes proposal generation explicitly time-of-check / time-of-use safe at
the reference-state level.

Validation itself is non-mutating.
