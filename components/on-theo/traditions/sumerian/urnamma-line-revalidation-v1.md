# The Death of Ur-Namma — Line Revalidation V1

Status: RESEARCH_AUDIT / LINE_AND_SEMANTIC_REVALIDATION / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #42
- predecessor head: 9ca2b40378a7ae22e3f10f392cb26cd62be1b9c8
- branch: research/sumerian-urnamma-line-revalidation-v1-20260918
- composition: c.2.4.1.1 / CDLI Q000386 / P469688

## Purpose

This pass revalidates the strongest lexical claims in *The Death of Ur-Namma* against the current CDLI composite.

The current artifact:
- is Old Babylonian;
- identifies 11 witnesses from Nippur, Susa, and an uncertain provenience;
- has a current transliteration revision approved 2026-08-18;
- exposes the full composite transliteration and translation.

The score endpoint was not readable in this runtime during this pass, so no witness-alignment claim is made.

Core control:

CURRENT_COMPOSITE_CONFIRMATION != WITNESS_ALIGNED_CONFIRMATION

## 1. Arali is explicit and separate from kur

Current CDLI line 62:

`a-ra-li ki sag-ki kalam-ma-sze3`

Translation:
"To Arali, the pre-eminent place of the Land,"

The same composite later preserves:
- line 127: `... dumu a-ra-li-ra`;
- a later variant segment: `... dumu? a-ra-li-ta`.

Disposition:
`CURRENT_COMPOSITE_CONFIRMED`.

Arali is therefore a direct source-form in the current composite, not merely an English harmonization.

## 2. kur polysemy is demonstrated inside one current composite

### Line 65 — foreign/unknown land use

Current CDLI:

`dilmun{ki}-gin7 kur ki nu-zu-na ...`

Translation:
"their boat ... was sunk in a land as foreign to them as Dilmun."

Here `kur` participates in a geographic/foreign-land expression.

Disposition:
`CURRENT_COMPOSITE_CONFIRMED_GEOGRAPHIC`.

### Line 73 — death-realm journey

Current CDLI:

`kaskal kur-ra ...`

Translation:
"The journey to the nether world is a desolate route."

Disposition:
`CURRENT_COMPOSITE_CONFIRMED_DEATH_REALM`.

The lexical result is direct:

`KUR_LINE65 != KUR_LINE73_IN_LOCAL_ENGLISH_SENSE`

while:

`NORMALIZED_LEXEME = KUR` for both.

This is one of the strongest internal falsifications of a global `kur = underworld` mapping.

## 3. kur as institutional death-realm vocabulary

The same current composite continues:

- line 76: seven chief porters of `kur`;
- lines 79-80: tumult in `kur`;
- line 83: food and water of `kur`;
- line 84: `garza kur-ra-ke4`;
- lines 85-86: `nidba kur-ra-ke4`;
- line 90: Nergal as `Enlil kur-ra`;
- line 95: Gilgameš as `lugal kur-ra-ke4`;
- line 99: `me kur-ra`;
- lines 132-133: offerings of `kur`;
- line 136: great dais of `kur`;
- line 137: dwelling place in `kur`;
- line 144: judgments of `kur`.

This is not one isolated metaphor. It is a dense institutional semantic field inside the composition.

Disposition:
`CURRENT_COMPOSITE_REPEATED_DOMAIN_CONFIRMED`.

## 4. me kur and garza kur remain separate constructions

Current composite:
- line 84: `garza kur-ra-ke4`;
- line 99: `me kur-ra`.

These are different constructions.

The project therefore preserves:
- `me kur` as one semantic/lexical construction;
- `garza kur` as another;
- shared `kur` domain does not make them synonyms.

Control:

`ME_KUR != GARZA_KUR`.

## 5. Royal offices and named authorities

Current composite explicitly preserves:
- line 90: Nergal as `Enlil kur-ra`;
- line 95: Gilgameš as `lugal kur-ra-ke4`;
- later segment: Gilgameš again as king of `kur`;
- line 136: a great dais of `kur`;
- line 144 / variant 72: judgments of `kur`.

This supports a literary representation of an organized postmortem domain with differentiated offices and adjudicative functions.

It remains a literary model, not an archaeological report of actual postmortem institutions.

## 6. Version / witness inventory control

CDLI P469688 currently lists 11 witnesses:
- Nippur: multiple witnesses;
- Susa: multiple witnesses;
- uncertain provenience: one witness.

The composite also contains distinct marked sections/versions, including a Nibru version and later segment material.

Because the score was unavailable in this runtime:
- do not infer which exact witness supports each line;
- do not call any line witness-aligned;
- preserve composite-level status only.

## 7. Freshness value

The current CDLI artifact shows transliteration revisions through 2026, including an approved transliteration update on 2026-08-18.

That makes the current composite a fresher digital readback surface than the older ETCSL interface.

It does NOT automatically make CDLI a new independent critical edition replacing Flückiger-Hawker 1999.

Project status:

`CDLI_Q000386 = CURRENT_DIGITAL_COMPOSITE_READBACK`

`FLUCKIGER_HAWKER_1999 = SCORE_EDITION_PROVENANCE_CONTROL`

These roles are complementary.

## 8. Current disposition

`URNAMMA_LINE_REVALIDATION_V1 = PARTIAL_PASS_WITH_INTERNAL_POLYSEMY_CONFIRMED`

Current-composite confirmed:
- Arali at line 62 and later references;
- geographic/foreign-land `kur` at line 65;
- death-realm `kur` beginning at line 73;
- repeated institutional `kur` vocabulary;
- `garza kur`;
- `me kur`;
- Gilgameš and Nergal death-realm titles;
- `kur` dwelling/judgment language.

Not upgraded:
- witness-specific line support, because score readback was unavailable.

Main semantic result:

The same current composition directly demonstrates that `kur` changes local sense by context. Translation-level "underworld" therefore cannot be treated as the lexeme's universal meaning.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
