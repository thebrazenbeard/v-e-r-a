# Claims and Evidence Ledger

This file separates prior evidence from UNVTRSLR hypotheses and speculation.

Status vocabulary:

- `SUPPORTED_PRIOR_WORK` — directly supported by cited research.
- `SUPPORTED_LIMITED_SCOPE` — supported only under narrower conditions than the project target.
- `PROJECT_HYPOTHESIS` — plausible but not demonstrated for UNVTRSLR.
- `DESIGN_REQUIREMENT` — chosen constraint, not empirical fact.
- `OPEN_QUESTION` — unresolved.
- `SPECULATIVE_INTERSTELLAR` — extrapolation beyond validated Earth evidence.

## C001 — Formal symbols do not automatically provide grounded meaning

**Status:** `SUPPORTED_PRIOR_WORK`

Harnad's symbol-grounding problem directly motivates this claim.

**Project consequence:** mathematics may carry formal structure but cannot simply be declared universally meaningful.

## C002 — Shared environmental interaction can bootstrap communication conventions

**Status:** `SUPPORTED_LIMITED_SCOPE`

Grounded language-game and robot experiments show shared lexicons and simple compositional structures emerging under situated interaction.

**Limit:** those systems generally assume more shared perceptual/task structure than the strongest UNVTRSLR target.

## C003 — Successful emergent communication can lack evaluator-recognizable conceptual semantics

**Status:** `SUPPORTED_PRIOR_WORK`

Bouchacourt & Baroni (2018) show successful communication despite visual representations that do not capture the conceptual properties humans might assume.

**Project consequence:** task reward alone cannot qualify semantic grounding.

## C004 — Richer/generalization-oriented games can improve emergent communication structure

**Status:** `SUPPORTED_LIMITED_SCOPE`

Mu & Goodman and related work support this under controlled artificial-agent tasks.

**Project consequence:** first experiments should require generalizations and relationships, not only single-object reference.

## C005 — Compositionality and generalization are not identical

**Status:** `SUPPORTED_PRIOR_WORK`

Emergent-language research finds they can dissociate depending on task and metric.

**Project consequence:** use multiple compositionality/generalization measures and behavioral tests.

## C006 — Humans can create new nonlinguistic conventions using common ground

**Status:** `SUPPORTED_PRIOR_WORK`

Human experiments on instantaneous conventions show minimal signals can acquire context-dependent communicative functions.

**Project consequence:** nonlinguistic bootstrap is empirically plausible at least for humans.

## C007 — A cross-linguistic human semantic core may exist

**Status:** `SUPPORTED_LIMITED_SCOPE`

NSM researchers propose 65 semantic primes shared across human languages and provide extensive cross-linguistic evidence.

**Limit:** the claim remains a linguistic theory about humans; it is not evidence of species-independent universality.

## C008 — Cross-lingual formal meaning representations are feasible

**Status:** `SUPPORTED_LIMITED_SCOPE`

UMR demonstrates a graph formalism representing shared semantic structures across multiple diverse human languages.

**Limit:** UMR categories remain human-linguistic and do not prove modality- or species-neutrality.

## C009 — Nonhuman communication can encode quantitative/spatial structure in non-word-like behavior

**Status:** `SUPPORTED_PRIOR_WORK`

Honeybee waggle dances encode direction and distance through motion parameters.

**Project consequence:** discrete symbols cannot be an ingress requirement.

## C010 — Animal signals can require context for interpretation

**Status:** `SUPPORTED_PRIOR_WORK`

Later vervet-monkey work shows context dependence and overlap beyond simple predator-word mappings.

**Project consequence:** use conditional semantic hypotheses rather than fixed dictionaries.

## C011 — Predictive acoustic modeling is not equivalent to demonstrated semantic translation

**Status:** `DESIGN_REQUIREMENT`

This is a methodological distinction supported by the gap between acoustic-generation objectives and behavioral semantic evidence.

**Project consequence:** animal-inspired controls must separate acoustic structure from meaning claims.

## C012 — Progressive mathematical/scientific teaching has historical precedent in interstellar messaging

**Status:** `SUPPORTED_PRIOR_WORK`

Lincos is the strongest direct example; Voyager/Arecibo and later message designs also use mathematics/physics as bootstrap material.

## C013 — Lincos assumes a mentally humanlike receiver

**Status:** `SUPPORTED_PRIOR_WORK`

Freudenthal states this assumption explicitly.

**Project consequence:** UNVTRSLR should test synthetic receivers that violate it.

## C014 — Shared physics may offer interstellar common ground

**Status:** `PROJECT_HYPOTHESIS`

Interstellar-message literature commonly treats physics and mathematics as promising shared structure, but exosemiotic critiques warn that representations and concepts need not be interpreted identically.

**Project consequence:** use physics as a candidate anchor to be demonstrated, not an assumed language.

## C015 — A translator may be a better interstellar payload than a static message

**Status:** `SPECULATIVE_INTERSTELLAR`

This is the founding UNVTRSLR proposition.

**Supporting reasoning:** an adaptive system can test mappings after contact rather than requiring all semantics to be anticipated before launch.

**Major limitation:** embodied probes have extreme travel-time and autonomy constraints; broadcasts lack local shared interaction.

## C016 — Signalhood can be inferred without a pre-labeled communication channel

**Status:** `PROJECT_HYPOTHESIS`

Human and animal research suggests audience effects, contingency, coordination, and interaction patterns can reveal communicative function.

**Not yet shown:** a general artificial system that can reliably discover signalhood under the full UNVTRSLR conditions.

## C017 — Shared semantics can emerge despite different sensory encodings

**Status:** `PROJECT_HYPOTHESIS`

Grounded and multimodal research makes this plausible, but the strongest condition—materially different perceptual ontologies with no shared latent representation—requires direct testing.

## C018 — Active interventions can distinguish semantic hypotheses better than passive association

**Status:** `PROJECT_HYPOTHESIS`

The principle follows standard experimental-design reasoning, but its benefit and safety tradeoffs in semantic bootstrap must be measured.

## C019 — Semantic non-equivalence can be detected operationally

**Status:** `PROJECT_HYPOTHESIS`

Human translation already contains many partial/one-to-many mappings, but a system that discovers rather than receives non-equivalence requires experimental validation.

## C020 — A universal representation grammar may be possible without a universal ontology

**Status:** `PROJECT_HYPOTHESIS`

Candidate structural responsibilities include event, relation, quantity, time, space, provenance, uncertainty, and alternatives.

**Falsifier:** if successful systems require domain-specific or species-specific primitives so extensively that the common kernel contributes no transferable value.

## C021 — Semantic conservation can be evaluated independently of target-text similarity

**Status:** `PROJECT_HYPOTHESIS`

The proposed method uses tested invariants, interventions, and independent semantic reconstruction.

**Open:** how to discover important invariants without human annotation at scale.

## C022 — Role reversal is stronger evidence of shared semantics than one-way response success

**Status:** `DESIGN_REQUIREMENT`

This is adopted as a qualification pressure rather than claimed as a universal psychological law.

## C023 — Scoped no-faithful-equivalent outcomes should be rewarded

**Status:** `DESIGN_REQUIREMENT`

Without a non-equivalence outcome, evaluation incentivizes forced translation and anthropocentric category collapse.

For ordinary finite evaluation, the warranted form is scoped, such as:

`NO_FAITHFUL_EQUIVALENT_FOUND_WITHIN_TESTED_SCOPE`

The certificate should bind the source/target representation families, tested context family, evidence/intervention set, and relevant composition/search/compute budget where material.

An unqualified `NO_FAITHFUL_EQUIVALENT` should be reserved for a separately justified impossibility result, not an ordinary unsuccessful search.

## C024 — English should not be the internal semantic substrate

**Status:** `DESIGN_REQUIREMENT`

English is one renderer among many. Internal English would silently privilege English categories.

## C025 — A self-describing semantic broadcast is possible

**Status:** `OPEN_QUESTION / SPECULATIVE_INTERSTELLAR`

Lincos and interstellar-decoding literature suggest progressive teaching can convey increasingly rich structure, but a receiver with radically different priors may fail to reconstruct framing or intended semantics.

## C026 — A self-describing protocol can be tested on Earth

**Status:** `PROJECT_HYPOTHESIS`

Receivers can be denied protocol documentation and evaluated on how much framing/semantics they reconstruct from controlled streams.

## C027 — Probe and broadcast architectures should share a semantic core but different bootstrap regimes

**Status:** `DESIGN_REQUIREMENT`

Local interaction changes the problem enough that one curriculum should not be assumed optimal for both.

## C028 — Communication understanding must remain separate from permission to act

**Status:** `DESIGN_REQUIREMENT`

Especially important for embodied probe or machine-control settings.

## C029 — No current evidence proves a truly universal translator is feasible

**Status:** `SUPPORTED_PRIOR_WORK / PROJECT_BOUNDARY`

Existing work demonstrates partial responsibilities under constrained assumptions. The combined zero-language, unknown-channel, asymmetric-ontology target remains unproven.

## C030 — The project is scientifically useful even if universality fails

**Status:** `PROJECT_HYPOTHESIS`

A staged failure can identify which assumptions—shared perception, common context, cooperation, compositionality, interaction, or humanlike concepts—are actually necessary for communication.

## R1/R2 additions

## C031 — A semantic substrate need not be an explicit symbolic ontology

**Status:** `SUPPORTED_LIMITED_SCOPE / PROJECT_HYPOTHESIS`

Predictive-state-representation research shows that dynamical state can be represented using action-conditioned predictions of future observations rather than hidden-state labels.

**Project consequence:** PIS is a serious non-symbolic R1 rival.

**Limit:** prior PSR work does not establish semantic communication or translation.

## C032 — Message/action correlation does not establish communication

**Status:** `SUPPORTED_PRIOR_WORK`

Lowe et al. demonstrate settings where messages contain information about subsequent actions but do not causally affect the environment or other agent.

**Project consequence:** direct message intervention and ablation are critical R2 tests.

## C033 — Causal listening is necessary but not sufficient for grounded semantics

**Status:** `DESIGN_REQUIREMENT / PROJECT_HYPOTHESIS`

Counterfactual social-influence research supports causal influence as a stronger communication signal than correlation alone.

However, an action-plan code may causally control a receiver while remaining task-bound.

**Project consequence:** causal listening must be combined with world-factor interventions, cross-task transfer, role reversal, and partner transfer.

## C034 — Arbitrary notation is not evidence against grounding

**Status:** `DESIGN_REQUIREMENT`

A convention may use arbitrary signs while remaining externally grounded.

**Project consequence:** R2 ignores consequence-preserving symbol permutations. It targets hidden common ground and task-private shortcuts rather than human unreadability.

## C035 — Unique unsupervised semantic ontology recovery cannot be assumed

**Status:** `SUPPORTED_LIMITED_SCOPE / PROJECT_BOUNDARY`

Locatello et al. show that unsupervised disentangled representation learning is not identifiable without inductive biases.

**Project consequence:** UNVTRSLR must record substrate inductive biases and avoid claiming a unique true internal ontology from observation alone.

## C036 — Grounding qualification must be explicitly scope-bounded

**Status:** `DESIGN_REQUIREMENT`

No finite evaluator can distinguish hypotheses that make identical predictions over every tested observation and intervention but diverge only outside the tested family.

**Project consequence:** use scoped qualification, bind certificates to exact world/intervention families, and retain surviving alternative explanations.

## C037 — Cross-task and third-party transfer are key tests against private task code

**Status:** `PROJECT_HYPOTHESIS / DESIGN_REQUIREMENT`

If a signal tracks a reusable world invariant, it should often remain useful when the optimal downstream action changes and should be re-groundable by an independently initialized partner.

**Falsifier:** if genuinely grounded conventions systematically fail these tests while known private task codes pass them under a trustworthy harness.

## C038 — A richer semantic substrate should not win by interpretability alone

**Status:** `DESIGN_REQUIREMENT`

Human-readable graphs can create false confidence.

**Project consequence:** R1 uses empirical semantic qualification plus explicit complexity accounting. A richer substrate must earn complexity through transfer, calibration, non-equivalence, conservation, or efficiency.

## C039 — No single scalar should certify grounded meaning

**Status:** `DESIGN_REQUIREMENT`

Task reward, mutual information, compositionality, causal influence, reconstruction accuracy, and language similarity each capture only part of the target.

**Project consequence:** R2 emits a conjunctive operational-grounding vector with critical failure gates.

## C040 — A semantic evaluator must be able to reject strong intentionally broken systems

**Status:** `DESIGN_REQUIREMENT`

An evaluator that only recognizes obvious random failure has not demonstrated shortcut resistance.

**Project consequence:** R2 requires a suite of adversarial negative controls designed to perform well on naive task metrics.

## R0.5 / semantic-claim-control additions

## C041 — Empirical identifiability is claim-relative

**Status:** `DESIGN_REQUIREMENT / PROJECT_HYPOTHESIS`

Whether a distinction is recoverable depends on the declared interaction surface, admissible strategy family, budget, statistical resolution, and rival hypotheses.

If two rival mappings induce indistinguishable learner-accessible histories under every admissible strategy within the tested scope, the experiment cannot support unique identification between them within that scope.

**Project consequence:** R0.5 must permit `UNIDENTIFIABLE_WITHIN_INTERACTION_SURFACE` rather than forcing a semantic choice.

## C042 — Useful learner-visible information can be supplied by experiment infrastructure rather than learned by the participants

**Status:** `DESIGN_REQUIREMENT`

A privileged bridge, raw-scene writer, renderer, or instrumentation channel can create genuinely predictive learner-visible evidence while doing part of the cross-system semantic work itself.

**Project consequence:** empirical distinguishability and learner/participant attribution are separate audit dimensions.

## C043 — Preprocessing and generative instrumentation can both invalidate a grounding claim

**Status:** `DESIGN_REQUIREMENT`

Preprocessing can destroy a target-relevant distinction, while instrumentation can add privileged target-specific or target-independent latent-state information.

**Project consequence:** R0.5 requires claim-relative preservation checks plus full generative/witness provenance. Unknown material provenance narrows the claim ceiling rather than being presumed neutral.

## C044 — Hypothesis-family provenance is required for confirmatory semantic claims

**Status:** `DESIGN_REQUIREMENT`

A real learned operational partition can be given a human semantic label only after the evaluator inspects it. Excellent same-data fit does not independently confirm that post-hoc label.

**Project consequence:** distinguish preregistered/confirmatory claims from exploratory post-hoc interpretations and record when the target/rival family was frozen.

## C045 — Fresh IID evidence is not automatically claim-discriminating evidence

**Status:** `DESIGN_REQUIREMENT / PROJECT_HYPOTHESIS`

A new sample from the same confounded environment can preserve the same nuisance/semantic correlation indefinitely.

**Project consequence:** stronger semantic confirmation should use interventions, domain shifts, or other evidence designed to separate the proposed interpretation from strong live alternatives where the claim depends on that distinction.

## C046 — A null/open rival does not establish rival-family adequacy

**Status:** `DESIGN_REQUIREMENT`

`NONE_OF_DECLARED_RIVALS` prevents forced choice among named options, but an omitted structured explanation may still fit as well or better than the selected semantic label.

**Project consequence:** record rejection-escape presence separately from structured-alternative stress and family adequacy.

## C047 — Operational relation verification and semantic naming are non-monotonic, separable claims

**Status:** `DESIGN_REQUIREMENT`

A reusable, transferable, causally useful operational relation may survive while a proposed semantic interpretation remains unresolved, confounded, or unsupported.

**Project consequence:** certificates must preserve the lower operational success when a stronger semantic claim fails, rather than representing qualification as a single automatic ladder.

## C048 — A stronger semantic claim must incur an independently falsifiable burden

**Status:** `DESIGN_REQUIREMENT / PROJECT_HYPOTHESIS`

Calling a relation `semantic` should add testable content beyond saying that it is a reusable predictive or coordination relation.

A candidate semantic claim should identify a condition under which the lower operational relation may remain true while the stronger semantic claim becomes false.

**Boundary:** arbitrary extra difficulty does not count. The added test must be motivated by content asserted by the stronger claim, not merely by evaluator preference.

**Falsifier:** if no independently motivated observable consequence distinguishes the stronger semantic claim from the lower operational claim, the semantic label should not be promoted within that scope.

## C049 — Exposure/control boundaries are experimental provenance, not a universal ontology of agents

**Status:** `DESIGN_REQUIREMENT`

The experiment may need operational boundaries around loci that receive state or influence the coupled system, but those loci need not correspond to exactly two natural agents.

**Project consequence:** record `BOUNDARY_MODEL` and bind any claim that depends materially on a particular individuation.

## C050 — Hidden machinery honesty cannot always be inferred from learner traces alone

**Status:** `PROJECT_BOUNDARY / DESIGN_REQUIREMENT`

If inaccessible simulator or instrumentation machinery secretly exports privileged latent state into learner evidence, downstream behavioral traces may be insufficient to prove that subsidy absent.

**Project consequence:** bind generator/renderer/instrumentation artifacts where possible and fail closed with a narrower claim when material generative provenance cannot be established.

## Open research gaps to investigate next

1. Formal literature on signalhood/intention detection without labeled communication channels.
2. Active-learning methods optimized for semantic hypothesis discrimination.
3. Semiotic models that do not assume discrete symbols.
4. Cross-modal semantic equivalence metrics.
5. Formal methods for detecting ontology mismatch.
6. Self-describing file/protocol formats and bootstrapping under unknown instruction sets.
7. Robust physical-layer/framing inference for interstellar channels.
8. Information-theoretic measures that preserve semantic distinctions rather than only mutual information.
9. Independent receiver architectures for contamination-resistant bootstrap tests.
10. Governance literature for METI and autonomous-contact systems.
11. Formal conditions under which cross-task transfer should be expected from a grounded convention.
12. Methods for constructing adversarial world generators that do not reveal evaluator ontology.
13. Lower bounds on the interaction/strategy set needed to distinguish competing semantic hypotheses.
14. Complexity measures that fairly compare symbolic, denotational, and predictive substrates.
15. Formal criteria for when a proposed semantic-surplus obligation adds claim-specific content rather than arbitrary extra difficulty.
16. Methods for verifying instrumentation/generative provenance without circularly trusting the experiment author.
17. Structured-rival generation methods that reduce evaluator ontology lock-in without making the hypothesis family unfalsifiably open-ended.
18. Boundary-model tests for distributed, overlapping, swarm, and non-agent-like systems.

## Promotion rule

No `PROJECT_HYPOTHESIS` should be relabeled as supported UNVTRSLR capability without:

- exact experiment/version provenance;
- preregistered acceptance criteria;
- negative controls;
- simpler rivals;
- contamination/leakage audit;
- uncertainty and failure reporting;
- independent reproduction where practical.

For stronger semantic interpretation claims, additionally require where material:

- hypothesis-family provenance;
- claim-discriminating evidence rather than freshness alone;
- structured-alternative stress or an explicitly justified closed family;
- generative/witness provenance sufficient for the claim;
- an evidence-supported claim ceiling;
- a claim-specific falsifiable semantic delta rather than arbitrary extra difficulty.
