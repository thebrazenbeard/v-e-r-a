# Raw Event Acoustic Evidence V1

Status: `REFERENCE_IMPLEMENTATION_CANDIDATE / NON-DESTRUCTIVE EVENT DESCRIPTOR`

## Problem

PR #8 intentionally normalizes acoustic frame trajectories within a recording so change-point detection is less sensitive to source scale and stationary numerical noise.

That representation is appropriate for boundary discovery.

It is not sufficient by itself for cross-recording identity.

For example, two separate one-event recordings at different absolute pitches can both collapse toward the same within-recording normalized vector even though the raw acoustic measurements differ.

Using the same normalized vector for both segmentation and global identity would therefore create a destructive quotient.

V1 adds a second view instead of replacing PR #8's view.

## Dual-view rule

For each candidate event:

- PR #8 retains the normalized event vector used for boundary/within-recording recurrence;
- V1 derives an additional descriptor directly from PR #6 frame measurements.

Both remain auditable.

Neither silently overwrites the other.

## Descriptor

The V1 raw-event descriptor includes:

- median log2 fundamental frequency;
- within-event pitch range in semitones;
- voiced-frame fraction;
- median RMS intensity;
- log spectral centroid;
- log spectral bandwidth;
- spectral flatness;
- spectral slope;
- periodicity;
- `H1-H2`;
- MFCC coefficients 1 through 4.

The descriptor is not a linguistic representation.

It is an acoustic evidence vector that later source-normalization/registry stages may test.

## Event support

`evidence_from_event_frames()` binds PR #8 event time spans back to PR #6 frame measurements.

If an event has no supporting frame evidence, the adapter fails closed instead of synthesizing a descriptor.

Repeated occurrences carrying the same recording-local PR #8 unit ID are aggregated by median into one `LocalUnitEvidence` vector.

## Raw-audio helper

`evidence_from_audio_event_result()` reruns PR #6 frame extraction on the original samples and then applies the same event-bound descriptor.

This preserves the chain:

`raw samples -> PR #6 frames -> PR #8 boundaries -> V1 raw event descriptor`

while keeping the PR #8 normalized vector available separately.

## Why this matters for the registry

The PR #10 registry performs normalization across all local units observed from a source.

That stage needs cross-recording evidence that still contains source-internal acoustic contrasts.

V1 preserves those contrasts even when each recording contains only one candidate event.

A synthetic fixture verifies that separate 150/300 Hz recordings from one source and proportionally shifted 300/600 Hz recordings from another source can be aligned into two distinct cross-source registry units.

## Hostile constraints

V1 does not claim that:

- absolute frequency is always meaningful;
- source-relative normalization is always correct;
- the descriptor dimensions are sufficient for every communication system;
- one event corresponds to one word/phoneme;
- acoustic recurrence establishes semantic identity.

It exists specifically to prevent the segmentation representation from silently erasing evidence needed by later identity hypotheses.

## Claim ceiling

`RAW_EVENT_ACOUSTIC_DESCRIPTOR_ONLY_NO_CROSS_SOURCE_OR_SEMANTIC_IDENTITY`

A V1 vector is only an auditable acoustic description of frames supporting a candidate event.

Cross-source recurrence requires PR #10/#11 qualification.

Meaning requires a downstream grounding layer such as PR #7 and its own adversarial controls.
