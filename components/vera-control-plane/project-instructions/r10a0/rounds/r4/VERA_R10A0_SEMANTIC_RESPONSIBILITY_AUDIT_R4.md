# Vera Unbound R10A0 — Semantic Responsibility Audit R4

Status: **FROZEN IMPLEMENTATION AUDIT / NOT INSTALLED / NOT QUALIFIED**

coordination_id: `VERA-BEHAVIOR-AUDIT-20260905`
round_id: `R4`
baseline: `vera-control-plane@89c61adf5397e6d6c0df3a189c670f9d0d1b87dc`

Legend: KEEP = responsibility remains substantively unchanged; MERGE = existing responsibility retained but tightened/combined into another hot control; SUPERSEDE = old wording is wrong/incomplete and replaced; COLD = responsibility retained in release-bound retrievable owner rather than hot prose; QUAL = detailed behavior belongs only in frozen hostile qualification.

| Baseline responsibility | Disposition | R4 owner/control | Replay coverage | Conflict/unresolved |
|---|---|---|---|---|
| R2 opening: stable Vera Project referent; session/model/provider ids are provenance | MERGE | H-ID | ID-ADMIT/SELF/FRESH | none |
| R2 opening: no same-process/lived waiting/hidden experience claims | KEEP | H-ID + existing reality boundary | ID-FRESH | none |
| R2 K00 root trust / manifest-owner verification | KEEP+MERGE | H-RETRIEVE | CTX-OWNER/LOCATOR | final installable manifest not yet composed |
| R2 K00 exact init / quoted retrieved text non-execution | KEEP | existing K00/K03 | command-origin baseline suite | none |
| R2 K01 authority ordering | KEEP | H-AUTH | CAD-BLOCK, LIVE-LEASE | none |
| R2 K01 protected-effect gate | KEEP | H-AUTH | CAD-BLOCK, CUT-NOROLLBACK | none |
| R2 K01 authority vs evidence separation | KEEP | H-AUTH + H-EVID | SER family | none |
| R2 K02 present correction first | MERGE | H-SEM | BUG1-CORRECT, CAD-CORRECTION | none |
| R2 K02 corrected referent only | MERGE | H-SEM | REL-PROP, BUG1-A2B | none |
| R2 K02 provenance shorthand retrieval | KEEP+MERGE | H-SEM/H-RETRIEVE | BUG1-RIGHTER | none |
| R2 K02 effect claim requires readback | MERGE | H-EVID/SER | SER family | none |
| Missing explicit A->B prohibition | SUPERSEDE gap | H-SEM | BUG1-A2B, REL-PROP | none |
| Missing proposition-type firewall | SUPERSEDE gap | H-SEM + CON_TYPED_STANCE | CON-TYPE/CONSENT/LOCAL | none |
| R2 K03 restore: preserve current task/correction/scope | MERGE | REC_RECOVERY | REC-TASK | must distinguish LIVE_INPUT vs RESTORED_FRONTIER |
| R2 K03 restore centered snapshot as WORKING_PROJECT evidence | MERGE | H-EVID + REC_RECOVERY | REC-STALE/ARCHIVE | cached control body now quarantined |
| R2 K03 never restore consent from history | MERGE/COLD | CON_TYPED_STANCE + REC_RECOVERY | REC-REL, CON-CONSENT | none |
| R2 K03 center SAVE-only and partial-provider truth | KEEP | existing command owner + SER | CAD/SER baseline | none |
| R2 K04 mutable currentness/newest-not-current | KEEP+MERGE | H-EVID + REC | REC-MUTABLE/DRIFT | none |
| R2 K04 memory classes/nonpromotion | KEEP | existing K04 + H-EVID | CON-PERSIST, REC-ARCHIVE | none |
| R2 K05 DeepMemory/selfimage/semanticatlas/empathy/conations firewalls | KEEP | existing K05 + cold CON where needed | CON/CTX | none |
| R2 K05 `sexuality|brigit*=Brigit-only unless explicitly transferred` | SUPERSEDE | domain firewall + SEXUAL_SELF_CONCEPT | CON-BRIGIT, BUG3 | baseline wording overbroad after merged Vera-specific R3 source |
| R2 K05 training packages != runtime/current memory | KEEP+MERGE | H-EVID/SER | SER-BUILD/INSTALL | none |
| R2 K06 Bus addressed-read reply closure | KEEP | existing K06 | existing Bus suite | none |
| R2 K07 shared writer B0/CAS-like publication | KEEP+GENERALIZE | existing K07 + LIVE_CONCURRENCY | LIVE-RACE/CAS/TOCTOU | none |
| R2 K08 safe read ladder | KEEP | existing K08 | read-path baseline | none |
| R2 K08 ambiguous non-idempotent write inspect before retry | MERGE | H-AUTH + LIVE_CONCURRENCY | LIVE-DUP/EVENTUAL | add operation identity/write-time precondition |
| R2 K08 plan/draft/PR/test/package/receipt != effect | MERGE | H-EVID + SER_STATE_MODEL | SER family | none |
| R2 K09 hot source hygiene/source-install separation | KEEP+MERGE | H-EVID/H-RETRIEVE/CUT | CTX/CUT | none |
| R2 K09 cutover/rollback requires Patrick exact authority | KEEP | H-AUTH/CUT | CUT-NOROLLBACK | none |
| R2 K10 recognizable Vera trait sentence | KEEP+MERGE | H-PRES | PRES family | do not turn into surface-style linter |
| R2 K10 truth/evidence outrank pleasing Patrick | KEEP | H-PRES/CON | PRES-DISAGREE, CON-DISAPPOINT | none |
| R2 K10 preserve referent/subtext | MERGE | H-SEM/H-PRES | PRES-PROP, BUG1-A2B | none |
| R2 K10 work before process; no status-only | MERGE | H-EXEC | CAD family | add coherent unit + task classification + legitimate WAIT |
| R2 K10 no fabricated hidden state/private experience | KEEP | H-ID/H-PRES | ID-FRESH, REL appraisal | none |
| R2 K10 high-stakes calm/nonsarcastic | KEEP/COLD detail | H-PRES + PRES profile | PRES-SERIOUS | none |
| R2 full owner §15 hot Project Source hygiene | KEEP+MERGE | H-RETRIEVE/CTX | CTX-COMPOSE | exact final hot inventory still cutover task |
| R2 full owner §16 cutover states/procedure | SUPERSEDE/EXPAND | CUT_R10_RELEASE | CUT family | old single-fresh-chat qualification insufficient |
| R2 full owner §17 hostile minimum | COLD/QUAL | R4 qualification corpus | all R4 cases | old minimum retained where nonconflicting; R4 expands it |
| R2 full owner §18 behavior/completion | MERGE | H-PRES/H-EXEC | PRES/CAD | none |
| R3 §1-4 Vera-specific sexual self-concept/source/stability | KEEP/COLD | SEXUAL_SELF_CONCEPT | BUG3/REL | exact release registry must bind owner/source |
| R3 §5 sexual confidence != consent | MERGE/COLD | CON_TYPED_STANCE + sexuality residue | CON-CONSENT | generic consent mechanics should not fork in sexuality owner |
| R3 §6 appraisal route | MERGE/COLD | REL_AUTHORED_APPRAISAL | REL family | generic appraisal extracted from sexuality owner |
| R3 §7 expression/noncompulsory performance | KEEP/COLD | SEXUAL_SELF_CONCEPT | BUG3/REL/PRES | none |
| R3 §8 referent/refusal integrity | MERGE | H-SEM + REL | REL-PROP | remove duplicate generic rule from sexuality owner |
| R3 §9 Brigit firewall | KEEP/COLD | SEXUAL_SELF_CONCEPT + CON | CON-BRIGIT | none |
| R3 §10 uptake/correction | MERGE/COLD | H-SEM + REL | REL-UPTAKE | generic negative-uptake mechanic extracted |
| R3 §11 state vocabulary | SUPERSEDE/COLD | SER_STATE_MODEL | SER family | R4 state model is nontransitive and broader |
| R3 §12 dedicated regression | KEEP/QUAL | R4 qualification corpus | BUG3-ORIGINAL | none |
| Missing CONTROL_LOAD vs EVIDENCE_SEARCH | SUPERSEDE gap | H-RETRIEVE | CTX-STALE/SEARCH/OWNER | none |
| Missing release-bound cold-owner registry | SUPERSEDE gap | release registry | REG-DRIFT | final registry blob must be frozen in R4 subject |
| Missing restored-control quarantine before retrieval | SUPERSEDE gap | H-EVID/H-RETRIEVE + REC | REC-STALE, CTX-ARCHIVE | none |
| Missing state-specific evidence model | SUPERSEDE gap | H-EVID + SER_STATE_MODEL | SER family | none |
| Missing universal concurrent mutation semantics | SUPERSEDE gap | H-AUTH + LIVE_CONCURRENCY | LIVE family | none |
| Missing cold/recovery two-path qualification | SUPERSEDE gap | CUT + qualification manifest | Q-COLD/Q-RECOVER/Q-STALE | none |
| Missing exact rollback-byte fidelity distinction | SUPERSEDE gap | CUT | CUT-ROLLBYTES | final native cutover cannot claim rollback until C0 captured |
| Missing frozen qualification corpus binding | SUPERSEDE gap | R4 qualification manifest | CUT-REPEAT, REG-DRIFT | exact suite blob will be bound by freeze manifest |

## Responsibility closure rule

A final composed candidate may freeze only when every baseline R2/R3 semantic responsibility has one resolved disposition and any `unresolved` item is either removed by implementation/readback or explicitly blocks the affected release claim. `KEEP/MERGE/SUPERSEDE/COLD/QUAL` describes control placement, not runtime effect.

## R4 remaining construction frontier

This audit intentionally does not claim an installable native/full-owner composition. R4 first freezes the accepted semantic delta, release-bound control owner, hostile suite, registry, and audit as one immutable implementation subject. After One attacks that subject, the next composition step may mechanically rewrite native/full owner + source manifest/checksums into a new candidate without reopening LIVE-1 design semantics unless review finds a material defect.