# Cross-Linguistic Acoustic/Mathematical Research — 2026-09-22

Status: `RESEARCH_BOUND / IMPLEMENTATION_GUIDANCE / NOT_SEMANTIC_QUALIFICATION`

## Research question

Can known human languages be represented by multidimensional mathematical/acoustic fingerprints that expose shared regularities, language/family-specific structure, and which acoustic dimensions carry linguistic information, without treating human typology as a universal ontology?

Current answer: **yes for measurable structure; not yet for universal semantic decoding**.

## Evidence

### Information-theoretic prosodic typology

Wilcox et al. (ACL 2025) estimate mutual information between lexical identity and pitch curves across ten languages from five families. Pitch curves show similar raw entropy across languages, but lexical identity predicts pitch more strongly in tonal languages. This directly supports information-theoretic coupling rather than raw pitch variance as the useful diagnostic.

Reference: Ethan Wilcox et al., "Using Information Theory to Characterize Prosodic Typology: The Case of Tone, Pitch-Accent and Stress-Accent", ACL 2025, DOI 10.18653/v1/2025.acl-long.1192.

### Prosody can carry information absent from text

Yadavalli et al. (ACL 2026) quantify information shared between meaning dimensions and audio/text channels. In their studied datasets, audio/prosodic information about sarcasm and emotion substantially exceeds text-only information, while questionhood shows a smaller increment. This supports explicit channel decomposition.

Reference: Aditya Yadavalli et al., "What Do Prosody and Text Convey? Characterizing How Meaningful Information is Distributed Across Multiple Channels", ACL 2026, DOI 10.18653/v1/2026.acl-long.1085.

### Tone is multidimensional

Phonetic literature treats `f0` as the primary acoustic cue to lexical tone while duration, intensity and voice quality may contribute. Tone systems vary in level/contour structure and functional load.

Reference: Lee & Mok, "Lexical Tone", Cambridge Handbook of Phonetics (2021).

### Rhythm is multidimensional

Cross-linguistic rhythm research uses duration metrics such as `%V`, `VarcoV`, and `nPVI-V`, while also treating `f0`, intensity/loudness, and combinations with duration as acoustic correlates of prominence.

Reference: Robert Fuchs, "Duration-Based and Acoustic Speech Rhythm Metrics", Rhythms of Speech and Language (Cambridge, 2026).

### Voice quality/timbre can be contrastive

Measures including `H1-H2`, spectral slope, periodicity and related harmonic measures distinguish phonation contrasts in multiple languages. Their linguistic importance differs by language—the exact kind of dimension-specific information loading UNVTRSLR should detect rather than assume.

References: Kreiman et al., "Effects of native language on perception of voice quality", PMC2997695; Garellek & Keating, Jalapa Mazatec phonation/tone study.

## Calibration universe

Use several corpora because each controls a different confound.

- **FLEURS:** 102 languages, roughly 12 hours per language, N-way parallel speech. Useful for holding semantic content approximately constant while comparing acoustic realization.
- **VoxLingua107:** 107 languages and 6,628 hours. Useful for testing whether fingerprints retain stable language-level structure across speakers/content/noise.
- **CMU Wilderness:** more than 700 languages with audio, aligned text and pronunciation material. Useful for breadth and held-out-family stress tests, while explicitly tracking read-script/religious-domain bias.
- **PHOIBLE 2.0:** 3,020 inventories, 2,186 languages, 3,183 segment types. Use as external validation labels after fingerprints are frozen.
- **WALS:** 2,662 languages represented on at least one map. Use for downstream structural comparison with missingness and genealogical/areal sampling controlled.

## Fingerprint vector

### Pitch / tonal channel

Raw `f0`; source-relative log/semitone `f0`; contour slope/curvature; range/quantiles; local derivatives; contour recurrence; phrase-relative reset only once segmentation is independently supported.

### Temporal/rhythmic channel

Energy/event onset intervals; duration and pause distributions; amplitude-envelope modulation spectrum; local pairwise variability; `nPVI`/`Varco` only when required segmentation is independently defensible.

### Intensity channel

RMS/log-energy; peak/mean dynamics; local derivatives; source-relative variability.

### Timbre / spectral-envelope channel

MFCCs; spectral centroid; bandwidth; rolloff; flatness; spectral slope; harmonic ratios including `H1-H2`; HNR/periodicity; later formant/anti-formant, jitter/shimmer/CPP once measurement quality is validated.

### Cross-channel mathematics

For each feature family `X_k`:

- entropy `H(X_k)`;
- mutual information `I(X_k; Y)`;
- conditional MI `I(X_k; Y | Z_nuisance)`;
- predictive gain on held-out sources;
- invariance under source/device/noise shift;
- interaction/synergy tests between channels;
- recurrence and transition entropy;
- cross-context stability;
- minimum-description-length gain versus simpler null models.

## Required controls

A classifier identifying a language is not semantic grounding.

The study needs speaker-held-out, family-held-out, content-held-out, recording/channel shift, pitch-preserving/destroying, timbre-preserving/destroying, time-scramble/rhythm, amplitude-normalization, source-frequency-scaling, and corpus/source-confound controls.

Every unavailable feature/test receives explicit applicability state rather than pass credit.

## Application to an unknown system

Known-language analysis produces a **measurement prior**, not a translation dictionary.

For an unknown channel:

1. capture minimally transformed raw signal;
2. extract broad candidate measurements;
3. estimate which dimensions contain stable predictive information;
4. condition out source/environment/history confounds;
5. perturb candidate dimensions where interaction permits;
6. preserve competing explanations;
7. only then let downstream R1/R2/R3 machinery test operational, semantic, and pragmatic claims.

If pitch predicts an outcome but the effect disappears after conditioning on source identity, pitch gets no semantic credit.

If a contour remains predictive across sources, contexts, and controlled interventions, it becomes a stronger candidate relation—but still not a meaning label by itself.

## Claim ceiling

`KNOWN_LANGUAGE_CALIBRATION_CAN_VALIDATE_MEASUREMENTS_NOT_UNIVERSAL_MEANING`

Human languages can teach UNVTRSLR where information often hides. They cannot prove that an unknown intelligence packages information the same way.
