# Cross-Recording Acoustic Unit Registry V1

Status: `REFERENCE_IMPLEMENTATION_CANDIDATE / CROSS-SOURCE RECURRENCE ONLY`

## Problem

PR #8 can discover candidate acoustic events and assign recording-local recurrence IDs such as `u0`, `u1`.

Those IDs are intentionally local.

`u0` in recording A is **not** evidence that `u0` in recording B is the same acoustic unit.

Without a cross-recording registry, PR #7's cross-situational learner could accidentally train on label collisions created by local clustering rather than on recurring signal structure.

V1 closes that interface gap.

## Input

Each evidence row contains:

- recording ID;
- source ID;
- recording-local unit ID;
- acoustic vector.

The registry does not use the local unit ID as a matching feature.

The ID exists only to identify the local hypothesis whose vector is being tested.

## Source contrast

A source must expose at least two distinct local units before it is eligible for cross-source normalization.

A source with only one observed unit receives:

`INSUFFICIENT_SOURCE_CONTRAST`

This prevents a one-point source from being centered to zero and spuriously matching every other one-point source.

## Normalization

For each eligible source, V1 computes per-dimension:

- median;
- median absolute deviation;
- observed spread;
- explicit scale floor.

The local-unit vectors are then expressed relative to that source's observed acoustic contrasts.

Raw evidence remains upstream in PR #8. This normalization is a registry hypothesis, not a destructive replacement for the original measurements.

## Cross-source recurrence

Eligible vectors are clustered with deterministic complete-link clustering.

Complete-link was chosen because every pair of members in a cluster must remain within the configured threshold. A chain of weak nearest-neighbor links is therefore not enough to collapse distant acoustic states into one unit.

A cluster receives a global registry ID only when it spans the configured minimum number of independent sources.

Otherwise its members remain:

`SOURCE_LOCAL_ONLY`

Promoted clusters receive opaque IDs such as:

`g_7fb2a1c804`

The ID is registry-version-local provenance. It is not a word, phoneme, concept, or semantic identity.

## Adapter from PR #8

`evidence_from_event_result()` converts one event-discovery result into one acoustic vector per recording-local recurrence ID by aggregating repeated events with a median.

This means the current path can be:

`raw audio -> PR #6 measurements -> PR #8 candidate events/local recurrence -> V1 cross-recording registry`

A later integration layer may feed only cross-source-supported registry IDs into PR #7's bridge.

## Research basis

ZeroSpeech's acoustic-unit benchmark explicitly frames the objective as retaining linguistically relevant contrast while discarding nuisance variation such as speaker voice and recording conditions.

R-Spin likewise treats speaker/noise invariance as something that must be learned and evaluated, not assumed merely because representations are discrete.

References:

- Zero Resource Speech Benchmark, Acoustic Unit Discovery / Speech Representation Learning: https://zerospeech.com/tasks/task_1/tasks_goals/
- Chang & Glass, *R-Spin: Efficient Speaker and Noise-invariant Representation Learning with Acoustic Pieces*, NAACL 2024, DOI `10.18653/v1/2024.naacl-long.36`.

## Hostile constraints

V1 deliberately refuses several tempting shortcuts:

- matching local ID strings does not create global identity;
- one-source recurrence does not create global identity;
- a source with no internal contrast cannot establish an invariant mapping;
- cluster membership does not imply semantic equivalence;
- global registry IDs are not stable ontology identifiers across registry rebuilds.

## Known limitations

Source-relative normalization can erase a genuinely communicative absolute dimension.

Different systems may preserve identity through nonlinear transformations that V1 cannot align.

Complete-link clustering can split a continuous manifold that a better model would represent continuously.

Conversely, a threshold that is too large can still merge distinct units.

Therefore V1 preserves a narrow claim ceiling and does not replace raw acoustic evidence.

## Claim ceiling

`CROSS_RECORDING_ACOUSTIC_RECURRENCE_ONLY_NO_SEMANTIC_IDENTITY`

A supported global registry ID means only that a candidate acoustic pattern recurs across independently contrastive sources under this declared normalization and clustering model.

It does not establish a word, phoneme, concept, meaning, communicative intent, or universal translation.
