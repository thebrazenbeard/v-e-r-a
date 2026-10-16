# MASSIVE 1.0 First Real-Corpus Run Packet

Run ID: `MASSIVE_V1_FIRST_REAL_CORPUS_20260922`

Status at commit time: `PREREGISTERED_NOT_YET_EXECUTED`

This packet is the first UNVTRSLR run designed to turn the target-construction and multilingual-qualification layers against real human multilingual data rather than synthetic fixtures.

## Exact subject

Dataset: **Amazon MASSIVE 1.0**, the 51-language version used in the original paper/leaderboard.

Canonical dataset source:

`https://amazon-massive-nlu-dataset.s3.amazonaws.com/amazon-massive-dataset-1.0.tar.gz`

Canonical repository: `alexa/massive`.

The execution script computes and records the SHA-256 of the actual downloaded tarball bytes. It does not trust the URL alone as an immutable byte identity.

## UNVTRSLR lineage

- learned target grounding: PR #17 @ `897362fea8c8ccf6483e8594f581019e4b47a90d`
- multiword target construction: PR #18 @ `3a378d02e534d739bfeb3be64fed76dd4976b1b0`
- multilingual held-out evaluator: PR #19 @ `cc72e50dced024a33731a690ca1225e6d9a5fe76`
- run packet is stacked from PR #19 without moving any delegated parent head.

The exact execution commit is captured from `GITHUB_SHA` into the generated receipt.

## What is being tested

This is intentionally **not** the whole universal-translator claim.

The first real run tests whether the current evidence-gated target-construction memory can recover and reuse exact target constructions across held-out MASSIVE content.

The MASSIVE intent and slot annotations are treated as **evaluator-authored operational semantics**.

Semantic adapter:

`intent:<intent>`
followed by each slot type from `annot_utt` in its observed order.

Target adapter:

Unicode NFC normalization followed only by whitespace tokenization of the raw `utt`.

No pretrained tokenizer, language model, translator, POS tagger, morphological analyzer, or target grammar is used by this run adapter.

## Languages

The preregistered locales are:

- `en-US`
- `fr-FR`
- `de-DE`
- `sw-KE`
- `tr-TR`

They are fixed before results are observed.

## Training evidence

For each locale, all MASSIVE `train` rows are passed to the target-construction layer.

Target source identity is the locale-scoped MASSIVE `worker_id`.

Frozen construction gate:

```text
min_sources = 2
min_positive_per_source = 1
```

This means an exact target construction must independently recur under the same semantic pattern from at least two locale-specific worker IDs.

## Holdout

The source dataset's `test` partition is used only for evaluation.

Exactly 200 test rows per locale are selected deterministically by sorting on:

`SHA256(locale + ":" + id)`

and taking the lowest 200 hashes.

This avoids result-aware manual sampling while keeping the complete prediction artifact small enough to preserve.

Qualification regime:

`HELD_OUT_CONTENT`

The run fails leakage audit if a selected test content ID appears in the training exposure.

## Frozen exploratory gate

The preregistered qualification thresholds are in `thresholds.json`.

They require:

- one declared corpus;
- all five declared languages;
- exactly/at least 200 held-out rows per language slice;
- coverage >= 0.10;
- exact target match >= 0.05;
- mean normalized token edit similarity >= 0.10;
- ambiguity rate <= 0.25.

These are **exploratory first-run thresholds**, not universal scientific constants. They are frozen before execution specifically so the gate is not moved after seeing the result.

## Generated artifacts

A successful execution writes:

- `dataset_provenance.json`
- `environment.txt`
- `model_manifest.json`
- `training_exposure.jsonl`
- `holdout_predictions.jsonl`
- `construction_stats.json`
- `multilingual_report.json`
- `run_receipt.json`

The GitHub Actions workflow uploads the entire generated directory as a workflow artifact. It has read-only repository permission and cannot merge or push generated results.

## Expected failure is evidence

A likely outcome is very low coverage.

That would not be a harness failure. It would mean the exact-construction memory from PR #18 does not generalize adequately to unseen MASSIVE content under the frozen evidence gate.

That result should drive the next model change: learn reusable target construction **slots/substructure** and test them on held-out recombinations, rather than weakening the real-corpus gate until memorization passes.

## Claim ceiling

`MASSIVE_V1_TARGET_CONSTRUCTION_GENERALIZATION_WITHIN_DECLARED_OPERATIONAL_ADAPTER`

Even a PASS would remain bounded to this dataset version, these languages, this operational annotation adapter, this sampling rule, these exact model heads, and these thresholds.
