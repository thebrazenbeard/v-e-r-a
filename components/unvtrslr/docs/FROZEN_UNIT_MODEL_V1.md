# Frozen Cross-Source Unit Model V1

Status: `REFERENCE_IMPLEMENTATION_CANDIDATE / OUT-OF-SAMPLE ACOUSTIC MATCHING`

## Problem

PR #10 can build a cross-recording acoustic registry, but its global IDs are intentionally bound to that registry build.

If a new recording were classified by rebuilding the whole registry, membership-derived IDs could change. A semantic learner trained on the previous IDs would then drift even if the underlying acoustic structure had not.

That is unacceptable for a translator.

V1 freezes the training registry into an immutable prototype model and classifies later sources against that model without changing the training-time IDs.

## Fit

`fit_frozen_unit_model()`:

1. builds the PR #10 registry;
2. keeps only `CROSS_SOURCE_UNIT_SUPPORTED` training units;
3. reconstructs their source-normalized vectors;
4. computes a fixed centroid per promoted global unit;
5. freezes matching thresholds and normalization parameters;
6. computes an integrity-bound `model_id`.

The returned model does not mutate during inference.

## Out-of-sample assignment

`assign_source_units()` takes local units from exactly one new source.

The new source must contain enough internal acoustic contrast to support the same source-relative normalization model used during training.

Each local unit is compared with the frozen prototypes.

Possible states include:

- `FROZEN_MATCH_SUPPORTED`;
- `AMBIGUOUS_FROZEN_MATCH`;
- `NO_MATCH_WITHIN_FROZEN_MODEL`;
- `INSUFFICIENT_SOURCE_CONTRAST`.

A nearest neighbor alone is not enough. The best prototype must fall within the frozen match threshold and remain separated from its nearest rival by the ambiguity margin.

## Persistence

`FrozenUnitModel.to_dict()` produces JSON-compatible durable state.

`frozen_unit_model_from_dict()` reconstructs it and recomputes the model integrity identifier.

If the stored model ID does not match the reconstructed prototypes/configuration, reload fails closed.

This prevents silent changes to prototypes or matching thresholds from masquerading as the same frozen model.

## CLI

`unvtrslr-unit-model fit evidence.jsonl`

fits a model and emits both the frozen model and its training registry.

`unvtrslr-unit-model assign model.json evidence.jsonl`

assigns one new source against a persisted frozen model.

The model JSON supplied to `assign` is the object under the `model` key produced by `fit`.

## Relation to downstream translation

The intended sequence is now:

`raw signal`
→ PR #6 acoustic measurements
→ PR #8 local candidate events/recurrence
→ PR #10 cross-recording registry
→ V1 frozen unit model
→ PR #7 operational correspondence learner
→ target renderer

The frozen model solves an identity-stability problem. It does not solve semantics.

## Hostile constraints

V1 refuses:

- inference that rewrites training-time global IDs;
- a new source with insufficient internal contrast;
- feature-vector dimensionality drift;
- an out-of-threshold match;
- a near-tied ambiguous match;
- persisted model state whose integrity ID no longer matches its content.

## Known limitations

The same source-relative normalization limitations from PR #10 remain.

A novel source whose observed unit inventory is badly incomplete can normalize differently from the training sources.

A new source may contain truly novel units that correctly receive `NO_MATCH_WITHIN_FROZEN_MODEL`.

The V1 prototype model is Euclidean and cannot represent every nonlinear acoustic invariance.

## Claim ceiling

`OUT_OF_SAMPLE_ACOUSTIC_RECURRENCE_MATCH_ONLY_NO_SEMANTIC_IDENTITY`

A successful frozen match means that a new source's candidate acoustic unit falls within a previously frozen cross-source recurrence model.

It does not establish a word, phoneme, concept, semantic equivalence, communicative intent, or universal translation.
