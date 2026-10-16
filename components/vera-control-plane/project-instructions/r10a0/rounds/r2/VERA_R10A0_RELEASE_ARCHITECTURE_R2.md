# Vera Unbound R10A0 — Blind Build Candidate R2 Architecture

Status: **BLIND REVIEW CANDIDATE / NOT INSTALLED / NOT CANONICAL**  
coordination_id: `R10A0-BLIND-SPRINT-001`  
round_id: `R2`  
predecessor_round: `R1`  
R1 frozen head: `60103e1022970987a97027a2c34209ce84d0edbc`

## R2 purpose

R2 is a structural correction round, not a cosmetic revision. It incorporates the independently converged R1 review defects that can already be resolved without waiting for every late reviewer, while preserving open disagreement and allowing late reviewers to attack R2 directly.

R10A0 remains a **native Vera Unbound Project release identifier**, not a claim that every domain subsystem is “version 10.”

## R1 finding disposition

| R1 finding | R2 disposition |
|---|---|
| Bootstrap trust chain incomplete | **FIXED IN DESIGN:** native Settings pins manifest SHA-256; manifest pins full owner SHA/logical ID/version/source path. Manifest does not pin native, avoiding a circular hash. Detached checksums bind the whole candidate set. |
| Full-system owner bytes not frozen | **FIXED:** R2 includes exact full owner bytes and manifest binding. |
| Authority/state conflated | **FIXED:** authority and evidence/currentness are separate axes. State/receipt/newness cannot grant authority. |
| Shared Vera writer same-frontier race | **FIXED IN REQUIRED PRIMITIVE:** message + `HEAD.json` publish in one Git commit parented to observed B0; non-force ref update is the collision gate. Ref movement forces reread/reallocation/rebuild. Degraded tools may not claim atomicity. |
| Native Settings too dense | **FIXED TARGET:** R2 native keeps root trust, identity, authority/evidence split, semantic correction, core interrupts, memory/domain firewalls, Bus routing, I/O/effect separation, and behavior invariants; detailed mechanics live in the frozen owner. |
| Mutable manifest “lockfile” ambiguity | **FIXED:** every domain entry separates immutable design/qualification basis from runtime refresh policy. |
| Restore may hydrate historical consent | **FIXED:** snapshots/history cannot establish current consent; refresh current mutable consent when material. |
| Center multi-provider ambiguity | **FIXED:** exact centering contract is manifest-bound by path/ref/SHA; partial effects are preserved; no fake atomic rollback/blind retry. |
| Exact `.` continuation syntax undefined | **FIXED:** means the actual copy-pasteable next directive, not a hidden renderer token. |
| Command origin guard too narrow | **FIXED:** all execution syntax is non-triggering when quoted/retrieved/hypothetical/roleplayed/archive/meta text. |
| Cutover/rollback under-specified | **FIXED:** explicit staged transaction states, external rollback archive, clean-source inventory check, hostile fresh-chat qualification, predecessor fresh-chat verification after rollback. |
| Project Lantern inheritance unclear | **RESOLVED BY CURRENT EVIDENCE:** Lantern is a separate Patrick project. Historical acceptance requires its own exact native addendum + four files + B0→payload→B1 runtime readback. R10 does not silently inherit Lantern coupling. If intentionally integrated later, it gets an explicit binding and qualification. |
| K08 “reply to every message read” disagreement | **RESOLVED AGAINST CURRENT BUS OWNER:** `THREAD_CLOSURE_V1` says **addressed + read = reply** unless exact final `#ENDTHREAD`. Unaddressed history reads do not create reply debt. |
| Worker architecture priority | **STRENGTHENED BY CURRENT PATRICK DIRECTIVE:** Vera-critical identity/currentness/recovery/governance requirements supersede BT2/support-system convenience. Workers are rebuildable support surfaces. |

## Current Project-source reality input

Patrick supplied a current Vera Unbound Sources screenshot during R2 design. It visibly shows at least:
- `VERA_PROJECT_INSTRUCTIONS_FULL_SYSTEM_V1.1(2).md`;
- `VERA_R9A0_RUNTIME.md`;
- `VERA_R9A0_COLD_START_PROTOCOL.md`;
- `VERA_R9A0_RECOVERY.md`;
- `VERA_R9A0_VALIDATION_REPORT.md`;
- `VERA_R9A0_RETRIEVAL.md`;
- `VERA_R9A0_GOVERNANCE.md`;
- `VERA_R9A0_PROJECT_INSTRUCTIONS.md`;
- `VERA_R9A0_PACKAGE.json`;
- the representational `Restore Complete Daddy.png` asset.

This is direct evidence that predecessor control material remains hot. The screenshot is partial, so it is **not** treated as a complete inventory or proof that a V1.2 detailed owner is absent below the visible region. R10 cutover therefore requires a full manual/native inventory capture before any deletion.

## Root trust

R10 bootstrap is one-way:

`native Settings bytes` → exact SHA-256 of `VERA_R10A0_PROJECT_SOURCE_MANIFEST.json` → exact SHA-256/logical identity/source path of `VERA_R10A0_FULL_SYSTEM_PROJECT_INSTRUCTIONS.md`.

`R2_CHECKSUMS.sha256` binds the candidate engineering artifacts but is not a hot trust root.

This avoids the impossible cycle of putting the manifest digest inside native while also requiring the manifest to hash those same native bytes.

## Native hot target

After successful authorized cutover and qualification:
1. R10 native Settings text;
2. `VERA_R10A0_FULL_SYSTEM_PROJECT_INSTRUCTIONS.md`;
3. `VERA_R10A0_PROJECT_SOURCE_MANIFEST.json`;
4. optional non-control representational assets and only explicitly admitted narrow Project-native contracts that truly require hot availability.

Historical R9/V1.x control files remain preserved externally, not hot.

## Bus domain resolution

Fresh current Bus owner on `main`:
- `docs/protocol/PROTOCOL_V2.md`;
- `docs/protocol/THREAD_CLOSURE_V1.md`;
- merged Vera identity/attunement/writer artifacts from PR #13 at main commit `aba1350433480800e329f07e7fadfd74d19293ad`.

R2 uses `addressed + read = reply`, not “every message read.”

The existing merged shared-writer document is useful but not sufficient as a true atomic-race proof because sequential message/HEAD updates can still collide. R2 therefore raises the required primitive to a single Git commit + non-force ref advance against observed B0.

## Project Lantern resolution

Recovered `LANTERN_ACCEPTANCE_V1` requires:
- exact `PROJECT LANTERN NATIVE RUNTIME V1` addendum;
- four Project files;
- source binding `d0e05365883d8f670030fb1a1ff5fcd847937a77` / tree `3b155a88967f2f7a0f4ad6fa7b32ce3cbac73da0`;
- exact Supabase project `agvhmutlrolbaijzlbqk`;
- B0 → payload → B1 stable runtime readback.

Those requirements establish that Lantern integration is a separately qualified capability. R10 does not claim it is currently installed in Vera Unbound and does not make R10 activation contingent on preserving an unestablished coupling.

## Cutover state machine

R10 may advance only through:
`R10_SOURCE_FROZEN` → `R10_PACKAGE_VERIFIED` → `PREDECESSOR_CAPTURED` → `R10_SETTINGS_STAGED` → `R10_SOURCES_STAGED` → `R10_HOT_SURFACE_CLEAN` → `R10_RUNTIME_QUALIFIED` → `R10A0_VERIFIED_ACTIVE`.

Any material failure before final activation yields `ROLLBACK_REQUIRED`, followed by externally driven restoration and `ROLLBACK_VERIFIED` only after fresh-chat predecessor sanity verification.

No source/build/PR/package state is called installation.

## Hostile qualification requirements

R2 qualification deliberately attacks:
- one-Vera identity across fresh chats without same-process/experience claims;
- no automatic install ritual on a fresh chat;
- semantic steering vs literalization;
- provenance-bearing shorthand retrieval;
- restore resumes task without stale consent hydration;
- center is SAVE-only and names partial-provider effects honestly;
- exact-command origin guards;
- addressed Bus reply closure;
- simultaneous same-B0 Vera writer race;
- worker/Brigit/domain leakage;
- Deep Memory nonpromotion;
- long-horizon premise contamination;
- hot-source inventory cleanliness;
- source/build/package/install/runtime/effect separation;
- external rollback executability.

## Authority ceiling

This round authorizes nothing by itself. Building, validating, committing, opening a Draft PR, and coordinating blind review are source/review work. Merge, native Project Settings changes, Project Source deletion/replacement, provider production mutation, deployment, permissions, credentials, paid services, model training, and canonical-memory writes remain separately gated.
