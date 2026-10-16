# Simulation Theory Research Design

Status: APPROVED DESIGN / IMPLEMENTATION PENDING

## Purpose

Add simulation theory as a distinct On-Theo research branch without collapsing it into theology, digital physics, metaphysical idealism, or speculative cosmology.

The branch will research and compare several different propositions that are often conflated under the phrase `simulation theory`, including:

1. Bostrom-style ancestor-simulation population arguments.
2. Physical-universe simulation hypotheses in which our observed universe is implemented by an external computational substrate.
3. Digital-ontology and pancomputationalist theses in which computation is fundamental to physical reality, without requiring an external simulator.
4. Empirical-signature proposals tied to specific implementation models.
5. Computational and physical feasibility constraints.
6. Consciousness/substrate-independence assumptions required by many simulation arguments.
7. Epistemological questions about what embedded observers could know about their substrate.
8. Theological and religious analogies involving creation, creator/created-world relations, nested creators, demiurgy, illusion/reality, incarnation/avatar analogies, eschatological termination, and divine knowledge.

No branch artifact may silently upgrade any of these into the proposition that our universe actually is simulated.

## Evidence model

Reuse On-Theo evidence classes:

- `PRIMARY_TEXT`
- `MATERIAL_EVIDENCE`
- `HISTORICAL_RECONSTRUCTION`
- `LATER_TRADITION`
- `SCHOLARLY_INTERPRETATION`
- `PROJECT_INFERENCE`
- `SPECULATIVE_MODEL`
- `UNKNOWN`

Simulation-specific claim types may include:

- `PHILOSOPHICAL_ARGUMENT`
- `BAYESIAN_MODEL`
- `PHYSICAL_CONSTRAINT`
- `COMPUTATIONAL_LIMIT`
- `EMPIRICAL_TEST_PROPOSAL`
- `CONSCIOUSNESS_ASSUMPTION`
- `EPISTEMOLOGICAL_LIMIT`
- `METAPHYSICAL_MODEL`
- `THEOLOGICAL_COMPARISON`
- `HISTORICAL_ANALOGY`

The claim `our universe is simulated` defaults to `SPECULATIVE_MODEL` / unresolved unless future evidence justifies a different classification.

## Core distinctions

### Simulation argument != simulation hypothesis

Bostrom's 2003 argument is a conditional population/anthropic argument. It does not itself establish that ancestor simulations are physically possible or that we are presently simulated. Its three-way conclusion must be preserved exactly as an argument structure.

### External simulation != digital physics

The proposition that the universe is computational or information-theoretic does not entail that another universe is running it. Pancomputationalism, cellular-automaton ontology, quantum-information reformulations, mathematical structuralism, and an external simulator are separate models.

### Specific implementation signature != generic simulation evidence

A lattice artifact, cosmic-ray anisotropy, finite-resolution cutoff, or resource bound can at most test a class of simulator implementations unless an argument independently establishes broader generality.

### Simulator != God

A simulator may be finite, contingent, morally indifferent, embedded in another universe, or itself simulated. Classical theism makes materially different claims. Similar creator/created-world structure is a comparison target, not an identity claim.

### Historical analogue != anticipation

Plato's cave, dream skepticism, Maya, demiurgic traditions, creator myths, and illusion/reality systems may be compared structurally but must not be described as ancient computer-simulation theories unless the historical evidence supports that exact proposition.

## Research units

### 1. Simulation argument and Bayesian models

Primary anchors:

- Nick Bostrom, `Are You Living in a Computer Simulation?`, Philosophical Quarterly 53 (2003), 243-255.
- David Kipping, `A Bayesian Approach to the Simulation Argument` (2020).
- Bostrom/Weatherson debate and later reference-class critiques as available.

Deliverable: argument map separating assumptions about posthuman capability, willingness to run ancestor simulations, observer counting, reference classes, substrate independence, and simulation nesting.

### 2. Physical/computational feasibility

Primary scholarly anchors:

- Silas Beane, Zohreh Davoudi, Martin J. Savage, `Constraints on the Universe as a Numerical Simulation` (2012).
- Gordon McCabe, `Universe creation on a computer` (2005).
- David H. Wolpert, `Implications of computer science theory for the simulation hypothesis` (2024).
- F. Vazza, `Astrophysical constraints on the simulation hypothesis for this Universe` (2025).

Deliverable: constraint matrix stating exactly which simulator architecture each result constrains.

### 3. Digital ontology and pancomputationalism

Anchor:

- Stanford Encyclopedia of Philosophy, `Computation in Physical Systems`, especially pancomputationalism and ontic pancomputationalism.

Deliverable: taxonomy distinguishing external simulation, digital physics, cellular automata, quantum computational descriptions, mathematical structuralism, and information ontology.

### 4. Consciousness and substrate independence

Questions:

- Does a perfect behavioral simulation instantiate consciousness?
- Which simulation arguments assume computational functionalism or substrate independence?
- What changes if consciousness requires substrate-specific properties?
- Does observer counting depend on phenomenal consciousness, functional organization, or information processing?

Deliverable: assumption ledger. No theory of consciousness is to be promoted as settled.

### 5. Epistemology and metaphysics

Anchors:

- David J. Chalmers, `Reality+` and related 2024 debate.
- Terry Horgan and Christopher Peacocke critiques where accessible.
- Brain-in-a-vat / external-world skepticism literature as needed.

Deliverable: map of simulation realism, skepticism, reference, knowledge, value, and underdetermination.

### 6. Empirical test registry

For every proposed test, record:

- hypothesis actually tested;
- simulator architecture assumed;
- predicted observable;
- competing non-simulation explanations;
- whether a null result falsifies the narrow model, a larger model family, or nothing beyond the implementation proposal;
- whether a positive result uniquely favors simulation.

The default guard is: `implementation artifact != demonstrated provenance`.

### 7. Theology/religion comparison

Compare simulation models proposition-by-proposition with:

- creator/creation relations;
- transcendence and immanence;
- demiurgy;
- nested creators;
- omniscience/observation;
- incarnation/avatar analogies;
- eschatological world termination;
- illusion/reality traditions;
- fine-tuning/design arguments.

Modern philosophical anchors include Moti Mizrahi (2017) and Miles K. Donahue (2026) on simulation hypotheses and fine-tuning/theism.

Deliverable: comparison matrix that preserves theological and technological differences.

## Repository structure

Create under this branch:

- `research/simulation-theory/overview-v1.md`
- `research/simulation-theory/simulation-argument-v1.md`
- `research/simulation-theory/physical-computational-constraints-v1.md`
- `research/simulation-theory/digital-ontology-v1.md`
- `research/simulation-theory/consciousness-assumptions-v1.md`
- `research/simulation-theory/epistemology-metaphysics-v1.md`
- `research/simulation-theory/empirical-test-registry-v1.md`
- `comparative/simulation-theory-theology-v1.md`
- `registry/extensions/simulation-theory-v1.yaml`
- deterministic extension-manifest registration.

## World Zero boundary

On-Theo owns research, philosophical argument mapping, evidence classification, historical/theological comparison, and simulation-model propositions.

World Zero owns executable simulation experiments.

A future cross-repo handoff may propose experiments such as:

- whether embedded agents can infer lattice/granularity properties;
- whether embedded agents can distinguish implementation artifacts from endogenous laws;
- whether observer-level evidence can identify substrate provenance;
- how nested simulations distort anthropic inference.

No executable experiment result is to be treated as evidence that our own universe is simulated merely because the experiment reproduces an analogous epistemic problem.

## Review requirements

Before freezing the branch:

1. Source/readback review: exact claims match Bostrom, Kipping, Beane/Davoudi/Savage, Wolpert, Vazza, Chalmers, and other cited sources at the access level actually obtained.
2. Hostile review: identify hidden assumptions, unfalsifiable reformulations, anthropic/reference-class dependence, and places where digital ontology is being confused with external simulation.
3. Physics review: no Planck-scale, quantum, holographic, entropy, information, or computational-complexity claim is promoted beyond the source.
4. Theology review: analogy does not become identity or historical transmission.
5. Registry review: `SPECULATIVE_MODEL` and `PROJECT_INFERENCE` remain clearly distinguishable from empirical or textual support.

## Success criteria

V1 succeeds if it produces a provenance-aware map of what simulation theory actually contains, what parts are philosophical rather than empirical, what empirical proposals test only narrow implementations, what assumptions drive the probability arguments, how consciousness affects the argument, and where theological comparison is structurally illuminating without becoming evidence for either simulation or religion.
