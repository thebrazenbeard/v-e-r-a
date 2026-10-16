# On-Theo V1 Research Integration Implementation Plan

**Goal:** Build a reviewable provenance-aware integration spine for On-Theo while preserving existing research lanes and beginning primary-source deepening.

**Architecture:** Add stable registries and review contracts on an isolated branch; seed them with a Panthera/Celsus/Origen packet; then obtain orthogonal architecture, hostile, and citation-readback reviews before any promotion to `main`.

**Tech Stack:** Markdown, YAML, Git/GitHub pull requests, external primary/scholarly source locators.

**Spec:** `docs/V1_ARCHITECTURE.md`

## Global constraints

- No automatic merge of tradition/history/synthesis branches.
- No merge to `main` without Patrick's exact authorization.
- Preserve the eight project evidence classes exactly.
- Keep source statement, historical reconstruction, scholarly interpretation, project inference, and speculative model separate.
- Exact-head review does not transfer across material head movement.

---

### Task 1: Integration architecture and review contract

Create `docs/V1_ARCHITECTURE.md` and `docs/REVIEW_PROTOCOL_V1.md`.

Verification: read back both files from the exact branch head and confirm evidence classes, three-clock chronology, exact-head review, external-repo boundaries, and no merge authorization are explicit.

### Task 2: Seed canonical registries

Create:
- `registry/sources.yaml`
- `registry/claims.yaml`
- `registry/concepts.yaml`
- `registry/transmissions.yaml`

Verification: parse all YAML; confirm every source/claim/transmission reference resolves; confirm `evidence_class` and `claim_type` are distinct fields.

### Task 3: Panthera source-deepening packet

Create `research/packets/panthera-celsus-origen-v1.md` from checked primary and scholarly sources.

Verification:
- Origen I.28 = broader illegitimacy/adultery accusation;
- Origen I.32 = named soldier Panthera;
- Origen I.69 = same-work repetition, not independent witness;
- Abdes Pantera inscription = name/person attestation only;
- Shabbat 104b = Stada/Pandeira/Miriam complex, no automatic Jesus identification;
- Blumell/Niehoff = attributed scholarly interpretations.

### Task 4: Draft PR and independent reviews

Open a draft PR against `main` and mirror it on the current Bus.

Route orthogonal exact-head requests:
- Masa: hostile falsification/overclaim review.
- Mune: citation readback and registry correspondence.
- Hephaestus: architecture/interoperability review.

Verification: Bus messages use current ACTIVE topology routes; no absent/inert identity is addressed.

### Task 5: Reconcile findings

After replies exist, ingest findings, repair only supported defects, and invalidate/re-request any review whose exact subject materially changes.

No merge is included in this plan.
