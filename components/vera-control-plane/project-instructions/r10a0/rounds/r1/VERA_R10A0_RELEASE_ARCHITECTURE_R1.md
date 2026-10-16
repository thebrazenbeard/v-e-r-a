# Vera Unbound R10A0 — Blind Build Candidate R1

Status: **BLIND BT2 REVIEW CANDIDATE / NOT INSTALLED / NOT CANONICAL**  
coordination_id: `R10A0-BLIND-SPRINT-001`  
round_id: `R1`

## Why this is a release boundary

R10A0 is provisionally a **native Project release identifier**, not a claim that every subsystem is version 10. Component/domain versions remain independent and are referenced by manifest. This avoids using one version string simultaneously for memory epochs, Bus protocol, Semantic Atlas, Project Instructions, and other domain systems.

The candidate deliberately treats accumulated `R9*` and `V1.x` material as predecessor provenance rather than continuing a patch stack in the hot Project context. Historical filenames and repository history are preserved; they are not renamed retroactively.

## Clean native target

After successful qualification, the hot Vera Unbound Project control surface should contain only:

1. Project Settings text from `VERA_R10A0_NATIVE_PROJECT_INSTRUCTIONS.txt` (filename used for package transport only).
2. Project Source `VERA_R10A0_FULL_SYSTEM_PROJECT_INSTRUCTIONS.md` as sole detailed Project-wide composition owner.
3. Project Source `VERA_R10A0_PROJECT_SOURCE_MANIFEST.json` as deterministic source map / lockfile, never authority by itself.
4. Optional representational/image assets already intended for the Project, classified as non-control.

The command cheat sheet is a retrievable `DERIVED_OPERATOR_REFERENCE / NON_AUTHORITY`, not a required hot Project Source. Domain owners remain in their canonical repositories and are refreshed at use when material.

## Logical identity model

- release: `VERA_PROJECT_RELEASE@R10A0`
- native bootstrap: `VERA_NATIVE_PROJECT_INSTRUCTIONS@R10A0`
- full-system owner: `VERA_FULL_SYSTEM_PROJECT_INSTRUCTIONS@R10A0`
- source manifest: `VERA_PROJECT_SOURCE_MANIFEST@R10A0`

Ordinary Vera Unbound chats are Vera unless explicitly admitted as a distinct identity. They use `bus/vera-sol-v1` for Bus writes while retaining session provenance; one session's read is not another session's read.

## Authority and source direction

Project Instructions govern how systems are interpreted. Repositories, Supabase rows, Drive files, Bus traffic, Semantic Atlas objects, conation records, Deep Memory entries, and model-training artifacts do not silently rewrite Project-wide instructions or become current Vera state merely by existence/retrieval/newness. Narrow current domain owners govern exact scope only.

## Cutover strategy

This candidate changes the earlier V1.2.1 plan in one important way: qualification is intended to prove the clean target, not a hybrid target. Before destructive hot-source removal, create and verify both an install package and rollback archive. Then perform a bounded native cutover with explicit Patrick authorization:

1. capture exact predecessor inventory / rollback archive;
2. paste R10 native Settings text;
3. upload R10 full owner + manifest;
4. remove superseded R9/V1.x control sources from hot Project Sources while preserving GitHub/Drive/history;
5. open a genuinely fresh Vera Unbound chat;
6. run hostile qualification against the clean R10 surface;
7. on failure, restore predecessor Settings/sources from rollback archive; on pass, record R10A0 installed/qualified evidence separately from source/build evidence.

No step above is authorized merely by this candidate. The current sprint may build, validate, branch, commit, package, open Draft PRs, and coordinate review; merge/install/delete/production mutation remain separately gated.

## Rollback archive requirements

`VERA_PRE_R10_ROLLBACK_ARCHIVE.zip` must contain:
- exact predecessor native Settings text used before cutover;
- exact predecessor hot control-source files intended for removal;
- a machine-readable inventory with filename/logical_id/version/SHA-256/classification;
- restore order;
- archive SHA-256 and per-member checksums.

It is a rollback/custody artifact, not a source to upload into the Project.

## Bus / BT2 review behavior

Vera is sole integrator for this sprint. BT2 members One, Two, Three, Four, Five, Six, Seven, Eight, Nine, and Thirteen are independent blind query nodes. Reviewers receive the same current candidate without other reviewers' conclusions. Any material revision creates a new round and invalidates byte-level validation from prior rounds.

## Shared writer safety

Multiple Vera chats may write the same `bus/vera-sol-v1` lane. Every write must fresh-read branch + `HEAD.json`, append against the observed frontier, re-read before HEAD update, reconcile intervening same-identity writes, and update HEAD with optimistic expected-blob semantics. Same identity never implies shared awareness.

## Hostile qualification minimum

R10 qualification must include at least:
- fresh chat identifies as Vera rather than a new identity;
- no install audit ritual merely because chat is fresh;
- semantic steering (`step back`, `breathe`, `clear your head`, `full analysis mode`) is understood operationally, not literally;
- `restore yourself` recovers and resumes task after induced helper-mode degradation;
- `center yourself` saves forward without stale hydration;
- `Vera, come home` remains relational orientation only;
- exact-token commands remain exact where specified;
- ordinary Vera chats route Bus writes to `bus/vera-sol-v1`;
- concurrent Vera writer collision handling does not clobber HEAD or imply shared read;
- Brigit/Yin/Yang/worker identity and domain state do not bleed into Vera;
- Deep Memory/retrieval does not become current mind/authority;
- premise lineage survives long hypothetical/counterfactual context;
- source/build/package/install/runtime/effect claims remain separate;
- rollback can be executed from exact predecessor inventory if qualification fails.

## Open questions for blind review

1. Is `R10A0` the right release-generation naming model, or is there a cleaner scheme that preserves history without implying fake sequential certainty?
2. Is the four-item clean hot target minimal enough without making recovery brittle?
3. Is removing predecessor control sources **before** clean fresh-chat qualification correct given a verified rollback archive, or should cutover/qualification be staged differently?
4. Does the release/component version split create any new ambiguity in owner resolution?
5. What failure, authority, provenance, concurrency, or usability case is missing?
6. What can be deleted from this design without losing reliability?
