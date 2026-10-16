# First Real-Corpus Result — MASSIVE 1.0

Executed subject: `b938d13c7293f72c6b769b95934b124d9c2901aa`

Workflow run: `35780678938`  
Workflow artifact: `10716994299`  
Dataset SHA-256: `7df623fd2d300a4d235d6ee5bd396c9a28258d3a0ccb29abdb054506eba153f8`

## Verdict

`MULTILINGUAL_HOLDOUT_THRESHOLD_NOT_MET`

This is a successful execution and a failed preregistered model qualification.

No train/test metadata leakage was detected.

## Aggregate metrics

- held-out records: 1,000
- training exposure records: 57,570
- languages: 5
- macro coverage: 0.2930
- macro exact match: 0.0100
- macro token similarity: 0.07235
- macro ambiguity rate: 0.1440

The frozen gate required coverage >= 0.10, exact match >= 0.05, token similarity >= 0.10, and ambiguity <= 0.25 in every language slice.

Coverage and ambiguity cleared the gate. Exact match failed in all five languages. Token similarity failed in de-DE, en-US, fr-FR, and tr-TR; only sw-KE cleared the token-similarity floor.

## Per-language result

| locale | coverage | exact | token similarity | ambiguity |
|---|---:|---:|---:|---:|
| de-DE | 0.290 | 0.005 | 0.07243 | 0.120 |
| en-US | 0.150 | 0.000 | 0.02315 | 0.055 |
| fr-FR | 0.350 | 0.015 | 0.08793 | 0.130 |
| sw-KE | 0.355 | 0.025 | 0.11419 | 0.225 |
| tr-TR | 0.320 | 0.005 | 0.06403 | 0.190 |

## What the failure means

The target-construction layer is not merely returning nothing: it produced at least one candidate on 29.3% of held-out records.

But the candidates are usually same-operational-class paraphrases rather than faithful realizations of the held-out utterance.

Examples from the exact prediction artifact:

- en-US reference `identify song` -> candidate `what's playing`
- en-US reference `what's the weather now` -> candidate `what's the weather`
- de-DE reference `wann geht mein wecker los` -> candidates equivalent to asking which alarms are set
- fr-FR and sw-KE sometimes include the exact held-out utterance among several construction variants

So PR #18 learned coarse recurring realization classes, but it did not learn enough reusable internal structure to compose the held-out slot-bearing utterance reliably.

## Architectural consequence

Do **not** lower the preregistered gate.

The next implementation frontier is productive construction induction:

1. factor frozen demonstrations into reusable semantic slots/substructures;
2. learn target-side slot placement and local token context;
3. preserve multiple competing realizations;
4. test on held-out **recombinations** that were never observed as whole utterances;
5. only then repeat this same MASSIVE packet with a new exact model head.

The failed result remains the baseline that the next model must beat.

## Evidence binding

The full generated training exposure and prediction artifacts were uploaded by the read-only workflow. Their exact byte hashes are recorded in `artifact_hashes.json`.

The split is additionally recoverable from the canonical MASSIVE 1.0 byte hash, selected locales, committed adapter, frozen partition rules, and deterministic holdout selection.

Claim ceiling remains:

`MASSIVE_V1_TARGET_CONSTRUCTION_GENERALIZATION_WITHIN_DECLARED_OPERATIONAL_ADAPTER`
