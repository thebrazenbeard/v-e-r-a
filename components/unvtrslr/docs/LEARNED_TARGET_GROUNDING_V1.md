# Learned Target-Language Grounding V1

Status: `TARGET_RENDERING_CANDIDATE / GROUNDED_DEMONSTRATIONS_ONLY`

## Problem

Earlier reference paths accepted an optional renderer such as:

```json
{"ctx:red": "red", "shape:square": "square"}
```

That is useful for debugging, but it is not a completed translator. The source side may have learned an operational relation while the final target string is still supplied by a human-authored codebook.

V1 makes the target side evidence-bearing too.

A target-language token begins as an opaque token. It becomes a candidate realization of an operational atom only after repeated grounded target-language demonstrations survive the same style of support, probability, effect, information, ambiguity, and cross-source replication controls used elsewhere in the reference stack.

English is therefore not privileged in the architecture. `target_language_id` may identify any target realization system represented by grounded demonstrations.

## Target grounding episodes

Each `TargetGroundingEpisode` contains:

- unique episode ID;
- target-side source/speaker ID;
- one or more opaque target tokens;
- simultaneously observed context atoms.

The learner receives no target dictionary.

Internally, target tokens are passed through the cross-situational `BridgeLearner`. A token is frozen only if its leading context relation:

- survives the bridge support/probability/effect/information/ambiguity gates;
- belongs to the exact declared semantic namespace;
- has repeated positive evidence from enough target-side sources.

Default target replication gates are:

```text
min_positive_sources = 2
min_positive_per_source = 2
```

The exact bridge thresholds are serialized into the target model and bound into its model ID.

## Exact semantic namespace and provenance

The target model is bound to:

- target-language ID;
- exact upstream model IDs;
- exact declared operational semantic atoms;
- target grounding thresholds;
- frozen target lexeme evidence;
- scoped non-equivalence evidence.

The CLI derives the default semantic namespace from the exact frozen translator semantic relations and, when supplied, the exact frozen ordered-relation model.

A target model trained against one translator/order lineage cannot silently stand in for another in the fully composed CLI path.

## Synonyms are not collapsed

Multiple target tokens may independently ground to the same operational atom.

If both `red` and `scarlet` survive the frozen evidence gates for the same atom, V1 returns:

`MULTIPLE_TARGET_REALIZATIONS_SUPPORTED`

with both realizations.

It does not arbitrarily select one synonym and pretend the alternatives do not exist.

`strict_renderer_mapping()` returns only atoms with exactly one unconflicted supported realization, for legacy/debug surfaces that still require a single string mapping.

## Homonym / ambiguity handling

A target token whose evidence remains tied between multiple operational atoms is not promoted.

The result for those atoms remains:

`UNKNOWN_TARGET_RENDERING`

until additional evidence discriminates the target token's use.

This means a familiar spelling or human intuition about a word does not bypass the evidence gate.

## No faithful equivalent versus unknown

Absence of a learned word is **not** evidence of non-equivalence.

V1 distinguishes:

`UNKNOWN_TARGET_RENDERING`

from:

`NO_FAITHFUL_EQUIVALENT_FOUND_WITHIN_DECLARED_SCOPE`

The latter requires explicit `NonEquivalenceObservation` evidence carrying:

- observation ID;
- target-side source ID;
- operational atom;
- declared scope ID.

By default, a scoped non-equivalence claim must be repeated at least twice within each of at least two target-side sources:

```text
min_non_equivalence_sources = 2
min_non_equivalence_per_source = 2
```

A scope might be something narrow such as `single-token`. The result then means only that no faithful equivalent survived within that declared scope. It is not a claim that the target language cannot express the concept by a phrase, explanation, action, diagram, or other construction.

## Conflicting evidence is preserved

If an atom has both:

- a supported target lexeme; and
- a qualified scoped non-equivalence claim,

V1 returns:

`CONFLICTING_TARGET_EVIDENCE`

It does not choose the convenient side.

## Rendering statuses

Per atom:

- `TARGET_RENDERING_SUPPORTED`
- `MULTIPLE_TARGET_REALIZATIONS_SUPPORTED`
- `UNKNOWN_TARGET_RENDERING`
- `NO_FAITHFUL_EQUIVALENT_FOUND_WITHIN_DECLARED_SCOPE`
- `CONFLICTING_TARGET_EVIDENCE`
- `OUTSIDE_TARGET_SEMANTIC_NAMESPACE`

Sequence-level results are:

- `TARGET_RENDERING_COMPLETE`
- `TARGET_RENDERING_PARTIAL`
- `TARGET_RENDERING_UNRESOLVED`

## Full no-codebook CLI path

Fit target grounding from demonstrations:

```bash
unvtrslr-target fit \
  translator.json \
  english-grounding.jsonl \
  --target-language-id en-reference \
  --ordered-model ordered-model.json \
  --non-equivalence non-equivalence.jsonl \
  > english-target-model.json
```

Render opaque operational atoms directly:

```bash
unvtrslr-target render-atoms \
  english-target-model.json \
  ctx:red shape:square
```

Or compose the qualified unknown-source path:

```bash
unvtrslr-target translate-qualified \
  translator.json \
  qualified-source-profile.json \
  ordered-model.json \
  english-target-model.json \
  query-evidence.jsonl
```

That path performs:

`qualified unknown signal`
→ frozen acoustic identities
→ frozen lexical operational relations
→ frozen order-sensitive relations
→ **learned target-language grounding**

without a hand-authored atom-to-English renderer map.

## Integrity

The target model ID is a content-derived integrity/provenance checksum, not an authenticity signature.

Reload independently validates:

- namespace membership;
- unique relation keys;
- bridge threshold ranges;
- support/source replication consistency;
- probability bounds;
- effect algebra;
- information bounds;
- non-equivalence observation/source counts.

Recomputing the checksum cannot legitimize an internally impossible target relation.

## Remaining limitations

V1 deliberately does not solve full target-language generation.

It currently operates at opaque target-token realization and does not establish:

- morphology;
- target word order;
- agreement;
- inflection;
- articles/determiners;
- idioms;
- multiword paraphrase optimization;
- discourse/pragmatics;
- stylistic choice;
- fluent sentence generation.

A target language can also lexicalize operational distinctions differently from the source or require constructions larger than one token. Those cases should remain multiple/unknown/non-equivalent within the declared scope rather than be forced into a one-word lookup.

## Claim ceiling

`TARGET_LANGUAGE_OPERATIONAL_RENDERING_WITHIN_GROUNDED_REFERENCE_SCOPE`

V1 closes the manual-codebook gap for supported target tokens. It does not prove uniquely correct semantics, full natural-language generation, universal translation, or production readiness.
