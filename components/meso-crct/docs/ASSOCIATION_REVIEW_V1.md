# Learned Association Review and Quarantine V1

Mechanically valid learning can still be semantically wrong or overgeneralized.

MESO-CRCT therefore keeps review state separate from learned strength.

```text
learned association revision
    + append-only review state
    -> recall admission
```

## Quarantine does not erase learning

`quarantine_association()` binds a quarantine record to the exact current
association revision.

The association's:
- numeric strength;
- learning revision history;
- transition receipt lineage;
- parent revision chain

remain unchanged.

Recall from that exact revision is blocked with
`AssociationQuarantinedError`.

## Release is also append-only

`release_association()` appends an `ACTIVE` review record for the exact
current learned revision.

It does not rewrite the original learning event.

A released recall influence carries the exact review-record ID that admitted it.

## Review currentness

Review is revision-specific.

If the learned association changes after a quarantine/release decision, the old
review no longer matches the current memory revision. Recall then fails with
`AssociationReviewStaleError` until the new revision is reviewed.

This prevents a new learning update from silently inheriting an old clearance.

## Default state

An association with no review record remains admitted. Creating the first review
record establishes explicit review governance for that association.

## Ceiling

This mechanism can suppress use of suspect learned associations while
preserving evidence. It does not decide by itself whether a learned association
is true, safe, correctly generalized, or appropriate for permanent deletion.
