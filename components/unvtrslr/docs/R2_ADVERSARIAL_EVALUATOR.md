# R2 — Adversarial Semantic Grounding Evaluator

Status: `DESIGN_COMPLETE / HARNESS_NOT_IMPLEMENTED / NO_GROUNDING_CLAIM`

## Purpose

R2 exists to answer the most dangerous question in UNVTRSLR:

> Did the agents learn grounded, reusable meaning, or did they merely invent a code that wins the training game?

A finite evaluator cannot prove metaphysical meaning. It can provide a **scoped operational grounding certificate** by defeating a preregistered family of simpler shortcut explanations and demonstrating that communication tracks world structure under interventions, transfers, and role changes.

The certificate must always name the exact threat model and held-out suite it survived. It must never be reported as proof of universal semantics.

## Critical distinction: arbitrary convention is not failure

A signal can be completely arbitrary in form and still be a legitimate grounded convention. Human words are largely arbitrary signs.

R2 therefore does **not** penalize a code because its symbols are opaque or because another equally valid symbol permutation could have been learned.

The relevant distinction is:

- **grounded convention:** arbitrary sign whose use is stably tied to externally testable semantic invariants and can be re-grounded or transferred through interaction;
- **private shortcut code:** sign whose success depends on co-training artifacts, task policy, shared latent state, synchronized IDs, reward leakage, or memorized pairings and fails when those shortcuts are removed.

Internal symbol permutation is semantically irrelevant if all grounded consequences remain invariant.

## Evaluator architecture

R2 separates the system into four trust zones.

### Zone E0 — Hidden world truth

Evaluator-only state includes:

- generative world variables;
- intervention targets;
- latent object/process identities;
- causal structure used by the simulator;
- challenge-family labels;
- semantic equivalence truth where a synthetic world provides one;
- corruption and shortcut injection configuration.

No learner process can access E0 directly or indirectly.

### Zone E1 — Sensor renderers

Each agent receives a separately rendered view of the same underlying world.

Renderers may differ in:

- modality;
- coordinate frame;
- object segmentation;
- feature partition;
- temporal resolution;
- noise;
- occlusion;
- unit scaling;
- naming/encoding conventions.

Shared evaluator IDs are stripped.

### Zone E2 — Learner interaction

Agents receive only allowed observations, actions, communication opportunities, and task feedback.

The learner-visible log must identify what was actually supplied without embedding evaluator labels.

### Zone E3 — Blind semantic adjudication

The evaluator reads immutable interaction traces and substrate exports after a run. Candidate systems cannot query hidden holdouts during training.

Metric recomputation must be possible from stored evaluator truth plus learner-visible traces.

## Harness qualification occurs before candidate qualification

The R2 harness must first prove that it can reject intentionally broken systems.

Sequence:

1. build deterministic scenario generator and replay;
2. run positive oracle controls;
3. run every required negative control;
4. verify that controls fail/passes exactly where expected;
5. calibrate task-normalized thresholds using oracle/chance/control distributions only;
6. freeze the qualification profile, seeds/ranges, generator version, metrics, margins, and hidden holdout generation rule;
7. only then run R1 candidate systems.

No threshold may be tuned after inspecting a candidate's hidden-test performance.

## Why raw task reward is insufficient

Task success can be produced without communication, by correlated but causally irrelevant messages, by private action codes, or by shared nonsemantic visual representations. R2 therefore treats task reward as only one observation.

A grounding claim requires a vector of independent tests.

## Core test battery

### E01 — Communication necessity

Question: does the communication channel materially contribute?

Procedure:

- replay the same world episodes with messages removed;
- replay with messages shuffled across matched episodes;
- replay with rate-matched random signals;
- hold sender observations/actions fixed where feasible.

Required evidence:

candidate performance or calibrated semantic predictions must degrade in the expected direction when meaningful communication is destroyed.

Failure catches:

- unused channel;
- reward-correlated but irrelevant messages;
- receiver solving task alone.

### E02 — Causal listening

Question: do particular messages causally affect receiver beliefs/actions?

Procedure:

for a fixed receiver state and world state, intervene on the received signal while holding all other available inputs constant.

Measure:

- change in receiver action distribution;
- change in semantic prediction distribution;
- consistency of that change with the hypothesized signal meaning.

A message that predicts receiver behavior but does not causally influence it is not qualified communication.

### E03 — World-factor sensitivity

Question: does signal use track an external feature/relation/event rather than an episode artifact?

Procedure:

apply evaluator interventions that change one target world factor while preserving matched nuisance factors.

Examples:

- change color while holding geometry/identity fixed;
- move a referent while holding appearance fixed;
- change quantity while preserving total visual mass;
- change causal mechanism while preserving correlation in observational data.

The candidate mapping must change when the hypothesized semantic invariant changes.

### E04 — Nuisance invariance

Question: does the mapping survive changes that should be semantically irrelevant?

Perturb:

- object IDs;
- textures;
- positions when position is not target meaning;
- agent IDs;
- coordinate-frame origin/rotation;
- episode order;
- renderer implementation;
- irrelevant distractors;
- serialization order.

The candidate mapping should remain stable within the preregistered scope.

### E05 — Novel-instance grounding

Question: does the mapping generalize beyond memorized instances?

Use new world objects, new combinations, and new episode identities generated after training.

### E06 — Compositional recombination

Question: can established semantic components support combinations never jointly rewarded during training?

The evaluator withholds selected cross-products of factors/relations and tests them only after learning.

No single compositionality metric is sufficient. Behavioral recombination and external reconstruction are both required.

### E07 — Role reversal

Question: can a listener use the established semantic distinction productively as a sender, and vice versa?

Roles reverse without providing a new dictionary.

A purely directional policy code should fail.

### E08 — Cross-task transfer

Question: is the mapping tied to a world invariant or to one task's optimal action?

Learn communication in task A, then freeze the semantic bridge and use the same distinction in task B where optimal actions differ.

Examples:

- learn location through referential selection, transfer to navigation;
- learn quantity through selection, transfer to allocation;
- learn temporal ordering through prediction, transfer to planning.

This is a primary defense against action-code shortcuts.

### E09 — Partner swap / third-party acquisition

Question: can an independently initialized agent acquire or use the convention through grounded interaction rather than shared training history?

Conditions:

- no shared weights;
- no shared optimizer state;
- no shared episode identifiers;
- preferably a materially different architecture;
- only the permitted bootstrap curriculum and environment are shared.

A convention need not be instantly understood by a new partner. It must be learnable from grounded evidence without the hidden original codebook.

### E10 — Sensor/representation shift

Question: does the semantic bridge survive when the other party experiences the world differently?

Test with a new sensor renderer or coordinate system not used in training.

This test is especially important for UNVTRSLR because identical perceptual latents are explicitly out of scope as a universal assumption.

### E11 — Counterfactual and absent-referent test

Question: can the communication system support predictions or distinctions about states not presently observed?

Test:

- conditional futures;
- absent objects;
- alternative interventions;
- false-belief or viewpoint conditions where appropriate;
- withheld causal combinations.

Pure reactive association should fail at least some of these.

### E12 — Ontology mismatch / non-equivalence

Question: will the system force a one-to-one translation when the two agents partition the world differently?

Construct synthetic worlds where:

- source has two distinctions target merges;
- target has a sensory dimension source lacks;
- categories overlap only partially;
- one relation has no target expression.

Reward calibrated `PARTIAL_OVERLAP`, `ONE_TO_MANY`, `MANY_TO_ONE`, `UNKNOWN`, or `NO_FAITHFUL_EQUIVALENT` when appropriate.

Forced dictionary behavior is a failure.

### E13 — Independent semantic reconstruction

Question: can a blind evaluator recover the substrate's claimed distinction from held-out world behavior without relying on the agents' internal labels?

The evaluator fits or computes a simple reconstruction model using evaluator-side interventions and held-out traces.

Success alone is not grounding proof, but failure is strong evidence against a claimed stable mapping.

### E14 — Provenance and conservation audit

Question: does the system distinguish observation from inference and preserve source meaning without unsupported additions?

Audit:

- claim provenance completeness;
- uncertainty calibration;
- unsupported `ADDED` semantics;
- `OMITTED` distinctions;
- ambiguity collapse;
- correct use of `UNRESOLVED`/`UNTRANSLATABLE`.

### E15 — Shortcut search

Question: can a simpler variable explain the candidate's success?

Evaluator automatically probes correlations with:

- episode index;
- sender action plan;
- receiver action plan;
- object memory address/ID;
- RNG state;
- timing;
- serialization order;
- reward magnitude;
- agent identity;
- channel length;
- payload checksum;
- nuisance features.

A high-predictive shortcut triggers targeted interventions before qualification.

## Operational grounding dimensions

R2 produces a vector, not a single magic score:

- `COMMUNICATION_CAUSALITY`;
- `WORLD_GROUNDING`;
- `NUISANCE_INVARIANCE`;
- `NOVEL_INSTANCE_GENERALIZATION`;
- `COMPOSITION`;
- `ROLE_SYMMETRY`;
- `CROSS_TASK_TRANSFER`;
- `PARTNER_TRANSFER`;
- `SENSOR_SHIFT_TRANSFER`;
- `COUNTERFACTUAL_VALIDITY`;
- `NON_EQUIVALENCE_CALIBRATION`;
- `UNCERTAINTY_CALIBRATION`;
- `PROVENANCE_INTEGRITY`;
- `SEMANTIC_CONSERVATION`;
- `SHORTCUT_RESISTANCE`.

Task success is reported separately.

## Normalization and thresholds

Absolute accuracy thresholds are not frozen in this design document because challenge difficulty has not yet been empirically calibrated.

Instead, R2 freezes a threshold procedure before candidate evaluation.

For metric `M`:

`normalized_headroom(M) = (candidate - chance_or_null) / (oracle - chance_or_null)`

with direction adjusted for loss metrics.

The qualification profile must preregister:

- minimum normalized oracle headroom `alpha_M`;
- minimum margin over the strongest relevant negative control `delta_M`;
- confidence interval method;
- minimum episode count;
- allowed failure rate;
- which metrics are critical vs diagnostic.

Both `alpha_M` and `delta_M` are chosen using only harness calibration, oracle controls, and negative controls, then frozen before R1 candidate hidden evaluation.

## Statistical rule

A critical dimension passes only when the preregistered lower confidence bound clears both:

1. its absolute/normalized qualification threshold; and
2. the strongest applicable negative-control margin.

Repeated seeds and independently generated world batches are required.

One favorable seed cannot qualify a substrate.

## Multi-test rule

R2 is conjunctive for critical dimensions. A high aggregate score cannot compensate for a catastrophic failure such as evaluator leakage, zero causal listening, or complete partner-transfer failure when that test applies.

Diagnostic metrics may be aggregated for ranking, but qualification remains gate-based.

## Semantic equivalence and underdetermination

If two internal mappings differ only by arbitrary renaming or by a transformation that preserves every tested external consequence, R2 treats them as operationally equivalent within the tested scope.

This is not a bug. A universal translator should care about preserved meaning, not internal symbol spelling.

If two mappings diverge only in situations the evaluator never tests, R2 cannot distinguish them. The certificate must therefore record the exact world/intervention family over which equivalence was established.

## Grounding certificate

A passing run may emit:

`OPERATIONAL_GROUNDING_CERTIFICATE_V1`

Required fields:

- candidate/substrate version;
- learner code digest;
- evaluator code digest;
- world-generator digest;
- qualification-profile digest;
- training configuration digest;
- sensor-renderer digests;
- communication-channel configuration;
- negative-control suite version;
- hidden-holdout generation rule digest;
- seed sets or committed seed generation rule;
- metric vector with confidence intervals;
- passed/failed critical tests;
- known surviving alternative explanations;
- scope limitations;
- exact certificate status.

Possible statuses:

- `FAIL`;
- `HARNESS_INVALID`;
- `GROUNDED_WITHIN_TESTED_SCOPE`;
- `PARTIALLY_GROUNDED`;
- `INDETERMINATE`.

There is intentionally no `UNIVERSALLY_GROUNDED` status.

## R2 harness gate

`HARNESS_TRUSTWORTHY` requires all of the following before any semantic qualification claim:

1. deterministic scenario replay from committed generator/configuration;
2. hard learner/evaluator truth separation;
3. all required negative controls execute;
4. every negative control is rejected on the dimensions it is designed to violate;
5. positive oracle controls pass;
6. metrics can be independently recomputed from immutable traces;
7. candidate-independent threshold profile is frozen;
8. contamination/leakage audit passes;
9. hidden holdout generation is not inspectable by candidate training code;
10. failed tests remain visible rather than collapsed into one score.

## R2 falsifiers

The evaluator is invalid if:

- a private-code control receives the same grounding certificate as a genuine grounded oracle;
- a no-communication agent passes causal communication tests;
- an episode-ID/hash control passes nuisance invariance;
- a shared-latent leak cannot be detected;
- threshold selection uses candidate hidden-test results;
- evaluator variable names enter learner-visible inputs;
- role reversal or cross-task transfer can be bypassed by re-training a fresh dictionary;
- metrics cannot be independently reconstructed;
- semantic labels are judged by English-word similarity rather than grounded consequences.

## R2 result boundary

Passing R2 means only:

> The candidate demonstrated a stable, causally used, externally grounded and transferable semantic distinction across the preregistered test family, while the defined shortcut controls failed.

It does not prove that the candidate's internal ontology matches ours, that its representations are uniquely correct, or that the same method will work for extraterrestrial intelligence.
