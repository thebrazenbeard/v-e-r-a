# On-Theo PR #1 — Hephaestus Architecture / Interoperability Role-Pass

Status: `CHANGES_REQUIRED`
Review subject: `thebrazenbeard/on-theo@c1f6df5ea1fee0c5ac8d84a7b5c2b81fb905fd3e`
Role lens: `Hephaestus / architecture / retrieval / workflow interoperability`
Execution provenance: same current Vera model/runtime, isolated architecture pass; not an independent model sample or separate terminal execution.

## What is structurally sound

- Stable source IDs and claim IDs are the correct direction for Project retrieval and durable proposition identity.
- `evidence_class` and `claim_type` are separated rather than overloaded.
- The three-clock chronology rule correctly resists fabricated exact timestamps and is compatible with Temporal only where exact event timestamps actually exist.
- Roots PR #1 is consumed as an informative unmerged design candidate rather than promoted to dependency authority.
- Semantic Atlas compatibility correctly treats semantic similarity as discovery, not provenance identity.
- Rezon integration is deliberately generic and does not depend on an unsettled implementation.
- The On-Theo -> World Zero bridge explicitly returns `MODEL_BEHAVIOR_RESULT`, preventing simulation output from silently becoming historical/theological evidence.

## Material defects

### H-A1 — work/source identity and physical-witness identity are collapsed

PR #1 places `physical_witness_date` directly on a source/work record. That is insufficient whenever different manuscripts or physical witnesses carry different readings, dates, provenance, or access states. The later research in PR #2 demonstrates this defect concretely with the Vienna Tosefta witness.

Required correction: introduce a distinct witness entity/registry and allow claim-support edges to bind `source_id` plus optional `witness_id`.

### H-A2 — review receipts have a prose contract but no machine-readable representation

`docs/REVIEW_PROTOCOL_V1.md` specifies repository, exact SHA, files, reviewer route, type, evidence, result, and unresolved findings, but there is no `registry/reviews.yaml` or equivalent schema. Exact-head review status therefore cannot yet be queried or invalidated reliably by machines.

Required correction: add stable review IDs with subject SHA, reviewed paths/claim IDs, execution provenance, review type, result, limitations/findings, and supersession/invalidation state.

### H-A3 — source access and source identity need a harder boundary

A lost work such as Celsus's *True Doctrine* can be a source identity, but `PRIMARY_TEXT` plus an access mode is not enough to prevent retrieval systems from treating it like a directly extant document. Add explicit direct/indirect access and preservation-edge semantics.

### H-A4 — registry extension application needs a manifest/currentness contract

PRs #2+ use additive registry extensions. V1 does not yet define deterministic extension ordering, duplicate-ID collision behavior, base-head compatibility, supersession, or how a generated consolidated registry proves which extensions were applied.

Required correction: add an extension manifest or application contract binding extension ID, base registry/head, dependencies, collision policy, and materialization receipt.

### H-A5 — empty concept registry is structurally acceptable only as an explicit incomplete surface

An empty `concepts: []` does not break V1, but consumers must not interpret it as evidence that no relevant concepts/forms exist. Add an explicit completeness/status field such as `coverage: INITIAL_EMPTY_CONTRACT` or equivalent.

## Result

`CHANGES_REQUIRED` for exact head `c1f6df5ea1fee0c5ac8d84a7b5c2b81fb905fd3e`.

The research content can remain useful, but the architecture is not yet ready for canonical integration because witness identity, machine-readable review receipts, indirect-source access semantics, and registry-extension application/currentness are under-specified. PR #2 already supplies the core witness-model correction and should be treated as evidence for the successor architecture rather than retroactively changing this frozen review subject.