# Candidate Event Discovery V1

Status: `REFERENCE_IMPLEMENTATION_CANDIDATE / PRELINGUISTIC_EVENT_HYPOTHESES`

## Purpose

PR #6 measures continuous acoustic structure. PR #7 learns relations from opaque candidate signal units. The missing interface is a way to propose repeatable signal units without assuming that the unknown system contains words, phonemes, syllables, or human linguistic boundaries.

V1 therefore performs **acoustic change-point and recurrence discovery**, not linguistic tokenization.

## Pipeline

`raw waveform -> acoustic frames -> source-relative normalized feature trajectory -> novelty peaks -> candidate events -> recurrence clusters`

The feature trajectory uses only learner-visible measurements from the acoustic layer, including source-relative pitch, intensity, spectral shape, periodicity, and a subset of cepstral coefficients.

Each recording is robustly normalized by median/MAD with explicit per-feature minimum scales. Those floors prevent near-constant numerical or phase variation from being magnified into fake structure.

## Boundaries

For frame position `i`, V1 compares robust median feature vectors in windows immediately before and after `i` and computes normalized Euclidean novelty.

A boundary must:

- exceed a frozen novelty threshold;
- be a local maximum;
- respect a minimum event duration;
- survive competition with stronger nearby peaks.

These are engineering hypotheses, not a definition of communication boundaries.

## Recurrence

Candidate events are represented by their median normalized feature vectors. A deterministic online prototype clusterer assigns repeated acoustically similar events to opaque IDs such as `u0`, `u1`.

The IDs carry no semantic content.

A later bridge may ask whether an opaque unit reliably corresponds to context distinctions. The event layer itself is not allowed to name the unit.

## Hostile fixture discovered during implementation

The first V1 implementation over-segmented a stationary tone because record-relative normalization amplified tiny numerical/phase differences.

The test was retained and the implementation was changed instead: every feature family now has a declared minimum physical/numerical scale before normalization. Stationary and globally amplitude-scaled tones remain single candidate events in the current synthetic fixtures.

## Failures that remain live

V1 can still be wrong because:

- a real unit may contain internal acoustic changes;
- multiple units may be acoustically similar;
- coarticulation may move boundaries;
- multimodal information may define a unit that audio alone cannot;
- recurrence may be continuous rather than categorical;
- source normalization may erase a distinction that is genuinely communicative;
- the correct communication system may not have discrete event units at all.

Therefore downstream evaluation must preserve competing segmentations and allow later evidence to reopen this layer.

## Current claim ceiling

`ACOUSTIC_EVENT_HYPOTHESES_ONLY_NO_LINGUISTIC_SEGMENTATION`

Passing synthetic tests means the implementation can recover controlled acoustic change points and recurrence. It does not establish words, phonemes, signalhood, communicative intent, semantics, or universal translation.
