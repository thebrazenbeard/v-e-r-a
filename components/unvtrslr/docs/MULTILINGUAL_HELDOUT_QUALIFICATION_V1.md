# Multilingual Held-Out Qualification V1

Status: `REAL_CORPUS_QUALIFICATION_HARNESS / NO_REAL_CORPUS_PASS_YET`

## Purpose

Synthetic fixtures can expose implementation defects, but they cannot establish multilingual transfer.

V1 defines the first executable qualification layer intended for **real multilingual corpora**. It separates:

- training exposure;
- held-out evaluation records;
- leakage regime;
- scoring;
- explicit pass thresholds;
- corpus/language slice reporting.

The harness does not choose scientific thresholds on behalf of the evaluator. A caller must declare them.

## Qualification regimes

Supported regimes:

- `HELD_OUT_LANGUAGE`
- `HELD_OUT_SOURCE`
- `HELD_OUT_CONTENT`
- `HELD_OUT_LANGUAGE_AND_CONTENT`
- `HELD_OUT_ALL`
- `PARALLEL_LANGUAGE_TRANSFER`

### Held-out language

No evaluation source language may occur in the declared training exposure.

### Held-out source

No evaluation corpus/source identity may occur in training. Evaluation rows must actually provide source IDs.

### Held-out content

No evaluation corpus/content identity may occur in training.

### Parallel language transfer

Evaluation languages must be unseen, **but evaluation content IDs must already exist in training in another language**.

That regime is especially useful for parallel corpora because it changes language while controlling semantic content.

## Why several corpora are required

No single benchmark supports the whole claim.

The pinned corpus manifest currently assigns complementary roles:

- **FLEURS** — parallel multilingual speech and language-transfer control;
- **CoVoST 2** — speech-to-text translation;
- **MASSIVE** — parallel labeled multilingual intent/slot semantics;
- **FLORES-200 / maintained successor** — broad parallel text transfer;
- **Common Voice Scripted Speech 27.0** — current speaker/channel/acoustic stress;
- **NLLB Multi Domain** — domain shift.

Common Voice is deliberately marked `ACOUSTIC_STRESS_ONLY` for this program. Large multilingual speech coverage without parallel semantic references cannot independently establish semantic translation.

Likewise, MASSIVE intent/slot labels are useful operational controls but remain evaluator-authored task semantics, not evidence for a universal ontology.

FLORES-style results must not stand alone: the benchmark is broad and useful, but later research has identified quality, domain, cultural-bias, and metric-shortcut concerns.

## Record contracts

### Training exposure

Each training row records only what the system was exposed to:

```json
{
  "corpus_id": "fleurs",
  "corpus_version": "published-fleurs",
  "record_id": "train-001",
  "language_id": "eng",
  "source_id": "speaker-001",
  "content_id": "sentence-00042"
}
```

### Evaluation record

Each held-out row records:

- exact corpus/version;
- record ID;
- source language;
- optional source/speaker ID;
- content ID;
- target language;
- one or more reference target token sequences;
- zero or more system candidate sequences;
- system status.

Multiple candidates are allowed because upstream UNVTRSLR layers may legitimately preserve multiple target constructions.

## Scoring

V1 reports per `corpus/version/language` slice:

- record count;
- coverage rate;
- exact-match rate against any reference;
- best normalized token edit similarity;
- ambiguity rate.

Macro averages are computed over slices, not individual records.

This prevents a large high-resource slice from hiding a small failing low-resource slice.

Qualification also requires **every slice** to clear the declared thresholds.

## Explicit thresholds

There are no hidden default scientific pass criteria.

The evaluator must supply:

- minimum number of corpora;
- minimum number of languages;
- minimum records per corpus-language slice;
- minimum coverage;
- minimum exact match;
- minimum token similarity;
- maximum ambiguity rate.

A report reaches:

`QUALIFIED_WITHIN_DECLARED_MULTILINGUAL_HOLDOUT`

only if the holdout audit passes and every declared breadth/metric threshold passes.

Otherwise it returns:

- `LEAKAGE_DETECTED`, or
- `MULTILINGUAL_HOLDOUT_THRESHOLD_NOT_MET`.

## Leakage controls

The harness always rejects exact training/evaluation record overlap.

Depending on regime it additionally checks:

- language overlap;
- corpus/source overlap;
- corpus/content overlap;
- missing source identity when source holdout is claimed;
- missing parallel-content control for `PARALLEL_LANGUAGE_TRANSFER`.

These checks are metadata-level controls. They do **not** prove absence of paraphrase leakage, duplicated audio under different IDs, speaker pseudonyms, translation-memory contamination, or pretrained-model exposure.

Those remain corpus-governance and model-provenance requirements.

## CLI

Audit before scoring:

```bash
unvtrslr-qualify-multilingual audit \
  training-exposure.jsonl \
  heldout-predictions.jsonl \
  --regime HELD_OUT_LANGUAGE
```

Evaluate with explicit thresholds:

```bash
unvtrslr-qualify-multilingual evaluate \
  training-exposure.jsonl \
  heldout-predictions.jsonl \
  --regime HELD_OUT_LANGUAGE \
  --min-corpora 3 \
  --min-languages 10 \
  --min-records-per-slice 100 \
  --min-coverage 0.80 \
  --min-exact-match 0.40 \
  --min-token-similarity 0.75 \
  --max-ambiguity-rate 0.25
```

The numbers above are an **example invocation**, not project-approved scientific qualification thresholds.

## Recommended staged program

### Q1 — text semantic/control qualification

Use MASSIVE and FLORES-like parallel text to test:

- held-out language;
- held-out content;
- target construction behavior;
- target-side ordering;
- ambiguity preservation.

### Q2 — parallel speech language transfer

Use FLEURS to hold semantic content constant while changing language.

This is a direct stress test for claims that source-side acoustic identity can generalize beyond the languages used for fitting.

### Q3 — real speech translation

Use CoVoST 2 to test the composed speech-to-target path.

### Q4 — speaker/channel stress

Use Common Voice current scripted speech for held-out speaker/channel acoustic qualification.

Do not count this stage as semantic translation evidence by itself.

### Q5 — domain shift

Use NLLB Multi Domain or another independently curated multidomain corpus so qualification is not just another IID news/web split.

### Q6 — benchmark disagreement

Require the project to preserve failures where corpora disagree.

A system that performs well on one benchmark and badly on another is not averaged into a universal-pass claim.

## Claim discipline

A real corpus PASS under this harness means only:

`MULTILINGUAL_HELDOUT_BEHAVIOR_WITHIN_DECLARED_CORPORA_AND_SPLITS`

It does not establish:

- universal language coverage;
- unseen-species communication;
- uniquely correct meaning;
- universal ontology;
- independence from pretraining leakage;
- human-level translation quality;
- production readiness.

## Claim ceiling

`MULTILINGUAL_HELDOUT_BEHAVIOR_WITHIN_DECLARED_CORPORA_AND_SPLITS`

The next evidence step after this harness is not another synthetic fixture. It is a pinned, reproducible run over real corpus records with exact model versions, exact split manifests, and preserved failures.
