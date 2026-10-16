# On-Theo Review Protocol V2

Status: `DRAFT / SUCCESSOR TO V1 / REVIEW REQUIRED`

V2 preserves the V1 exact-head gates and adds machine-readable execution provenance, witness awareness, extension/currentness rules, and review-receipt semantics.

## 1. Review subject

Every review binds at minimum:

- repository;
- PR/branch context;
- exact subject commit SHA;
- exact paths and/or claim/source/witness IDs reviewed;
- review type;
- reviewer role;
- execution provenance;
- evidence/access surfaces consulted;
- result;
- findings and unresolved limitations.

A review result never floats forward across material head movement.

## 2. Execution provenance

Role separation and execution independence are different properties.

Allowed provenance values:

- `SAME_RUNTIME_ROLE_PASS`: one model/runtime deliberately executes multiple bounded role lenses. Useful for adversarial decomposition, but not evidence of independent sampling.
- `INDEPENDENT_RUNTIME`: separately instantiated execution with independent context/output generation.
- `EXTERNAL_HUMAN_REVIEW`: human review outside the model runtime.
- `UNKNOWN`: provenance unavailable; cannot be upgraded by assumption.

Review prose and machine receipts must state the actual value. A Masa/Mune/Hephaestus role-pass executed inside one Vera runtime may be valid role-separated review, but it must not be described as three independent model samples.

## 3. Required gates

### SOURCE_VERIFY

Verify source identity, preservation chain, direct/indirect access, locator, and proposition scope. A lost source known only through an intermediary must preserve that intermediary on the support edge.

### CHRONOLOGY_VERIFY

Independently verify claimed-event, work/composition, and physical-witness clocks. Witness date is not work date. Work date is not event date.

### SEMANTIC_PROPOSITION_VERIFY

Verify proposition identity, semantic scope, evidence class, claim type, and language/period context. Similar strings, names, motifs, or translations are discovery leads, not automatic identity or derivation.

### HOSTILE_ALTERNATIVES

Attempt falsification, simpler explanations, source-dependence alternatives, polemical invention, apologetic development, mistranslation, textual variation, chronology error, selection bias, and project confirmation bias.

### CITATION_READBACK

Read every consequential proposition-to-source edge after freezing the subject. Record whether support is direct text, witness-specific text, indirect preservation, scholarly interpretation, contextual support, or project inference.

### ARCHITECTURE_INTEROPERABILITY

For registry/control-plane changes, verify stable IDs, collision behavior, extension ordering, currentness, witness/source separation, review invalidation, and machine-readable receipt generation.

## 4. Review receipts

Machine-readable receipts live in `registry/reviews.yaml`.

A receipt must contain:

- stable review ID;
- exact subject SHA;
- reviewed artifacts/IDs;
- review type;
- reviewer role;
- execution provenance;
- result;
- findings;
- receipt artifact locator when a prose report exists.

Allowed result values remain:

`PASS_EXACT`, `PASS_WITH_LIMITATIONS`, `CHANGES_REQUIRED`, `FAIL`, `UNRESOLVED`, `NOT_REVIEWED`.

## 5. Witness-aware readback

If a proposition depends on a manuscript or artifact-specific reading, the review must bind both `source_id` and `witness_id`. A modern digital edition or apparatus is an access surface, not the physical witness identity.

## 6. Registry extension review

Any registry extension must declare its base, dependencies, introduced-at SHA, and entity types. Materialization follows `registry/extension-manifest.yaml` and must stop on unresolved references or unreviewed collisions.

## 7. Protected effects

No review result authorizes merge, deployment, publication expansion, credentials/permission mutation, paid compute, destructive rewrite, or another separately protected effect. Those require their own authority.