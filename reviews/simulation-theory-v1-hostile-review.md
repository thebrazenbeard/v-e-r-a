# Simulation Theory V1 Hostile Review

Review subject: `07c96b1dcece9491432d1c01da430d2fee42519e`

Execution provenance: Vera coordinator runtime applying the project hostile-review lens. This is a distinct analytical pass, not an independently instantiated model/runtime review.

Result: `PASS_WITH_LIMITATIONS`

## Scope

Reviewed the V1 simulation-theory branch for:

- simulation-argument overstatement;
- hidden anthropic/reference-class assumptions;
- substrate-independence smuggling;
- physics overreach;
- Planck/quantum/holography category errors;
- empirical unfalsifiability;
- digital-ontology/external-simulation conflation;
- simulator/God equivocation;
- historical analogy inflation;
- registry evidence-class promotion;
- false semantic dependencies in the extension graph.

## Blocking finding discovered and repaired before this exact-head review

### HR-01 — false semantic dependency on Qur'anic system

Initial manifest registration made `EXT-SIMULATION-THEORY-V1` depend on `EXT-QURANIC-SYSTEM-V1` only because the simulation work branch was based on the Qur'anic corpus head.

That was structurally wrong.

Branch ancestry and semantic dependency are different axes. Simulation theory does not require Qur'anic content to be meaningful, and the extension manifest's `base_head_rule` already carries ancestry/currentness constraints.

Repair:

- `EXT-SIMULATION-THEORY-V1.depends_on` changed to `[]`.
- repaired exact head: `07c96b1dcece9491432d1c01da430d2fee42519e`.

Status: `RESOLVED`.

## Hostile findings on repaired head

### HR-02 — generic simulation hypothesis remains deliberately underconstrained

The corpus correctly distinguishes narrow, testable implementations from an unrestricted simulator hypothesis.

The strongest guard appears repeatedly:

`implementation-like structure != demonstrated external provenance`.

No packet turns lack of falsifiability into evidence for simulation.

Status: `PASS`.

### HR-03 — Bostrom is not misreported as proving simulation

The corpus separates:

- Bostrom's three-way conditional argument;
- substrate independence;
- posthuman capacity;
- civilization willingness;
- reference-class/observer counting;
- the separate proposition that our universe is simulated.

`CLM-OUR-UNIVERSE-IS-SIMULATED` has no supporting source and remains `[SPECULATIVE_MODEL, UNKNOWN]`.

Status: `PASS`.

### HR-04 — consciousness assumption is visible rather than smuggled

Bostrom's explicit substrate-independence assumption is documented and given its own concept/claim identity.

The corpus explicitly rejects the inference:

`behaviorally convincing artificial agent -> demonstrated phenomenal consciousness`.

Status: `PASS`.

### HR-05 — physics tests are scoped to their implementation families

Beane/Davoudi/Savage is bound to cubic-lattice numerical simulation.

Vazza is bound to information/energy constraints under sufficiently similar parent-universe physics.

Wolpert's recursion/computer-science results are not converted into empirical evidence that our universe self-simulates.

Status: `PASS`.

### HR-06 — popular quantum/Planck/holography claims are not promoted

The empirical-test registry classifies:

- Planck scale as simulation pixel;
- wavefunction collapse as rendering;
- speed of light as processor cap;
- holography as literal simulation evidence;
- quantum randomness as pseudorandom code;

as analogies/category leaps unless a specific model adds discriminatory predictions.

Status: `PASS`.

### HR-07 — theology comparison avoids simulator/God identity

The comparison distinguishes relative transcendence from metaphysical ultimacy and finite technological creators from classical-theistic creator attributes.

Mizrahi and Donahue are preserved as attributed philosophical arguments that reach materially different assessments.

Status: `PASS_WITH_LIMITATION`.

Limitation: the `classical theism` comparison is currently a comparative synthesis, not yet tied to dedicated tradition-by-tradition source nodes for Jewish, Christian, and Islamic philosophical theology. Any future consequential claim about a specific theological school should use its own primary/scholarly sources.

### HR-08 — historical analogues remain analogues

Plato's cave, dream skepticism, demiurgic models, illusion/reality traditions, avatar/incarnation analogies, and layered cosmologies are not labeled ancient computer-simulation theories.

Status: `PASS`.

### HR-09 — source access is bounded but not uniformly full-text

Strong/full access:

- Bostrom author full text;
- Kipping open preprint;
- Beane/Davoudi/Savage open preprint;
- McCabe open archive;
- Wolpert open preprint;
- Vazza open preprint;
- SEP full reference article;
- Donahue open-access publisher page.

Bounded access:

- Chalmers 2024 chapter: publisher abstract-level in current pass;
- Horgan 2024 chapter: publisher abstract-level;
- Peacocke 2024 chapter: publisher abstract-level;
- Mizrahi 2017 article: publisher abstract-level.

The registry records these limitations explicitly.

Status: `PASS_WITH_LIMITATION`.

### HR-10 — Bostrom critic coverage is incomplete

The prose packet mentions Weatherson/Bostrom debate as evidence that the indifference/reference-class step is nontrivial, but V1 does not yet give Weatherson and Bostrom's reply dedicated registry source nodes.

The claim being made is modest and supported by Bostrom's public debate index, so this does not invalidate the V1 argument map.

Status: `LIMITATION / NEXT-PASS SOURCE EXPANSION`.

### HR-11 — registry report-versus-truth semantics could be sharper

Some claim records mark `contested: true` even when the proposition is a report of what an author argues rather than an assertion that the author's model is correct.

Example: `CLM-BOSTROM-SIMULATION-DISJUNCTION` is textually secure as a report of Bostrom's conclusion, while the argument's soundness is contested.

This is not evidence promotion, but future registry schema work should distinguish:

- `report_accuracy_contested`;
- `proposition_truth_contested`;
- `model_assumptions_contested`.

Status: `NON-BLOCKING SCHEMA LIMITATION`.

## Adversarial model checks

### Escape-hatch test

Question: Can the generic hypothesis evade every physical constraint by positing arbitrary parent physics and simulator behavior?

Answer: yes.

Corpus response: explicitly treats this as loss of empirical content rather than support.

`PASS`.

### Anthropic circularity test

Question: Does the corpus infer many simulated observers from the conclusion that simulations are common?

Answer: no. It exposes simulator prevalence, conscious implementation, and reference class as separate assumptions.

`PASS`.

### Digital-ontology conflation test

Question: Does finding computational structure become external-simulator evidence automatically?

Answer: no.

`PASS`.

### Physics-mysticism test

Question: Are quantum weirdness, Planck units, entropy, or holography treated as inherently simulation-like?

Answer: no.

`PASS`.

### Theology-equivocation test

Question: Is a finite programmer silently promoted into an omniscient/necessary/perfect God?

Answer: no.

`PASS`.

## Review conclusion

The repaired V1 research cut is safe to freeze as a **draft research branch**.

It is not evidence that our universe is simulated. Its main achievement is a disciplined taxonomy of what would have to be true for different simulation arguments to work and what different empirical proposals actually test.

Remaining limitations are source-depth and schema-resolution issues, not hidden truth promotion.

Final result on exact subject `07c96b1dcece9491432d1c01da430d2fee42519e`: `PASS_WITH_LIMITATIONS`.
