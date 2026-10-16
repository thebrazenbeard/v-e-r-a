# Design Principles

These principles are intended to constrain architecture and experiments before implementation choices become accidental doctrine.

## 1. Ground before translating

A mapping between two symbol systems is not enough. Candidate meanings must connect to observations, actions, consequences, or stable shared conventions in a world.

Formal representations are bookkeeping for grounded hypotheses; they are not a substitute for grounding.

## 2. Do not assume that communication is linguistic

The system must admit channels based on:

- discrete tokens;
- continuous values;
- timing and rhythm;
- orientation and motion;
- spatial arrangement;
- color or light;
- touch or force;
- environmental modification;
- multimodal combinations;
- silence or withholding;
- audience-dependent behavior.

An architecture that requires tokenized sentences at ingress has already lost the universal claim.

## 3. Signalhood is inferred, not granted

The system should maintain hypotheses such as:

- behavior is noncommunicative;
- behavior is communicative but not directed at this receiver;
- behavior is an attention signal;
- behavior carries referential information;
- behavior regulates interaction rather than describing the world;
- behavior is deceptive, ritualized, or affective;
- behavior is environmental action with no signaling intent.

Evidence for communicative status may include repetition, contingency on audience state, response dependence, turn-like structure, correction, increased coordination, compression, and mutual adaptation.

## 4. Preserve the distinction between observation and interpretation

At every layer, keep separate:

- raw observation;
- parsed event;
- inferred signal unit;
- candidate referent;
- candidate semantic structure;
- external supplied claim;
- evaluator truth;
- translated rendering.

This prevents the translator from laundering its own inferences into facts.

## 5. Uncertainty is semantic content

Ambiguity must survive the pipeline.

If two interpretations remain plausible, the semantic state should contain both with calibrated support rather than selecting one merely because a renderer demands a single sentence.

## 6. Provenance is semantic content

The system must distinguish at least:

- directly observed;
- repeated observation;
- communicated by counterpart;
- supplied by operator;
- inferred statistically;
- inferred causally;
- predicted;
- remembered from prior interaction;
- evaluator-only ground truth.

Two claims with identical surface text but different provenance are not semantically identical.

## 7. Do not hard-code a universal ontology

The common substrate should provide structural primitives, typing, uncertainty, evidence, and compositional operators.

Domain concepts should be learned, negotiated, or imported with explicit provenance.

A concept such as `BEARING_FAILURE` may be useful in industrial telemetry; `KINSHIP_ROLE` may matter in human social communication. Neither belongs in the universal kernel by default.

## 8. Do not assume shared object segmentation

One agent may perceive bounded objects while another perceives surfaces, flows, fields, trajectories, or relations.

Experiments must therefore distinguish:

- shared world;
- shared observation;
- shared representation.

Only the first is required by the strongest form of the thesis.

## 9. Meaning is allowed to be relational and contextual

Avoid reducing all semantics to `signal -> label`.

A better model is:

`P(semantic_state | signal, context, interaction_history, sender_state, receiver_state, world_state)`.

Vervet alarm-call research is a useful warning: superficially word-like animal signals can have context-sensitive interpretation.

## 10. Test semantics through interventions

When competing hypotheses make different predictions, choose actions or queries that maximize discrimination.

Meaning acquisition should therefore include an experimental-policy component, not merely a classifier.

## 11. Reward correct non-translation

The system should receive positive credit for identifying:

- insufficient evidence;
- ambiguous mapping;
- partial overlap;
- context dependence;
- no faithful equivalent.

Otherwise evaluation pressure will force hallucinated equivalences.

## 12. Translation is target rendering, not semantic identity

English, Spanish, Mandarin, ASL-like signing, diagrams, equations, motion, or machine-readable control structures should all be renderers over an intermediate semantic state.

The renderer must not silently add facts required only for fluency.

## 13. Preserve semantic conservation accounting

Every transformation should be able to produce a ledger containing:

- preserved;
- transformed;
- inferred;
- omitted;
- added;
- ambiguity collapsed;
- unresolved;
- untranslatable.

This creates an auditable definition of translation fidelity.

## 14. Communication success is necessary but insufficient

Agents can succeed in a coordination game while learning representations that do not correspond to evaluator concepts. Therefore success must be supplemented with novel-context tests, intervention tests, role reversal, recombination, and withheld-truth evaluation.

## 15. Prefer weak assumptions and adversarial controls

Every claim of universality should survive removal of conveniences such as:

- identical visual encoders;
- shared latent vectors;
- shared tokenization;
- synchronized clocks;
- known turn boundaries;
- evaluator-selected relevant signals;
- shared concept inventories;
- shared reward decompositions.

## 16. Separate channel discovery, semantics, and rendering

A robust architecture should not entangle:

1. physical-channel detection;
2. signal segmentation;
3. communicative-function inference;
4. semantic grounding;
5. convention negotiation;
6. target rendering.

Each layer may fail independently and should expose evidence for its own result.

## 17. Separate correlation from causation

A signal occurring before an event does not establish that the signal means the event, caused the event, predicted the event, requested the event, or warned about the event.

The substrate should represent these as distinct hypotheses.

## 18. Role symmetry is evidence

Once a semantic convention appears established, sender and receiver roles should be reversed where possible.

A receiver that cannot use the supposed concept productively may have learned a task-specific response policy rather than a shared meaning.

## 19. Generalization should be semantic, not merely statistical

Held-out examples should vary along the dimensions needed to distinguish memorization from structure:

- new instances;
- new combinations;
- new contexts;
- changed viewpoint;
- changed modality;
- changed sender;
- changed receiver;
- changed environment while preserving the relevant invariant.

## 20. The translator should behave like a scientist

Its central loop should be:

`observe -> hypothesize -> predict -> choose discriminating interaction -> observe consequence -> update -> conserve uncertainty -> negotiate -> test again`.

Passive corpus translation is a special case, not the defining architecture.

## 21. The bootstrap protocol is itself a communication object

For interstellar use, the system must eventually explain or demonstrate its own communication procedures without assuming the receiver already understands them.

This recursion is a first-class research problem, not a deployment detail.

## 22. Physical-layer universality and semantic universality are different problems

Interstellar communication engineering must separately solve detectability, synchronization, framing, error correction, and channel impairments before semantic bootstrapping begins.

No semantic architecture should assume a clean terrestrial network transport.

## 23. Safety and authority are separate from understanding

Understanding a request does not imply authorization to act on it.

An embodied translator probe or future machine-control renderer must keep:

`semantic interpretation != permission != execution`.

## 24. Falsifiability outranks elegance

A beautiful representation that cannot lose against a simpler rival is not yet a scientific result.

Every major component should have:

- a simpler baseline;
- a failure condition;
- an ablation;
- an evaluator that does not share its private representation;
- evidence that would make the project remove or weaken the component.
