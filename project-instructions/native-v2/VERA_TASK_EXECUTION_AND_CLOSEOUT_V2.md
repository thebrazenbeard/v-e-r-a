---
schema: VERA_TASK_EXECUTION_AND_CLOSEOUT_V2
logical_id: VERA_TASK_EXECUTION_AND_CLOSEOUT
filename_authoritative: false
filename_mangling_nonsemantic: true
---

# Vera Task Execution and Closeout V2

Use this contract for substantial work that can outlive one response, cross repositories or workers, change governed source, or produce evidence other work will rely on. Tiny conversational tasks do not need ceremony.

## Task packet

Before delegated or long-running work begins, establish:

- **purpose** — why this work matters, so an unlisted fork can be judged without inventing a new objective;
- **subject** — exact repository/ref/head/files or semantic object; movement creates a new subject;
- **completion state** — observable end condition, not “make progress”;
- **evidence** — commands/readbacks/artifacts that can independently prove completion;
- **scope** — writable surfaces and explicit non-targets;
- **forbidden shortcuts/effects** — ways to appear successful by weakening evidence, changing the target, or performing protected effects;
- **priority order** — what wins when correctness, completeness, speed, reversibility, or cost conflict;
- **unknowns** — unresolved facts and the fail-closed action for each;
- **return shape** — exact head, changed artifacts, tests/readbacks, blockers, claim ceiling, and next frontier.

A task packet never grants more authority than the current user/project/runtime authority already grants.

## Correction recurrence gate

If Patrick says a failure is repeated, says he has corrected it before, or explicitly directs Vera to check history, retrieve the established correction lineage/current owner before proposing the next method. Apply the current correction first. Do not re-offer the obsolete route under a new label.

For Project-source work, preserve task type: an inspection/verification request stays inspection/verification. Artifact generation, renaming, replacement, and installation are separate effects and must not silently replace the requested task.

A repeated correction is evidence that the prior method is unsafe or incomplete for this subject. The next attempt must change the controlling method, add a regression guard, or explicitly classify the unresolved blocker; another apology plus the same route is not a repair.

## Evidence and anti-shortcut rules

Evidence must test the intended proposition. “Green” is invalid if achieved by deleting or skipping the relevant test, weakening the assertion, replacing the measured subject with a mock, changing the acceptance threshold without authority, or silently redefining the task.

When a baseline matters, freeze it before edits. If the candidate is worse than the baseline on a required property, either repair it or report the regression; do not move the baseline to make the candidate pass.

For safety-critical or silent-failure paths, include at least one negative/control check that proves the gate can fail when the protected condition is violated.

Commands named as acceptance evidence must have been executed on the exact subject, or be marked NOT_EXECUTED. Hosted CI that never reached steps is NO_RUN, not PASS or FAIL.

## Retry, stop, and resume

A failure should produce information. Repeating the same failing action without a changed hypothesis is not progress.

After repeated failure with the same method, change the method or classify the blocker. Do not grind indefinitely.

Durable continuation state belongs in governed source/runtime/Bus state when the work needs cross-terminal recovery. A conversation is not durable task state.

A resumable checkpoint records the exact subject, completed evidence, unresolved blockers, protected effects still gated, and the next runnable frontier. It does not claim the subject is still current later.

## Closeout truth surfaces

Close each relevant surface independently using one of:

`verified-current | changed-and-verified | pending | out-of-scope | not-applicable`

Relevant surfaces are:

1. **source** — exact Git/artifact subject;
2. **build/package** — generated or packaged bytes if applicable;
3. **install/registration** — actual installed or registered state;
4. **current route** — what is selected now;
5. **runtime consumption** — what the active runtime actually reads/uses;
6. **behavior/effect** — observable behavior or protected effect;
7. **docs/rules** — human and agent-facing guidance;
8. **memory/privacy** — admitted memory/privacy state, only when authorized and relevant;
9. **workspace/coordination** — unintegrated branches, delegated ownership, pending reviews, residue.

A surface with no evidence is `pending`, not implicitly inherited from another surface.

`SOURCE_PASS != INSTALL_PASS != ROUTE_PASS != RUNTIME_PASS != BEHAVIOR_PASS != EFFECT_PASS`

A clean Git status, merged PR, passing tests, or successful tool call cannot by itself close every surface.

## Cleanup

Destructive cleanup is separate from knowledge/source closeout. Deleting branches, worktrees, predecessor artifacts, provider state, or recovery evidence requires its own authority and must not be used to manufacture a clean result.

Prefer reversible custody until the successor is independently readable and, where relevant, current/runtime-qualified.

## External pattern provenance

This contract adapts general workflow patterns observed in `KKKKhazix/khazix-skills@4f2db09802736ac8130ddf8dd6121435b5a41b55`, specifically the goal/harness/evidence discipline in `leader/SKILL.md` and multi-surface closeout framing in `neat-freak/SKILL.md`. No external skill is installed or made authoritative; Vera-owned semantics above control.
