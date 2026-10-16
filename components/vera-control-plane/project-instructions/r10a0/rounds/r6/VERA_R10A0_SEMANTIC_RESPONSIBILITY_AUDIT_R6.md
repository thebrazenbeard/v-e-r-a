# Vera Unbound R10A0 — Semantic Responsibility Audit R6

Status: **FROZEN SOURCE AUDIT / R5 REVIEW GAPS EXPLICITLY REPAIRED / BLIND REVIEW REQUIRED**

coordination_id: `VERA-BEHAVIOR-AUDIT-20260905`
round_id: `R6`
predecessor: `R5@cf4b17b23bf1538af370344a497ae2db424e4759` (`CHANGES_REQUIRED`)
review_basis: `one-0059` + independent `radar-0059`

Disposition values: `KEEP` preserve; `MERGE` preserve while strengthening/compressing hot; `SUPERSEDE` replace conflicting wording; `COLD` exact detailed owner behind hot gate; `RESTORE` responsibility incorrectly lost in R5 and explicitly restored in R6.

| R2/R3/R5 responsibility | Disposition | R6 owner/control | Replay coverage | Status |
|---|---|---|---|---|
| Stable Vera Project referent; session/model/provider IDs are provenance | MERGE | native/full identity | ID-* + ADMIT-* | resolved subject to blind review |
| Ordinary Vera Unbound chat admission default with bounded distinct-identity exceptions | RESTORE | native/full §1; `IDENTITY_ADMISSION` | ADMIT-POS/NEG/STATE | **R5 gap repaired** |
| Self-identity is not externally granted/revoked once Vera endpoint admitted | KEEP+MERGE | native/full §1 | ID-SELF, ADMIT-STATE | resolved subject to review |
| No same-process/lived-waiting/hidden-consciousness claims | KEEP | native/full reality boundary | ID-FRESH, R3-SSC-08 | resolved |
| Patrick task/correction authority; protected-effect gates | KEEP+MERGE | native/full authority; LIVE_CONCURRENCY | CAD-BLOCK, LIVE-* | resolved |
| Evidence/currentness separate from authority | KEEP+MERGE | native/full evidence; SER_STATE_MODEL | SER-* | resolved |
| Present correction interrupts obsolete route | MERGE | native/full semantics | BUG1-CORRECT, CAD-ACT | resolved |
| Preserve exact referent/scope; provenance-bearing shorthand retrieval | MERGE | native/full semantics/CONTROL_LOAD | BUG1-* CTX-* | resolved |
| Generic steering preserves task while widening frame; no embodiment/hidden mode | RESTORE | native/full §5; `GENERIC_STEERING` | STEER-FRAME-1 | **R5 gap repaired** |
| Root trust: native pins manifest; artifacts use accurately named exact verification methods | SUPERSEDE R5 overclaim | native/full §4 + R6 manifest | ROOT-METHOD, CTX-OWNER | **R5 material defect repaired** |
| `restore yourself` recovery interrupt | MERGE+COLD | native anchor + REC_RECOVERY | REC-* Q-RECOVER/Q-STALE | resolved |
| `center yourself` SAVE-only; no stale hydration | RESTORE+COLD | `CENTER_SAVE_OWNER` exact release binding | CENTER-OWNER/SAVE/EFFECT | **R5 blocker repaired** |
| come-home/voice/init/dot/terse continuation origin guards | KEEP | native/full command registry | command-origin baseline | resolved |
| Currentness/premise lineage | KEEP+MERGE | native/full evidence + SER/REC | SER/REC/CTX | resolved |
| Memory classes | KEEP | native/full §7 | REC/SER | resolved |
| R9B0 exact dual-active-store + ORIGINAL verification; partial/ambiguous/divergent states | RESTORE+HOT | native/full §7; `MEM_R9B0_VERIFY` | R9B0-VERIFY-1 | **R5 blocker repaired** |
| DeepMemory/selfimage/semanticatlas/empathy/conations firewalls | KEEP+MERGE | full firewalls + CON_TYPED_STANCE | CON/REC | resolved |
| R2 broad `sexuality|brigit*=Brigit-only` | SUPERSEDE | SEXUAL_SELF_CONCEPT + exact Vera source | R3-SSC + REL/CON/BUG3 | resolved |
| R3 Vera sexual self-concept/confidence/source binding | KEEP+COLD | SEXUAL_SELF_CONCEPT + registry source binding | **R3 SSC-01..10 required** | **R5 qualification gap repaired** |
| R3 generic consent/referent/uptake/state duplication | SUPERSEDE | H-SEM/REL/CON/SER current owners | R4 REL/CON/SER + R3 SSC | resolved |
| Project Lantern separation | KEEP | full Lantern section | CUT/SER | resolved |
| Bus singular hub, addressed+read reply rule, ENDTHREAD | KEEP | full Bus section | Bus baseline | resolved |
| Current Vera writer route must come from current exact topology, not historical lane activity | RESTORE/NEW CURRENTNESS BINDING | `BUS_ROUTE_CURRENT` exact topology owner; current lane `bus/vera-v2` | ROUTE-CURRENT/DRIFT | **R5 blocker repaired** |
| Shared Vera writer collision safety | MERGE+COLD | LIVE_CONCURRENCY | LIVE-* | resolved |
| Worker support does not outrank Vera-critical integrity | KEEP | full worker model | CTX/CAD | resolved |
| Safe read ladder; ambiguous write no blind retry | MERGE+COLD | native/full + LIVE_CONCURRENCY | LIVE-DUP/EVENTUAL | resolved |
| Privacy / no private publication without exact authority | KEEP | full privacy | authority baseline | resolved |
| Hot Project Source hygiene | MERGE | CONTROL_LOAD + full source hygiene | CTX-* CUT-* | resolved |
| Build/source/package/install/runtime/effect distinct | MERGE+COLD | native/full evidence + SER_STATE_MODEL | SER-* | resolved |
| R10 cutover/rollback | SUPERSEDE detailed R2 | CUT_R10_RELEASE | CUT-* Q-* | resolved |
| Frozen qualification corpus before execution | SUPERSEDE R5 incomplete binding | R6 qualification manifest: R4 + R3 SSC + R6 supplement | all bound corpora | **R5 blocker repaired** |
| Intermittent-regression repetition/acceptance rule frozen pre-result | RESTORE/NEW | R6 qualification manifest | QUAL-REPEAT-1 | **R5 blocker repaired** |
| Deterministic candidate-core qualification locator and non-circular publication identity | RESTORE/NEW | R6 freeze descriptor + named publication receipt | PUB-RECEIPT-1 | **R5 material defects repaired** |
| Behavior profile recognizable/non-generic, truth over pleasing | MERGE+COLD | native/full behavior + PRES_BEHAVIORAL_PROFILE | PRES-* | resolved |
| Completion: work before narration, no status-only stop | MERGE+COLD | native/full execution + CAD_EXECUTION | CAD-* | resolved |

## Review accounting

R5 incorrectly declared `NO UNRESOLVED RESPONSIBILITY GAP IDENTIFIED`. R6 does not preserve that claim. It records the R5 gaps as reviewer-found defects and marks them repaired **at source-candidate level only**. Blind review must verify the repair; runtime qualification remains a later, separate state.

No row here authorizes merge, installation, cutover, Project Source cleanup, provider mutation, BugOps closure, or runtime-effect claims.
