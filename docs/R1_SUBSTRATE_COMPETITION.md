# R1 — Minimal Semantic Substrate Competition

Status: `DESIGN_COMPLETE / NOT_IMPLEMENTED / NOT_QUALIFIED`

## Purpose

R1 exists to prevent the project from canonizing a rich semantic representation merely because it is intuitive to humans.

Three materially different semantic substrates are defined below. They do not differ only in serialization. They make different claims about what a meaning representation should fundamentally be:

1. **TPH — Typed Probabilistic Hypergraph:** meaning as explicit structured hypotheses about entities, events, relations, context, and claims.
2. **DCA — Denotational Constraint Algebra:** meaning as an executable constraint/operator that selects or transforms compatible situations or trajectories.
3. **PIS — Predictive-Intervention State:** meaning as action-conditioned predictions and changes in those predictions under signals and interventions.

The competition is deliberately adversarial. No substrate is privileged. A richer substrate must earn every additional representational commitment.

## R1 boundary

R1 does **not** decide whether extraterrestrial minds use entities, predicates, compositional syntax, possible-world semantics, or predictive-state representations. Those are candidate inductive biases to test.

R1 also does not claim that an internal representation is meaningful because it is interpretable to a human. Human readability is evidence for auditability, not grounding.

## Common behavioral contract

The evaluator must compare the substrates through a common behavioral interface without requiring identical internal data structures.

Each candidate must support an adapter that can:

- ingest an observation or interaction event by opaque reference;
- update its current semantic state;
- maintain more than one candidate interpretation when evidence is ambiguous;
- attach uncertainty and provenance to outputs;
- condition on a received candidate signal;
- predict future observables under a proposed action or intervention;
- compare two source expressions/signals for scoped equivalence or non-equivalence;
- expose evidence supporting and contradicting a candidate mapping;
- answer evaluator queries about a held-out situation without direct evaluator labels;
- produce enough information for a conservation ledger;
- preserve `UNKNOWN` and `NO_FAITHFUL_EQUIVALENT` as valid outcomes.

Any adapter complexity counts against the substrate. A representation cannot hide essential semantic machinery in an uncounted compatibility layer.

## What is fixed across all competitors

The following responsibilities are architectural requirements, not substrate-specific advantages:

- learner/evaluator separation;
- raw observation references remain recoverable;
- evaluator-only truth never enters learner-visible state;
- uncertainty is explicit;
- provenance is explicit;
- observations, counterpart claims, model inferences, predictions, and evaluator truth are different evidence classes;
- no English or human-language concept labels are available to the learner;
- communication signals may be arbitrary, continuous, temporal, spatial, multimodal, or environmental actions;
- all semantic claims are scoped to demonstrated contexts.

## Substrate A — TPH: Typed Probabilistic Hypergraph

### Core commitment

The world can usefully be modeled through explicit structured hypotheses linked by typed relationships.

TPH represents semantic state as a probabilistic hypergraph:

`G = (V, E, C, P)`

where:

- `V` contains opaque hypothesis nodes and observation references;
- `E` contains typed n-ary relationships;
- `C` contains context/provenance scopes;
- `P` contains uncertainty distributions or factor potentials over hypotheses.

### Minimal structural node classes

The fixed node classes are deliberately meta-semantic rather than English-semantic:

- `OBSERVATION_REF`;
- `HYPOTHESIS`;
- `CONTEXT`;
- `CLAIM`;
- `SIGNAL_CANDIDATE`;
- `CONVENTION`.

More specific types such as object, event, agent, possession, red, predator, gift, or promise are **not** built into the R1 kernel. They must be learned or expressed through opaque type identifiers whose empirical behavior can be tested.

### Hyperedge form

A minimal relation record is:

`edge_id, relation_type_id, arguments[], scope, probability, provenance_refs[], support_refs[], contradiction_refs[]`

Relation type identifiers are not human labels during learning.

### Composition

Composition occurs by graph unification, role binding, context restriction, and probabilistic conjunction.

A complex signal can therefore become a structured candidate such as an opaque relation among several opaque referents without requiring the evaluator's names for those relations or referents.

### Intervention support

TPH may attach causal hypotheses to edge structures, but a causal relation is never promoted from temporal correlation alone. Intervention outcomes update edge probabilities.

### Strengths

- explicit compositional structure;
- natural provenance tracing;
- convenient representation of one-to-many and many-to-one mappings;
- direct support for semantic-conservation accounting;
- interpretable failure analysis;
- likely strong fit for natural-language rendering if the learned structure is valid.

### Risks

- anthropomorphic ontology leakage through node/relation design;
- type explosion;
- false confidence caused by readable graphs;
- brittle graph matching;
- expensive inference;
- a tendency to encode evaluator categories in the representation rather than discover them.

### Minimality burden

TPH loses to a simpler rival if its extra structure does not produce measurable gains in transfer, non-equivalence detection, calibration, compositional recombination, conservation, or sample efficiency.

## Substrate B — DCA: Denotational Constraint Algebra

### Core commitment

Meaning need not be a graph describing what exists. It can be modeled as an operator that constrains which situations, trajectories, or transformations remain compatible with an expression.

For an expression or signal `x` in context `c`, DCA represents a probabilistic denotation:

`D(x | c) -> score over candidate situations/trajectories`

The learner does not receive evaluator state-variable names. Candidate situations are represented through learned perceptual variables and opaque references.

### Minimal primitive machinery

DCA contains:

- learned atomic detectors or partitions over observations;
- variables/bindings over opaque referents or trajectory segments;
- weighted constraints;
- composition operators;
- provenance and uncertainty records.

The initial operator set is intentionally small:

- `FILTER` — restrict a candidate set;
- `JOIN` — relate compatible candidates;
- `PROJECT` — preserve only selected variables/bindings;
- `COMPOSE` — apply one denotation/operator after another;
- `NEGATE` — exclude a candidate denotation where the task supports contrast;
- `COMPARE` — express equality/difference/order over learned values;
- `SHIFT` — relate a denotation to another time/interaction slice;
- `INTERVENE` — evaluate compatibility after an action or controlled perturbation.

These are mathematical operators, not claims that an alien mind natively uses them.

### What counts as a concept

A concept-like mapping is a stable constraint or operator that isolates the same relevant class of situations across novel contexts while ignoring nuisance changes.

For example, the learner need not possess a node named `BEHIND`. It may learn an operator whose denotation consistently selects the appropriate spatial configurations across objects, viewpoints, and tasks.

### Composition

A complex expression is an algebraic composition of simpler learned denotations. The evaluator tests whether this composition predicts held-out combinations rather than whether it resembles human syntax.

### Non-equivalence

Two expressions are equivalent only if their denotations remain equivalent over a preregistered family of held-out contexts and interventions.

Partial overlap is represented directly by overlap between denotations. `NO_FAITHFUL_EQUIVALENT` is appropriate when no target expression/operator preserves the required denotation within scope.

### Strengths

- fewer ontological commitments than TPH;
- semantics tied directly to discriminable conditions;
- natural treatment of context and partial overlap;
- strong fit for compositional and non-equivalence testing;
- formal equivalence can be evaluated extensionally over held-out worlds.

### Risks

- denotation may become an enormous lookup table;
- learned perceptual variables can hide a human ontology if not audited;
- generic operators are still inductive biases;
- extensional agreement can hide different untested intensions;
- hard to express rich epistemic or social meaning without adding machinery;
- evaluator world variables must remain strictly isolated from learner operands.

### Minimality burden

DCA must show that explicit operator structure provides benefits over purely predictive operational state. If operator composition adds no transfer or explanatory value, it has not earned its complexity.

## Substrate C — PIS: Predictive-Intervention State

### Core commitment

A semantic system may not need explicit entities, predicates, denotations, or ontology at all. Meaning can be operationally grounded in what a signal changes about predictions of future observations under possible actions.

PIS is inspired by predictive-state representations, where state is represented through action-conditional predictions of future observations rather than inaccessible hidden-state labels.

Let `q(h)` be a vector of predictions after interaction history `h`:

`q_i(h) = P(test_i succeeds | h)`

where each `test_i` is an action/observation sequence or other bounded future experiment.

### Signal semantics

A candidate signal `m` is represented by its context-dependent operator on predictive state:

`T_m : q(h) -> q(h, m)`

The operational meaning of the signal is therefore the stable pattern of predictive/interventional consequences it produces across contexts.

### Composition

Sequential or composite signals become operator composition:

`T_(m1,m2) = T_m2 o T_m1`

The evaluator does not assume that this corresponds to linguistic concatenation. It tests whether composed operators support novel predictions and actions.

### Equivalence

Two signals are semantically equivalent within a scope if their predictive/interventional operators are indistinguishable over the preregistered held-out state distribution.

They are partially equivalent when their effects coincide only over a subset of relevant tests or contexts.

### Intervention support

Intervention is native rather than added later. The substrate is judged by whether signal-conditioned predictions respond correctly when the evaluator manipulates world variables, actions, or communication channels.

### Provenance

PIS keeps an append-only evidence log linking each predictive update to:

- observations;
- received signals;
- actions;
- intervention identities visible to the learner;
- model/version identity;
- uncertainty/calibration state.

It does not expose evaluator truth.

### Strengths

- minimal ontological commitment;
- strongly grounded in observable consequences;
- natural fit for active experiments and causal listening tests;
- potentially robust under radically different perceptual categories;
- provides a serious non-symbolic rival to graph-first semantics.

### Risks

- may learn task-specific predictive shortcuts rather than portable meaning;
- can be difficult to render into human language;
- long-horizon predictive tests may be expensive;
- an opaque vector can conceal private-code coordination;
- abstract, counterfactual, social, or absent-referent meaning may require large test sets;
- operational equivalence remains scoped to tested interventions.

### Minimality burden

PIS must demonstrate that its low ontology burden does not destroy compositional transfer, non-equivalence detection, or conservation accounting. If it cannot bridge to new partners/tasks, its predictive success is insufficient.

## Why these are genuinely competing

| Question | TPH | DCA | PIS |
|---|---|---|---|
| What is meaning fundamentally? | structured relational hypothesis | constraint/operator over compatible situations | change in action-conditioned predictions |
| Explicit entities required? | candidate entities supported | optional bindings only | no |
| Explicit relations required? | yes, opaque typed relations | relational operators | no explicit semantic relation |
| Composition mechanism | graph unification/binding | operator algebra | operator composition on predictive state |
| Grounding anchor | evidence-linked graph claims | denotation over observations/trajectories | future observable consequences |
| Human auditability | high | medium-high | low-medium |
| Ontology prior | highest | medium | lowest |
| Natural uncertainty | factor probabilities | weighted denotations | predictive probabilities |
| Natural causal testing | possible | explicit intervention operator | native |
| Risk of task-private code | medium | medium | high unless evaluator is strong |

## Fair competition protocol

### Frozen common inputs

Each substrate receives exactly the same:

- world episodes;
- sensor streams per role;
- communication opportunity structure;
- action affordances;
- interaction budget;
- learner-visible feedback;
- training/validation split;
- held-out evaluator suite.

### Prohibited advantages

No candidate may receive:

- evaluator variable names;
- human semantic labels;
- shared hidden object IDs between agents unless the challenge explicitly allows them;
- shared latent vectors;
- synchronized random seeds that identify episodes;
- direct access to another agent's internal state;
- evaluator truth through file names, metadata, reward channels, timing, or ordering artifacts.

### Complexity accounting

For each substrate record:

- serialized representation bytes;
- number of fixed primitive operators/types;
- number of learned primitive operators/types;
- trainable parameter count outside the common perceptual front end;
- peak memory;
- compute per interaction;
- interactions to qualification;
- adapter complexity;
- human-authored ontology bytes.

### Representation neutrality

Where possible, perceptual encoders are held constant across substrate runs. When a substrate requires a materially different encoder, that difference is declared and counted as part of the candidate system.

### Repeated runs

Use multiple seeds and independently generated worlds. A substrate cannot qualify from one favorable run.

## Decision rule

R1 does not require a single winner.

A substrate is **dominated** if another substrate:

1. passes every critical R2 semantic-grounding test it passes;
2. is non-inferior on preregistered semantic metrics; and
3. is strictly simpler on at least one material complexity dimension without being materially worse on another.

A richer substrate is promoted only when its extra representational commitments buy a preregistered benefit.

If two or three candidates remain Pareto-nondominated, preserve them into later controls rather than manufacturing a winner.

## R1 falsifiers

The R1 premise is weakened if:

- all three substrates collapse to the same effective internal representation after training;
- success depends primarily on a common model component outside the substrates;
- evaluator results are insensitive to substrate ablation;
- no substrate can outperform intentionally broken private-code controls;
- substrate choice matters less than seed or world-generator artifacts;
- the common interface forces every candidate into TPH-like semantics.

## R1 gate

`R1_COMPETITION_SPECIFIED` requires:

- all three candidate specifications frozen;
- common interface frozen;
- complexity accounting frozen;
- R2 evaluator and negative-control suite frozen;
- no candidate implementation trained against hidden R2 holdouts.

`R1_SUBSTRATE_SELECTED` is a later empirical status and is **not** granted by this document.
