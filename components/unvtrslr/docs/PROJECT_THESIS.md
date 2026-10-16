# Project Thesis

## Founding motivation

UNVTRSLR is motivated by a problem that ordinary translation systems avoid: communication where there may be **no shared language, no shared symbolic convention, and no guarantee that the other intelligence communicates linguistically at all**.

The extraterrestrial case makes the assumptions visible. A static interstellar message has to anticipate, before contact, enough of the receiver's cognition, perception, notation, and interpretive frame to be decoded. That is a brittle burden. A more powerful artifact would carry procedures for discovering common ground after contact.

The project therefore shifts the objective from:

> design one universally intelligible message

into:

> design a system that can establish a semantic bridge with an initially unknown communicator.

## Refined thesis

The working thesis is:

> A sufficiently capable pair of agents can, under some conditions, bootstrap shared semantics from interaction with a common world even when they begin with no shared symbolic language, provided they can observe regularities, act or query, detect contingency, test hypotheses, retain uncertainty, and negotiate conventions.

The universal element is not assumed to be English, human grammar, a fixed set of concepts, or a single ontology. It is the **method for constructing and testing mappings between representations**.

## Why “math” remains important but changes role

The initial idea described a pipeline like:

`source -> mathematics -> English`

That is useful intuition but too strong if interpreted literally. Mathematics is itself represented through conventions, notation, and interpretive assumptions. Formal structure alone does not solve the symbol-grounding problem.

UNVTRSLR therefore treats mathematics as a **formal carrier** for semantic hypotheses that have independent grounding and evidence.

A formal substrate is valuable because it can explicitly represent:

- entities and candidate entities;
- events and states;
- quantities and ratios;
- spatial and temporal relationships;
- causal hypotheses;
- actions and goals;
- beliefs and uncertainty;
- provenance;
- alternative interpretations;
- evidence for and against a mapping;
- semantic invariants that should survive translation.

The substrate is not meaningful merely because it is mathematical. It becomes useful because its terms are connected to observations, interventions, shared conventions, and predictive tests.

## The stronger product concept

UNVTRSLR is best understood as a **universal semantic mediation system**, with five responsibilities:

1. **Observe** a potentially communicative system without assuming its channel or grammar.
2. **Infer** candidate signal units, contexts, referents, relations, and communicative functions.
3. **Experiment** to distinguish competing semantic hypotheses.
4. **Stabilize** shared conventions and a translation bridge.
5. **Render** the resulting semantic structure into a requested target representation while preserving uncertainty and provenance.

That means the architecture is closer to a scientist, protocol negotiator, and translator combined than to a dictionary.

## Central research hypotheses

### H1 — Shared-world grounding can establish reference

If two agents can jointly observe or affect the same environment, repeated interactions can establish stable mappings between otherwise arbitrary signals and aspects of that environment.

This is supported in limited form by grounded language-game and emergent-communication research, but the project must demonstrate it under much stronger constraints.

### H2 — Signalhood itself can be learned

The system need not be handed a clean message channel. It may be possible to infer that some behavior is communicative by detecting contingency, audience effects, response dependence, information gain, repetition, correction, and coordination benefit.

### H3 — Shared semantics need not require shared perceptual encoding

Agents with different sensors may still construct overlapping semantic structures if they can discover invariant relationships in a common world.

This must be tested explicitly. Shared RGB pixels or identical object vectors are hidden common language and are therefore insufficient evidence.

### H4 — Active experimentation is necessary for deep grounding

Passive correlation may support provisional mappings, but ambiguous meanings often require interventions or discriminating queries.

If a signal may mean RED or SPHERE, changing color while preserving shape and changing shape while preserving color are stronger semantic tests than collecting more passive co-occurrences.

### H5 — Communication success is weaker than semantic understanding

Two agents can coordinate using an arbitrary code that exploits task artifacts without representing the concepts an evaluator attributes to that code.

Therefore task reward alone cannot establish semantic grounding.

### H6 — Compositional transfer is a stronger test than memorized mapping

A useful semantic system should support novel combinations and relationships, not merely repeated labels. New object combinations, new spatial arrangements, new temporal structures, and role reversal provide evidence that reusable semantic structure exists.

### H7 — Non-equivalence is discoverable and should be preserved

Two systems may carve reality differently. A faithful translator should be able to report:

- exact equivalence;
- approximate equivalence;
- context-dependent equivalence;
- one-to-many mapping;
- many-to-one mapping;
- partial overlap;
- unknown mapping;
- no faithful equivalent.

Forcing every source concept into a target category is semantic hallucination.

### H8 — A small set of cross-domain representational primitives may be enough

UNVTRSLR does not assume a fixed universal vocabulary, but it hypothesizes that a reusable **representation grammar**—for things such as relation, event, sequence, quantity, uncertainty, provenance, agent, action, and constraint—may cover a broad range of communicative systems.

This is deliberately weaker than claiming that a human-derived list of concepts is universal across all intelligence.

### H9 — Earth communication can provide graded controls

Known human languages, signed languages, animal communication systems, synthetic languages, continuous channels, and deliberately alien artificial ontologies can provide increasingly difficult controls while retaining evaluator ground truth.

### H10 — An interstellar translator is more plausible as a bootstrap system than as a prewritten phrasebook

An embodied probe with sensors and interaction may be able to create common ground locally. A broadcast version would require a more difficult self-describing curriculum because it lacks immediate shared embodiment and may face enormous round-trip delays.

## What would falsify the thesis

The project should be considered materially falsified or narrowed if, after controlling for hidden common priors and leakage:

- agents cannot establish stable grounded mappings without a predeclared symbolic channel;
- successful mappings collapse when perceptual representations differ;
- apparent semantics fail novel-context, role-reversal, or intervention tests;
- all successful systems require a large human-authored ontology;
- the protocol cannot distinguish genuine non-equivalence from translation failure;
- signalhood cannot be learned without essentially being labeled by the evaluator;
- communication success remains explainable by task-specific private codes;
- semantic conservation cannot be operationalized independently of target-language similarity.

A negative result would still be scientifically valuable because it would tell us which assumptions really are necessary.

## Non-goals

UNVTRSLR does **not** currently claim:

- that extraterrestrial intelligence exists;
- that extraterrestrial cognition resembles human cognition;
- that mathematics is automatically understandable to aliens;
- that the 65 Natural Semantic Metalanguage primes are universal beyond humans;
- that any existing animal communication system is language in the human sense;
- that large language models already solve grounding;
- that successful referential games prove semantic understanding;
- that one representation can capture all meaning without loss;
- that a safe policy for transmitting information into space has been settled.

## Working definition of success

A mature UNVTRSLR system would receive an unfamiliar stream of behavior or signals and, through observation and interaction, construct a calibrated translation bridge that can say not merely:

> “signal X means Y”

but:

> “Under contexts C1 and C2, signal pattern X is best explained by semantic hypothesis Y with confidence p; competing hypothesis Z remains plausible. This mapping predicts responses R and R2, has survived interventions I1-I4, and has no exact target-language equivalent. The closest rendering is ..., with the following information loss.”

That is the standard this repository is designed to approach.
