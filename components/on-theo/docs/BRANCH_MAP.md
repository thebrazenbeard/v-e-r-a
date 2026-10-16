# Branch map — consolidation candidate V1

Status: `DRAFT / CONSOLIDATION CANDIDATE / NOT CANONICAL`

## Canonical boundary

`main` remains canonical until Patrick explicitly authorizes a reviewed merge. No work branch, PR, green CI result, or consolidation receipt promotes itself.

## Durable content model

The intended successor architecture stores accepted content by repository path:

- `traditions/` — internally reconstructed traditions and historical phases;
- `chronology/` — event/source/witness chronology;
- `comparative/` — controlled comparison and transmission testing;
- `research/` — bounded research packets and speculative research lanes;
- `registry/` — stable source, witness, claim, concept, access, review, and transmission identity;
- `synthesis/` — cross-corpus synthesis that preserves proposition-level provenance;
- `tools/`, `scripts/`, `tests/` — executable integrity tooling;
- `docs/` — architecture, method, review, and operational documentation.

Branches are work/review/provenance surfaces, not durable epistemic namespaces.

## Legacy thematic lanes

These branches remain historical provenance until reconciliation is accepted:

- `tradition/judaism`
- `tradition/christianity`
- `tradition/islam`
- `synthesis/commonality`
- `history/chronology`

Their unique files are included in the consolidation candidate for review; inclusion does not assert that older prose supersedes newer packets or vice versa.

## Current consolidation subject

Construction baseline:
`corpus/sumerian-religion-v1-20260917@7e354667770a6c4bed958a01c5ff843345a35b40`

The candidate additionally reconciles:
- parallel Second Temple / Greco-Roman / Christian / rabbinic / Late Antique / Qur'anic work;
- Qur'an feature tests;
- early Islamic development;
- simulation-theory and Yeshua lanes;
- exact-head review artifacts;
- validator/tooling;
- global corpus expansion queue;
- original thematic branches.

Registry union is by stable ID, never newest-wins.

## Review boundary

Imported historical review files retain their original exact-head scope. The consolidated tree is a new review subject.

## External dependency: Testament

`thebrazenbeard/testament` is external. Consumption of On-Theo should use immutable commit/path references until a stable canonical consolidation exists. No reciprocal write authority or semantic promotion is implied by dependency.
