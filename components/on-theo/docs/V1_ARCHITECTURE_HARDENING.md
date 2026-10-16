# On-Theo V1 Architecture Hardening

Status: `DRAFT / SUCCESSOR CUT / REVIEW REQUIRED`
Base research head: `625272e016fce6fede9531e4ca1bbab315345d69`
Triggering review head: PR #5 `48a202a2f974f28c4a7484adb5066ed3b1410473`

## Purpose

This cut addresses the architecture defects found by the PR #1 Hephaestus role-pass without rewriting the frozen PR #1 review subject or pretending that later fixes retroactively change its review result.

## Defect-to-repair map

### H-A1 — source/work and physical-witness identity collapsed

Repair: `registry/witnesses.yaml` defines a distinct witness entity with `witness_of`, witness-specific date/provenance/access, and a claim-edge invariant requiring `witness_id` when a proposition depends on a witness-specific reading.

Existing research already demonstrates the need:

- `WIT-TOSEFTA-VIENNA-COD-HEBR-20` in `EXT-PANTHERA-RABBINIC-PARALLELS-V1`;
- `WIT-P45-MARK-6-3` in `EXT-MARK6-MATRONYMIC-V1`.

The canonical witness registry remains unmaterialized while those extensions are draft. This prevents duplicate-ID laundering while still establishing the entity contract.

### H-A2 — exact-head reviews are not machine-queryable

Repair: `registry/reviews.yaml` defines machine-readable review receipts and immediately records the three PR #1 role-passes with actual execution provenance.

The key semantic guard is explicit: role separation does not imply independent model sampling.

### H-A3 — lost-source identity vs direct access under-specified

Repair: `registry/source-access.yaml` separates source identity from access/preservation state. In particular, Celsus's lost *True Doctrine* can remain a source identity while being marked `direct_access: false` and `INDIRECT_PRESERVATION` through Origen.

### H-A4 — stacked registry extensions lack deterministic application/currentness

Repair: `registry/extension-manifest.yaml` fixes application order, dependency semantics, base-head rules, duplicate-ID handling, unknown-reference failure, patch/CAS requirements, review invalidation, and materialization receipts.

The current stacked chain is recorded explicitly:

`EXT-PANTHERA-RABBINIC-PARALLELS-V1`
→ `EXT-MARK6-MATRONYMIC-V1`
→ `EXT-JOHN8-41-PORNEIA-V1`.

No extension is promoted merely because it appears in the manifest.

### H-A5 — empty concept registry can be mistaken for complete coverage

Repair: `registry/concepts.yaml` gains an explicit coverage/completeness state. An empty list means the contract exists but V1 concept population is incomplete; it does not mean no relevant linguistic/theological concepts exist.

## Review-provenance hardening

`docs/REVIEW_PROTOCOL_V2.md` adds execution provenance as a first-class review property. This resolves a coordination ambiguity encountered during the PR #1 review loop: Masa, Mune, and Hephaestus can be executed as distinct analytical role-passes in one controlling model/runtime, but those outputs must not be represented as three independent samples or terminals.

V2 also adds an explicit `ARCHITECTURE_INTEROPERABILITY` gate for registry/control-plane changes.

## What this cut does not do

- It does not merge PR #1, #2, #3, #4, or #5.
- It does not materialize stacked registry extensions into canonical `main` registries.
- It does not claim that the PR #1 Hephaestus review now passes; that review remains `CHANGES_REQUIRED` on its frozen exact head.
- It does not change the evidentiary status of Panthera/Pandera, Mark 6:3, John 8:41, or the rabbinic parallels.

A new exact-head architecture review is required for this successor cut.