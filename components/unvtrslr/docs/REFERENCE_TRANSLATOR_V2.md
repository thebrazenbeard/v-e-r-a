# Source-Calibrated Reference Translator V2

Status: `SUCCESSOR_INTEGRATION_CANDIDATE / QUERY_NORMALIZATION_FROZEN`

## Why V2 exists

V1 composed acoustic identity and semantic grounding, but its inference API normalized a new source from the same evidence batch that contained the query units.

That created a real defect:

`query batch -> source median/scale -> query classification`

Adding or removing an unrelated query could move the source median/scale and therefore change the classification of a query that had not changed.

V2 removes that feedback path.

## V2 inference sequence

The sequence is now:

`training corpus`
→ frozen cross-source acoustic model
→ frozen cross-source semantic relations
→ persisted translator model

Then, for each new source:

`source calibration evidence`
→ **frozen SourceCalibrationProfile**

and only after that:

`query evidence`
→ normalize with frozen source profile
→ frozen acoustic prototype match
→ frozen operational relation
→ optional renderer

Query evidence never participates in fitting or updating its own normalization profile.

## Source calibration profile

`fit_source_calibration_profile()` receives calibration evidence from exactly one source.

It freezes:

- translator model ID;
- acoustic model ID;
- source ID;
- feature dimension;
- calibration-unit count;
- per-dimension source center;
- per-dimension source scale;
- content-derived profile ID.

The profile is immutable during query translation.

`source_calibration_profile_from_dict()` validates model binding, dimensions, positive scales, evidence floor, schema, claim ceiling, and profile integrity.

A profile created for one translator/acoustic model cannot be silently reused with another.

## Distinct acoustic contrast gate

V2 requires at least three **distinct acoustic states**, not merely three evidence rows.

This applies at both end-to-end translator training and source calibration.

Three recordings containing the same vector do not satisfy the contrast requirement.

The three-state floor does not prove that source normalization is sufficient. It only closes the degenerate two-point and duplicate-row cases identified during hostile self-review.

## Semantic replication gate

A PR #7 relation must still clear its statistical gates.

V2 further requires:

- at least `semantic_min_sources` sources with positive relation evidence; and
- at least `semantic_min_positive_per_source` positive observations within each counted source.

Defaults:

```text
semantic_min_sources = 2
semantic_min_positive_per_source = 2
```

One positive observation from a second source is therefore not enough to freeze a relation.

This remains a bounded replication gate, not proof that source IDs represent biologically or physically independent sources.

## Training episode identity

Training `episode_id` values must be unique.

This blocks exact episode duplication from silently inflating the semantic evidence count.

It does not solve every form of pseudoreplication; semantically duplicated observations under different IDs remain a corpus-governance concern.

## Query translation

`translate_query_evidence()` accepts:

- a frozen `ReferenceTranslatorModel`;
- a frozen `SourceCalibrationProfile`;
- one or more query `LocalUnitEvidence` rows.

A single query unit is allowed because the normalization profile was already established independently.

Possible acoustic states remain:

- `FROZEN_MATCH_SUPPORTED`;
- `AMBIGUOUS_FROZEN_MATCH`;
- `NO_MATCH_WITHIN_FROZEN_MODEL`.

A matched acoustic unit without a frozen semantic relation remains unresolved.

## Batch-invariance regression

The V2 test suite explicitly freezes a source profile, translates a known query, then translates that same query alongside an unrelated extreme acoustic query.

The original query must retain the same:

- global acoustic unit ID;
- prototype distance;
- operational relation.

The unrelated query is allowed to fail. It is not allowed to renormalize the existing query.

## CLI

### Prepare WAV evidence

```bash
unvtrslr-translate prepare-wav calibration-a.wav \
  --recording-id cal-a \
  --source-id source-C > cal-a.jsonl
```

Repeat for enough source calibration contrasts and combine the JSONL rows.

### Fit translator

```bash
unvtrslr-translate fit training-episodes.jsonl > translator.json
```

Optional evidence floors include:

```bash
--semantic-min-sources 2
--semantic-min-positive-per-source 2
--min-units-per-source 3
```

### Freeze a new-source profile

```bash
unvtrslr-translate calibrate \
  translator.json \
  source-C-calibration.jsonl > source-C-profile.json
```

### Translate later query evidence

```bash
unvtrslr-translate translate \
  translator.json \
  source-C-profile.json \
  source-C-query.jsonl \
  --renderer renderer.json
```

The query file is not used to recompute the source profile.

## Current fail-closed gates

V2 rejects or leaves unresolved:

- duplicate training episode IDs;
- fewer than three distinct acoustic training states per source;
- acoustic training units that fail cross-source recurrence;
- relations lacking multi-source replicated positive evidence;
- calibration from multiple source IDs;
- fewer than three distinct calibration states;
- calibration/query dimension mismatch;
- query source mismatch;
- tampered translator model;
- tampered source profile;
- acoustic no-match;
- acoustic ambiguity;
- matched acoustic units lacking frozen semantic relations.

## Remaining weaknesses

V2 still does not establish that the source-normalization model is correct for arbitrary communication systems.

Important open problems include:

- nonlinear source transformations;
- calibration-set representativeness;
- source IDs that do not correspond to independent physical sources;
- repeated-measures/source imbalance;
- multimodal signals whose identity cannot be recovered acoustically;
- continuous communication systems that resist discrete unit hypotheses;
- real-corpus held-out qualification;
- semantic grounding beyond operational context association.

These remain explicit qualification frontiers rather than hidden assumptions.

## Claim ceiling

`OUT_OF_SAMPLE_ACOUSTIC_MATCH_TO_CROSS_SOURCE_OPERATIONAL_RELATION_WITHIN_REFERENCE_FIXTURES`

V2 repairs query-dependent normalization and strengthens replication gates. It does not establish universal translation, uniquely correct meaning, linguistic units, communicative intent, a universal ontology, or production readiness.
