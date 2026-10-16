# Research Landscape

UNVTRSLR sits at the intersection of several existing research traditions. None is sufficient by itself, but each contributes an important piece.

## 1. Symbol grounding

Stevan Harnad's 1990 “The Symbol Grounding Problem” asks how symbols can acquire meaning that is not merely parasitic on another interpreter's meanings. Harnad argues that symbolic representations ultimately require grounding in nonsymbolic representations, including iconic/perceptual and categorical representations.

**Contribution to UNVTRSLR:** formal semantic structures cannot be treated as meaningful merely because they are internally consistent. Grounding must connect them to perception, action, or other nonsymbolic evidence.

**UNVTRSLR extension:** grounding must be negotiated across agents that may not share perceptual categories.

## 2. Grounded language games and symbol emergence

Luc Steels, Paul Vogt, and related researchers demonstrated that robots or simulated agents can develop shared lexicons and primitive compositional structures through repeated situated language games.

Vogt's work on perceptually grounded language games shows conditions under which semantics and compositional structure can emerge, and Steels' robot experiments emphasize shared environments and social interaction.

**Contribution:** shared context plus feedback can bootstrap conventions without a centrally designed lexicon.

**UNVTRSLR extension:** remove the assumptions that the channel is verbal, that message boundaries are known, and that both parties share similar perceptual organization.

## 3. Emergent communication and referential games

Modern multi-agent emergent-communication research often uses Lewis-style sender/receiver games. Agents develop signaling systems that help solve cooperative tasks.

A major warning comes from Bouchacourt & Baroni (2018): agents can communicate successfully while their aligned visual representations fail to capture the conceptual properties humans assume the symbols denote.

Mu & Goodman (2021) similarly argue that simple single-object referential games encourage uninterpretable task-bound codes; games requiring generalizations improve systematicity and interpretability.

Chaabouni et al. (2020) show that compositionality and generalization are not trivially identical and require careful measurement.

**Contribution:** communication can emerge computationally.

**Warning:** task success is not semantic proof.

**UNVTRSLR requirement:** transfer, role reversal, intervention, semantic minimal pairs, and independent conservation evaluation.

## 4. Coordination and conventions

David Lewis' signaling-game framework treats conventions as solutions to recurring coordination problems. Later human experiments show that people can establish flexible conventions with extremely minimal nonlinguistic signals when they share enough context and jointly infer intent.

**Contribution:** communication conventions can arise without a fixed prior code.

**UNVTRSLR extension:** model joint inference and context, while allowing the possibility that no communication is occurring.

## 5. Natural Semantic Metalanguage (NSM)

NSM research by Anna Wierzbicka, Cliff Goddard, and colleagues proposes a small set of cross-linguistically universal semantic primes. The contemporary program identifies 65 primes and argues that their combinatorial grammar provides a human semantic metalanguage.

**Contribution:** decades of cross-linguistic work provide a serious empirical hypothesis about semantic structures shared across human languages.

**Boundary:** this is evidence about humans, not proof of universal concepts for animals, AI systems, or extraterrestrial intelligence.

**UNVTRSLR use:** positive-control benchmark and source of candidate human semantic challenges, never hard-coded alien ontology.

## 6. Abstract and Uniform Meaning Representation

Abstract Meaning Representation (AMR) and newer Uniform Meaning Representation (UMR) seek language-independent or cross-lingual graph representations of meaning.

The 2024 UMR release explicitly represents sentence-level predicate/argument structure plus document-level coreference, temporal, and modal relationships, and was released across six typologically diverse languages.

**Contribution:** practical evidence that semantic representation benefits from explicit events, roles, modality, time, and document-level relations.

**Boundary:** UMR is still a linguistic formalism whose categories are designed around human-language semantics.

**UNVTRSLR use:** architectural inspiration and human-language control, not universal substrate canon.

## 7. Animal communication

### Honeybee waggle dance

Honeybees communicate resource vectors through dance geometry. Direction is related to waggle-run orientation and distance to waggle duration; research also shows that perceptual mechanisms such as optic flow affect distance estimation and that audience conditions can influence dance precision.

**Contribution:** communication can encode meaningful continuous spatial information through motion rather than word-like symbols.

### Vervet alarm calls

Classic vervet work showed acoustically distinct alarm calls associated with predator categories and corresponding adaptive responses. Later work demonstrates substantial context dependence and overlap with other social situations.

**Contribution:** apparently lexical signals can require context; one-to-one signal dictionaries may be misleading.

### Sperm whale communication / Project CETI

Project CETI combines large-scale acoustic and behavioral data with machine learning to study sperm whale communication. WhAM (NeurIPS 2025) models whale acoustic structure and can synthesize or transform coda-like audio.

**Contribution:** modern multimodal animal-communication research emphasizes rich contextual data and scalable modeling.

**Boundary:** acoustic prediction/synthesis is not automatically semantic translation. UNVTRSLR requires grounded behavioral evidence for semantic claims.

## 8. Interstellar message design

### Pioneer/Voyager

The Pioneer plaques and Voyager Golden Record demonstrate the challenge of creating self-explanatory physical artifacts. Voyager uses symbolic playback instructions, binary arithmetic, astronomical/physical references, images, natural sounds, music, and multilingual greetings.

### Lincos

Hans Freudenthal's 1960 Lincos is a designed language for cosmic communication. It proposes a progressively taught radio language beginning with mathematics and extending to richer discourse.

Freudenthal explicitly assumes a receiver sufficiently humanlike in mental state and experience.

**Contribution:** the idea of semantic curriculum and progressive bootstrapping is not new.

**UNVTRSLR extension:** infer signalhood, exploit shared observable environments, permit nonlinguistic channels, and explicitly attack humanlike cognitive assumptions.

### Exosemiotics

Vakoch and others have challenged both the optimistic assumption that mathematics/science will be straightforwardly shared and the pessimistic claim that communication is impossible. One proposed middle path is to simulate or present natural phenomena themselves, using iconic/shared physical structure as common ground.

**Contribution:** supports grounding through shared phenomena rather than arbitrary notation.

### Interstellar digital communications engineering

Messerschmitt & Morrison emphasize that transmitter and receiver cannot coordinate beforehand and recommend layered architecture for detectability, synchronization, channel impairments, reliability, and higher-level message structure.

**Contribution:** semantic bootstrapping must sit above a separately solved physical/framing layer.

## 9. Self-describing messages and decoding

Interstellar-decoding work proposes first finding message dimensions and symbol structures, then inferring meanings from redundancy, relationships, functions, and shared physics patterns.

**Contribution:** a receiver may have to infer framing and symbol classes before semantics.

**UNVTRSLR extension:** make that inference bidirectional and interactive where possible, and allow the system to discover that the channel is not symbolic in the first place.

## 10. Active learning and scientific inference

UNVTRSLR's active semantic-discovery loop is closely related to experimental design: choose an observation or intervention that best distinguishes competing hypotheses.

Information-gain-style selection is a natural baseline, although no one probabilistic formalism should be assumed mandatory.

**Contribution:** provides a principled way to ask “what should I do next to tell these meanings apart?”

## 11. Multimodal grounding

Embodied AI and multimodal learning show that linguistic or symbolic representations can be tied to perception and sensorimotor interaction.

**Contribution:** meaning can be linked to action/perception rather than text alone.

**UNVTRSLR extension:** neither modality nor perceptual decomposition is assumed shared.

## 12. What appears novel in the combined program

The individual components have substantial precedent. The potentially distinctive contribution is their combination under an unusually strict target:

1. no assumed linguistic channel;
2. signalhood discovery;
3. shared-world but potentially asymmetric perception;
4. active semantic hypothesis testing;
5. negotiated conventions;
6. probabilistic/provenance-aware semantic substrate;
7. explicit semantic conservation ledger;
8. rewarded non-equivalence detection;
9. Earth languages and animal-inspired systems used as controls rather than universal truth;
10. self-describing interstellar bootstrap as a downstream test case.

This novelty claim is provisional. A formal literature review should continue to search for prior systems combining the same responsibilities.

## Research discipline

Related work should be classified as one of:

- `DIRECT_PRECURSOR` — solves substantially the same problem;
- `PARTIAL_PRECURSOR` — solves one required responsibility;
- `CONTROL_RESOURCE` — useful as evaluator ground truth or stress test;
- `ARCHITECTURAL_INSPIRATION` — suggests a representation or algorithm;
- `WARNING/COUNTEREXAMPLE` — demonstrates a false-success mode;
- `OPEN_COMPETITOR` — a simpler or stronger rival architecture.

The project should prefer discovering that a supposed novelty already exists over rebranding prior work.
