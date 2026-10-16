> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# UNVTRSLR

**Universal semantic mediation for communication without a shared language.**

UNVTRSLR began from a simple idea: if humanity wants to communicate with an unknown intelligence, especially an extraterrestrial one, sending a static message may be the wrong abstraction. A better artifact may be a system that can **discover how the other party communicates, establish shared reference, negotiate a semantic bridge, and then translate through that bridge**.

The original shorthand was:

> any language -> math -> English

The research program in this repository uses a stronger formulation:

> **meaning-bearing observations -> grounded formal semantic hypotheses -> tested shared semantics -> target rendering**

Mathematics is therefore not assumed to *be* universal meaning. It is used as a formal carrier for structures that have been grounded, tested, and assigned explicit uncertainty and provenance.

## Core research question

Can interacting systems with:

- zero shared symbols,
- no assumed linguistic communication channel,
- potentially different sensory systems,
- potentially different internal ontologies,
- no guaranteed shared segmentation of objects/events/agents/messages,
- and only whatever causal or observational interaction surface is actually available,

**discover signalhood or other stable interaction regularities, establish grounded semantic invariants, create compositional communication, and identify both translatable and genuinely non-equivalent concepts?**

If that can be demonstrated under increasingly hostile controls, UNVTRSLR becomes more than a translator. It becomes a candidate **semantic bootstrap protocol**.

## Why this is different from ordinary translation

Ordinary machine translation assumes both sides already use human language and that enough semantic overlap exists to map one linguistic surface into another.

UNVTRSLR does not assume:

- words,
- syntax,
- discrete symbols,
- speech,
- text,
- shared sensory categories,
- a shared ontology,
- a shared concept of an object,
- fixed message boundaries,
- exactly two naturally individuated agents,
- or even that a behavior is intended as communication.

The system must be able to consider continuous signals, timing, motion, geometry, environmental modification, multimodal behavior, distributed processes, and contextual meaning.

## Foundational design commitments

1. **Ground before translating.** Formal symbols do not become meaningful merely by referring to other symbols.
2. **Do not assume language.** Linguistic communication is one possible channel, not the architecture.
3. **Do not assume the Rosetta Stone.** A shared environment or interaction surface is a candidate source of common reference, but it can silently smuggle shared segmentation, salience, timing, objecthood, or evaluator-authored structure. Those assumptions must be audited.
4. **Signalhood is a hypothesis.** The system must distinguish behavior from communication rather than receiving a pre-labeled message stream.
5. **Meaning is contextual.** Signal + environment + history + producer state + receiver state may be required to infer meaning.
6. **Uncertainty is part of meaning.** Ambiguity must not be silently collapsed.
7. **Provenance is part of meaning.** Observation, supplied claim, inference, prediction, negotiated convention, and evaluator truth must remain distinct.
8. **Translation may be lossy or impossible.** A scoped no-equivalent result is valid; the system must not force a mapping.
9. **Communication success is not enough.** Agents can invent private codes that solve a task without learning reusable grounded distinctions.
10. **Arbitrary notation is not failure.** A convention may use arbitrary signs; the failure is hidden common ground or task-bound code that does not survive grounding tests.
11. **Meaning must survive tests.** Novel instances, context changes, role reversal, composition, intervention, cross-task transfer, partner transfer, and counterfactual prediction are stronger evidence than agreement on a symbol.
12. **English is a renderer, not the semantic center.** Other natural languages, diagrams, equations, actions, or other modalities are equally valid target realizations.
13. **A universal ontology is not assumed.** The universal layer should be a grammar for representing hypotheses, relationships, uncertainty, provenance, and evidence—not an encyclopedia of human concepts.
14. **Grounding claims are scoped.** No finite evaluator proves a uniquely correct ontology or universal meaning; certificates bind the exact worlds, interventions, controls, rival families, and threats survived.
15. **Experiment integrity precedes semantic credit.** If preprocessing destroys a distinction, instrumentation leaks simulator truth, or a hidden bridge performs semantic normalization, the learner does not get credit for recovering that distinction.
16. **Semantic naming must be earned separately.** A real operational partition may remain semantically unnamed. Post-hoc human interpretations are exploratory until frozen and tested on claim-discriminating fresh evidence.
17. **Stronger semantic words incur stronger empirical burdens.** If `semantic correspondence` adds no falsifiable obligation beyond `reusable operational relation`, use the weaker claim.

## R0.5 — pre-R1 information and experiment-integrity audit

Before the R1 substrates are compared, UNVTRSLR now inserts a deliberately thin **R0.5** layer.

R0.5 does not attempt to solve semantics. It asks:

- is the declared distinction empirically identifiable from learner-accessible evidence?
- did preprocessing preserve the distinctions the experiment later credits the learner with recovering?
- did an adapter, renderer, simulator, instrumentation path, task API, or evaluator secretly supply the bridge?
- who authored the rival hypothesis family, and was it frozen before candidate evidence was inspected?
- are participant/agent boundaries experimenter-declared or independently earned?
- is an open/null rival available, and has structured rival misspecification actually been stressed?

Important controls include:

- `CTRL_BRIDGE_ORACLE`
- `CTRL_RAW_SCENE_ORACLE`
- `CTRL_GLOBAL_STATE_WATERMARK`
- `CTRL_DESTRUCTIVE_QUOTIENT`
- `CTRL_POSTHOC_SEMANTIC_NAMING`
- `CTRL_IID_HOLDOUT_ILLUSION`

R0.5 may legitimately return `UNIDENTIFIABLE_WITHIN_INTERACTION_SURFACE`, `PREPROCESSING_PRESERVATION_UNKNOWN`, or `GENERATIVE_PROVENANCE_UNVERIFIED` rather than forcing a semantic conclusion.

See [`docs/R0_5_INFORMATION_INTEGRITY_AUDIT.md`](docs/R0_5_INFORMATION_INTEGRITY_AUDIT.md).

## Executable reference stack on main

The current `main` candidate contains executable reference components in addition to the original research/design program:

- acoustic measurement and information channels;
- candidate acoustic event discovery;
- non-destructive raw event descriptors;
- cross-recording recurrence registry;
- frozen out-of-sample acoustic unit models;
- nuisance-conditioned cross-linguistic calibration;
- cross-situational operational correspondence learning;
- source-calibrated reference translation with frozen query-independent normalization;
- order-sensitive AB-vs-BA operational relations over frozen global acoustic units;
- learned target-language grounding from target-side demonstrations, including explicit ambiguity and scoped non-equivalence;
- multiword target constructions and target-specific ordering learned directly from grounded sequence demonstrations;
- leakage-audited multilingual held-out qualification across declared real corpora.

The current integrated successor is documented in [`docs/REFERENCE_TRANSLATOR_V2.md`](docs/REFERENCE_TRANSLATOR_V2.md).

The implementation claim remains narrow: these components have synthetic/reference fixtures and explicit fail-closed states. They have **not** established universal translation, uniquely correct semantics, real-corpus qualification, or deployment readiness.
## Current R1/R2 architecture challenge

The project has three deliberately competing minimal semantic substrates:

- **TPH — Typed Probabilistic Hypergraph:** explicit structured relational hypotheses;
- **DCA — Denotational Constraint Algebra:** executable constraints/operators over compatible situations and trajectories;
- **PIS — Predictive-Intervention State:** action-conditioned predictions and signal-induced predictive changes.

No substrate is architecture canon. The richer candidates must empirically earn their additional commitments.

The R2 evaluator is designed to distinguish grounded convention from private shortcut code using causal message interventions, world-factor interventions, nuisance shifts, role reversal, cross-task transfer, partner swap, sensor shifts, counterfactual tests, ontology mismatch, conservation audits, and a required suite of intentionally deceptive negative controls.

R2 now also separates **operational relation verification** from **semantic interpretation confirmation**. A post-hoc label cannot be confirmed using the same evidence that selected it; fresh IID evidence is not enough if it preserves the original confound; and a stronger semantic claim must carry an explicit `SEMANTIC_SURPLUS_OBLIGATION`—some additional falsifiable prediction or qualification burden beyond ordinary operational success.

See [`docs/R2_SEMANTIC_CLAIM_CONTROLS.md`](docs/R2_SEMANTIC_CLAIM_CONTROLS.md).

A passing result may eventually receive `GROUNDED_WITHIN_TESTED_SCOPE`; there is intentionally no `UNIVERSALLY_GROUNDED` status.

## Repository map

- [`docs/PROJECT_THESIS.md`](docs/PROJECT_THESIS.md) — the refined concept and hypotheses.
- [`docs/DESIGN_PRINCIPLES.md`](docs/DESIGN_PRINCIPLES.md) — architecture-level constraints.
- [`docs/SEMANTIC_SUBSTRATE.md`](docs/SEMANTIC_SUBSTRATE.md) — proposed semantic responsibilities before R1 competition.
- [`docs/R0_5_INFORMATION_INTEGRITY_AUDIT.md`](docs/R0_5_INFORMATION_INTEGRITY_AUDIT.md) — pre-R1 identifiability, preprocessing, generative-provenance, bridge-attribution, and hypothesis-family audit.
- [`docs/R1_SUBSTRATE_COMPETITION.md`](docs/R1_SUBSTRATE_COMPETITION.md) — three genuinely competing minimal semantic substrates and the fair competition rule.
- [`docs/R2_ADVERSARIAL_EVALUATOR.md`](docs/R2_ADVERSARIAL_EVALUATOR.md) — adversarial semantic-grounding evaluator and scoped certificate.
- [`docs/R2_NEGATIVE_CONTROLS.md`](docs/R2_NEGATIVE_CONTROLS.md) — shortcut systems plus positive oracles the harness must classify correctly.
- [`docs/R2_SEMANTIC_CLAIM_CONTROLS.md`](docs/R2_SEMANTIC_CLAIM_CONTROLS.md) — confirmatory/exploratory interpretation discipline, structured-rival adequacy, claim-discriminating holdouts, and semantic-surplus obligations.
- [`specs/R1R2_EVALUATION_CONTRACT_V1.yaml`](specs/R1R2_EVALUATION_CONTRACT_V1.yaml) — machine-readable R1/R2 evaluation contract; a future revision must bind the R0.5 fields and new claim controls before implementation qualification.
- [`docs/BOOTSTRAP_PROTOCOL.md`](docs/BOOTSTRAP_PROTOCOL.md) — how communication could be established from zero shared symbols.
- [`docs/SEMANTIC_CONSERVATION.md`](docs/SEMANTIC_CONSERVATION.md) — what it means to preserve meaning.
- [`docs/EXPERIMENTAL_PROGRAM.md`](docs/EXPERIMENTAL_PROGRAM.md) — staged falsification program.
- [`docs/FIRST_100_CHALLENGES.md`](docs/FIRST_100_CHALLENGES.md) — 100 semantic challenges, not 100 presumed universal words.
- [`docs/CONTROL_SUITE.md`](docs/CONTROL_SUITE.md) — Earth-language, synthetic, nonlinguistic, asymmetric, and negative controls.
- [`docs/INTERSTELLAR_DEPLOYMENT.md`](docs/INTERSTELLAR_DEPLOYMENT.md) — probe, broadcast, and hybrid architectures.
- [`docs/FAILURE_MODES.md`](docs/FAILURE_MODES.md) — ways the project can fool itself.
- [`docs/RESEARCH_LANDSCAPE.md`](docs/RESEARCH_LANDSCAPE.md) — relationship to prior research.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — ordered research phases and gates.
- [`research/CLAIMS_AND_EVIDENCE.md`](research/CLAIMS_AND_EVIDENCE.md) — evidence-status ledger.
- [`research/REFERENCES.md`](research/REFERENCES.md) — base literature and source notes.
- [`research/R1R2_RESEARCH_NOTES.md`](research/R1R2_RESEARCH_NOTES.md) — representation/evaluator research synthesis.
- [`research/R1R2_REFERENCES.md`](research/R1R2_REFERENCES.md) — sources added specifically for R1/R2.
- [`docs/ACOUSTIC_MATHEMATICAL_FINGERPRINT_V1.md`](docs/ACOUSTIC_MATHEMATICAL_FINGERPRINT_V1.md) — executable acoustic measurement contract.
- [`docs/CANDIDATE_EVENT_DISCOVERY_V1.md`](docs/CANDIDATE_EVENT_DISCOVERY_V1.md) — prelinguistic event-hypothesis layer.
- [`docs/CROSS_RECORDING_UNIT_REGISTRY_V1.md`](docs/CROSS_RECORDING_UNIT_REGISTRY_V1.md) — cross-source recurrence registry.
- [`docs/FROZEN_UNIT_MODEL_V1.md`](docs/FROZEN_UNIT_MODEL_V1.md) — stable out-of-sample acoustic identity model.
- [`docs/RAW_EVENT_ACOUSTIC_EVIDENCE_V1.md`](docs/RAW_EVENT_ACOUSTIC_EVIDENCE_V1.md) — non-destructive raw event evidence view.
- [`docs/REFERENCE_SEMANTIC_BRIDGE_V1.md`](docs/REFERENCE_SEMANTIC_BRIDGE_V1.md) — operational cross-situational correspondence learner.
- [`docs/REFERENCE_TRANSLATOR_V2.md`](docs/REFERENCE_TRANSLATOR_V2.md) — source-calibrated end-to-end successor integration.
- [`docs/CALIBRATION_HOLDOUT_QUALIFICATION_V1.md`](docs/CALIBRATION_HOLDOUT_QUALIFICATION_V1.md) — held-out acoustic qualification for frozen source calibration profiles.
- [`docs/ORDERED_COMPOSITIONAL_RELATIONS_V1.md`](docs/ORDERED_COMPOSITIONAL_RELATIONS_V1.md) — AB-vs-BA order-sensitive operational structure over frozen global acoustic units.
- [`docs/LEARNED_TARGET_GROUNDING_V1.md`](docs/LEARNED_TARGET_GROUNDING_V1.md) — target-language realization learned from grounded demonstrations rather than a hand-authored atom-to-word codebook.
- [`docs/MULTIWORD_TARGET_CONSTRUCTIONS_V1.md`](docs/MULTIWORD_TARGET_CONSTRUCTIONS_V1.md) — multiword realization and target-side ordering learned from grounded semantic-sequence demonstrations without a hand-authored grammar.
- [`docs/MULTILINGUAL_HELDOUT_QUALIFICATION_V1.md`](docs/MULTILINGUAL_HELDOUT_QUALIFICATION_V1.md) — leakage-declared real multilingual evaluation regimes, metrics, and qualification contract.
- [`research/MULTILINGUAL_CORPUS_MANIFEST_V1.json`](research/MULTILINGUAL_CORPUS_MANIFEST_V1.json) — pinned corpus roles, versions, strengths, and limitations.

## The key experimental standard

A semantic mapping is not counted as established merely because the receiver performs correctly once.

A candidate distinction should survive, where applicable:

1. communication ablation;
2. direct message intervention;
3. world-factor intervention;
4. nuisance transformations;
5. novel instances;
6. novel contexts;
7. role reversal;
8. recombination with other established distinctions;
9. transfer to a task with different optimal actions;
10. acquisition/use by an independently initialized partner;
11. changed perceptual presentation;
12. counterfactual or predictive tests;
13. ontology-mismatch/non-equivalence traps;
14. independent evaluator reconstruction;
15. provenance and semantic-conservation audit;
16. automated search for simpler shortcut explanations;
17. R0.5 preprocessing/generative-provenance and bridge-attribution controls;
18. confirmatory-vs-post-hoc hypothesis-family provenance;
19. claim-discriminating holdout or intervention against strongest live structured alternatives;
20. an explicit semantic-surplus obligation for any claim stronger than an operational relation.

The system must also be rewarded for correctly preserving unmodeled relations, uncertainty, partial overlap, and non-equivalence rather than forcing them into evaluator-authored categories.

## Interstellar motivation

Historical interstellar messages such as the Pioneer plaques, Arecibo transmission, Voyager Golden Record, and the Lincos project attempt to construct content that a radically unfamiliar recipient might decode. UNVTRSLR asks a different question:

> **What if the transmitted artifact is not primarily the message, but the machinery for constructing a shared semantics?**

For an embodied probe, that machinery could interact locally with a recipient and a shared environment. For a broadcast, it could be a progressively self-demonstrating, convention-forming, and eventually self-describing semantic curriculum and protocol. A hybrid architecture could use both.

## Status

`R0_5_R1_R2_DESIGN_BASELINED / REFERENCE_IMPLEMENTATION_CANDIDATES_ACTIVE / REAL_CORPUS_QUALIFICATION_HARNESS_ACTIVE / NO_REAL_CORPUS_PASS`

The repository now contains both the research program and draft executable reference candidates for measurement, event discovery, cross-source acoustic identity, operational grounding, and source-calibrated translation. These are reference implementations under adversarial review, not a proven universal language, universal ontology, or extraterrestrial communication solution. The strongest claims here are intentionally written so they can fail.