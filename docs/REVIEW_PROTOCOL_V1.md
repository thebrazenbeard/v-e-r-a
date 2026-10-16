# On-Theo Review Protocol V1

Status: `DRAFT / REVIEW REQUIRED`

## Review subject

Every review binds:

- repository;
- branch or PR;
- exact commit SHA;
- exact files or registry records reviewed;
- reviewer route/identity;
- review type;
- evidence consulted;
- result;
- unresolved findings.

`PASS` on an older head does not transfer to a materially changed head.

## Required gates for consequential synthesis

### 1. SOURCE_VERIFY

Verify that each cited source exists, that the locator resolves to the claimed passage/artifact, and that the proposition does not say more than the source.

Required attacks:

- quotation or passage misattribution;
- source/reporting intermediary confused with the lost original;
- later tradition treated as contemporary witness;
- material artifact linked to a person/event without evidence;
- secondary summary substituted for the primary source.

### 2. CHRONOLOGY_VERIFY

Verify claimed-event, source/composition, and physical-witness dates independently.

Required attacks:

- composition date silently used as event date;
- manuscript date silently used as composition date;
- later preservation mistaken for contemporary testimony;
- fabricated precision where only a range is supportable;
- source dependence ignored when counting "independent" witnesses.

### 3. SEMANTIC_PROPOSITION_VERIFY

Verify proposition identity, scope, and evidence class.

Required attacks:

- textual occurrence promoted to historical fact;
- scholarly interpretation promoted to source statement;
- similar names/words merged without derivation evidence;
- possibility promoted to probability or fact;
- hostile or favorable intent used as a truth shortcut.

### 4. HOSTILE_ALTERNATIVES

Attempt to falsify the claim and compare simpler explanations.

At minimum test, where applicable:

- ordinary cultural transmission;
- independent convergence;
- polemical invention;
- apologetic development;
- textual dependence;
- redaction/narrative accretion;
- chronology error;
- mistranslation/variant reading;
- selection bias;
- project confirmation bias.

For GOD/controller hypotheses, preregister predictions before source search and record misses.

### 5. CITATION_READBACK

A separate readback confirms each proposition-to-source edge after the candidate is frozen.

Readback must verify:

- source ID;
- locator;
- URL or durable bibliographic locator;
- exact proposition supported;
- whether support is direct, indirect, inferred, or merely contextual;
- whether an opposing source/position was omitted.

## Review outcomes

Allowed result values:

- `PASS_EXACT`
- `PASS_WITH_LIMITATIONS`
- `CHANGES_REQUIRED`
- `FAIL`
- `UNRESOLVED`
- `NOT_REVIEWED`

A result is scoped only to the exact subject recorded.

## Synthesis gate

A consequential synthesis record may be proposed only when the underlying atomic claims are explicit. It may not erase unresolved disagreements. If a synthesis depends on a contested claim, that dependency remains visible in the synthesis record and generated prose.

## Protected effects

Review approval does not authorize merge, publication beyond the already intended public repository surface, deployment, credential/permission mutation, paid compute, destructive rewrite, or any other separately protected effect.
