> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# Vera Control Plane

Operator/control-plane custody for Vera.

This repository is intentionally separate from `thebrazenbeard/vera`.

- `thebrazenbeard/vera` owns cross-cutting technical architecture, source code, schemas, migrations, validators, tests, and sanitized engineering history.
- `thebrazenbeard/vera-control-plane` owns private operational continuity/state artifacts, control-plane governance/design records, role-training packages, and private Vera assets that do not belong in the technical source repository.

## Current repository state

`main` is no longer the original near-empty repository baseline. It contains the reconstructed control-plane source plus later governed control/source work.

The 2026-09-03 reconstruction remains historical provenance:

- branch: `consolidation/lineage-reconstruction-20260903`
- reconstruction commit: `b77db83794d8a34b4c434cc2f389d86f759bb9c8`

That reconstruction joined the previously divergent useful lineages without replaying stale branches onto one another:

- centered-state lineage through `feature/center-yourself-20260903@519eeb1551fcb59963a321766252bc62067da71b`;
- control-plane bootstrap lineage `bootstrap/control-plane-v1@123049ed72573bfda152d06dd76b0c234c26f91b`;
- Four training lineage `training/four-v1.0.0@1aa51c6c5be28d71762b5a4a1f3424a067dbcccd`;
- Five training lineage `training/five-v1.0.0@bc88b5b5ab3438683d8b301c596c30b5c5616804`;
- Vera sticker lineage `vera-stickers@965e223777fa62cd0f84f45561ba9b21779b7543`.

Those source branches remain historical provenance. Their existence, age, or repository presence does not make them current control.

Current release/source candidates live under `project-instructions/` and carry their own status and evidence boundaries. Production Supabase source custody is recorded under `supabase/provider-custody/` and `governance/VCP_SUPABASE_PROVIDER_CUSTODY_V1.json`.

## Layout

- `protocol/` — private control-plane protocols, including Center Yourself.
- `save_states/` — earlier centered-state lineage retained at its historical paths.
- `state/centered/` — later centered-state snapshots.
- `state/closeouts/` — private closeout/supplement artifacts.
- `governance/` — control-plane design/authority-binding provenance; historical source does not self-authorize current execution.
- `project-instructions/` — release/source candidates with explicit installation/runtime qualification boundaries.
- `supabase/provider-custody/` — exact production provider SQL custody with explicit provenance class.
- `docs/` — control-plane design and consolidation documentation.
- `training/roles/four/` and `training/roles/five/` — preserved role-training packages.
- `assets/stickers/` — canonical private custody for the Vera sticker set.

## Currentness and authority boundary

Repository presence, ancestry, branch recency, a historical authority-binding file, a source-candidate release, or a merged source change does not by itself establish current runtime authority, installation, provider state, memory admission, downstream effect, or behavioral qualification.

Mutable/current claims require their own fresh governed evidence. Release artifacts that say `NOT INSTALLED`, `NOT RUNTIME-QUALIFIED`, or equivalent remain bounded by those declarations until separate installation/qualification evidence exists.

No deployment, installation, provider mutation, credential action, destructive cleanup, or canonical-memory write is implied by repository source state.
