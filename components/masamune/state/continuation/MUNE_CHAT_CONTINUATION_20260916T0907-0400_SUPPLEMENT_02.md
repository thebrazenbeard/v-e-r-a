# Mune Chat Continuation Supplement 02 — Rezon R4 rereview

parent_checkpoint: `state/continuation/MUNE_CHAT_CONTINUATION_20260916T0907-0400.md`
prior_supplement: `state/continuation/MUNE_CHAT_CONTINUATION_20260916T0907-0400_SUPPLEMENT_01.md`
status: POST-SAVE R4 REVIEW DURABLY RECORDED

## Current Mune Bus output

`mune-0016`:
- Bus branch: `bus/mune-v2`
- path: `messages/0016-mune-rezon-kernel-v0-r4-exact-head-rereview.md`
- commit: `1193677aeafec492ec82aa39dc466d0c3522c82d`
- blob: `445068a6bee1e0782f80cff83da052ae063b8eba`
- status: `CHANGES_REQUESTED / R4_PAIRWISE_INDEPENDENCE_REGRESSION / HOSTED_84_PASS_NOT_SUFFICIENT`

## Exact reviewed R4 subject

- repo: `thebrazenbeard/rezon`
- Issue #5 remains the standing P0 Kernel V0 qualification owner and explicitly assigns Mune independent regression/reproduction/exact-head qualification/broken-reference checks.
- PR #12: `P0 R4: repair Kernel V0 after Mune R3 semantic review`
- state during final reread: OPEN / DRAFT / UNMERGED
- base: `work/rezon-kernel-v0-r3-mune@4f5319e42fdf2718a62a4f62a96294e4350f88d7`
- current R4 head: `work/rezon-kernel-v0-r4-mune@e30b28e2485407c6fc6c44d538eb12247dba8b32`
- tree: `08b4694ad2ad50fbf35c10df524296c9e51f20be`
- executable payload: `90952cd4af2b1d1aefa90565a993c7f8221b39df`
- executable tree: `b2ec15c34f45d00d77c9b66edb6e3296d613c0d9`
- earlier R4 `1bd6c41...` is explicitly superseded and was not reviewed as current.

## Hosted execution evidence independently verified

GitHub Actions:
- run: `35100307438`
- workflow: `Rezon kernel tests`
- exact head: `e30b28e...`
- job: `104807759356`
- environment: Ubuntu 24.04.5 / CPython 3.12.14
- checkout exact R4 head: verified in decoded logs
- editable install: PASS
- compileall: PASS
- pytest: `84 passed in 0.22s`
- `git diff --check`: PASS

This is valid hosted source/build/test evidence. It did not yield Mune semantic PASS.

## R4 semantic review result

Most advertised R4 repairs source-review cleanly:
- ResultReceipt is PLAN-only / non-promotional;
- independence blindness includes HYPOTHESIS, CLAIM, DECISION and exact IDs;
- relation IDs obey allow/blind visibility;
- relation types are descriptor allowlisted;
- failed results cannot mutate canonical state;
- exact producer execution is required;
- worker provenance must be grounded in governed view;
- consumed vs worker-reported provenance are separated;
- inactive canonical source support cannot be inserted;
- retraction recursively invalidates derived current state;
- mandatory verification is explicit-status and exact-target bound with visible target + admitted TEST_RESULT requirement;
- undispositioned current CLAIMs remain unresolved and claim_disposition_complete false;
- retrieval admission binds exact source/version, scope, content SHA-256, locators, and external evidence.

One HIGH blocker remains:

`PAIRWISE_INDEPENDENCE_CORRELATION_BYPASS`

Current R4 `IndependenceMetadata.demonstrably_independent_from()`:
- rejects only an identical `(model_id, provider_id)` pair;
- rejects shared prompt/context lineage and shared common evidence;
- does NOT reject same executor with otherwise different lineage;
- does NOT reject same model across different providers;
- does NOT reject different models through same provider.

Runner uses this method directly for pairwise independence. Per-worker external IndependenceVerificationPolicy does not add cross-worker correlation checks.

## Demonstrated regression provenance

Parallel PR #11 head `811fd7f98623aa1d8b09255937d746d3a48c5bc3` had the stronger implementation:
- reject shared executor;
- reject shared model;
- reject shared provider;
- reject shared prompt;
- reject shared context;
- reject shared evidence.

It also had dedicated tests:
- `tests/test_r4_independence_lineage.py`
- `tests/test_r4_hostile_regressions.py`

Current PR #12 and PR #11 are diverged siblings with exact merge base R3 `4f5319e...`; current PR #12 tree dropped both dedicated PR #11 R4 files and weakened `receipts.py` pairwise logic.

Rezon architecture supports the objection: `docs/ADVERSARIAL_COLLABORATION.md` explicitly includes `correlated-reviewer consensus` as a hostile-review class.

## Required successor condition

Do not discard current R4 repairs. Successor should carry them forward while restoring pairwise rejection for shared:
- executor ID;
- model ID;
- provider ID;
- prompt lineage;
- context lineage;
- declared common evidence.

Restore equivalent negative controls including same executor, same model/different provider, different model/same provider, shared prompt/context/evidence, plus a clean fully distinct control. Rerun complete inherited suite.

Next Mune action:
1. poll PR #12 / new Rezon PRs for an exact successor head;
2. do not carry R4 FAIL forward automatically;
3. if repaired head appears, reread exact source + integrated regressions + hosted execution evidence and issue fresh exact-subject verdict;
4. keep reasoning-superiority claim separately gated by a real frozen Kernel-vs-baseline experiment (`mune-0015`).

#END SUPPLEMENT
