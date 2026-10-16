# Reference Semantic Bridge V1

Status: `REFERENCE_IMPLEMENTATION_CANDIDATE / OPERATIONAL_CORRESPONDENCE_ONLY`

## What now works

UNVTRSLR can now execute a bounded semantic-bootstrap experiment rather than only describe one.

Given repeated interaction episodes containing:

- opaque signal units;
- simultaneously learner-visible opaque context distinctions;
- optional source identity;

V1 learns candidate signal/context correspondences across individually ambiguous episodes, composes supported relations, preserves unresolved/ambiguous tokens, and requests a discriminating contrast when the evidence cannot separate its leading hypotheses.

It is intentionally not handed a dictionary.

## Why this is a translator rather than a lookup table

A lookup table receives the mapping.

The V1 bridge receives episodes such as:

```text
signal=[ka] context=[c:red, s:circle]
signal=[ka] context=[c:red, s:triangle]
signal=[zu] context=[c:blue, s:square]
signal=[zu] context=[c:green, s:square]
```

From repeated contrasts it can recover the operational hypotheses:

```text
ka -> c:red
zu -> s:square
```

and compose:

```text
[ka, zu] -> [c:red, s:square]
```

The IDs remain opaque to the learner. A separate renderer may turn `c:red` into the target-language string `red`; that renderer does not retroactively prove that `ka` has a universal semantic essence of RED.

## Evidence calculation

For token `T` and context atom `A`, V1 measures:

- support count for `T`;
- smoothed `P(A | T)`;
- smoothed `P(A | not T)`;
- effect size `P(A | T) - P(A | not T)`;
- empirical binary mutual information between presence of `T` and `A`.

A relation is promoted only when frozen support/probability/effect/information thresholds are satisfied and the best candidate is separated from its nearest rival.

No aggregate score overrides an ambiguity gate.

## Fail-closed behavior

If `ka` is observed only when both `c:red` and `s:square` are present, V1 does not arbitrarily choose one. It returns `AMBIGUOUS` and requests a contrast that separates the two candidates.

Unknown tokens return `UNKNOWN_TOKEN`.

Low-support relations return `INSUFFICIENT_EVIDENCE`.

If no candidate clears the evidence gates, the result is `UNRESOLVED`.

## Probe behavior

For an ambiguous token with candidates `A` and `B`, the learner emits a requested experimental contrast equivalent to:

```text
observe T where A is present without B
versus
observe T where B is present without A
```

This is a request for discriminating evidence, not a claim that UNVTRSLR can force an arbitrary world or interlocutor to produce that experiment.

## Relation to the acoustic layer

The acoustic fingerprint candidate in PR #6 measures pitch, contour, intensity, timing/rhythm, periodicity, harmonic structure, timbre/spectral envelope, and cepstral shape.

The bridge consumes opaque signal units, not raw waveforms. A later segmentation/event-discovery layer must connect continuous acoustic measurements to candidate units without silently supplying linguistic boundaries.

That boundary is deliberate:

`RAW SIGNAL -> MEASUREMENTS -> CANDIDATE EVENT/UNIT HYPOTHESES -> BRIDGE RELATIONS -> TARGET RENDERER`

No stage is allowed to claim evidence earned by another stage.

## Current claim ceiling

`OPERATIONAL_CORRESPONDENCE_SUPPORTED_WITHIN_SYNTHETIC_REFERENCE_FIXTURES`

V1 does not establish:

- universal translation;
- uniquely correct semantics;
- communicative intent;
- words or phonemes;
- human-like concepts;
- species-independent ontology;
- external deployment readiness.

It establishes something narrower and necessary: the repository now contains a runnable learner that can discover, compose, preserve ambiguity about, and actively seek evidence for operational correspondences instead of receiving a predefined codebook.
