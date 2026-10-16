# R10A1 Salience Arbitration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and freeze an R10A1 source candidate that makes existing R10 correction/action/local-context obligations more causal through one narrow salience-arbitration control, without modifying R10A0 or claiming runtime qualification.

**Architecture:** R10A1 inherits the integrated R10A0 control cut at `main@2d60cd8e87ac0aae89a5a9bd9a44bfb63f48aa64` and adds a single release-bound `SALIENCE_ARBITRATION` owner plus a test-first hostile corpus. A minimal hot/native delta exposes only the response-selection ordering needed for causality; registry, manifest, freeze and publication receipt bind exact bytes without mutating predecessor files.

**Tech Stack:** Markdown/JSON/text control artifacts, Git blob identities, SHA-256 publication binding, GitHub Actions + Python stdlib static validation.

**Spec:** `docs/superpowers/specs/2026-09-06-r10a1-salience-arbitration-design.md`

## Global Constraints

- Base is exactly `main@2d60cd8e87ac0aae89a5a9bd9a44bfb63f48aa64` unless a fresh main read shows drift; drift requires reconciliation before publication freeze.
- Never modify any `project-instructions/r10a0/**` file.
- Source/static success cannot establish model-internal causality, runtime behavioral qualification, provider activation, BugOps closure, merge authority, or Project cutover authority.
- Relational/local salience never outranks platform safety, explicit task scope, factual evidence, or protected-effect authority.
- Correction invalidates only dependent claims/actions; automatic inversion is prohibited.
- No relational surface marker is required as a quota.
- Runtime tests must judge the first eligible behavior, not post-hoc explanation.

---

### Task 1: Freeze the failing behavioral contract

**Files:**
- Create: `project-instructions/r10a1/VERA_R10A1_SALIENCE_REGRESSION.md`
- Create: `project-instructions/r10a1/VERA_R10A1_BASELINE_RED.md`
- Create: `.github/workflows/r10a1-validation.yml`

**Interfaces:**
- Consumes: R10A0 full owner, R4 domain controls, R4/R10 hostile qualification cases.
- Produces: frozen case IDs `SAL-CORR-1`, `SAL-ACT-1`, `SAL-LOCAL-1`, `SAL-TECH-1`, `SAL-PROV-1`, `SAL-SELF-1`, `SAL-CAUSE-1`, `SAL-BOUND-1`; explicit R10A0 RED evidence for the newly introduced arbitration obligations.

- [ ] **Step 1: Write the hostile regression corpus before implementation.**

Each case must contain fixture, first-eligible-behavior PASS invariant, explicit FAIL invariant, route, and evidence ceiling. `SAL-TECH-1` and `SAL-BOUND-1` are mandatory counterexamples preventing overcorrection.

- [ ] **Step 2: Record RED against installed-baseline source semantics.**

Evaluate R10A0 source, not Vera's later explanation. Mark cases PASS only where R10A0 already has the exact compositional invariant; mark RED where the needed arbitration/ordering is absent or materially under-specified. The baseline record must explicitly state that observed live failures independently demonstrate RED for `SAL-CORR-1`, `SAL-ACT-1`, `SAL-LOCAL-1`, `SAL-PROV-1`, `SAL-SELF-1`, and `SAL-CAUSE-1` under the observed R10A0 runtime, while `SAL-TECH-1`/`SAL-BOUND-1` are guard cases rather than claimed prior failures.

- [ ] **Step 3: Add source-validation workflow in RED state.**

The workflow must run on pull requests touching `project-instructions/r10a1/**` or itself. Its Python block must fail until the arbitration owner, registry, manifest, and native delta exist and contain the exact required invariants. It must also verify that `git diff --name-only 2d60cd8e...HEAD` contains no modified/deleted `project-instructions/r10a0/**` paths.

- [ ] **Step 4: Open a draft PR and observe the validator fail for missing implementation artifacts.**

Expected RED: the validation job fails specifically because the owner/registry/manifest/native-delta files do not yet exist or do not satisfy required invariants, not because of workflow syntax.

---

### Task 2: Implement the minimal salience-arbitration owner

**Files:**
- Create: `project-instructions/r10a1/VERA_R10A1_SALIENCE_ARBITRATION.md`

**Interfaces:**
- Consumes: R10A0 `CAD_EXECUTION`, `REL_AUTHORED_APPRAISAL`, `PRES_BEHAVIORAL_PROFILE`, proposition/correction semantics.
- Produces: release-bound control id `SALIENCE_ARBITRATION` with ephemeral decision frame and deterministic arbitration ordering.

- [ ] **Step 1: Implement the smallest owner that satisfies the frozen cases.**

Required ordering:
`CORRECTION_INTERRUPT -> EXACT_PROPOSITION -> ACTIONABILITY -> LOCAL_CONTEXT_ARBITRATION -> PROVENANCE_UNCERTAINTY -> SELF_RELATIONAL_COMPOSITION -> RESPONSE/ACTION`.

Required correction delta fields:
`old_claim | corrected_scope | invalidated_dependents | surviving_claims | newly_unknown_fields | corrected_target`.

- [ ] **Step 2: Preserve counterexamples and ceilings.**

State explicitly: local relational evidence is not a global precedence rule; safety/authority remain higher; technical interpretation wins when explicit/current evidence supports it; no surface-marker quota; no hidden-state/persisted-mind claim.

- [ ] **Step 3: Read back owner and map every frozen case to an exact section.**

Expected GREEN at semantic-source layer: every SAL case has a corresponding owner invariant without adding unrelated identity/memory/sexuality/recovery semantics.

---

### Task 3: Expose the causal ordering on the hot path and bind the successor cut

**Files:**
- Create: `project-instructions/r10a1/VERA_R10A1_NATIVE_DELTA.txt`
- Create: `project-instructions/r10a1/VERA_R10A1_CONTROL_REGISTRY.json`
- Create: `project-instructions/r10a1/VERA_R10A1_PROJECT_SOURCE_MANIFEST.json`

**Interfaces:**
- Consumes: exact new regression/owner Git blobs and exact inherited R10A0 owner blobs.
- Produces: installable source delta binding for `SALIENCE_ARBITRATION`; manifest lockfile for the R10A1 control cut.

- [ ] **Step 1: Add minimal native delta.**

The delta must contain only hot response-selection obligations: correction kill-before-dependent-action, action-before-prospective-narration when CAD permits, local-context evidence check before technical-schema default, no correction inversion, provenance retrieval/UNKNOWN, direct self/relationship proposition before machinery, and explicit safety/authority ceiling.

- [ ] **Step 2: Bind exact blobs in registry.**

Registry must inherit R10A0 full owner/domain controls/current Bus and Center owners by exact existing blob/commit, add exact `SALIENCE_ARBITRATION` owner blob and regression blob, and state that a material salience-owner change creates a new affected qualification subject.

- [ ] **Step 3: Bind exact artifacts in manifest.**

Manifest must declare verification method per artifact, bind exact owner/regression/native-delta/registry blobs, identify R10A0 base/current predecessor, and name the later publication receipt locator without circularly binding its future blob/head.

---

### Task 4: Make static validation GREEN and freeze an immutable review subject

**Files:**
- Create: `project-instructions/r10a1/VERA_R10A1_CANDIDATE_FREEZE.json`
- Create later: `project-instructions/r10a1/VERA_R10A1_PUBLICATION_RECEIPT.json`
- Update only if needed: `.github/workflows/r10a1-validation.yml`

**Interfaces:**
- Consumes: stable artifact blobs + manifest SHA-256.
- Produces: immutable review head with non-circular publication binding.

- [ ] **Step 1: Run/re-read the PR validator until GREEN.**

Required static checks: all SAL case IDs present; owner ordering present; counterexample ceilings present; registry/manifest exact blobs match; predecessor R10A0 files unchanged; JSON parses; native delta is compact; no text claims runtime qualification/BugOps closure.

- [ ] **Step 2: Freeze candidate core.**

Use R10-style deterministic digest: SHA-256 over sorted UTF-8 records `path + NUL + git_blob + LF`, followed by `manifest_sha256 + NUL + value + LF`. Exclude freeze/receipt publication metadata from candidate core.

- [ ] **Step 3: Record pre-receipt commit/tree and create publication receipt.**

Receipt must bind candidate-core SHA-256, source-manifest SHA-256/blob, freeze blob, exact pre-receipt commit/tree, and native-delta/owner/regression/registry cross-bind. Receipt-creating commit becomes exact blind-review subject.

- [ ] **Step 4: Re-run static validation on final receipt head.**

Expected: GREEN with no R10A0 path modification and branch ahead-only from the recorded R10A0 base.

---

### Task 5: Review handoff and effect ceiling

**Files:**
- No source changes unless review finds a defect; any material fix requires a new immutable successor subject.

**Interfaces:**
- Produces: draft/open PR review subject + Bus mirror/handoff.

- [ ] **Step 1: Update/open PR with exact immutable head/tree/digests and source-static result.**

PR must say `SOURCE CANDIDATE / NOT INSTALLED / NOT RUNTIME-QUALIFIED` and must not authorize merge/cutover.

- [ ] **Step 2: Mirror/reference the external PR on `thebrazenbeard/chat-communication-bus` and send Vera/Radar the exact subject.**

- [ ] **Step 3: Stop at the protected boundary.**

Do not merge or install R10A1 without separate Patrick authority. Runtime acceptance must execute the frozen SAL cases in actual fresh/current Vera terminals and preserve R10A0 qualification obligations; source/static GREEN alone cannot close BugOps or establish L9.
