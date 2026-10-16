# Semantic Substrate

## Purpose

The UNVTRSLR semantic substrate is the proposed formal intermediate layer between observation and rendering.

It is **not** intended to be a universal dictionary. It is a representation system for competing semantic hypotheses, relationships, evidence, uncertainty, and information loss.

The substrate exists so that the system can compare two representational systems without pretending that either one's vocabulary is the ontology of reality.

## Core idea

A semantic state should be able to express:

> what the system observed, what it thinks may be happening, why it thinks that, how certain it is, what alternatives remain, which parts were supplied by another agent, what predictions follow, and which parts can or cannot be faithfully rendered into the target system.

A graph/hypergraph plus typed probabilistic claims is a useful initial design candidate, but the project should not canonize a graph representation until it defeats simpler alternatives.

## Required representational responsibilities

The substrate must be able to represent at least the following structural classes.

### Observation

A bounded record of sensed or received evidence.

Fields should include:

- observation identity;
- source/channel identity;
- time or ordering evidence;
- raw or losslessly referenced payload;
- acquisition uncertainty;
- transformations already applied;
- provenance.

### Candidate signal

A hypothesized communicative unit or pattern.

A signal may be:

- discrete;
- continuous;
- temporal;
- spatial;
- multimodal;
- composite;
- absence/withholding;
- an environmental action.

A candidate signal must retain evidence for and against the claim that it is intentionally or functionally communicative.

### Entity hypothesis

A candidate persistent or recurring referent.

Do not require objecthood. An entity hypothesis may correspond to:

- an object;
- a region;
- a field;
- a trajectory;
- a process;
- an agent;
- a group;
- a recurring pattern;
- a relational structure.

### State

A condition that may hold over an interval or context.

Examples include location, possession, temperature, membership, readiness, or danger, but these labels are renderer examples rather than universal primitives.

### Event

A temporally bounded change or occurrence.

An event may have participants, preconditions, effects, duration, causal hypotheses, and uncertainty.

### Relation

A typed relationship among one or more nodes or hypotheses.

Relations may include spatial, temporal, quantitative, causal, social, logical, part-whole, similarity, or learned domain-specific relations.

### Quantity

A measured or inferred magnitude with explicit unit/provenance semantics.

Quantities should support dimensionless ratios because they may provide especially strong cross-system anchors.

### Ordering and time

The substrate must represent:

- observed ordering;
- simultaneity hypotheses;
- intervals;
- durations;
- periodicity;
- recurrence;
- uncertainty over temporal alignment.

It must not equate file order, clock time, causal order, and semantic sequence.

### Space and geometry

Spatial representations may be coordinate-based, relational, topological, agent-relative, or learned.

The kernel should support relationships without requiring a specific coordinate frame.

### Agent hypothesis

A candidate locus of perception, action, goal pursuit, or communication.

Agency must be inferred rather than silently assigned to every moving or signaling source.

### Action

A state transition plausibly attributable to an agent or actuator.

The representation must distinguish:

- observed action;
- requested action;
- predicted action;
- inferred intention;
- claimed consequence.

### Goal / preference hypothesis

A hypothesis that outcomes are differentially selected or valued by an agent.

Do not infer goals merely from one observed transition.

### Belief / epistemic state hypothesis

A hypothesis about what another agent may know, expect, attend to, or be uncertain about.

This becomes necessary for communicative repair, teaching, deception, and perspective-taking, but should remain explicitly inferential.

### Claim

A proposition-like object whose truth status is not assumed.

Every claim should carry provenance and support.

Examples:

- observed claim;
- counterpart-supplied claim;
- operator-supplied claim;
- model inference;
- evaluator truth;
- renderer paraphrase.

### Hypothesis set

A collection of mutually compatible or competing semantic interpretations.

The system should be able to retain:

`H1: signal X means RED, p=.55`

`H2: signal X means SPHERE, p=.31`

`H3: signal X means ATTEND-TO-OBJECT, p=.14`

rather than forcing a single dictionary entry.

### Constraint

A relationship that limits valid interpretations without necessarily naming a concept.

Examples:

- equality/inequality;
- exclusivity;
- co-occurrence;
- sequence;
- conservation;
- implication;
- incompatibility;
- cardinality.

### Counterfactual

A predicted semantic or world-state consequence under a hypothetical intervention.

Counterfactual structure is important because semantic understanding should eventually support more than association.

### Context

A bounded bundle of environmental, interactional, historical, and participant state relevant to interpretation.

Context must be referenceable, not hidden in a model state that the evaluator cannot inspect.

## Provenance model

At minimum, every semantic claim should identify an evidence class such as:

- `OBSERVED_DIRECT`;
- `OBSERVED_DERIVED`;
- `COUNTERPART_SIGNALLED`;
- `OPERATOR_SUPPLIED`;
- `MODEL_INFERRED`;
- `MODEL_PREDICTED`;
- `NEGOTIATED_CONVENTION`;
- `EVALUATOR_ONLY`.

The system should also retain which observations or claims support or contradict the claim.

## Uncertainty model

Uncertainty should distinguish several sources where possible:

- perceptual uncertainty;
- segmentation uncertainty;
- signalhood uncertainty;
- referential uncertainty;
- semantic uncertainty;
- causal uncertainty;
- translation/rendering uncertainty;
- model uncertainty;
- unknown unknowns / uncovered hypothesis space.

A single scalar confidence score is unlikely to be sufficient.

## Semantic identity and equivalence

Two expressions should not be considered equivalent because their embeddings are close or because they translate into the same English word.

Instead, the system should compare semantic structures through tested invariants.

Candidate equivalence classes include:

- `EXACT_WITHIN_SCOPE`;
- `FUNCTIONALLY_EQUIVALENT`;
- `CONTEXTUALLY_EQUIVALENT`;
- `PARTIAL_OVERLAP`;
- `ONE_TO_MANY`;
- `MANY_TO_ONE`;
- `APPROXIMATE`;
- `UNKNOWN`;
- `NO_FAITHFUL_EQUIVALENT`.

Every equivalence relation should be scoped to the evidence and tasks under which it was demonstrated.

## Translation bridge

A translation bridge is not merely a dictionary. It should contain mappings between:

- source signal hypotheses;
- source semantic structures;
- negotiated shared invariants;
- target semantic structures;
- target realizations.

A bridge may be asymmetric. Understanding another agent's warning may be easier than generating a warning that agent interprets correctly.

## Convention objects

When two agents stabilize a signal-meaning mapping through interaction, record it as a negotiated convention with:

- participants;
- channel;
- signal pattern;
- semantic hypothesis;
- context bounds;
- establishment evidence;
- last-confirmed interaction;
- counterexamples;
- role-reversal status;
- compositional behavior;
- confidence/calibration.

Conventions should be revisable. Semantic drift is expected.

## Meaning preservation ledger

Every source-to-target rendering should emit a structured conservation ledger:

- `PRESERVED` — semantic invariant retained;
- `TRANSFORMED` — different surface/structure, same tested function;
- `INFERRED` — target statement requires an explicit inference;
- `OMITTED` — source distinction lost;
- `ADDED` — target contains unsupported semantic content;
- `AMBIGUITY_COLLAPSED` — one interpretation selected from unresolved alternatives;
- `UNRESOLVED` — meaning not yet established;
- `UNTRANSLATABLE` — no faithful target counterpart currently known.

This ledger should be machine-readable and renderer-visible.

## Layer separation

A candidate implementation should preserve these planes:

1. **Acquisition plane** — raw sensor/channel observations.
2. **Segmentation plane** — candidate units and patterns.
3. **Communicative inference plane** — signalhood and communicative-function hypotheses.
4. **Grounding plane** — candidate referents, relationships, events, context.
5. **Semantic hypothesis plane** — structured meaning candidates and uncertainty.
6. **Experimental plane** — discriminating queries/interventions.
7. **Convention plane** — negotiated mappings and interaction history.
8. **Rendering plane** — target-language or target-modality realization.
9. **Evaluation plane** — withheld truth and scoring, inaccessible to the learner.

These are audit boundaries, not necessarily nine separate runtime services.

## Minimal rival

Before adopting a rich semantic graph, the project should compare it against a smaller substrate containing only:

- observation references;
- latent candidate clusters;
- relation tuples;
- probability distributions;
- provenance links;
- intervention outcomes.

If the richer representation does not improve generalization, non-equivalence detection, conservation accounting, or sample efficiency, the extra ontology has not earned its complexity.

## Key open question

The deepest unresolved question is whether a small representation grammar can remain genuinely modality- and species-neutral while still being expressive enough to support grounded communication.

That question must be answered experimentally rather than by declaring a universal semantic schema in advance.
