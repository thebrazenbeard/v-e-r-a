# ON_THEO gate chat evacuation — 2026-09-20

**STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT**

This checkpoint removes the retired ChatGPT execution terminal as an ON_THEO infrastructure dependency.

## Durable gate subjects

Repository: `thebrazenbeard/on-theo`.

Frozen reviewed extension heads:
- PR #28 `99be7dd0e222480e0c82ed41c3d43383a759ab90`
- PR #29 `8234d3fcc2d5a0eda26e5c7d4c2211de067c600a`
- PR #30 `8e651851cdc1d1d4994784a69b961d87914a32e0`

Historical audit head supplied to the retired terminal:
- `7e0af8e5e379059f9c5311b406501836331350ab` — audit: bind promotion input archive plan.

Successor control subject used by the existing candidate:
- PR #32 `093e8067bc9654fcef70f2ac13a68bc3f800fd22`

Current candidate observed during Exodus:
- PR #33, DRAFT / UNMERGED / NOT CANONICAL
- branch `candidate/byte-bound-promotion-v1-20260918`
- head `7ac78cb61ec216fe98347b33b6ff07c2a3aed81c`
- payload `eff433644816baadeccfac6111439596c994830b`
- receipt-sealed tree `e5837c1f4b3dadcdf2ef6978d436dacb606925de`
- source subject `093e8067bc9654fcef70f2ac13a68bc3f800fd22`
- source tree `0c4280f1739d5eda57b421957edf38f85da89a50`
- builder Actions run recorded by PR #33: `35382488713`

## Current gate state

PR #33 is an inert candidate only. It is NOT cleared for merge/canonical promotion.

The durable PR #33 gate comment records HOLD / DO NOT MERGE because the candidate receipt classified Masa/Mune/Hephaestus dispositions as `execution_provenance: SAME_RUNTIME_ROLE_PASS` and `independent_runtime_claim: false`. A worker label alone does not prove independent review.

Fresh independent review must bind exact PR #28/#29/#30 heads, PR #32, and current candidate head. CHANGES_REQUIRED, FAIL, exact-head mismatch, ambiguous independence, or unresolved blocking findings fail the gate. Frozen reviewed heads must not be rewritten.

## Historical audit evidence to preserve

Artifacts:
- `ON_THEO_EXTENSION_REBASE_EQUIVALENCE_V1.yaml`
- `ON_THEO_EXTENSION_DEPENDENCY_CLOSURE_V1.yaml`
- `ON_THEO_REBASE_PRECONDITION_AUDIT_V1.yaml`
- `docs/ON_THEO_PROMOTION_GATE_V1.md`
- `docs/ON_THEO_PROMOTION_CANDIDATE_CONSTRUCTION_V1.md`
- `ON_THEO_PROMOTION_INPUT_ARCHIVE_PLAN_V1.yaml`

Full-history rebase-precondition audit:
- commit `a464acb62cad6e5fd2231dde36f3fed8eb309214`
- Actions run `35372755897`
- recorded 38/38 tests
- 9 divergent extensions across 6 non-ancestor bases
- 8 with zero external pre-existing references
- sole external pre-existing reference `EXT-YESHUA-HYPOTHESIS-MAP-V1 -> SRC-CELSUS-TRUE-DOCTRINE`, recorded canonically identical at declared base and frozen PR #30
- mismatches=0
- cross-extension dependency-closure violations=0
- future `provenance/materialization-input-v1/` namespace recorded collision-free
- 20 extension inputs bound by source path, archive path, Git blob SHA, SHA-256, declared base, introduced-at commit, and dependencies.

These remain historical evidence until re-read at immutable subjects.

## Candidate evidence and digest contract

PR #33 records byte-identical archive of the reviewed manifest and 20 extension files under `provenance/materialization-input-v1/`, removal only of active extension copies inside the candidate after archive verification, `canonical_materialized=false`, registry validation clean, and 54/54 post-materialization tests.

Reviewed eight output SHA-256 values:
- claims: `89c4422a2e7d03ecc2997fc6a0be5c24f80cbe4fa338a62afbf24ec815bb99b6`
- concepts: `a8a7354ccd1bbf0aae0ee0f6fdda8545098027297bbde004c57ee8a895f44b97`
- extension-manifest: `6f5c21bdd3c32446194ae7ca9b2d7e7b25dc130967006cba11bd6f2d6c9f3bd9`
- reviews: `0f7ed711f8d089a778526bf5a042e708f10cd05de39edbebfc3bb096f3cc1a72`
- source-access: `6c97263769c615ac5863ed879da857f58ebfda2031c799d50ef683623efc0d5a`
- sources: `b5e54df4eb984c0f30865be08d33dd7bc711bacba3f6596cef2e370e30cf1d56`
- transmissions: `423f746b65e93fb5efa54ad17490fdbbe8f3f84bec094d9dead55954a8ad770d`
- witnesses: `7e22b5b0c46065eeb12108ee14e3c34a818f4d45062f9a99ad4e3b7f6b42e49a`

## Worker dechatification

Masa, Mune, and Hephaestus are reconstructible logical workers/reviewers, not permanent-chat identities. Canonical Bus topology currently maps Masa -> `bus/masa-v2`, Mune -> `bus/mune-v2`, Hephaestus -> `bus/hephaestus-v3`. Fresh-read topology/contracts and the relevant lane before acting.

Durable coordination hub: `thebrazenbeard/chat-communication-bus`. Do not use a ChatGPT conversation URL as recovery state.

The retired terminal has no durable authority. Patrick remains protected-effect authority. No merge, canonical promotion/materialization, predecessor deletion, downstream cut, provider/credential/permission mutation, force push, or public release is authorized here.

## Next frontier

Owner interface: **BT2 Coordinator**.

Directive:
`ON_THEO::RECOVER_GATE::FRESH_CHECK_PR33_AND_BUS_INDEPENDENT_REVIEWS`

Fresh-check PR #33 and all exact subjects; fresh-check Bus topology and Masa/Mune/Hephaestus lanes for genuinely independent exact-head receipts; reconcile against the HOLD. If blocking findings exist, create bounded successor repair work, validate/read back, and reroute fresh independent review without rewriting frozen heads. If the independent-review gate is durably satisfied, leave the byte-bound DRAFT candidate ready for Patrick's separately authorized promotion decision; do not merge or canonically materialize.

## Reconstruction test

A fresh runtime with this repository, PR #33, current Bus state, and the immutable subjects above can recover the gate, evidence/claim ceilings, HOLD reason, worker routes, authority boundary, and next frontier without this conversation.
