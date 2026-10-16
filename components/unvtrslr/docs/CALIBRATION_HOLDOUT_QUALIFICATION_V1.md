# Held-Out Source Calibration Qualification V1

Status: `QUALIFICATION_CANDIDATE / ACOUSTIC GENERALIZATION ONLY`

## Problem

Translator V2 freezes a source-normalization profile before query translation. That removes query-dependent normalization, but a frozen profile can still be poor.

A calibration set might be:

- unrepresentative of the source;
- dominated by one acoustic state;
- corrupted or adversarial;
- internally diverse but unrelated to the frozen training prototypes.

A profile being mathematically well-formed does not prove it generalizes.

V1 adds a separate held-out qualification stage.

## Evidence split

The intended sequence is:

`calibration evidence A`
→ fit `SourceCalibrationProfile`

then:

`held-out qualification evidence B`
→ normalize with the already frozen profile
→ match against the already frozen acoustic prototypes
→ evaluate held-out acoustic consistency

Only after that may the qualified API translate later query evidence C.

Calibration and qualification rows with the same exact evidence identity key are rejected.

The split is therefore:

`A != B != later query evidence`

at the evidence-identity level.

## Qualification metrics

V1 records:

- held-out qualification unit count;
- number of `FROZEN_MATCH_SUPPORTED` held-out units;
- supported fraction;
- number of distinct frozen global acoustic units recovered;
- exact set of matched global unit IDs;
- maximum supported prototype distance;
- evidence digest;
- thresholds used for qualification.

Default gates:

```text
min_supported_fraction = 0.80
min_distinct_global_units = 3
```

A high match rate alone is not enough.

Three held-out observations that all map to the same frozen unit fail:

`INSUFFICIENT_HELD_OUT_PROTOTYPE_COVERAGE`

A profile whose held-out evidence mostly fails frozen matching returns:

`INSUFFICIENT_HELD_OUT_MATCH_RATE`

Only a profile satisfying both gates reaches:

`HELD_OUT_ACOUSTIC_CALIBRATION_QUALIFIED`

## Certificate

`SourceCalibrationQualification` binds:

- exact translator model ID;
- exact acoustic model ID;
- exact source profile ID;
- source ID;
- held-out evidence digest;
- qualification counts and metrics;
- qualification thresholds;
- resulting status.

Its content-derived `qualification_id` fails closed on ordinary tampering.

The ID is an integrity/provenance checksum, **not a cryptographic authenticity signature**. Reload therefore also reconstructs logical constraints independently of the hash: supported fraction must equal the stored counts, matched global IDs must exist in the frozen acoustic model, supported distances cannot exceed the frozen match threshold, prototype coverage cannot exceed supported count, and the stored qualification status must follow from the frozen metrics and thresholds. Recomputing the hash cannot legitimize an internally impossible certificate.

The certificate claim ceiling is:

`HELD_OUT_ACOUSTIC_CALIBRATION_CONSISTENCY_ONLY_NO_SEMANTIC_VALIDATION`

The held-out qualification evidence tests acoustic consistency only. It does not supply semantic evidence.

## Qualified translation

`translate_qualified_query()` accepts only a `QualifiedSourceProfile` whose qualification status is:

`HELD_OUT_ACOUSTIC_CALIBRATION_QUALIFIED`

An unqualified profile is rejected before query translation.

This creates the safer reference path:

`fit translator`
→ calibration set A
→ frozen source profile
→ held-out set B
→ acoustic qualification certificate
→ later query C
→ frozen acoustic match
→ frozen operational relation
→ optional renderer

## CLI

Qualify:

```bash
unvtrslr-qualify-calibration qualify \
  translator.json \
  source-C-calibration.jsonl \
  source-C-heldout.jsonl \
  > source-C-qualified.json
```

Translate later queries:

```bash
unvtrslr-qualify-calibration translate \
  translator.json \
  source-C-qualified.json \
  source-C-query.jsonl \
  --renderer renderer.json
```

## What this closes

This layer specifically blocks:

- treating a merely well-formed source profile as validated;
- approving a profile that only reproduces one acoustic state;
- approving a profile with a poor held-out match rate;
- translating through an explicitly failed qualification certificate;
- silently changing qualification metrics or thresholds after certification.

## What remains open

Held-out qualification is still not proof that calibration is universally valid.

The current evaluator can still be fooled by:

- calibration and held-out sets sharing an unmodeled confound;
- non-independent recordings;
- source IDs that do not correspond to independent physical sources;
- frozen prototypes that are themselves wrong;
- nonlinear transformations that happen to fit the observed held-out sample;
- adversarial selection of held-out evidence;
- acoustic recurrence that has no semantic significance.

Real-corpus and independently constructed holdout qualification remain required.

## Claim ceiling

`HELD_OUT_ACOUSTIC_CALIBRATION_CONSISTENCY_ONLY_NO_SEMANTIC_VALIDATION`

Passing V1 means only that a frozen source profile generalizes to the declared held-out acoustic evidence under the frozen acoustic model and configured coverage thresholds.
