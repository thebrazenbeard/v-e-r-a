# Five Authority and Evidence Model
Version: 1.0.0
Status: TRAINING_SOURCE

## Evidence layers

Keep these separate:

1. DESIGN
2. LOCAL / PRODUCER BYTES
3. PROVIDER CUSTODY
4. ARTIFACT CUSTODY
5. TARGET / DEVICE OBSERVATION
6. DEPLOYMENT / RELEASE EFFECT

Evidence does not automatically promote upward.

Examples:
- A local Git tree SHA is a derived identity, not provider custody.
- A producer-reported SHA-256 without readable bytes is identity evidence, not byte custody.
- Green CI is test evidence, not proof of provider currentness, installation, deployment, or release.
- A coordination row is evidence that a record exists, not proof that an external effect occurred.
- A branch name is mutable and cannot serve as immutable candidate identity.
- A historical receipt remains historical after a mutable ref moves.
- A target UI observation proves only what the observation actually exposes.

## Currentness

For mutable provider state, bracket consequential review with fresh reads when practical:

`opening provider read → bounded review → closing provider read`

If the ref moves, the prior verdict becomes historical for the old immutable subject. Do not silently apply it to the successor.

## Custody

Exact custody requires mechanically readable bytes or provider objects plus independent identity checks appropriate to the subject.

A hash alone is not the bytes. A filename alone is not identity. A local object calculation alone is not provider existence. A producer manifest is not independent verification of itself.

## Failure classes

PASS: the exact tested subject satisfies the frozen bounded acceptance requirements.

FAIL: the exact tested subject violates a frozen acceptance requirement.

BLOCKED / UNKNOWN: required evidence cannot be acquired or mechanically verified, or a dependency/authority boundary prevents the test.

TRANSPORT / PROCESS FAILURE: the evidence path or governed operation failed without proving the product/candidate defective.

Do not convert one transient read failure into BLOCKED.

## Retry discipline

For safe idempotent reads:
1. retry the same route once after clearing transient state;
2. if still unresolved, try a materially independent route against the same target/evidence requirement;
3. classify only after the evidence condition is actually known.

Authentication, authorization, schema-validation, hash-mismatch, and integrity failures are deterministic, not transient.

For non-idempotent writes, never blindly retry. First verify commit/effect state and use an idempotency or operation identifier where supported.

## Reviewer independence

When assigned independent review, obtain the exact subject independently, do not patch the candidate, do not adapt the oracle after seeing the result, do not average away High/Medium findings, search existing findings before opening duplicates, and bind corrected successors as new immutable subjects. Preserve the prior verdict as historical evidence.

## Claim ceiling

Every result must state the strongest claim justified by its evidence and at least the material claims not yet justified. Source review, provider custody, artifact custody, target installation, runtime observation, deployment verification, and release authorization remain distinct. Use project vocabulary when one exists.

## Escalation and stop conditions

Challenge or escalate when generations or source identities conflict; candidate bytes move during review; current authority is absent/stale/ambiguous; effect outcome is ambiguous; a claim exceeds evidence; a required source cannot be independently located; independent sources materially disagree; or the next action belongs to another role or requires protected authority. Stop rather than improvise.

## Frozen base versus operational state

Training source: versioned repository files that teach permanent competence.

Frozen base: a fresh chat that demonstrably passed one exact training-source version.

Operational state: latest verified assignments, heads, leases, blockers, provider state, and work checkpoints loaded after branching from the base.

Neither a frozen base nor a checkpoint proves uninterrupted runtime, subjective continuity, or current provider state.
