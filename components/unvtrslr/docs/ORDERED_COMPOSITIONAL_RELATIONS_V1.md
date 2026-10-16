# Ordered Compositional Relations V1

Status: `STRUCTURAL_GROUNDING_CANDIDATE / ADJACENT_BIGRAM_ORDER_ONLY`

## Problem

The existing reference translator can ground individual frozen acoustic units to operational context relations. That is necessary but not enough.

If a translator treats a sequence as only a bag of grounded units, then `A B` and `B A` can collapse to the same output even when order changes the operational meaning.

V1 does not assume human syntax. It asks a narrower falsifiable question:

> Does the ordered adjacent pattern AB carry a reproducible operational distinction that the reverse pattern BA does not?

## Input and provenance

V1 consumes `Episode` objects whose signal field already contains frozen global acoustic unit IDs.

Training binds the resulting order model to:

- exact translator model ID;
- exact acoustic model ID;
- exact valid global-unit vocabulary.

Unknown training tokens fail closed.

## Contrast design

For pair `A,B`, V1 compares episodes containing adjacent `A B` against episodes containing adjacent `B A`.

Episodes containing both directions or neither direction are not discriminating evidence.

For each opaque context atom V1 records:

- ordered support;
- reverse support;
- source coverage for both directions;
- replicated positive-source coverage;
- smoothed `P(atom | AB)`;
- smoothed `P(atom | BA)`;
- order effect;
- empirical binary mutual information.

## Default evidence gates

```text
min_ordered_support = 4
min_reverse_support = 4
min_order_source_coverage = 2
min_positive_sources = 2
min_positive_per_source = 2
min_probability = 0.75
min_effect = 0.40
min_information_bits = 0.05
ambiguity_margin = 0.08
```

If source 1 supplies AB while source 2 supplies BA, the result is `SOURCE_CONFOUNDED_ORDER_CONTRAST`.

If the positive AB relation does not replicate across enough sources, the result is `INSUFFICIENT_CROSS_SOURCE_REPLICATION`.

If two context atoms remain equally compatible with AB, V1 returns `AMBIGUOUS`.

## Frozen model

`OrderedRelationModel` stores only relations that survive those gates.

Its model ID binds the exact translator/acoustic lineage, thresholds, pattern, relation and evidence statistics.

The ID is an integrity checksum, not an authenticity signature. Reload separately verifies that every stored relation still satisfies its declared support, source-coverage, replication, probability, effect and information gates. Recomputing the hash cannot make an internally impossible relation valid.

## Translation

`translate_ordered_sequence()` scans adjacent global-unit pairs.

`translate_qualified_sequence()` composes:

1. held-out-qualified source profile;
2. frozen acoustic matching;
3. individual operational relations;
4. ordered AB-vs-BA relations.

If an acoustic position is unresolved, V1 refuses to silently bridge across that missing position and invent a shorter sequence.

## CLI

Fit:

```bash
unvtrslr-order fit translator.json ordered-training.jsonl > ordered-model.json
```

Translate global IDs:

```bash
unvtrslr-order translate-tokens ordered-model.json g_a g_b
```

Full qualified acoustic path:

```bash
unvtrslr-order translate-qualified \
  translator.json \
  qualified-source-profile.json \
  ordered-model.json \
  query-evidence.jsonl \
  --renderer renderer.json
```

## What this closes

V1 can distinguish an order-sensitive operational relation from:

- orderless token presence;
- absent reverse-order evidence;
- source-confounded ordering;
- one-source-only positive replication;
- ambiguous context interpretations;
- vocabulary drift;
- translator-lineage replay.

## What remains open

V1 is not a general grammar learner. It does not establish:

- arbitrary syntax;
- non-adjacent dependencies;
- recursion;
- morphology;
- agreement;
- constituent structure;
- discourse/pragmatics;
- prosodic grammar;
- universal compositionality.

## Claim ceiling

`ORDER_SENSITIVE_OPERATIONAL_RELATION_WITHIN_REFERENCE_FIXTURES`

The step forward is narrow but necessary: arrangement itself can now be tested as a candidate carrier of operational meaning rather than discarded by construction.
