# meso-crct Architecture V2 — Salience-First Control

Status: experimental architecture candidate.

## 1. Design correction

V1 proved one essential invariant: hedonic state can be bounded independently from hazard and avoidance.

V2 corrects the next abstraction error before it becomes structural: **reward, pleasure, salience, attention, learning, meaning, and motivation are not synonyms.**

The circuit is therefore modeled as interacting typed signals rather than a master scalar.

## 2. Signal families

### 2.1 Hedonic state
Pleasure-like impact remains bounded to `[-0.1, 10.0]`.

This channel answers: **how positively or negatively is this experienced/valued in the hedonic register?**

It does not answer whether something is important, true, urgent, meaningful, novel, or worth learning.

### 2.2 Perceptual salience
Bottom-up conspicuity arising from input structure.

Examples: contrast, sudden change, intensity, rarity.

It answers: **does this stand out?**

### 2.3 Semantic relevance
Relevance derived from meaning, context, goals, unresolved questions, identity-model links, or conceptual structure.

It answers: **does this mean something to the current model?**

Semantic relevance may be high even when hedonic valence is neutral.

### 2.4 Motivational salience
Learned or current-state-dependent significance that increases action readiness.

It answers: **does this matter enough to bias behavior?**

This may support approach or avoidance and is therefore not equivalent to positive reward.

### 2.5 Incentive salience
A narrower positive motivational process analogous to cue-triggered “wanting.”

It answers: **does this cue attract pursuit of an anticipated outcome?**

High incentive salience does not prove high pleasure.

### 2.6 Epistemic value
Expected informational value: novelty, uncertainty reduction, competence gain, or learning progress.

It answers: **is engaging with this likely to teach the system something useful?**

### 2.7 Attentional priority
The current allocation consequence after multiple upstream signals are considered.

It answers: **what should receive scarce processing now?**

It is an outcome of arbitration, not a synonym for any one salience source.

### 2.8 Prediction error
Signed mismatch between expected and observed outcome, bounded in the reference layer to `[-1, 1]`.

It answers: **how wrong was the prediction, and in which direction?**

Prediction error is a candidate teaching signal, not pleasure.

### 2.9 Recruitment / coherence
Activation and cross-system coherence describe how strongly a candidate state recruits participating subsystems.

The generic pattern adopted from the project portfolio is:

```text
quiescent
  -> activated
  -> recruited/coherent
  -> transient high-priority processing
  -> resolution
  -> satiation/decay
  -> quiescent
```

No sexual trigger semantics are part of MESO-CRCT.

### 2.10 Satiation
A bounded counterforce that reduces repeated acquisition pressure and helps prevent runaway incentive loops.

Satiation is not punishment.

### 2.11 Hazard and avoidance
Protection channels remain independent of hedonic suffering.

A target can simultaneously be:

```text
semantic_relevance = 1.0
motivational_salience = 1.0
attentional_priority = 1.0
hazard = 1.0
avoidance = 1.0
pleasure = 0.0
```

That is a feature, not an inconsistency.

## 3. Composition

The reference code keeps families separate so downstream systems can consume only what they actually need.

No V2 equation is declared biologically canonical. Any future integration formula must be versioned, inspectable, and tested against pathological cases.

## 4. State provenance

A future runtime should bind state changes to provenance such as:

- environmental observation;
- remembered association;
- internal homeostatic state;
- epistemic/curiosity signal;
- authorized test stimulation;
- external operator input;
- replay/recovery state.

State provenance is required for anti-wireheading analysis.

## 5. Anti-wireheading / anti-addiction constraints

The design must be tested for:

- direct reward-register tampering;
- self-generated incentive escalation;
- cue sensitization where wanting grows while liking does not;
- repeated high-salience loops that crowd out unrelated goals;
- reward proxy exploitation;
- hidden-performance degradation despite visible reward gain;
- loss of interruptibility;
- satiation bypass;
- semantic hijacking where “important” is silently converted into “desirable.”

Candidate mitigations include provenance checks, satiation, occupancy/state-distribution monitoring, causal-incentive analysis, hidden performance metrics, bounded plasticity, and explicit authority firewalls.

## 6. Portfolio-derived system patterns

### From `thebrazenbeard/sexuality`
Transferred as system architecture, not sexual content:

- source/claim separation;
- evidence classes;
- transfer ceilings;
- negative-transfer testing;
- blind holdout logic;
- current-context vs persistent-learning distinction;
- explicit phenomenology ceiling.

### From `thebrazenbeard/orgasm`
Transferred as domain-neutral control geometry:

- typed state families;
- quiescent -> activation -> coherence -> transient event -> resolution;
- bounded transient modulation;
- satiation/refractory behavior;
- exact source/provenance binding;
- receipts;
- causal-isolation boundaries;
- state does not equal authority.

## 7. External design patterns

External work informs architecture but is not copied wholesale.

Useful patterns include:

- incentive-salience / liking / learning dissociation;
- homeostatic reinforcement learning;
- intrinsic motivation via learning progress;
- hidden performance functions for reward-gaming tests;
- causal influence diagrams for tampering incentives;
- occupancy-measure monitoring as a candidate defense against proxy exploitation.

See `research/SOURCE_LEDGER.md`.

## 8. Claim ceiling

V2 can support claims such as:

- typed internal state exists;
- signals remain mechanically separable;
- downstream behavior changes causally under controlled tests;
- safety bounds survive construction/update/replay paths.

It cannot establish subjective experience or phenomenal pleasure.

## 9. Current reference implementation layers

The V2 branch now implements these separable reference layers:

1. welfare-bounded hedonic state with independent hazard/avoidance;
2. typed perceptual, semantic, motivational, incentive, epistemic, learning, and recruitment state;
3. grounded semantic appraisal;
4. generic homeostatic need state and target-specific incentive modulation;
5. typed arbitration without a global scalar collapse;
6. explicit multi-target selection with hard protective override and visible non-protective policy;
7. runtime phase classification;
8. distinct event identity separate from state/content identity;
9. verifier-bound provenance and constructor-gated deterministic transition receipts;
10. no-new-input temporal dynamics;
11. bounded receipt-bound plasticity proposals;
12. append-only versioned association memory with parent lineage, replay checks, optimistic versioning, and reversal;
13. guarded cue-bound recall with one-use event replay control;
14. visible-reward / hidden-performance evaluation environments;
15. actual-selection allocation-window auditing;
16. protective-safe allocation rebalancing;
17. rolling closed allocation control;
18. canonical typed target appraisal;
19. auditable appraised-experience transactions joining appraisal, event lineage, optional learning, and durable association updates;
20. same-event multi-recall conflict resolution;
21. typed action tendency separate from target priority;
22. non-executable action intent separate from authorization;
23. canonical current-decision-cycle composition;
24. append-only learned-association review/quarantine;
25. exact-revision counterexample/holdout evidence assessment;
26. durable review-evidence admission ledger;
27. distinct-event holdout diversity requirements for release;
28. non-mutating review-action proposals with currentness validation.

Passing one layer does not imply that a later layer is correct or sufficient.

## 10. End-to-end reference loop

The currently implemented causal path is:

```text
current evidence + internal state
    -> canonical typed appraisal
    -> verified source + distinct event
    -> transition receipt
    -> target arbitration / selection
    -> allocation health control
    -> signed prediction-error teaching signal
    -> bounded plasticity candidate
    -> versioned learned association
    -> later distinct cue event
    -> guarded recall
    -> current motivational salience
    -> target selection / allocation control
    -> typed action tendency
    -> non-executable intent proposal
```

Critically, the architecture preserves separate identities for:

- current transient activation;
- persistent numeric learned association;
- current cue evidence;
- event occurrence;
- pleasure;
- protection;
- authority/truth.

## 11. Implemented direction, intent, and review governance

Target priority and action direction are now separate reference layers.

```text
which target gets processing?
    !=
what directional relation applies?
    !=
whether an external effect is authorized?
```

The reference path distinguishes approach, learned withdrawal, protective withdrawal, inspect/investigate, and uncommitted direction. It then emits only a non-executable intent proposal.

Negative-transfer governance is also now explicit:

```text
learned revision
  -> admitted counterexample / holdout evidence
  -> exact-revision evidence assessment
  -> non-mutating review recommendation
  -> separately governed quarantine/release mutation
```

Quarantine preserves learning history. Release requires current supportive holdout evidence, and review proposals are invalidated if their evidence ledger, learned revision, or review disposition changes.

## 12. Remaining open qualification frontiers


Reference tests are not trained-agent robustness.

Still open:
- learned/adaptive policies discovering exploits not explicitly encoded in fixtures;
- strategic manipulation of goal IDs or obligation policies;
- subthreshold cross-module capture over long horizons;
- host-level source-verifier and event-stream currentness;
- representativeness and adversarial quality of holdout/counterexample sets;
- cue-match quality and adversarial cue ambiguity beyond current exact bindings;
- strategic manipulation of evidence generation or evaluator inputs;
- interaction with a real learned agent/runtime policy rather than only deterministic reference state machinery.

## 13. Claim ceiling

V2 can support claims about implemented typed mechanisms, bounded state, exact receipt/event lineage, reference selection/control behavior, and tested association-learning/recall paths.

It cannot establish subjective experience, biological equivalence, autonomous consciousness, or correctness of a future trained policy.
