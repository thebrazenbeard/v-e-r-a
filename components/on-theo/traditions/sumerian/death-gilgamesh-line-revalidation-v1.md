# The Death of Gilgameš — Line Revalidation V1

Status: RESEARCH_AUDIT / VERSION_AND_LINE_PROVENANCE_CONTROL / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #41
- predecessor head: a60d4ba8af209ddef7e6f42ecf01cade64e8a87a
- branch: research/sumerian-death-gilgamesh-line-revalidation-v1-20260918
- ETCSL composition: c.1.8.1.3
- CDLI composite: Q000363 / P469669

## Purpose

This pass applies line-level currentness control to *The Death of Gilgameš*.

Unlike the Inana and Gilgameš/Enkidu score surfaces, CDLI Q000363 currently reports:
- 12 witnesses;
- 0 witnesses aligned to the composite.

That creates a hard evidence ceiling.

Current CDLI can confirm what its composite transliteration reads.
It cannot, in its present score state, independently upgrade those readings to aligned-witness confirmation.

Core control:

CURRENT_COMPOSITE_CONFIRMATION != WITNESS_ALIGNED_CONFIRMATION

A second control is equally important:

ETCSL c.1.8.1.3 contains both a Nippur version and a Me-Turan version.
CDLI Q000363 is labeled "Death of Gilgamesh: Nippur Version" even though its witness set includes material from Nippur and Me-Turan.

Version-specific claims must therefore preserve where a line comes from instead of treating the ETCSL composite presentation as one undifferentiated textual state.

## 1. Current CDLI evidence ceiling

CDLI Q000363:
- 12 witnesses;
- 0 aligned to the composite text;
- score explicitly states that none of the witnesses have yet been aligned.

Disposition:

Q000363 = CURRENT_COMPOSITE_ONLY_FOR_LINE_READBACK

No line in this pass is labeled WITNESS_ALIGNED_CONFIRMED.

This is a meaningful negative capability result, not a failure of the research.

## 2. Nippur composite: kur and gidim

### Dark place of kur

CDLI Q000363 line 88' preserves:

`kur-ra ki ku10-ku10-ka ...`

This corresponds to a death-realm context in the Nippur textual sequence.

Disposition:

`CURRENT_COMPOSITE_CONFIRMED`

not:

`WITNESS_ALIGNED_CONFIRMED`.

### Ghost festival

Line 93' preserves:

`... ezen gidim-ma-ke4-ne`

The composition therefore has direct current-composite support for a festival/occasion involving `gidim`.

Disposition:
`CURRENT_COMPOSITE_CONFIRMED`.

This is stronger than claiming gidim merely from an English translation, but weaker than physical-witness-aligned readback.

### Royal office / ghost sequence

The current Nippur composite preserves:

- line 145': `nam-szagina kur-ra [...]`
- line 146': `za-e gidim-zu [...]`

These lines place royal/governor-of-kur language and a `gidim` expression in the same local damaged sequence.

Disposition:

`CURRENT_COMPOSITE_CONFIRMED_WITH_DAMAGE`

Important limitation:
The current CDLI Nippur composite is fragmentary here. It does not, by itself, support every syntactic detail of a smooth reconstructed translation.

Therefore the earlier project proposition:

"Gilgameš as gidim becomes governor of kur"

should retain its support from ETCSL/Cavigneaux-al-Rawi reconstruction, while CDLI Q000363 supplies only partial current-composite corroboration at this locus.

It must not be upgraded to witness-level confirmation from CDLI.

## 3. ETCSL Me-Turan version: stronger reconstruction of the royal ghost office

ETCSL's Me-Turan version preserves a much fuller passage:

- line 38: Gilgameš in a `gidim` expression among/below the dead;
- line 39: `cagina kur-ra ... palil gidim ...`;
- parallel lines 131-132 repeat the same structure.

This is the source of the stronger composition-level reconstruction that Gilgameš is represented as a distinguished ghost with office in kur.

Classification:
- textual reconstruction/access: PRIMARY_TEXT through the ETCSL/Cavigneaux-al-Rawi edition lineage;
- current CDLI independent witness-alignment: NOT AVAILABLE in Q000363.

Control:

ETCSL_ME_TURAN_RECONSTRUCTION != CDLI_WITNESS_ALIGNED_READBACK

## 4. Arali is version-specific in the checked surfaces

ETCSL's Me-Turan version explicitly preserves at line 166:

`iri gal a-ra-li ...`

translated/reconstructed as the Great City Arali.

A search of the current CDLI Q000363 Nippur composite finds no `a-ra-li` string.

This does not mean Arali is absent from every witness assigned to Q000363; the witnesses are not aligned/transliterated on the score surface.

It means:

ARALI_CLAIM_CURRENTLY = ETCSL_ME_TURAN_VERSION_CONTROL

not:

ARALI_CLAIM = CURRENT_CDLI_NIPPUR_COMPOSITE_CONFIRMATION

This repairs a provenance flattening risk in the prior composition map.

## 5. Nippur and Me-Turan must remain separate textual states

Current source surfaces show:
- Nippur version: fragmented composite with kur/gidim material;
- Me-Turan version: fuller royal-afterlife passage and explicit Arali line.

The project must preserve:

COMPOSITION_IDENTITY
!=
VERSION_IDENTITY
!=
PHYSICAL_WITNESS_IDENTITY

For this composition, a future occurrence registry should add a version field at minimum:
- NIPPUR_VERSION
- ME_TURAN_VERSION
- CROSS_VERSION_RECONSTRUCTION

## 6. Cavigneaux / al-Rawi 2000 remains the edition authority boundary

The current ETCSL bibliography uses Cavigneaux and al-Rawi 2000, *Gilgameš et la Mort: Textes de Tell Haddad VI*, which publishes major Me-Turan material and republishes Nippur fragments.

The current CDLI witness list explicitly includes:
- Nippur witnesses;
- Me-Turan witnesses published in CM 19.

Therefore the correct V1 hierarchy is:

CAVIGNEAUX_AL_RAWI_2000 = MAJOR_EDITION_CONTROL
ETCSL = SEARCHABLE_TEXTUAL_ACCESS/COMPOSITE_PRESENTATION
CDLI_Q000363 = CURRENT_DIGITAL_COMPOSITE_AND_WITNESS_INVENTORY
CDLI_Q000363_ALIGNMENT = CURRENTLY_ZERO

No surface alone replaces the others.

## 7. Evidence-state repair

Recommended statuses for Death of Gilgameš occurrences:

- CURRENT_COMPOSITE_CONFIRMED
- CURRENT_COMPOSITE_CONFIRMED_WITH_DAMAGE
- ETCSL_ME_TURAN_VERSION_CONFIRMED
- ETCSL_NIPPUR_VERSION_CONFIRMED
- MAJOR_EDITION_LINEAGE_CONFIRMED
- WITNESS_ALIGNMENT_PENDING
- VERSION_SPECIFIC_PROVENANCE_REQUIRED

Immediate changes to prior V1 claims:

### `kur-ra ki ku10-ku10`
Status:
CURRENT_COMPOSITE_CONFIRMED / NIPPUR_VERSION

### `ezen gidim-ma-ke4-ne`
Status:
CURRENT_COMPOSITE_CONFIRMED / NIPPUR_VERSION

### royal `nam-szagina kur` + `gidim`
Status:
CURRENT_COMPOSITE_CONFIRMED_WITH_DAMAGE / NIPPUR_VERSION
plus:
ETCSL_ME_TURAN_VERSION_CONFIRMED for the fuller syntax.

### Arali
Status:
ETCSL_ME_TURAN_VERSION_CONFIRMED
WITNESS_ALIGNMENT_PENDING

## 8. Current disposition

`DEATH_GILGAMESH_LINE_REVALIDATION_V1 = PARTIAL_PASS_WITH_VERSION_SPLIT_AND_ALIGNMENT_CEILING`

Confirmed:
- current Nippur composite contains death-realm `kur`;
- current Nippur composite contains `gidim`;
- current Nippur composite contains damaged royal-office/ghost wording;
- ETCSL Me-Turan version preserves the fuller governor-of-kur / gidim passage;
- ETCSL Me-Turan version explicitly preserves Arali.

Not confirmed at witness-alignment level:
- any Q000363 composite line, because current score has zero aligned witnesses.

Required next step for stronger status:
- direct CM 19 score/plates or future CDLI witness alignment;
- occurrence records split by Nippur vs Me-Turan version;
- no version-neutral Arali claim.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
