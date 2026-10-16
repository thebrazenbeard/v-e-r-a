# Multiword Target Constructions V1

Status: `TARGET_CONSTRUCTION_CANDIDATE / EXACT GROUNDED SEQUENCE REALIZATION`

## Problem

The learned target-grounding layer removes the hand-authored atom-to-word dictionary for supported single target tokens.

That still does not produce a general target-language utterance.

A target language may realize one operational distinction with several words, may require function-like tokens that have no one-to-one source counterpart, and may order target material differently from the source operational sequence.

V1 learns those constructions from grounded sequence demonstrations instead of inserting a human grammar.

## No built-in grammar

V1 has no part-of-speech inventory, English word-order rule, morphology table, determiner rule, case grammar, or constituency parser.

A construction example contains only:

- unique episode ID;
- target-side source ID;
- an **ordered operational semantic sequence**;
- the **observed target token sequence**.

Examples the same machinery may learn include:

```text
[action:moved-left]
    -> ["moved", "left"]
```

```text
[ctx:red, shape:square]
    -> ["the", "red", "square"]
```

and target-specific reordering:

```text
[agent:alice, action:sees, patient:bob]
    -> ["bob", "ACC", "alice", "NOM", "sees"]
```

The architecture does not know that `ACC` or `NOM` are case markers. They are simply repeated target tokens in a grounded construction.

## Exact semantic-sequence key

The semantic pattern is a tuple, not a set.

Therefore `[ctx:red, shape:square]` and `[shape:square, ctx:red]` are different candidate constructions.

They may learn the same target realization, different realizations, or remain unresolved independently.

This is the target-side ordering mechanism in V1: preserve the exact operational sequence and exact observed target sequence. No target-language order is inserted by rule.

## Replication gate

A candidate construction is grouped by:

`(ordered semantic pattern, ordered target token sequence)`

and freezes only when its exact realization receives repeated positive evidence from enough target-side sources.

Defaults:

```text
min_sources = 2
min_positive_per_source = 2
```

A construction seen repeatedly from one source does not freeze.

## Multiple valid constructions

If several target token sequences independently survive the replication gates for the same semantic pattern, V1 returns:

`MULTIPLE_TARGET_CONSTRUCTIONS_SUPPORTED`

It does not silently select one variant.

## Unknown patterns

If an ordered semantic sequence has no frozen construction, V1 returns:

`UNKNOWN_TARGET_CONSTRUCTION`

There is deliberately no fallback that concatenates individually grounded words, copies source order, or invokes a built-in English grammar.

## Qualified acoustic composition

`operational_semantic_sequence()` converts a held-out-qualified source query into a positional semantic sequence while preserving original position, repeated atoms, and unresolved positions.

It does not use the deduplicated relation list exposed by earlier convenience translation surfaces.

If any acoustic position lacks a frozen semantic relation, the construction path remains unresolved.

`translate_qualified_construction()` then applies the exact learned target construction.

## Lineage binding

The construction model binds:

- target language ID;
- exact upstream model IDs;
- exact semantic namespace;
- construction replication thresholds;
- every frozen semantic-pattern / target-token-sequence pair;
- support and source-coverage evidence.

The CLI normally binds the construction model to the exact reference translator, exact learned target-grounding model, and optional exact ordered-relation model.

## Integrity

The construction model ID is a content-derived integrity/provenance checksum, not an authenticity signature.

Reload independently verifies canonical IDs and namespace, canonical construction ordering, namespace membership, nonempty tokens/patterns, source replication floors, and support/source-count consistency.

## CLI

Fit from grounded construction demonstrations:

```bash
unvtrslr-construct fit \
  translator.json \
  target-model.json \
  construction-training.jsonl \
  --ordered-model ordered-model.json \
  > construction-model.json
```

A training line:

```json
{"episode_id":"target-demo-001","source_id":"target-speaker-A","semantic_atoms":["ctx:red","shape:square"],"target_tokens":["the","red","square"]}
```

Render a known semantic pattern:

```bash
unvtrslr-construct render construction-model.json ctx:red shape:square
```

Compose with a held-out-qualified source:

```bash
unvtrslr-construct translate-qualified \
  translator.json \
  qualified-source-profile.json \
  target-model.json \
  construction-model.json \
  query-evidence.jsonl
```

## What V1 closes

Within its reference scope V1 removes three hidden assumptions:

1. one semantic atom need not equal one target token;
2. source order need not equal target order;
3. target function-like material need not be hand-inserted.

## What V1 does not yet solve

V1 is a construction memory with evidence gates, not a productive grammar inducer.

It does not yet generalize an unseen combination by learning reusable slots, inflectional paradigms, agreement, long-distance dependencies, recursion, constituent structure, probabilistic target generation, or discourse-level realization.

An unseen semantic sequence remains unknown even if its individual pieces were seen elsewhere.

## Claim ceiling

`MULTIWORD_TARGET_CONSTRUCTION_WITHIN_GROUNDED_REFERENCE_SCOPE`

V1 demonstrates evidence-bound multiword realization and target-specific ordering for previously grounded semantic sequences. It does not establish general target grammar, fluent natural-language generation, universal translation, or production readiness.
