# Failure Modes and Threat Model

UNVTRSLR is especially vulnerable to producing convincing false positives. This document treats ways the project can fool itself as first-class design requirements.

## 1. Symbol grounding failure

**Failure:** the system learns relationships among symbols without connecting them to observations, actions, or tested world structure.

**False appearance:** fluent translation or consistent internal graphs.

**Required defense:** grounded tasks, interventions, and explicit provenance linking semantic claims to evidence.

## 2. Private-code success

**Failure:** two agents invent an arbitrary coordination code that solves the game but has no reusable evaluator-recognizable semantics.

**False appearance:** near-perfect communication reward.

**Required defense:** transfer tasks, novel contexts, role reversal, independent semantic probes, and negative controls modeled after known emergent-communication shortcut failures.

## 3. Hidden shared representation

**Failure:** agents appear to negotiate meaning but actually share object IDs, embeddings, synchronized indices, feature extractors, or latent labels.

**Required defense:** aggressively asymmetric encoders, independent implementations, inspectable learner inputs, and explicit no-shared-latent tests.

## 4. Human ontology injection

**Failure:** evaluator-created object categories, labels, or semantic templates silently perform the hard part.

**Required defense:** distinguish evaluator truth from learner-visible structure; include ontology-mismatch experiments and unsupervised candidate segmentation.

## 5. Token-language assumption

**Failure:** the architecture requires discrete tokens or message boundaries.

**Consequence:** nonlinguistic channels are excluded by construction.

**Required defense:** continuous, timing, movement, and environmental-modification controls.

## 6. Signalhood oracle

**Failure:** the experiment tells the learner exactly which events are communicative.

**Consequence:** the system is a decoder, not a universal bootstrapper.

**Required defense:** unknown-channel experiments with noncommunicative distractor behavior and no-message controls.

## 7. Context collapse

**Failure:** one signal is assigned one global meaning even when interpretation depends on environment, participant, history, or social context.

**Required defense:** context-dependent controls and conditional semantic models.

## 8. Forced equivalence

**Failure:** every source concept must map to some target concept.

**Consequence:** semantic hallucination and destruction of genuine ontology differences.

**Required defense:** explicit `UNKNOWN`, `PARTIAL_OVERLAP`, and `NO_FAITHFUL_EQUIVALENT` outcomes rewarded by evaluation.

## 9. Overconfident ambiguity collapse

**Failure:** the renderer chooses one interpretation from several viable hypotheses and outputs it as fact.

**Required defense:** uncertainty conservation and an `AMBIGUITY_COLLAPSED` ledger entry whenever a target surface forces selection.

## 10. Provenance laundering

**Failure:** counterpart claims, model inferences, operator annotations, and direct observations become indistinguishable.

**Required defense:** typed provenance on every semantic claim and renderer rules that preserve source class.

## 11. Causal hallucination

**Failure:** temporal correlation or communicated association is rendered as causality.

**Required defense:** causal relations require explicit evidence class; intervention-supported causality must be distinguished from predictive association and supplied claims.

## 12. Reward leakage

**Failure:** the reward function tells the agents which semantic dimensions matter.

**Example:** separate reward components for “correct color” and “correct shape” effectively supply the ontology.

**Required defense:** use task rewards that do not expose the intended decomposition; compare against alternative concept structures.

## 13. Dataset artifact exploitation

**Failure:** agents use ordering, filenames, timing quirks, background pixels, or simulator artifacts instead of target semantics.

**Required defense:** randomized nuisance variables, new generators, adversarial datasets, and cross-generator transfer.

## 14. Memorization mistaken for composition

**Failure:** the system remembers complete message configurations rather than building reusable semantic units.

**Required defense:** held-out combinations, systematic recombination tests, and transfer to structurally new tasks.

## 15. Metric Goodharting

**Failure:** a compositionality, mutual-information, embedding-similarity, or task-success metric becomes the target and ceases to track semantic quality.

**Required defense:** multiple orthogonal metrics, behavioral tests, and adversarial examples where the metric and desired capability diverge.

## 16. Shared-environment overclaim

**Failure:** agents are said to share only a world, but in practice they receive identical preprocessed observations.

**Required defense:** report world state separately from each agent's sensory projection and include asymmetric embodiment stages.

## 17. Objecthood assumption

**Failure:** all semantics are built around stable objects.

**Consequence:** field-like, process-based, distributed, or relation-centered cognition is excluded.

**Required defense:** simulations where one agent lacks object identity or segments the world differently.

## 18. Anthropocentric semantic curriculum

**Failure:** “first 100 concepts” are treated as universal because humans find them basic.

**Required defense:** use semantic challenges rather than mandatory word targets; allow alternate internal decompositions and non-equivalence.

## 19. NSM overextension

**Failure:** human cross-linguistic semantic primes are assumed universal across all intelligent systems.

**Required defense:** treat NSM as a human-language control/hypothesis, not alien ontology.

## 20. UMR/AMR overextension

**Failure:** a linguistic meaning representation becomes the universal semantic kernel merely because it is cross-lingual.

**Required defense:** use UMR/AMR as evidence about useful representational responsibilities while testing nonlinguistic and asymmetric controls.

## 21. Acoustic modeling mistaken for translation

**Failure:** a model that predicts or synthesizes animal-like vocalizations is described as understanding their meanings.

**Required defense:** require behavioral/contextual semantic evidence separate from acoustic fidelity.

## 22. Self-confirming active experiments

**Failure:** the learner chooses tests that reinforce its favored hypothesis and never samples plausible alternatives.

**Required defense:** explicit hypothesis coverage, exploration baselines, evaluator-visible experiment-selection logs, and counter-hypothesis tests.

## 23. Unsafe intervention

**Failure:** semantic learning chooses actions that are harmful, irreversible, or interpreted as hostile.

**Required defense:** separate experimental policy from action authorization; define conservative, reversible, bounded interaction sets.

## 24. Deception vulnerability

**Failure:** the counterpart intentionally teaches false mappings.

**Required defense:** counterpart signals remain claims, not truth; reliability is modeled; world evidence and cross-context prediction can contradict supplied semantics.

## 25. Nonstationary convention failure

**Failure:** once learned, a mapping is assumed permanent.

**Required defense:** convention versioning, drift detection, confidence decay, and repair negotiation.

## 26. Receiver-specific overfitting

**Failure:** a bridge works only with one counterpart implementation.

**Required defense:** multiple independently implemented senders/receivers and cross-partner transfer.

## 27. Renderer hallucination

**Failure:** fluent target-language generation adds unstated causal, social, temporal, or certainty information.

**Required defense:** semantic ancestry for target claims and conservation ledger with `ADDED` flags.

## 28. Translation-by-English bottleneck

**Failure:** all semantics are converted to English internally, making English categories the hidden ontology.

**Required defense:** semantic state must be inspectable without English; cross-renderer tests should go directly between non-English/nonlinguistic systems.

## 29. One-way comprehension overclaim

**Failure:** receiver responds correctly but cannot productively use the mapping.

**Required defense:** role reversal and generative communication tests.

## 30. False universal representation

**Failure:** a rich formal substrate can encode everything tested only because all tests were designed around it.

**Required defense:** simpler rival representations, ablations, new domains, and tasks not anticipated by the schema authors.

## 31. Physical-layer semantic confusion

**Failure:** framing, synchronization, or error-correction artifacts are interpreted as semantic structure.

**Required defense:** separate physical/channel inference from semantic inference and test under controlled corruption.

## 32. Interstellar human-likeness assumption

**Failure:** aliens are implicitly assumed to share human notions of objects, agents, goals, arithmetic pedagogy, or conversation.

**Required defense:** document every assumption and attack it with synthetic agents missing that assumption.

## 33. Universal-physics notation assumption

**Failure:** because physical laws are shared, our formulas or numeral encodings are assumed obvious.

**Required defense:** bootstrap mappings through demonstrated relationships rather than raw notation.

## 34. Self-description circularity

**Failure:** the bootloader requires the receiver to understand the very semantics it is supposed to teach.

**Required defense:** progressively demonstrated operations, redundancy, contrastive examples, and tests using receivers never trained on the protocol.

## 35. Evaluator contamination

**Failure:** evaluator truth leaks into learner prompts, metadata, model weights, or pretraining.

**Required defense:** frozen synthetic worlds, held-out semantics, independent receiver architectures, and contamination declarations for any pretrained component.

## 36. Pretraining semantic prior leakage

**Failure:** a large pretrained model succeeds because it has already seen the target language/system.

**Required defense:** synthetic languages generated after model training, novel symbol systems, and from-scratch baselines.

## 37. Unmeasured information loss

**Failure:** target output appears sensible but silently drops source distinctions.

**Required defense:** semantic conservation ledger and minimal-pair tests.

## 38. Unfalsifiable universality claim

**Failure:** every failure is explained away as the other agent being insufficiently intelligent or cooperative.

**Required defense:** preregistered scope, defined necessary conditions, and explicit outcomes that narrow or falsify the thesis.

## 39. Probe autonomy creep

**Failure:** a translator probe gains escalating physical authority because interaction improves learning.

**Required defense:** hard separation between interpretation, experiment proposal, authorization, and execution.

## 40. METI policy conflation

**Failure:** successful message design is treated as permission to transmit it.

**Required defense:** transmission governance is explicitly outside the semantic research authorization boundary.

## Qualification rule

For every major claimed capability, the research record should include:

- strongest alternative explanation;
- negative control;
- ablation;
- evidence that would falsify the claim;
- remaining assumptions;
- known evaluator subsidies;
- whether success transfers to a new partner, world, task, or channel.

The project should prefer a narrower truthful result over a dramatic universal claim supported by a permissive experiment.
