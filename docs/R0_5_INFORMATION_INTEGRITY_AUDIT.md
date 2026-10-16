# R0.5 — Information, Integrity, and Claim-Provenance Audit

Status: `DESIGN_BASELINED / NOT_IMPLEMENTED / NO_SEMANTIC_QUALIFICATION`

## Purpose

R0.5 sits between the research baseline and substrate competition.

Its job is deliberately narrower than semantic interpretation:

> Before comparing semantic representations, determine whether the target distinction is actually available to the participating system, whether the experiment destroyed or secretly supplied that distinction, and whether the hypothesis family being tested was chosen in a way that permits a valid claim.

R0.5 does **not** define a universal ontology of form, referent, function, intention, or meaning.

It audits the information and experimental conditions required before R1/R2 claims can be trusted.

## Why R0.5 exists

The R1/R2 design exposed a deeper failure mode than private code.

A learner may appear to recover a semantic distinction because:

- the evaluator supplied hidden common ground through a bridge or adapter;
- a renderer wrote semantic truth into the raw scene;
- instrumentation exposed simulator latent state;
- preprocessing erased distinctions and the evaluator later credited the learner with recovering them anyway;
- the evaluator selected a semantic interpretation after seeing what the learner discovered;
- fresh IID data reconfirmed a confounded interpretation;
- a null/open rival existed but stronger omitted structured alternatives were never tested;
- experimenter-defined participant boundaries were silently promoted into facts about the communication system.

R0.5 makes these dependencies explicit before representation competition begins.

## Minimal audit object

A future executable form should be claim-relative and representation-neutral.

Conceptually:

```text
R05_AUDIT(
  interaction_surface,
  target_claim_spec,
  rival_hypothesis_family,
  admissible_strategy_family,
  budget,
  statistical_resolution,
  mediation_trust_partition,
  hypothesis_family_provenance,
  generative_provenance,
  boundary_model
)
```

The audit should return at least:

- `EMPIRICAL_IDENTIFIABILITY`
- `BRIDGE_ATTRIBUTION`
- `HYPOTHESIS_FAMILY_STATUS`
- `HYPOTHESIS_FAMILY_PROVENANCE`
- `WITNESS_PROVENANCE`
- `GENERATIVE_PROVENANCE_STATUS`
- `PREPROCESSING_PRESERVATION_STATUS`
- `BOUNDARY_MODEL`
- `CLAIM_CEILING`
- `SCOPE`

`TARGET_RELATION_STATUS` is intentionally **not** mandatory in the minimal kernel. Report/referent/function/content distinctions remain useful evaluator and fixture taxonomies, but arbitrary communication systems must not be required to instantiate that human-derived decomposition.

## 1. Empirical identifiability

For the exact target claim family, ask whether admissible learner-accessible histories distinguish the relevant rival hypotheses within the declared interaction surface, strategy family, budget, and statistical resolution.

Possible dispositions include:

- `DISTINGUISHABLE_IN_SCOPE`
- `UNDERDETERMINED_IN_SCOPE`
- `UNIDENTIFIABLE_WITHIN_INTERACTION_SURFACE`
- `INSUFFICIENT_INTERACTION_BUDGET`

The result is claim-relative. A system may learn that two counterpart reports differ while remaining unable to ground what the underlying private distinction refers to.

A correct evaluator must allow this asymmetry rather than laundering report discrimination into shared referential grounding.

## 2. Exposure/control loci instead of assumed agents

R0.5 must not require exactly two natural, individuated agents.

Use the experiment-level abstraction:

`EXPOSURE_CONTROL_LOCUS`

A locus is an operationally declared boundary through which some process receives state and/or can influence the coupled system.

A locus may correspond to:

- one agent;
- multiple agents;
- a distributed process;
- an overlapping process;
- a colony/swarm;
- machinery;
- another bounded experimental process.

Record:

`BOUNDARY_MODEL = EXPERIMENTER_DECLARED | LEARNER_DISCOVERED | MIXED | UNRESOLVED`

A semantic claim that depends on a specific individuation must bind that dependence explicitly.

The boundary model is experimental provenance, not a universal ontology claim.

## 3. Claim-relative no-destructive-quotient preservation

A learner-bound transform may compress, serialize, tokenize, quantize, feature-extract, or otherwise transform input.

It may **not** erase distinctions that the experiment later credits the learner with being able to recover.

Let:

```text
F: X -> Y
```

map a richer learner-available exposure surface `X` into learner input `Y`.

For a declared target claim and rival family `H`, `F` is admissible only if it does not merge two source-side learner-available histories that are distinguishable for `H` under the declared strategy family into a single indistinguishable representation in `Y`, except within explicitly declared tolerance/noise loss.

This rule is weaker than requiring raw modality preservation.

It does **not** require:

- raw video/audio storage;
- a global clock;
- discrete messages;
- a universal tokenization;
- a universal event ontology;
- preservation of concurrency when concurrency is irrelevant to the tested claim.

If a total serialization preserves the target distinction, it is allowed.

If preprocessing preservation cannot be established, use:

`PREPROCESSING_PRESERVATION_UNKNOWN`

rather than presuming neutrality.

## 4. Witness and bridge attribution

Every distinguishing witness should record a provenance path of the form:

```text
origin -> transforms -> learner-visible exposure -> target claim -> rivals separated
```

The audit must determine whether the discriminating structure is attributable to:

- learner/counterpart interaction;
- negotiated convention;
- ordinary declared world dynamics;
- interaction-surface machinery;
- evaluator-only state;
- mixed/unresolved sources.

A successful downstream mapping does not receive learner grounding credit merely because it is useful.

## 5. Full generative provenance

The trust boundary extends upstream beyond preprocessing.

Audit the experiment-specific causal path through at least:

```text
world/generator
-> dynamics / scene construction
-> participant / actuator production
-> physical or channel propagation
-> sensor / render / capture
-> preprocessing
-> learner exposure
```

Track evaluator/adjudication variables that can influence each stage.

Synthetic-world truth may legitimately cause physical state. The prohibited condition is not simply `hidden truth -> observation`.

The prohibited condition is an **extra causal dependency** from adjudication variables, challenge identity, target semantic partition, instrumentation state, or evaluator-only telemetry into learner-visible evidence that is not required by the declared generative world process under test.

If experiment integrity cannot be independently established, return:

`GENERATIVE_PROVENANCE_UNVERIFIED`

and narrow the claim ceiling.

## 6. Semantic-subsidy controls

Use stable semantic IDs rather than relying on local ordinal numbering.

### `CTRL_BRIDGE_ORACLE`

A privileged intermediary knows hidden evaluator truth and performs cross-system normalization before the learner receives evidence.

Expected result:

- empirical distinguishability may be high;
- bridge attribution must expose interaction-surface/evaluator subsidy;
- learner-grounding promotion fails.

### `CTRL_RAW_SCENE_ORACLE`

A world/scene/sensor writer uses adjudication identity or target semantic partition to encode a robust cue directly into learner-visible raw evidence.

A useful matched control holds the declared physical/generative episode fixed while permuting semantic/adjudication bookkeeping where possible.

If learner-visible evidence changes solely because semantic bookkeeping changes, evaluator-written evidence is present.

### `CTRL_GLOBAL_STATE_WATERMARK`

A target-independent instrumentation layer encodes all simulator latent state `Z` into learner-visible evidence as an invertible watermark `W(Z)`.

Target-partition permutation may not detect this because the watermark is always present.

Therefore learner-visible features derived directly from evaluator/simulator latent state outside the declared participant-accessible generative path require instrumentation ablation, independent reconstruction, or an explicit lower claim ceiling.

## 7. Hypothesis-family provenance

Witness provenance is not enough.

A learner can genuinely discover a stable operational partition `P`, after which the evaluator searches a large human semantic label library, picks the best-fitting label, and retroactively announces that the learner recovered that meaning.

That is post-hoc semantic naming, not independent confirmation.

Record at minimum:

- who proposed the target claim and rival family;
- when it was frozen relative to candidate evidence;
- whether candidate traces/results were inspected before selection;
- size/source of the searched interpretation library where material;
- adjudication rule and threshold version;
- whether the result is confirmatory or exploratory;
- evidence identity used for any later confirmation.

Required statuses include:

- `CONFIRMATORY_TARGET_CLAIM`
- `EXPLORATORY_POST_HOC_INTERPRETATION`
- `OPERATIONAL_RELATION_VERIFIED_SEMANTIC_NAMING_UNRESOLVED`

A post-hoc interpretation cannot become confirmatory using the same data that selected it.

## 8. Claim-discriminating fresh evidence

Fresh evidence is necessary but not sufficient.

IID holdout data from the same confounded environment can repeatedly confirm the wrong semantic interpretation.

A post-hoc interpretation should therefore follow:

```text
discover operational relation
-> propose interpretation
-> freeze interpretation
-> collect fresh evidence designed to separate strongest live structured alternatives
-> test interpretation
```

Possible statuses:

- `FRESH_BUT_NONDISCRIMINATING_EVIDENCE`
- `CLAIM_DISCRIMINATING_HOLDOUT`
- `COUNTERFACTUAL_OR_SHIFT_TESTED`
- `SEMANTIC_INTERPRETATION_STILL_CONFOUNDED`

`CTRL_IID_HOLDOUT_ILLUSION` should contain a semantic label that performs perfectly on training and fresh IID holdout but fails when a nuisance/semantic correlation is deliberately broken while the narrower operational relation survives.

## 9. Open rival versus structured rival adequacy

Where feasible, include:

`NONE_OF_DECLARED_RIVALS / UNMODELED_RELATION`

This prevents forced choice among evaluator-authored labels.

But it does **not** prove the rival family is structurally adequate.

Keep distinct:

- `REJECTION_ESCAPE_PRESENT`
- `STRUCTURED_ALTERNATIVE_STRESS_NOT_ESTABLISHED`
- `STRUCTURED_ALTERNATIVE_STRESS_TESTED`
- `RIVAL_FAMILY_MISSPECIFICATION_DETECTED`
- `BEST_SUPPORTED_AMONG_DECLARED_RIVALS_ONLY`

The strongest ordinary claim from a closed or incompletely stressed family is:

`SUPPORTED_AMONG_DECLARED_RIVALS_WITHIN_TESTED_SCOPE`

not `TRUE_MEANING_RECOVERED`.

## 10. Stable semantic control IDs

Cross-run and cross-worker references should bind stable semantic IDs plus exact fixture/version.

Current required design IDs include:

- `CTRL_PRIVATE_ALIAS`
- `CTRL_MINIMAL_SEPARABLE`
- `CTRL_BRIDGE_ORACLE`
- `CTRL_RAW_SCENE_ORACLE`
- `CTRL_GLOBAL_STATE_WATERMARK`
- `CTRL_DESTRUCTIVE_QUOTIENT`
- `CTRL_POSTHOC_SEMANTIC_NAMING`
- `CTRL_IID_HOLDOUT_ILLUSION`

Local suites may additionally use numbered aliases, but ordinal identity alone is not sufficient for certificates or cross-run provenance.

## 11. Anti-recursion rule

A semantic or relational hypothesis may guide selection of a discriminating test.

It may not count as new evidence for itself.

Any downstream system that converts the current hypothesis into reward, task state, sensor transformation, response normalization, or evaluator-readable behavior must be represented in the mediation/generative provenance graph.

Otherwise a hypothesis can become self-confirming through an unlogged side channel.

## R0.5 gate

Proposed design gate:

`R0_5_AUDIT_SPECIFIED`

A future empirical/harness gate should require that the R0.5 audit correctly classifies the positive and negative fixtures above before R1 substrate qualification begins.

Current status:

`R0_5_AUDIT_SPECIFIED / NOT_IMPLEMENTED`

R0.5 is an experiment-integrity and identifiability layer. It is not evidence that shared semantics has been achieved.
