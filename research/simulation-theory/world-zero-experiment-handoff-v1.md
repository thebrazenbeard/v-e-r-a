# World Zero Experiment Handoff — Simulation Theory V1

Status: `RESEARCH-TO-EXPERIMENT HANDOFF / NO EXECUTION AUTHORITY`

Owning research repo: `thebrazenbeard/on-theo`

Execution target if separately authorized: `thebrazenbeard/world-zero`

## Boundary

On-Theo supplies hypotheses, variables, epistemic questions, and falsification criteria.

World Zero may implement toy/controlled universes that test what agents inside constructed systems can infer about their substrate.

No World Zero result, however successful, counts as evidence that our own universe is simulated merely because it reproduces an analogous inference problem.

This handoff authorizes no merge, deployment, paid compute, provider mutation, or World Zero write by itself.

## Experiment family 1: lattice inference by embedded observers

### Question

Can embedded agents distinguish a discrete implementation lattice from apparently continuous effective laws using only in-world observations?

### World models

A. cubic lattice with local update rules;
B. non-cubic discrete graph;
C. continuous numerical model sampled at finite precision;
D. base comparison world where observational data are generated directly from the effective law without accessible lattice artifacts.

### Agent evidence

Provide agents only in-world measurements:

- propagation speeds;
- high-energy event distributions;
- angular anisotropy;
- dispersion relations;
- noise/systematics.

### Success measure

Agents infer the correct model family at a rate significantly above chance/model-prior expectation under preregistered inference rules.

### Key failure mode

Agents detect discreteness but incorrectly infer **external simulation** rather than merely discrete ontology.

### On-Theo lesson

This quantifies the gap:

`implementation structure detected` -> `external provenance inferred`.

## Experiment family 2: implementation artifact versus endogenous law

### Question

When an implementation artifact is stable and universal, can embedded agents distinguish it from a fundamental physical law?

### Design

Construct two worlds with observationally identical low-energy behavior:

- World A: effect is caused by implementation constraint.
- World B: effect is directly specified as fundamental in-world law.

Allow agents increasing ranges of experimental access.

### Outcome

Measure whether any finite in-world evidence distinguishes causal provenance when observable histories are isomorphic.

### Expected conceptual result

If worlds are observationally equivalent, provenance may be underdetermined even when implementation differs.

This would illustrate an epistemological point, not prove that real physics is underdetermined in exactly the same way.

## Experiment family 3: adaptive / demand-driven rendering

### Question

Can resource-saving, observer-targeted simulation remain observationally consistent under multiple interacting observers?

### Models

- full-state computation;
- local lazy evaluation;
- adaptive resolution;
- event-driven remote-state generation;
- adversarial observer coordination designed to force simultaneous high-detail measurements.

### Measurements

- computational savings;
- cross-observer consistency;
- latency artifacts;
- conservation-law violations;
- statistical discontinuities at resolution transitions.

### Relevance

Tests whether common `only render what is observed` replies to resource objections are technically coherent in controlled toy worlds.

## Experiment family 4: nested-simulation anthropic counting

### Question

How do observer-counting conclusions change when simulated agents create nested simulations under finite resource budgets?

### Variables

- branching factor;
- simulation depth;
- computational cost per observer;
- observer lifetime;
- fidelity;
- conscious-observer proxy definition;
- resource-sharing overhead;
- termination rules.

### Outputs

Compare:

- raw observer-instance counts;
- observer-moment counts;
- resource-weighted counts;
- depth-weighted counts;
- reference-class-sensitive probabilities.

### Guard

World Zero cannot establish which counting measure is philosophically correct. It can expose how strongly conclusions depend on the chosen measure.

## Experiment family 5: simulator intervention authentication

### Question

What evidence would embedded agents need to distinguish an external intervention from an unknown endogenous agent/law?

### Conditions

Inject events with increasing information content:

1. rare anomaly;
2. repeated law deviation;
3. encoded mathematical message;
4. response to agent challenge;
5. response containing information unavailable anywhere in current in-world causal history;
6. reproducible state manipulation across controlled trials.

### Competing explanations

- fraud by in-world agent;
- unknown physical process;
- hidden subsystem;
- data corruption;
- external simulator.

### Goal

Estimate how much evidence is required before external provenance becomes the best model *within the toy setup*.

## Experiment family 6: false-positive simulation detectors

### Question

How often do embedded agents infer simulation from ordinary but unfamiliar physical structure?

### Design

Give agents worlds containing:

- discrete physics but no external simulation layer;
- random cosmic anisotropy;
- finite precision measurement;
- information bounds;
- holographic-like dual representation;
- rare coincidence clusters.

Track rates of false inference to an external simulator.

### Relevance

Directly tests the inferential weakness behind popular arguments such as:

- `pixelated Planck scale`;
- `quantum rendering`;
- `hologram means simulation`;
- `coincidence means scripting`.

## Experiment family 7: model-selection with unconstrained simulator

### Question

What happens in Bayesian model comparison when `simulation` is allowed arbitrary simulator motives and interventions?

### Models

- constrained simulator with fixed likelihood;
- flexible simulator with a prior over interventions;
- unconstrained simulator capable of producing any data;
- non-simulation physical models of varying complexity.

### Goal

Show quantitatively how an unrestricted simulator model can fit observations while suffering undefined/penalized predictive power depending on prior/model specification.

### Relevance

Formalizes the On-Theo hostile claim that explanatory flexibility is not equivalent to evidential support.

## Experiment family 8: consciousness proxy caution

World Zero should not label internal agents `conscious` as an experimental fact unless an independently justified consciousness criterion exists.

Allowed labels:

- `agent`;
- `observer-model`;
- `information-processing process`;
- `self-modeling agent`;
- `behavioral observer proxy`.

Disallowed inference:

`agent behaves like observer` -> `phenomenal consciousness established`.

## Suggested output contract back to On-Theo

For every World Zero simulation-theory experiment, return:

- experiment ID;
- exact code/model commit;
- model assumptions;
- simulated law set;
- observer information boundary;
- intervention privileges;
- inference algorithm;
- results;
- falsified toy hypotheses;
- unresolved alternative models;
- whether result bears on `epistemology of embedded agents`, `computational feasibility`, or another category;
- explicit statement: `NO DIRECT CLAIM ABOUT WHETHER THE REAL UNIVERSE IS SIMULATED`.

## Highest-value first experiment

Recommended first target:

`WZ-SIM-01 IMPLEMENTATION_ARTIFACT_VS_FUNDAMENTAL_LAW`

Reason:

It attacks the central inference error directly. If two toy worlds can be observationally equivalent while one feature is implemented externally and the other is fundamental internally, the experiment gives us a concrete framework for discussing why implementation-like physics need not reveal provenance.

This is useful regardless of whether simulation theory is true.
