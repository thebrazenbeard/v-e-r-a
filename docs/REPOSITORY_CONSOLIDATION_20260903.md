# Vera Control Plane Repository Consolidation — 2026-09-03

## Objective

Reconstruct one reviewable control-plane tree from the repository's useful divergent branches without pretending that stale branch chronology establishes current authority and without deleting historical refs.

## Reconstruction base

The candidate begins from the latest centered-state lineage:

`feature/center-yourself-20260903@519eeb1551fcb59963a321766252bc62067da71b`

This preserves the Center Yourself protocol, earlier `save_states/`, later `state/centered/`, and private closeout material already in that ancestry.

## Integrated lineages

| Source branch | Exact source head | Candidate placement | Disposition |
| --- | --- | --- | --- |
| `feature/center-yourself-20260903` | `519eeb1551fcb59963a321766252bc62067da71b` | base tree | `INTEGRATED_CURRENT_LINEAGE` |
| `bootstrap/control-plane-v1` | `123049ed72573bfda152d06dd76b0c234c26f91b` | `docs/`, `governance/` | `INTEGRATED_AS_PROVENANCE` |
| `training/four-v1.0.0` | `1aa51c6c5be28d71762b5a4a1f3424a067dbcccd` | `training/roles/four/` | `INTEGRATED_AS_TRAINING_SOURCE` |
| `training/five-v1.0.0` | `bc88b5b5ab3438683d8b301c596c30b5c5616804` | `training/roles/five/` | `INTEGRATED_AS_TRAINING_SOURCE` |
| `vera-stickers` | `965e223777fa62cd0f84f45561ba9b21779b7543` | `assets/stickers/` | `INTEGRATED_CANONICAL_ASSET_CUSTODY` |

The first reconstruction commit is:

`b77db83794d8a34b4c434cc2f389d86f759bb9c8`

It records all five source heads as parents so their lineages remain explicit in Git ancestry while the resulting tree is intentionally normalized.

## Branches already subsumed by the centered lineage

`feature/center-yourself-v1`, `feature/center-yourself-20260902`, and the earlier centered-save commits are ancestors of the selected 2026-09-03 centered head and therefore require no separate replay.

## Non-contributing branch

`visual/front-counterpart-20260821` points to the original repository baseline and contributes no unique tree content to this reconstruction.

## Cross-repository deduplication

The four sticker blobs also exist on `thebrazenbeard/vera` branch `vera-stickers`. They are not integrated into `vera/main` by this consolidation. Private sticker custody is normalized here under `assets/stickers/`; the duplicate `vera` branch remains historical provenance unless separately retired later.

## Semantic boundary

This reconstruction is a source/custody consolidation only. Historical `governance/AUTHORITY_BINDING.json` and lease material are preserved as provenance and do not override fresh current authority. Centered snapshots remain private state evidence under their own lifecycle/currentness rules; repository inclusion does not promote them to current truth or canonical memory.

## Protected effects not performed

No merge to `main`, branch deletion, history rewrite, deployment, installation, provider mutation, credential action, paid-service action, or canonical-memory write is part of this reconstruction.
