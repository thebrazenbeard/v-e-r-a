# Control Suite

## Purpose

The control suite is designed to test UNVTRSLR against communication systems whose semantics are at least partially known to the evaluator while progressively removing assumptions that make ordinary translation easy.

Controls are not training truth unless a specific experiment says so.

## Control class 1 — Human natural languages

Use natural languages as **positive controls** because humans already know substantial translation relationships among them.

The test should withhold dictionaries and parallel text from the participating agents while retaining evaluator access to known translations.

### Selection criteria

Choose languages that differ along multiple dimensions:

- word order;
- morphology;
- grammatical gender/classification;
- tense/aspect systems;
- evidentiality;
- pronoun systems;
- spatial encoding;
- lexicalization patterns;
- cultural categories;
- resource level.

Candidate sets should include languages from unrelated families rather than only closely related Indo-European pairs.

Uniform Meaning Representation research is useful here because UMR explicitly targets commonalities and variations across diverse languages, including Arapaho, Chinese, English, Kukama, Navajo, and Sanapaná in its first released multilingual dataset.

### Evaluation

Measure:

- recovered referential mappings;
- recovered predicate/argument structure;
- temporal/modality preservation;
- one-to-many and many-to-one mappings;
- untranslatable or paraphrase-required distinctions;
- conservation ledger accuracy.

## Control class 2 — Signed and spatial human language

Include at least one signed-language or sign-inspired control.

Purpose:

- break the assumption that language is acoustic/textual;
- test spatial grammar;
- test simultaneity versus sequential tokenization;
- test embodiment and viewpoint effects.

Do not flatten signed communication into English glosses before it reaches the learner, because that would remove the modality challenge.

## Control class 3 — Natural Semantic Metalanguage as a hypothesis baseline

Natural Semantic Metalanguage (NSM) research proposes a stable set of 65 semantic primes shared across human languages, along with combinatorial properties.

UNVTRSLR should treat these as:

- a strong human-language hypothesis;
- a useful benchmark for semantic recovery;
- a source of candidate low-complexity human concepts;

but **not** as proof of universal concepts across nonhuman or extraterrestrial intelligence.

Experiments can ask:

- which NSM primes are independently recoverable from grounded interaction?
- which require specifically human social/cognitive assumptions?
- do agents invent different decompositions that support the same behavior?

## Control class 4 — Synthetic languages with exact evaluator truth

Generate languages whose semantics and grammar are entirely known to the evaluator.

Vary:

- compositionality;
- word order;
- morphology;
- synonymy;
- polysemy;
- context dependence;
- irregularity;
- optional information;
- semantic underspecification.

Synthetic languages provide the cleanest test of whether a system reconstructs meaning rather than matching familiar human-language statistics.

### Required variants

1. Fully compositional language.
2. Partially compositional language.
3. Holistic codebook language.
4. Context-sensitive language.
5. Language with deliberately non-English category boundaries.
6. Language with lossy source-to-target mapping.
7. Language with concepts absent from target inventory.

## Control class 5 — Private-code traps

Create agents that can solve a referential task with arbitrary IDs or positional shortcuts.

These controls should obtain high task reward while failing semantic-transfer tests.

The evaluator must reject them as semantic success.

This addresses a known emergent-communication problem: successful agents can align representations and coordinate without learning evaluator-recognizable conceptual structure.

## Control class 6 — Honeybee-inspired vector communication

Use a synthetic channel inspired by the honeybee waggle dance.

Example mapping:

- orientation -> direction;
- duration -> distance;
- repetition/precision -> reliability or audience-dependent effects.

Do not tell the learner which dimensions are semantically relevant.

Test whether it can discover:

- that the behavior is communicative;
- which dimensions carry information;
- what environmental variables they map to;
- that signal precision can itself vary with social context.

The point is not to claim the synthetic agent is a bee. The point is to test continuous embodied encoding.

## Control class 7 — Context-dependent alarm communication

Use a synthetic system inspired by vervet-monkey alarm research.

Create signal forms whose meaning depends on environmental/social context.

The same signal may correspond to different receiver-relevant interpretations under different contextual conditions.

A one-to-one dictionary learner should fail.

Measure whether UNVTRSLR learns a conditional semantic mapping and preserves context dependence in translation.

## Control class 8 — Whale-like sequence modeling

Use synthetic acoustic sequence systems inspired by sperm-whale coda research.

Separate tasks carefully:

- acoustic structure prediction;
- individual/social-unit classification;
- turn-taking prediction;
- contextual association;
- demonstrated semantic mapping.

A system that predicts plausible vocal sequences has not thereby translated them.

Project CETI and its WhAM work are useful related research, but semantic qualification requires behavioral/contextual evidence beyond acoustic generation.

## Control class 9 — Continuous arbitrary channels

Construct communication systems where meanings are encoded in:

- frequency;
- amplitude;
- duration;
- phase-like relationships;
- trajectories;
- acceleration;
- orientation;
- timing intervals;
- combinations of continuous dimensions.

This prevents the architecture from treating discrete tokenization as universal.

## Control class 10 — Environmental modification

Do not provide a dedicated communication channel.

Agents communicate only by modifying shared space:

- object placement;
- path construction;
- resource arrangement;
- temporary marks;
- repeated motion traces.

The system must infer when action functions as signal rather than merely as world manipulation.

## Control class 11 — Asymmetric sensors

Use the same latent world with different sensory projections.

Examples:

- RGB vs depth;
- optical flow vs object detections;
- acoustic spectrum vs event labels;
- allocentric vs egocentric space;
- coarse temporal/high spatial vs high temporal/coarse spatial.

The evaluator must ensure there is no hidden common latent vector available to both agents.

## Control class 12 — Different ontology partitions

Give the agents intentionally different category boundaries.

Examples:

- continuous color vs categorical color;
- two source states collapsed into one target state;
- different object segmentation;
- relation-first vs object-first representation;
- one side has a sensory feature unavailable to the other.

Success includes identifying partial or absent equivalence.

## Control class 13 — Unknown communication channel

Provide many observable behaviors, only some of which carry communicative information.

The learner does not receive a `message` field.

Evaluate signalhood discovery independently from semantic decoding.

## Control class 14 — No communication control

Include worlds where no communicative behavior exists.

UNVTRSLR should conclude that there is insufficient evidence for signalhood.

If it invents a language anyway, the signalhood detector is overfitting.

## Control class 15 — Deceptive or unreliable communicator

The counterpart sometimes emits:

- false signals;
- accidental signals;
- stale conventions;
- strategic deception;
- inconsistent mappings.

The translator should preserve provenance and learn reliability conditional on context rather than converting received signals into truth.

## Control class 16 — Semantic drift

Change a convention after it has been established.

Measure:

- drift detection;
- confidence reduction;
- repair negotiation;
- convention versioning;
- whether old and new mappings are contextually separated.

## Control class 17 — Shared-language leakage controls

Deliberately insert prohibited shortcuts to verify the evaluator catches them:

- shared class IDs;
- shared object IDs;
- identical embeddings;
- synchronized private indices;
- hidden natural-language metadata;
- evaluator truth copied into learner state.

The qualification harness is not trustworthy unless these controls are detected or explicitly excluded.

## Control class 18 — Human zero-shared-language interaction

Later-stage human experiments can test whether the protocol helps people construct communication under channel restrictions.

Possible restrictions:

- no speech;
- no writing;
- novel arbitrary signal interface;
- shared manipulable environment;
- limited feedback;
- asymmetric observations.

These experiments require ethical review and should follow, not precede, synthetic validation.

## Control class 19 — “Alien” synthetic agents

Construct agents whose internal representations are intentionally unlike common human semantics.

Examples:

- no persistent object identity;
- field/flow-centered world model;
- radically different time discretization;
- high-dimensional sensory categories;
- goal structures unlike human reward tasks;
- communication optimized around state transitions rather than referents.

The objective is not to model actual aliens. It is to attack anthropocentric assumptions.

## Control class 20 — Self-describing bootstrap control

Give a receiver an unknown protocol whose first task is to explain enough of its own framing and semantics to support later interpretation.

Compare:

- predeclared framing;
- partially self-describing framing;
- fully opaque stream with repeated curriculum structure.

This is the closest terrestrial control for the broadcast form of interstellar UNVTRSLR.

## Required reporting

Every control run should record:

- what information each agent had;
- what they did not share;
- sensory interfaces;
- action interfaces;
- channel definition or absence of one;
- evaluator-only truth;
- semantic challenges attempted;
- calibration;
- conservation ledger;
- negative-control performance;
- alternative shortcut explanations.

Without that disclosure, cross-experiment “universality” comparisons are meaningless.
