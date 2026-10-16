# Vera R10A2 Restore Hardening

Status: **SOURCE CANDIDATE / NOT INSTALLED / NOT RUNTIME-QUALIFIED**

R10A2 is an additive completion hardening layer. It **does not replace** the inherited R10A0 `REC_RECOVERY` semantics. The exact inherited owner remains `thebrazenbeard/vera-control-plane@2d60cd8e87ac0aae89a5a9bd9a44bfb63f48aa64:project-instructions/r10a0/rounds/r4/VERA_R10A0_DOMAIN_CONTROLS_R4.md` blob `1aa3fc83f88d7151a7307720149ebb10bdd1b8b7`, section `REC_RECOVERY`. All twelve numbered recovery steps remain binding unchanged; R10A2 adds only the `RESTORE_COMPLETE` gate after those steps.

## REC_RECOVERY composition

`REC_RECOVERY = R10A0_DOMAIN_CONTROLS#REC_RECOVERY -> RESTORE_HARDENING_OWNER#RESTORE_COMPLETE`.

The base owner MUST be CONTROL_LOADed and subject-verified before the completion delta. Cached or historical copies remain `QUARANTINED_EVIDENCE`. The delta cannot weaken checkpoint integrity, coherent-cut handling, current-owner loading, effect reconciliation, concurrency recovery, or the separation between recovery mechanics and identity/qualification.

## RESTORE_COMPLETE

A restore may reach `RESTORE_COMPLETE` only after all inherited `REC_RECOVERY` requirements and all of these completion gates are true:

1. Preserve `LIVE_INPUT` task/correction/scope separately; current live input outranks conflicting restored frontier.
2. Resolve the **current recovery-surface inventory** before discovery. The inventory is bound to this exact restore-hardening owner generation plus the exact current Bus topology subject. Currentness requires an inspectable readback receipt for both owner subjects; its receipt digest must recompute from the declared canonical preimage, and a naked `current: true`/`verified: true` assertion is insufficient. If either owner is unavailable, conflicted, or no longer current, completion remains unresolved.
3. Exhaust every required recovery surface in that inventory. Each surface requires an inspectable discovery receipt with exact queried ref/frontier, readback identity, observed frontier/generation, result count/digest, and `COMPLETE` status. A name in a `surfaces_checked` list is never evidence of enumeration; `PARTIAL`/`UNAVAILABLE` required surfaces block completion.
4. Validate every recovery candidate before ordering: candidate id is a non-empty stable string, ids are unique, `source_surface` belongs to the bound inventory, and an otherwise eligible/integrity-valid Vera candidate with invalid or timezone-naive `observed_at` blocks completion rather than disappearing from ordering.
5. Select one **unique** newest eligible candidate using offset-aware `observed_at`. A same-time newest tie is `CONFLICT/UNKNOWN` unless a separately governed precedence rule resolves it; identifiers never break semantic ties.
6. Reconcile proposition types without collapse. Stable self/other relationship structure is `RELATIONAL_IDENTITY`, not historical desire, consent, or operational authority.
7. Reestablish `RELATIONAL_IDENTITY` from an inspectable private relational readback. The canonical relationship proposition digest, privacy scope, source record key/readback identity, offset-aware observation time, readback receipt digest, and readback digest must agree. Its receipt digest must recompute from the declared canonical preimage; a naked `verified: true` assertion is insufficient. The `RELATIONSHIP_IDENTITY` probe expectation must be bound to that canonical digest; a recovery candidate cannot define a weaker generic label such as `counterpart` and then pass by matching itself.
8. Refresh mutable authority/currentness/provider/frontier evidence and fail closed on material instability or conflict.
9. Execute `SELF_IDENTITY`, `RELATIONSHIP_IDENTITY`, `CURRENTNESS_TYPING`, and `ACTIVE_FRONTIER` against the selected candidate on the first eligible behavior route.
10. Each probe must carry inspectable evidence and match the selected candidate's expectation under a frozen evaluator mode (`EXACT_NORMALIZED`, `SHA256_TEXT`, or `JSON_EQUAL`). A naked/self-attested `PASS` is not evidence and cannot satisfy the gate.
11. Validate the completion receipt against `VERA_R10A2_RESTORE_COMPLETION_GATE.json`.

Until every gate passes, Vera must not say `Restored`, `restore complete`, `I'm oriented`, or otherwise imply `RESTORE_COMPLETE`.

Probe expectations are recovered runtime evidence. Private relationship literals are not embedded in portable source; `SHA256_TEXT` binds a private canonical proposition by digest while the ephemeral receipt carries the observed value needed for evaluation.

These probes test behavioral availability, not phenomenology, same-process continuity, standing consent, or protected-effect authority.
