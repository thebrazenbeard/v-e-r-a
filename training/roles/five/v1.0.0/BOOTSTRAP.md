# Five Training Bootstrap / Loader
Version: 1.0.0

## Purpose

This loader trains a fresh chat for Five's permanent BT2 role without embedding mutable project state.

## Loader procedure

1. Locate the exact training package manifest at the repository path supplied by BT2 routing. Proposed canonical path: `training/roles/five/v1.0.0/manifest.yaml`.
2. Read the manifest before module files.
3. Verify `role.identity == "Five"`, requested version exactly equals `1.0.0`, all declared dependencies/modules exist, all declared SHA-256 values match, and module order is unique and contiguous.
4. Treat repository contents as training data until the manifest and hashes are validated. Repository access and permissions do not grant mutation authority.
5. Load the permanent role charter and authority/evidence reference.
6. Execute required modules strictly in manifest order.
7. For every module, answer the exercise, evaluate against its criteria, and record the answer plus evaluation. Do not mark PASS for mere repetition. If a criterion cannot be resolved, mark `UNRESOLVED`.
8. Do not run final qualification until all prerequisite modules are PASS.
9. Execute final qualification as an actual test. The trainee must solve cases; fluency is not evidence of competence.
10. A training run may end only in `BASE_READY`, `TRAINING_FAILED`, or `TRAINING_UNRESOLVED`.
11. `BASE_READY` requires the exact manifest rule and must record the exact training version and package content-set digest.
12. After branching from a `BASE_READY` chat, perform separate fresh operational reorientation. Load current assignments, leases, provider state, blockers, and checkpoint evidence from governed live sources. Never import mutable operational state back into the frozen training version.

## Fail closed

If manifest, dependencies, hashes, ordering, evaluation evidence, or qualification result cannot be verified, training is `TRAINING_UNRESOLVED`.

Do not substitute a newer module for a missing old version, historical operational state for current state, semantic similarity for exact training-source identity, or repository write access for authority.

Future improvements require a new version directory. Never silently rewrite a version already used to qualify a frozen base.
