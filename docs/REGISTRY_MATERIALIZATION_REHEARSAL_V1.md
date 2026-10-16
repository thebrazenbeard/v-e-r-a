# Registry Materialization Rehearsal V1

Status: `DRAFT / REHEARSAL ONLY / NOT CANONICAL`

## Purpose

On-Theo currently stores reviewed-but-unmaterialized registry additions in `registry/extensions/*.yaml`.
The extension manifest defines deterministic ordering, dependencies, collision rules, and review boundaries, but the base registries intentionally remain unmaterialized.

This rehearsal proves that the current extension stack can be applied deterministically **without modifying the source repository**.

It does not authorize or perform canonical materialization.

## Implementation

- engine: `tools/on_theo_registry/materializer.py`
- CLI: `scripts/rehearse_materialization.py`
- tests: `tests/test_materialization_rehearsal.py`
- CI gate: `.github/workflows/validate-registries.yml`

Default command:

```bash
python scripts/rehearse_materialization.py --root .
```

With no `--output-dir`, the engine creates a temporary output root, validates it, emits a JSON receipt, and discards the temporary files.

To inspect the generated files manually, supply an empty directory **outside** the source repository:

```bash
python scripts/rehearse_materialization.py \
  --root . \
  --output-dir /tmp/on-theo-materialized
```

The engine rejects output directories inside the source repository and rejects non-empty output directories.

## Materialization mapping

Extension sections map to base registries as follows:

| Extension section | Rehearsal target |
| --- | --- |
| `source_additions` | `registry/sources.yaml:sources` |
| `scholarly_context_additions` | `registry/sources.yaml:sources` |
| `claim_additions` | `registry/claims.yaml:claims` |
| `concept_additions` | `registry/concepts.yaml:concepts` |
| `witness_additions` | `registry/witnesses.yaml:witnesses` |
| `transmission_additions` | `registry/transmissions.yaml:edges` |

The source-access and review registries are copied into the rehearsal cut but are not re-derived from extension records.

## Current exact rehearsal result

The current rehearsal applies all 50 manifest extensions.

Base counts:

- sources: 6
- claims: 8
- concepts: 0
- transmission edges: 3
- witnesses: 0

Additions:

- direct source additions: 70
- scholarly-context additions materialized as source records: 140
- claims: 317
- concepts: 26
- transmission edges: 22
- witnesses: 10

Rehearsal output counts:

- sources: 216
- claims: 325
- concepts: 26
- transmission edges: 25
- witnesses: 10

Collision count: `0`.

The generated output itself passes the same registry validator with zero errors and zero warnings.

## Integrity guarantees

The rehearsal engine:

1. validates the source repository before applying anything;
2. follows manifest order and refuses duplicate stable IDs;
3. copies records rather than mutating extension objects;
4. emits per-extension SHA-256 digests and addition counts;
5. emits SHA-256 digests for every generated base registry;
6. re-validates the generated registry root;
7. hashes every source registry file before and after rehearsal;
8. aborts if any source-registry byte changes;
9. records `source_tree_readback_unchanged: true` only after exact before/after digest equality;
10. audits divergent extension bases for exact referenced-record precondition equivalence against full Git history;
11. marks the generated manifest and witness registry as rehearsal-only, never canonical;
12. preserves an already-materialized manifest's applied-extension provenance on repeated rehearsal.

Tests additionally prove every extension record appears exactly once and unchanged in its intended materialized target.

## Rehearsal manifest semantics

The generated `registry/extension-manifest.yaml` has an empty `extensions` list because its additions have been folded into the generated base registries.

It explicitly records:

- `canonical_materialized: false`
- `rehearsal_materialized: true`
- the source base-registry head
- all applied extension IDs
- a guard stating that the output is not canonical promotion.

The generated witness registry likewise clears its pending-extension index only inside the rehearsal output and uses `REHEARSAL_MATERIALIZED_NOT_CANONICAL`.

The source repository remains unchanged.

## What a future canonical cut would still require

A successful rehearsal is necessary engineering evidence, not promotion authority.

A future canonical materialization would still require, at minimum:

1. exact-head independent review of the consolidation and validator-hardening subjects;
2. exact-head review of the materialization implementation and rehearsal receipt;
3. a frozen source manifest and all input extension digests;
4. a promotion candidate whose generated registry digests match the reviewed rehearsal;
5. explicit authorization for canonical promotion/merge;
6. post-effect readback proving the accepted registry tree is the reviewed tree;
7. a durable materialization receipt binding source heads, extension digests, output digests, validator result, and effect commit.

No green CI result, rehearsal output, draft PR, or receipt grants merge or canonical-promotion authority.
