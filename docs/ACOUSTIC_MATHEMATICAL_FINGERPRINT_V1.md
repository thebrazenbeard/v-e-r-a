# Acoustic Mathematical Fingerprint V1

Status: `REFERENCE_IMPLEMENTATION_CANDIDATE / ACOUSTIC_STRUCTURE_ONLY`

## Purpose

UNVTRSLR must not discard acoustic structure before it knows whether that structure carries information.

For spoken, vocal, musical, bioacoustic, or otherwise frequency-bearing channels, the learner treats at least these as candidate information channels:

- fundamental frequency (`f0`) and time-varying contour;
- duration and temporal spacing;
- intensity/amplitude;
- spectral envelope and timbre;
- spectral centroid, bandwidth, flatness, rolloff, and slope;
- harmonic structure including `H1-H2` where measurable;
- periodicity/voicing;
- cepstral shape (MFCCs);
- envelope-modulation/rhythm structure.

These are measurements, not semantic labels.

## Mathematical question

For candidate feature `X`, operational distinction or observed outcome `Y`, and nuisance/context variables `Z`, the core diagnostic is:

`I(X ; Y | Z)`

Mutual information does not prove meaning. It asks whether observing `X` reduces uncertainty about `Y` after conditioning on known nuisance structure.

Candidate `Z` variables include source identity, recording device, environment, interaction phase, partner, known context, and other channels.

A feature is interesting only if predictive information survives nuisance conditioning and fresh/shifted evaluation.

## Source-relative normalization

Raw pitch in hertz is not a semantic primitive. Different sources can express the same contour at different absolute frequencies.

V1 retains raw `f0` for audit but represents the main contour relative to the utterance median:

`pitch_st = 12 * log2(f0 / median(f0))`

Analogous normalization is required for other source-sensitive features before cross-source semantic credit.

## Why multi-channel

Known human languages already falsify a text-only or pitch-only view.

- lexical tone uses `f0` height/contour to distinguish words;
- prosodic pitch can mark stress, boundaries, questionhood, stance, or affect;
- intensity and duration can contribute to tonal/prosodic distinctions;
- phonation/voice quality can itself be contrastive;
- rhythm is multidimensional and may involve duration, `f0`, and intensity.

Channel discovery must therefore test dimensions independently and jointly.

## R0.5 integration

The acoustic extractor is learner preprocessing and falls under `NO_DESTRUCTIVE_QUOTIENT`.

It must preserve raw/derived provenance and must not silently remove a distinction later used for evaluator credit. A negative result after lossy preprocessing cannot establish that the original signal lacked the distinction.

## R1/R2/R3 integration

This layer does not choose a semantic substrate.

It produces learner-visible measurements that TPH, DCA, PIS, or later candidates may use.

It does not establish signalhood, communicative intent, lexical units, words/syllables, semantic correspondence, pragmatic function, or universal acoustic categories.

Segmentation remains a hypothesis. Fixed frames are an engineering measurement surface, not a claim that frames are linguistic units.

## V1 output ceiling

`ACOUSTIC_STRUCTURE_ONLY_NO_SEMANTIC_QUALIFICATION`

A V1 fingerprint may support claims such as:

- two samples differ reliably in pitch contour;
- a dimension carries predictive information after source conditioning;
- a pattern generalizes across held-out sources.

It cannot by itself support "this contour means danger", "this is a word", "this species uses tone", or "translation is established".

Those require downstream grounding and adversarial qualification.

## Next study

Calibrate the vector across many known languages and families, then test whether the same machinery rediscovers known typological distinctions without receiving typology labels as input during feature extraction.

The calibration result is a prior over useful measurements, not an ontology imposed on unknown systems.
