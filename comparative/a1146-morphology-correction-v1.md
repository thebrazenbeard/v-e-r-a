# A.1146 Death-Verb Morphology Correction V1

Status: RESEARCH_CORRECTION / PHILOLOGICAL_DOWNGRADE / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #52
- predecessor head: cf5c517faca6faff27e7ba28cd738ae49dd9523f
- branch: research/a1146-morphology-correction-v1-20260918

## Correction target

Earlier lexical-control work treated the reconstructed A.1146 form commonly rendered "they kill him" as securely derived from Akkadian daku "to kill."

That confidence is too high.

## 1. Marello / Mettinger morphology problem

Mettinger's discussion of A.1146 reports that Marello explicitly noted a morphological problem:

if the form is from daku "to kill," the written/reconstructed form is irregular.

Mettinger gives the transmitted/reconstructed form as:
idakkushu

and notes that a regular form expected from daku would differ.

Therefore:

A1146_DAKU_LEMMA = POSSIBLE / COMMONLY ADOPTED
not:
A1146_DAKU_LEMMA = MORPHOLOGICALLY_SECURE.

## 2. Sasson's alternative

Mettinger also reports Jack Sasson's alternative possibility:

the form may instead derive from a verb interpreted approximately as:
"press in / pierce / push in"

with a reading along the lines of:
"they push him in."

This alternative is reported second-hand in Mettinger from scholarly correspondence.

It is not independently primary-edition controlled in this project.

Therefore:

SASSON_ALTERNATIVE = REPORTED_PHILOLOGICAL_ALTERNATIVE
not:
ESTABLISHED_READING.

## 3. Context still supports a death/harm frame

Even with the morphological ambiguity, the passage compares the letter writer's repeated escapes from death with Dumuzi's fate.

The contextual frame makes a harm/death interpretation plausible.

But context cannot settle the exact lemma or morphology.

Correct project distinction:

CONTEXTUAL_DEATH_FRAME = STRONG

EXACT_VERB_LEMMA = DISPUTED

EXACT_ENGLISH_GLOSS = RECONSTRUCTION_DEPENDENT.

## 4. "They kill him" remains a scholarly translation, not secure source-form identity

Daniel Fleming's translation "they kill him" remains an important scholarly reconstruction and has been repeated by Mettinger and later authors.

But the project must no longer infer:

FLEMING_TRANSLATION
=> SECURE_DAKU_MORPHOLOGY.

Instead:

FLEMING_TRANSLATION = SCHOLARLY_RECONSTRUCTION_SUPPORTED_BY_CONTEXT.

## 5. Effect on Dumuzid/Baal lexical comparison

The previous broad comparison still survives:

A.1146 and the Baal Cycle do not preserve one demonstrably shared lexical death-return formula.

But one component must be weakened.

Old formulation:
A.1146 = secure agentive daku "kill" + iterative taru "return."

Corrected formulation:
A.1146 = disputed harm/death verb commonly translated "they kill him" + iterative taru "return."

The Ugaritic side remains:
- mt / hlq for death/perishing;
- hy / existence language for renewed life.

Therefore:

SHARED_LEXICAL_FORMULA_NOT_FOUND

still stands.

But:

A1146_AGENTIVE_DAKU_HIGH_CONFIDENCE

is superseded.

## 6. Evidence-state correction

Recommended statuses:

- A1146_DEATH_CONTEXT: HIGH
- A1146_DEATH_VERB_TRANSLATION_KILL: SCHOLARLY_RECONSTRUCTION
- A1146_DAKU_LEMMA: DISPUTED
- A1146_ALTERNATIVE_PUSH_IN_READING: REPORTED_ALTERNATIVE
- A1146_EXACT_MORPHOLOGY: UNRESOLVED
- A1146_TARU_RETURN: RETAINS_SEPARATE_LEXICAL_CONTROL

## 7. Current disposition

A1146_MORPHOLOGY_CORRECTION_V1 =
CORRECTION_REQUIRED_AND_APPLIED

Superseded:
- high-confidence claim that idakkushu is securely a regular daku "kill" form.

Retained:
- death/harm context;
- common scholarly translation "they kill him" as reconstruction;
- iterative return comparison;
- no-shared-lexical-formula result versus Baal.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
