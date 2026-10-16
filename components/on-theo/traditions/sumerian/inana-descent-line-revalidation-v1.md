# Inana's Descent — Line Revalidation V1

Status: RESEARCH_AUDIT / LINE_LEVEL_REVALIDATION / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #40
- predecessor head: e1fbd46e151d65ac786257b268a28237b8e66d77
- branch: research/sumerian-inana-line-revalidation-v1-20260918
- composition: c.1.4.1 / CDLI Q000343

## Purpose

This pass applies the witness-sensitive method established in PR #40 to *Inana's Descent to the Netherworld*.

It tests whether the existing composition-level semantic model survives the current CDLI score:
- `kur` as broad death-realm language;
- `Ganzer` as a more specific palace/gateway locus;
- repeated `me kur-ra(-ke4)` and `garza kur-ra(-ke4)` formulae at the seven gates.

Primary controls:
- CDLI Q000343 current composite/score: 58 witnesses, 44 aligned.
- ETCSL c.1.4.1 transliteration/translation/glossing.
- Pascal Attinger, *La descente d'Innana dans le monde infernal (1.4.1)*, published 2019, updated 2021.

Attinger remains a later philological crosscheck. This runtime has verified the open metadata/currentness of that work, but this pass does not claim full direct line-by-line collation against Attinger's PDF.

## 1. Descent formula: kur at lines 4-13

CDLI's current score preserves the repeated descent formula with `kur-ra` across multiple aligned Nippur witnesses.

Examples:
- line 4 composite: `... kur-ra ba-e-a-e11`
  - P268937 preserves `kur-ra`;
  - P267276 preserves `kur-ra ba-e-a-e11`;
- line 5 repeats the same formula with aligned witness support;
- lines 6-12 continue the pattern;
- line 13 and city-expansion variants continue `kur(-ra) ... e11`.

Disposition:

`WITNESS_ALIGNED_REPEATED_FORMULA_CONFIRMED`

This materially strengthens the claim that `kur` is not an isolated translator choice in the descent opening. It is a repeated source lexeme across the composite and several physical witnesses.

Control:

`KUR_IN_C141_DESCENT = LOCAL_DEATH_REALM_USE`

does not imply:

`KUR_EVERYWHERE = UNDERWORLD`.

## 2. Ganzer and kur at the entry sequence

### Line 73 — palace Ganzer

CDLI composite:
`dInanna e2-gal ganzer-sze3 um-ma-te`

Aligned Nippur witness P345344:
`dInanna e2-gal ganzerx(|KUR.ZA.KUR|)-sze3 um-ma-[...]`

Disposition:
`WITNESS_ALIGNED_CONFIRMED`.

The palace/Ganzer expression is therefore not dependent only on the ETCSL English translation.

### Lines 74-75 — door/gate of kur

CDLI composite:
- line 74: `gesz-ig kur-ra-ka ...`
- line 75: `abul kur-ra-ka ...`

P345344 preserves the kur construction in line 74; P345597 preserves kur in the line 74/75 sequence.

Disposition:
`WITNESS_ALIGNED_CONFIRMED`.

### Semantic result

The same local episode distinguishes:
- palace Ganzer;
- door/gate of kur.

This preserves the PR #38 model:

`GANZER != KUR`

while allowing:

`GANZER ∈ SAME_DEATH_REALM_SEMANTIC_DOMAIN_AS KUR`.

## 3. Neti, seven gates, and palace Ganzer

### Line 117

Composite:
`dNeti i3-du8 gal kur-ra-gu10`

Nippur witness P356898 preserves:
`... i3-du8 gal kur-ra-mu`

Disposition:
`WITNESS_ALIGNED_CONFIRMED`.

Neti's office is explicitly expressed with `kur`.

### Line 119

Composite:
`abul kur-ra 7-bi ...`

Nippur witnesses P274957 and P356898 preserve the seven-gate / kur expression, though with local variation/damage.

Disposition:
`WITNESS_ALIGNED_CONFIRMED_WITH_VARIATION`.

### Line 120

Composite:
`e2-gal ganzer dili-bi ...`

Nippur witness P356898 preserves:
`e2-gal2 ganzer dili-bi ...`

Disposition:
`WITNESS_ALIGNED_CONFIRMED`.

The immediate sequence itself therefore alternates:
- seven gates of kur;
- individual doors of palace Ganzer.

This is stronger than a dictionary-level distinction.

## 4. Line 126 — high-value co-domain witness

The current CDLI score preserves the later repeated palace-Ganzer instruction.

Of special value is witness P266238, which preserves a form combining the Ganzer palace sequence with `igi kur-ra-ka` in the same local textual environment.

Disposition:
`WITNESS_LEVEL_CODOMAIN_CONFIRMATION`.

This supports:
- Ganzer and kur are semantically related in the composition;
- they remain lexically distinct;
- English "underworld" cannot substitute for source-lexeme identity.

## 5. The repeated me kur-ra formula

The seven-gate sequence repeatedly answers Inana's question with a formula containing:
`me kur-ra(-ke4)`
followed by a `garza kur-ra(-ke4)` instruction.

### Line 132

Composite:
`si-a dInanna me kur-ra-ke4 szu al-du7-du7`

Aligned witnesses:
- P266238 (Nippur): preserves `me kur-ra-ke4`;
- P346462 (Ur): preserves `me kur-ra-ke4`;
- P469280 (Sippar-Amnanum): preserves `me kur-ra-ke4`.

Disposition:
`MULTI_WITNESS_ALIGNED_CONFIRMED`.

### Line 137

Composite repeats:
`me kur-ra-ke4`.

Aligned evidence includes:
- P356898 (Nippur): preserves `me kur-ra-ke4`;
- P266238 preserves a local case/ending variant around `kur-ra`.

Disposition:
`WITNESS_ALIGNED_CONFIRMED_WITH_MINOR_VARIATION`.

### Line 162

Composite:
`si-a dInanna me kur-ra-ke4 szu al-du7-du7`

Aligned witnesses:
- P269767 (Nippur): preserves `me kur-ra-ke4`;
- P274244 (Sippar-Amnanum): preserves `me kur-ra`;
- P346093 (Ur): preserves `me kur-ra-ke4`;
- P346094 (Ur): preserves the full formula `me kur-ra-ke4 szu al-du7-du7`.

Disposition:
`MULTI_WITNESS_ALIGNED_CONFIRMED`.

This is the strongest V1 witness-level support for the formula.

## 6. garza kur-ra is distinct evidence from me kur-ra

The paired response formula also uses `garza kur-ra(-ke4)`, translated by ETCSL as the rites/procedure of the underworld.

Examples:
- line 133;
- line 138;
- line 158;
- line 163.

The current CDLI score has aligned Nippur, Ur, and Sippar-Amnanum support at multiple repetitions.

Project consequence:

Do not flatten:
- `me kur-ra`
- `garza kur-ra`

into one English abstraction.

They are different lexical constructions sharing the `kur` domain.

## 7. Translation-loss confirmation

ETCSL glossing is especially useful because it exposes the translation layer.

For example:
- line 94 lexically glosses `kur` as "(mountain) land" while paragraph translation gives Neti as doorman of the "underworld";
- line 100 similarly gives `abul kur-ra-ka` while English gives "gate of the underworld";
- lines 137 and 162 show `me kur-ra-ke4` while English gives "divine power of the underworld."

This is not an ETCSL error. It is exactly the translation-compression problem On-Theo must preserve.

Control:

`TRANSLATION_SURFACE = UNDERWORLD`

does not erase:

`SOURCE_LEXEME = KUR`.

## 8. Current evidence states

Recommended line states:

- `WITNESS_ALIGNED_REPEATED_FORMULA_CONFIRMED`
- `WITNESS_ALIGNED_CONFIRMED`
- `WITNESS_ALIGNED_CONFIRMED_WITH_VARIATION`
- `MULTI_WITNESS_ALIGNED_CONFIRMED`
- `LATER_PHILOLOGICAL_CROSSCHECK_PENDING`

Attinger status:
`LATER_PHILOLOGICAL_CROSSCHECK_PENDING`.

No stronger direct Attinger line claim is made in this pass.

## 9. Current disposition

`INANA_DESCENT_LINE_REVALIDATION_V1 = PARTIAL_PASS_WITH_STRONG_WITNESS_ALIGNMENT`

Strongly revalidated:
- repeated opening `kur` descent formula;
- Ganzer palace at line 73;
- kur door/gate at lines 74-75;
- Neti's `kur` office at line 117;
- seven gates of `kur` at line 119;
- palace Ganzer at line 120;
- Ganzer/kur co-domain evidence around line 126;
- repeated `me kur-ra(-ke4)` at lines 132, 137, 162;
- repeated `garza kur-ra(-ke4)` formulae.

Still pending:
- direct line-by-line Attinger 2019/2021 crosscheck;
- full critical-edition comparison beyond current CDLI/ETCSL surfaces;
- manuscript-specific semantic treatment for all seven gate repetitions;
- extension to later Dumuzi substitution material.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
