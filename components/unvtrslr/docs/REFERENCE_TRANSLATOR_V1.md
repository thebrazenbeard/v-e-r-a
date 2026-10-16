> **Historical blocked design.** V1 exact head `8a5df39b08afc91f9bd3f11d1130be8762d983a5` was blocked after coordinator self-review found query-dependent source normalization: query units participated in estimating the same source profile used to classify them. Adding an unrelated extreme query could therefore change earlier translation outcomes. Review was cancelled. See `REFERENCE_TRANSLATOR_V2.md` for the source-calibrated successor.

# End-to-End Reference Translator V1

Status: `INTEGRATION_CANDIDATE / CROSS-SOURCE OPERATIONAL TRANSLATION`

## What this branch does

This is the first UNVTRSLR branch that composes the executable acoustic and semantic work into one frozen translation model.

The lineage is explicit:

`raw PCM audio`
→ PR #6 acoustic frame measurements
→ PR #8 candidate event / local recurrence hypotheses
→ PR #12 raw event acoustic evidence
→ PR #10 cross-recording recurrence
→ PR #11 frozen out-of-sample acoustic unit model
→ PR #7 cross-situational operational correspondence
→ V1 frozen semantic relation
→ optional target renderer

The integration commit has both the exact PR #12 lineage head and exact PR #7 semantic-bridge head as parents. It does not rewrite either delegated subject.

## Training contract

Each training episode contains:

- an episode ID;
- a source ID;
- one or more `LocalUnitEvidence` rows;
- simultaneously observed opaque context atoms.

The translator first fits cross-source acoustic identities.

A training acoustic unit is not admitted to semantic learning unless it has already reached:

`CROSS_SOURCE_UNIT_SUPPORTED`

Only the resulting frozen global acoustic IDs become tokens for the PR #7 bridge.

## Cross-source semantic gate

PR #7 already requires support, conditional probability, effect size, mutual information, and separation from the nearest rival.

The integrated translator adds another gate:

a token→context relation must have positive supporting episodes from at least `semantic_min_sources` independent sources.

Default:

`semantic_min_sources = 2`

A statistically strong relation observed positively from only one source is not frozen into the translator.

This prevents a speaker/source-specific correlation from becoming a persistent translation merely because other sources provided negative evidence.

## Three-contrast acoustic gate

PR #11's lower-level acoustic model permits two source-internal units.

The end-to-end translator intentionally requires at least **three acoustic contrasts per source**.

Reason: with only two points, source-relative centering/scaling can map nearly any two distinct observations onto the same symmetric pattern. That is too underconstrained for semantic promotion.

Therefore V1 rejects:

`min_units_per_source < 3`

This is an integration-level safety/evidence gate. It does not mutate PR #11.

## Frozen model

`ReferenceTranslatorModel` contains:

- the frozen PR #11 acoustic model;
- only semantic relations that survived the PR #7 thresholds;
- positive source coverage for each relation;
- the required semantic source floor;
- a content-derived translator `model_id`.

Reload recomputes the integrity ID.

Changing the acoustic model, a frozen relation, evidence metrics, or the semantic source floor without changing the model identity causes reload to fail closed.

## Inference

A new source is classified as a batch because source-relative identity requires internal contrast.

`translate_source_evidence()`:

1. classifies the source's local acoustic units against the frozen acoustic model;
2. preserves no-match and ambiguous-match failures;
3. maps only `FROZEN_MATCH_SUPPORTED` acoustic units to frozen semantic relations;
4. optionally renders opaque context atoms into target-language strings.

Possible top-level results:

- `REFERENCE_TRANSLATION_SUPPORTED`
- `PARTIAL_REFERENCE_TRANSLATION`
- `UNRESOLVED`

The renderer is presentation only. It contributes no evidence to acoustic identity or semantic grounding.

## CLI

### 1. Prepare raw WAV evidence

```bash
unvtrslr-translate prepare-wav signal.wav \
  --recording-id observation-001 \
  --source-id source-A > observation-001.jsonl
```

This runs the exact acoustic/event lineage in the branch and emits recording-local raw acoustic evidence.

### 2. Fit a frozen translator

Training JSONL contains one episode per line:

```json
{"episode_id":"e1","source_id":"source-A","context":["ctx:red","shape:circle"],"evidence":[{"recording_id":"r1","source_id":"source-A","local_unit_id":"u0","vector":[1.0,2.0,3.0]}]}
```

Then:

```bash
unvtrslr-translate fit episodes.jsonl > translator.json
```

### 3. Translate a new source batch

```bash
unvtrslr-translate translate translator.json source-C-evidence.jsonl
```

An optional renderer JSON may map opaque operational relations to display strings:

```bash
unvtrslr-translate translate translator.json source-C-evidence.jsonl \
  --renderer renderer.json
```

## Hostile properties

V1 fails closed when:

- training acoustic units do not survive cross-source recurrence;
- fewer than three acoustic contrasts per source are requested for end-to-end fitting;
- no semantic relation survives multi-source positive-evidence gating;
- a new source has insufficient internal acoustic contrast;
- a new local unit does not match a frozen acoustic prototype;
- two frozen acoustic prototypes are too close to discriminate;
- a matched acoustic token has no frozen semantic relation;
- persisted translator state fails its integrity check.

## What this proves

Within controlled reference fixtures, UNVTRSLR can now perform the complete operational sequence:

1. stabilize signal identity across source transformations;
2. learn context correspondences from repeated ambiguous observations;
3. freeze only cross-source-supported relations;
4. classify a new source against the frozen signal model;
5. emit supported target relations while refusing unresolved evidence.

## What this does not prove

It does not establish:

- universal translation across arbitrary species or signal systems;
- uniquely correct meaning;
- linguistic words or phonemes;
- communicative intent;
- a universal ontology;
- adequacy on real multilingual corpora;
- robustness to nonlinear source transformations;
- deployment readiness.

## Claim ceiling

`OUT_OF_SAMPLE_ACOUSTIC_MATCH_TO_CROSS_SOURCE_OPERATIONAL_RELATION_WITHIN_REFERENCE_FIXTURES`

The next qualification frontier is adversarial end-to-end evaluation on held-out sources and real known-language corpora, with negative controls that distinguish genuine signal structure from speaker, channel, corpus, and experiment-design shortcuts.
