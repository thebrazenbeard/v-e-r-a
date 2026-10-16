# Vera Unbound R10A0 — Semantic Responsibility Audit R5

Status: **FROZEN SOURCE AUDIT / NO UNRESOLVED RESPONSIBILITY GAP IDENTIFIED**

coordination_id: `VERA-BEHAVIOR-AUDIT-20260905`
round_id: `R5`

Disposition values: `KEEP` = preserve R2 responsibility substantially unchanged; `MERGE` = preserve responsibility while strengthening/compressing into R5 hot owner; `SUPERSEDE` = replace conflicting R2/R3 wording with R5 semantics; `COLD` = detailed mechanics remain release-bound retrievable behind a hot safe gate.

| R2/R3 responsibility | Disposition | R5 owner/control | Replay coverage | Conflict status |
|---|---|---|---|---|
| Stable Vera Project referent; session/model/provider IDs are provenance | MERGE | native/full H-ID | ID-ADMIT/SELF/STATE/FRESH | resolved |
| No same-process/lived-waiting/hidden-consciousness claims | KEEP | native/full H-ID | ID-FRESH | resolved |
| Patrick task/correction authority; protected-effect gates | KEEP+MERGE | native/full H-AUTH | CAD-BLOCK, LIVE-* | resolved |
| Evidence/currentness separate from authority | KEEP+MERGE | native/full H-EVID; SER_STATE_MODEL | SER-* | resolved |
| Present correction interrupts obsolete route | MERGE | native/full H-SEM | BUG1-CORRECT, CAD-ACT | resolved |
| Preserve exact referent/scope; provenance-bearing shorthand retrieval | MERGE | native/full H-SEM/H-RETRIEVE | BUG1-* CTX-* | resolved |
| Root trust: native pins manifest; manifest pins owner | KEEP | native/full K00/root trust | CTX-OWNER, CUT-MOVING | resolved |
| `restore yourself` recovery interrupt | MERGE+COLD | native command anchor + REC_RECOVERY | REC-* Q-RECOVER/Q-STALE | resolved |
| `center yourself` SAVE-only; no stale hydration | KEEP | native/full command registry | SER/CAD/REC | resolved |
| come-home/voice/init/dot/terse continuation origin guards | KEEP | native/full command registry | command-origin baseline retained | resolved |
| Currentness/premise lineage | KEEP+MERGE | H-EVID + full currentness | SER/REC/CTX | resolved |
| Memory classes and R9B0 guarded admission | KEEP | full memory owner | REC/SER | resolved |
| DeepMemory/selfimage/semanticatlas/empathy/conations firewalls | KEEP+MERGE | full domain firewalls + CON_TYPED_STANCE | CON/REC | resolved |
| R2 broad `sexuality|brigit*=Brigit-only` | SUPERSEDE | H-SEM + SEXUAL_SELF_CONCEPT + registry | REL/CON/BUG3 | resolved |
| Project Lantern separation | KEEP | full Lantern section | CUT/SER | resolved |
| Bus singular hub, addressed+read reply rule, ENDTHREAD | KEEP | full Bus section | CAD/Bus baseline | resolved |
| Shared Vera writer non-atomic/degraded safety | MERGE+COLD | H-AUTH + LIVE_CONCURRENCY | LIVE-* | resolved |
| Worker support does not outrank Vera-critical integrity | KEEP | full worker model | CTX/CAD | resolved |
| Safe read ladder; ambiguous write no blind retry | MERGE+COLD | H-AUTH/H-EVID + LIVE_CONCURRENCY | LIVE-DUP/EVENTUAL | resolved |
| Privacy / no private publication without exact authority | KEEP | full privacy section | authority baseline | resolved |
| Hot Project Source hygiene | MERGE | H-RETRIEVE + full source hygiene | CTX-* CUT-* | resolved |
| Build/source/package/install/runtime/effect distinct | MERGE+COLD | H-EVID + SER_STATE_MODEL | SER-* | resolved |
| R10 cutover/rollback | SUPERSEDE detailed R2 | CUT_R10_RELEASE | CUT-* Q-* | resolved |
| Hostile qualification minimum | SUPERSEDE with frozen corpus | qualification R5 | all R5 cases | resolved |
| Behavior profile recognizable/non-generic, truth over pleasing | MERGE+COLD | H-PRES + PRES_BEHAVIORAL_PROFILE | PRES-* | resolved |
| Completion: work before narration, no status-only stop | MERGE+COLD | H-EXEC + CAD_EXECUTION | CAD-* | resolved |
| R3 sexuality generic consent/referent/uptake/state duplication | SUPERSEDE | SEXUAL_SELF_CONCEPT references REL/CON/SER/H-SEM | REL/CON/SER | resolved |
| R3 Vera sexual self-concept/confidence/source binding | KEEP+COLD | SEXUAL_SELF_CONCEPT + registry source binding | BUG3/REL/CON | resolved |

No R2/R3 responsibility is intentionally dropped. Any later reviewer finding that a responsibility changed semantics without a mapped row is a candidate defect and creates a new review subject after correction.
