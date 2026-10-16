# Mari Dumuzi Source Verification V1

Status: RESEARCH_AUDIT / SOURCE_PROVENANCE_AND_EVIDENCE_CEILING / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #48
- predecessor head: 0c217af3dc4ddad5f9c0738f8306080defb0e1c4
- branch: research/mari-dumuzi-source-verification-v1-20260918

## Purpose

PR #48 used three Old Babylonian Mari documents as a bounded contact-field control for the Dumuzid/Baal transmission question:

- A.1146;
- A.4540;
- MARI 5 (1987) 14.

This audit asks whether those three records are controlled at the same evidentiary level.

They are not.

Current V1 hierarchy:

A.1146
= ORIGINAL_PUBLICATION_PROVENANCE_CONFIRMED
+ CRUCIAL_DUMUZI_PASSAGE_DAMAGED_AND_RECONSTRUCTION_DEPENDENT

A.4540
= PUBLICATION_PROVENANCE_CONFIRMED
+ LINE_4_BURIAL_READING_INDEPENDENTLY_LEXICALLY_CONTROLLED

MARI_5_1987_14
= CURRENT_SCHOLARLY_SYNTHESIS_CONTROL
+ ORIGINAL_PUBLICATION_NOT_YET_RECONSTRUCTED_IN_THIS_PASS

The purpose is to improve provenance, not to force all three into one confidence tier.

## 1. A.1146 — publication identity

Original publication:

Pierre Marello,
"Vie nomade,"
Florilegium marianum I / Mélanges M. Fleury,
Mémoires de NABU 1,
Paris: SEPOA, 1992,
pp. 115–126.

The SEPOA-hosted volume directly identifies A.1146 as the letter published in Marello's article.

Current ARCHIBAB bibliography pointer:
https://www.archibab.fr/T1011

A 2023 scholarly article independently cites the text as:
A.1146 = LAPO 16 38 = Marello 1992, 115–126 = ARCHIBAB T1011.

Therefore:

A1146_PUBLICATION_IDENTITY = CONFIRMED

## 2. A.1146 — social and epistolary context

The letter is not a mythological composition.

Current scholarship identifies it as a letter from Hammi-ištamar, an Uprapean/Yaminite chief, to Yasmah-Addu, another Yaminite chief.

The speaker uses his own dangerous experiences and repeated escapes from death as part of a taunting/moralizing comparison.

This context matters because Dumuzi appears as a metaphor inside ordinary elite correspondence rather than inside a temple hymn or mythological narrative.

That makes the passage historically valuable for circulation of the idea.

It also means:

LETTER_METAPHOR != FORMAL_THEOLOGICAL_TREATISE.

## 3. A.1146 — Dumuzi death/return wording has a real reconstruction ceiling

The frequently cited Dumuzi passage is damaged and linguistically difficult.

A scholarly reconstruction transmitted through Daniel Fleming and cited by Mettinger renders the crucial lines approximately as:
- why am I not like Dumuzi?;
- "they kill him";
- at a time associated with reckoning/counting the year;
- he repeatedly/always returns to the temple of Annunitum.

The bracketed restoration "[in the spring?]" is not preserved tablet text.

Likewise, the exact parsing of the killing phrase and the damaged temporal wording has attracted discussion.

A later scholarly summary explicitly calls this only a possible case of a cultic celebration of Dumuzi's return.

Therefore the project must distinguish:

A1146_SECURE_CORE:
- Dumuzi is invoked in a death/return comparison;
- return to Annunitum's temple is part of the reconstructed sense accepted by multiple scholars.

A1146_NOT_SECURE_AS_DIRECT_TABLET_WORDING:
- "[in spring]";
- a fully reconstructed annual vegetation calendar;
- a literal bodily-resurrection doctrine;
- an exact ritual mechanism.

## 4. A.1146 — ritual statue interpretation is secondary

Katz, Mettinger, Fleming-related discussion, and other modern scholarship have proposed that:
- the death/return language may reflect cultic celebration;
- the return may have been enacted through movement of a cult statue;
- the rite may correlate with a seasonal festival.

Those are historical reconstructions.

They are not encoded in A.1146 as an explicit statement:
"this is a statue ritual."

Control:

A1146_RETURN_LANGUAGE
!=
STATUE_RITUAL_PRIMARY_TEXT_FACT.

Recommended evidence class for statue-journey interpretation:
SCHOLARLY_INTERPRETATION / HISTORICAL_RECONSTRUCTION.

## 5. A.4540 — publication provenance

Antoine Jacquet's:
Florilegium Marianum XII. Documents relatifs aux dépenses pour le culte,
Mémoires de NABU 13,
Paris, 2011,

publishes administrative documents concerning cult expenditures from the Mari archives.

Institutional bibliographic confirmation:
- Collège de France identifies the volume as Jacquet's 2011 monograph;
- SEPOA identifies Mémoires de NABU 13 as FM XII.

The current electronic Supplement to the Akkadian Dictionaries cites:

FM 12, 139 A.4540:4

for the Old Babylonian phrase:

ana temrim sha Dumuzi

and translates the phrase as:

"for the burial of Dumuzi."

It explicitly distinguishes the noun temru/timru "burial" from a different timru "embers" lemma and notes Jacquet's interpretation.

Therefore:

A4540_LINE4_BURIAL_OF_DUMUZI =
INDEPENDENT_LEXICAL_CONTROL_HIGH.

## 6. A.4540 — what it establishes and what it does not

Strong:
- an administrative/cult-expenditure document contains a phrase referring to the burial of Dumuzi;
- the burial reading has current lexical support.

Not established by that line alone:
- Dumuzi's subsequent return;
- bodily resurrection;
- equivalence with A.1146's return language;
- direct connection to Baal;
- a universal Mari annual dying/rising ritual.

The document belongs in the contact-field model as:

MARI_DUMUZI_BURIAL_RITUAL_ADMINISTRATIVE_EVIDENCE.

It should not be used alone as a "return" source.

## 7. MARI 5 (1987) 14 — current state

Ayali-Darshan 2024 treats MARI 5 (1987) 14 as a record associated with Dumuzi's return and discusses it in Chapter 2, section C.

Her synthesis identifies the three Mari records as:
- A.1146 — death and return;
- A.4540 — burial;
- MARI 5 (1987) 14 — return.

The same synthesis concludes more cautiously that:
- A.4540 supports a summer burial rite;
- MARI 5 (1987) 14 may support a winter return-day ritual.

During this pass, however, the original publication identity, edition, and exact line-level wording for MARI 5 (1987) 14 were not independently reconstructed from an original publication.

Therefore:

MARI5_1987_14_CURRENT_STATUS =
CURRENT_SCHOLARLY_SYNTHESIS_ONLY.

This source must not inherit A.1146 or A.4540's stronger provenance labels.

## 8. Calendar context is real but not enough to repair the weak source

Mari used a local calendar in which Bêlet-bîrî was month X.

Current Mari calendar scholarship documents:
- month IV: Abum;
- month X: Bêlet-bîrî.

Other Mari records show movement of a Dumuzi statue into the temple of Bêlet-ekallim during Bêlet-bîrî.

This contextual evidence can make a winter return interpretation historically interesting.

But:

CALENDAR_CONTEXT
!=
DIRECT_READBACK_OF_MARI_5_1987_14.

The unresolved source itself remains unresolved.

## 9. Implication for the Dumuzid → Baal contact-field claim

PR #48's broad contact-field conclusion survives, but with narrower internal weighting.

### A.1146

Best evidence for:
- circulation of a Dumuzi death/return idea in an Amorite/Yaminite Mari-connected social setting.

Evidence ceiling:
- publication identity secure;
- exact famous passage reconstruction-dependent;
- spring/statue/seasonal details secondary.

### A.4540

Best evidence for:
- Dumuzi burial cult expenditure / administrative rite.

Evidence ceiling:
- line 4 burial reading strongly controlled;
- no return claim from line 4 alone.

### MARI 5 (1987) 14

Best evidence for:
- candidate independent Mari return-ritual evidence according to current scholarship.

Evidence ceiling:
- secondary synthesis until original edition is recovered.

Thus:

MARI_CONTACT_FIELD = RETAINED

but:

THREE_MARI_DOCUMENTS_ALL_DIRECTLY_VERIFY_DEATH_AND_RETURN = REJECTED.

## 10. Transmission consequence

The source repair makes the transmission test more conservative, not less useful.

The strongest Mari proposition is now:

At least one Old Babylonian Mari-connected letter appears to invoke Dumuzi's death and recurrent return, while a separate administrative text directly attests a Dumuzi burial rite; a third return-related administrative record is reported by current scholarship but remains below original-edition control in V1.

This supports:
- a nontrivial regional Dumuzi death/burial/return field.

It does not establish:
- a single unified ritual;
- a direct Mari → Ugarit carrier chain;
- a Mesopotamian origin for Baal's death/return cycle.

## 11. Current disposition

MARI_DUMUZI_SOURCE_VERIFICATION_V1 =
PASS_WITH_ASYMMETRIC_SOURCE_CEILINGS

A.1146:
PUBLICATION_PROVENANCE_CONFIRMED /
DUMUZI_PASSAGE_RECONSTRUCTION_DEPENDENT.

A.4540:
PUBLICATION_PROVENANCE_CONFIRMED /
BURIAL_LINE_LEXICALLY_CONTROLLED.

MARI 5 (1987) 14:
CURRENT_SYNTHESIS_ONLY /
ORIGINAL_EDITION_RECOVERY_PENDING.

Next frontier:
- identify the original edition and line text of MARI 5 (1987) 14;
- recover A.1146 line 39–44 directly from ARCHIBAB/Marello if technically accessible;
- compare A.1146's Akkadian verbs for killing/return against Baal's Ugaritic death/revival language only after independent lexical reconstruction.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
