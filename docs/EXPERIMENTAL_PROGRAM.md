# Experimental Program

## Goal

The experimental program exists to answer one question rigorously:

> Can shared semantics emerge without hidden shared language, and can we tell the difference between genuine semantic structure and task-specific coordination shortcuts?

The program should progress from easy controls with known answers toward conditions that increasingly resemble genuinely unfamiliar intelligence.

## Evaluation philosophy

The central danger is false success.

An experiment can appear to demonstrate communication while actually relying on:

- shared latent representations;
- identical perceptual encoders;
- evaluator-provided segmentation;
- synchronized object identities;
- hidden labels;
- task artifacts;
- memorized pairings;
- a private code that works only in one game;
- target leakage;
- reward shaping that supplies the semantics.

Therefore every stage needs both a success criterion and an adversarial explanation that would invalidate the success.

## Stage 0 — Infrastructure and evaluator isolation

Before semantic experiments, prove that the harness can keep learner-visible data separate from evaluator truth.

Required properties:

- deterministic scenario replay;
- explicit seeds/configuration;
- separate learner and evaluator channels;
- no hidden class labels in learner-visible metadata;
- logged interaction history;
- independent reconstruction of metrics;
- support for multiple sensory encodings;
- negative-control agents that should fail.

Gate:

`HARNESS_TRUSTWORTHY`

Do not claim semantic results before this gate passes.

## Stage 1 — Known-language positive controls

Give two agents access to the same underlying scene but different known human language labels or descriptions.

Do not provide a bilingual dictionary or parallel sentence pairs.

Candidate controls:

- English vs Spanish;
- English vs Mandarin;
- English vs typologically different languages;
- spoken/text-like channel vs signed/spatial representation.

The evaluator knows the intended semantic relationships and can measure what is recovered.

Purpose:

- verify that the protocol can reconstruct mappings that humans know exist;
- establish calibration and sample-efficiency baselines;
- identify where grammatical or lexical asymmetries produce partial rather than exact mappings.

## Stage 2 — Synthetic compositional language

Generate an artificial language with known semantics, grammar, ambiguity, and exceptions.

The learning agents do not receive the grammar.

The synthetic language should support:

- compositional constructions;
- synonymy;
- polysemy;
- context-sensitive expressions;
- irregular mappings;
- optional information;
- word-order or channel variation.

Because evaluator truth is exact, this stage is ideal for measuring whether UNVTRSLR reconstructs semantic structure rather than memorizing utterances.

## Stage 3 — Minimal grounded language game

Remove pre-existing vocabulary entirely.

Two agents observe a shared environment and must negotiate arbitrary signals for referents and relationships.

This stage should replicate and extend the tradition of grounded language games while imposing stronger anti-leakage controls.

Required tests:

- novel objects;
- novel combinations;
- role reversal;
- changed viewpoints;
- changed distractor sets;
- withheld attributes;
- transfer to a second task.

## Stage 4 — Unknown signal channel

Do not tell the learner which behavior constitutes communication.

Provide multiple behavioral channels, only some of which are informative or intentional.

Examples:

- motion;
- pulses;
- pauses;
- orientation;
- light/color modulation;
- environmental placement;
- random motor behavior.

Measure whether the system can identify which patterns function as signals and under which contexts.

## Stage 5 — Continuous/nonlinguistic channels

Replace discrete messages with continuous or embodied signals.

Candidate channels:

- duration encodes one dimension, orientation another;
- trajectories encode spatial goals;
- force or vibration encodes urgency;
- timing intervals encode sequence;
- environmental rearrangement encodes choices.

The honeybee waggle dance is an Earth example showing that motion parameters can communicate spatial information without human-like linguistic form.

## Stage 6 — Context-dependent meaning

Construct signals whose interpretation changes with context.

Example:

same signal form may mean:

- predator warning when no rival group is present;
- social/aggressive alert when rival-group context is present.

The evaluator should punish one-to-one dictionary mappings that ignore context.

This stage is motivated by animal communication research showing that seemingly lexical alarm calls can require contextual interpretation.

## Stage 7 — Asymmetric embodiment

Agents share a world but not a perceptual encoding.

Examples:

- Agent A: RGB vision;
- Agent B: depth/range only;
- Agent A: object detections;
- Agent B: optical flow;
- Agent A: allocentric map;
- Agent B: egocentric bearings;
- Agent A: high temporal resolution, low spatial resolution;
- Agent B: the reverse.

Success requires discovering relational invariants rather than aligning identical inputs.

## Stage 8 — Ontology mismatch

Deliberately give the agents different category systems.

Examples:

- one divides color continuously, another categorically;
- one has object identity, another only trajectories;
- one distinguishes two states the other initially merges;
- one has a sensory dimension unavailable to the other.

The success metric includes correct detection of partial and non-equivalent mappings.

## Stage 9 — Compositional semantic transfer

Require the negotiated communication system to solve a task structurally different from the one in which the meanings were learned.

Examples:

- learn spatial relations in referential games, then use them for navigation;
- learn event relations in observation, then use them for prediction;
- learn quantity distinctions in selection, then use them for resource allocation.

This tests whether the semantics are reusable rather than task-bound.

## Stage 10 — Intervention and causal discrimination

Introduce competing semantic hypotheses that passive observation cannot distinguish.

The system must choose safe interventions or queries.

Example:

A signal correlated with an object could mean:

- the object's color;
- its identity;
- a request to approach it;
- a warning about it.

Only controlled interventions distinguish these.

Measure:

- information gain per interaction;
- hypothesis calibration;
- unnecessary intervention cost;
- false causal attribution.

## Stage 11 — Counterfactual communication

Test whether the established semantic system supports statements or signals about events not currently occurring.

Examples:

- future prediction;
- conditional action;
- alternative location;
- absent referent;
- hypothetical state;
- false belief.

This is a major boundary between reactive coordination and richer semantic modeling.

## Stage 12 — Deception, error, and noncooperation

Introduce a counterpart that is occasionally:

- mistaken;
- noisy;
- inconsistent;
- deceptive;
- strategically withholding;
- noncooperative.

UNVTRSLR must not treat counterpart signals as ground truth.

Measure whether provenance and uncertainty prevent semantic corruption.

## Stage 13 — Human-in-the-loop zero-shared-language control

Use pairs of humans who do not share a language and restrict conventional channels.

Possible experimental variants:

- no speech/text;
- arbitrary minimal signal set;
- shared manipulable world;
- differing sensory access;
- time-limited convention creation.

Human experiments require appropriate ethics review and are not an early implementation dependency.

## Stage 14 — Animal-communication-inspired controls

Use synthetic simulations inspired by known Earth systems rather than claiming to decode live animals initially.

Candidate structures:

- honeybee-like vector encoding;
- context-dependent alarm calls;
- turn-taking acoustic sequences;
- audience-dependent precision;
- identity/social-unit acoustic signatures.

Project CETI's work on sperm-whale communication is relevant as an example of combining acoustic data with behavioral context and machine learning, but UNVTRSLR should not claim equivalence between predictive acoustic modeling and demonstrated semantic translation.

## Stage 15 — Interstellar bootstrap simulation

Simulate agents with aggressively different priors and channels.

The test should remove:

- human words;
- human object labels;
- common coordinate frames;
- common tokenization;
- shared time units;
- shared numeral notation.

Allow only reproducible physical regularities and interaction.

The system must bootstrap its own units and conventions.

## Core metrics

### Signalhood discovery

- precision/recall for communicative patterns;
- false-positive signal attribution;
- context-specific signalhood accuracy.

### Grounding accuracy

- referent/relation recovery;
- hypothesis calibration;
- semantic minimal-pair discrimination.

### Generalization

- novel instances;
- novel combinations;
- novel contexts;
- viewpoint changes;
- task transfer.

### Role symmetry

- receiver-to-sender productive transfer;
- convention stability under role reversal.

### Compositionality

Use multiple measures; no single compositionality metric should define success.

### Semantic conservation

- preserved invariants;
- unsupported additions;
- omissions;
- ambiguity collapse;
- non-equivalence detection.

### Sample efficiency

- interactions required per stable mapping;
- information gained per intervention.

### Robustness

- sensor mismatch;
- channel noise;
- semantic drift;
- partial observability;
- deceptive inputs.

### Calibration

- accuracy of semantic confidence estimates;
- willingness to return `UNKNOWN` or `NO_FAITHFUL_EQUIVALENT`.

## Concept establishment gate

A candidate concept should not count as established from a single task reward.

Where applicable, require a subset of:

1. repeated success;
2. novel-instance success;
3. context variation;
4. contrast/minimal-pair discrimination;
5. role reversal;
6. compositional use;
7. intervention confirmation;
8. counterfactual prediction;
9. evaluator-side independent reconstruction;
10. no simpler shortcut explaining the behavior.

The exact gate should be preregistered per challenge family.

## Required negative controls

Every major experiment should include one or more agents that deliberately violate the desired property:

- memorizer;
- direct label leaker;
- private-code coordinator;
- nonadaptive baseline;
- shuffled-context agent;
- identical-latent shortcut agent;
- overconfident forced translator;
- random communicator.

The harness is invalid if these controls pass the same semantic qualification.

## Experimental status

`PROGRAM_DEFINED / HARNESS_NOT_YET_BUILT / NO_SEMANTIC_QUALIFICATION_CLAIMED`
