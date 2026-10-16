# Sumerian Death-Corpus Edition Currentness Audit V1

Status: RESEARCH_AUDIT / EDITION_CURRENTNESS_CONTROL / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #38
- predecessor head: 6a049eb026a8959c860c17430e666f496adea369
- branch: research/sumerian-death-edition-currentness-v1-20260918

## Purpose

The composition-level lexical map in PR #38 uses ETCSL because it provides searchable composite transliteration, translation, and glossing.

ETCSL is an access surface, not an automatic claim that its text is the newest full philological edition for every composition.

This audit asks a narrower question for each of the four mapped death texts:

1. Is there a later full edition or re-edition than the ETCSL composition?
2. Is there a later philological translation/control that should be consulted even if it is not a full new manuscript edition?
3. Does current scholarship expose new manuscripts or textual reconstruction that can make ETCSL-only line mapping stale?
4. What evidence ceiling should the PR #38 occurrence map carry until line-level revalidation is completed?

Core control:

ETCSL_SEARCHABLE != LATEST_CRITICAL_EDITION

and:

LATER_TRANSLATION != NEW_CRITICAL_EDITION

## 1. Gilgamesh, Enkidu and the Netherworld — c.1.8.1.4

Disposition:

NEW_FULL_EDITION_IDENTIFIED / PR38_REVALIDATION_REQUIRED

Alhena Gadotti's 2014 monograph, *Gilgamesh, Enkidu, and the Netherworld and the Sumerian Gilgamesh Cycle*, explicitly presents a new edition of the composition.

Publisher description states that:
- the previous full publication was Aaron Shaffer's 1963 dissertation;
- several additional manuscripts had come to light;
- the new evidence prompted both a new edition and a re-examination of the composition.

The volume contains:
- manuscript discussion;
- translation;
- eclectic text;
- textual matrix;
- commentary;
- plates.

Source:
- Alhena Gadotti, *Gilgamesh, Enkidu, and the Netherworld and the Sumerian Gilgamesh Cycle* (De Gruyter, 2014)
  https://doi.org/10.1515/9781614515456

Project consequence:

ETCSL c.1.8.1.4 remains a useful searchable access surface, but it is not sufficient as the terminal philological control for this composition.

The PR #38 occurrence map should therefore carry:

GEN_OCCURRENCES_ETCSL = PROVISIONAL_UNTIL_GADOTTI_2014_LINE_REVALIDATION

This does not mean the mapped kur / Ganzer / gidim distinctions are presently disproved.

It means:
- exact line numbering;
- variant readings;
- manuscript distribution;
- reconstruction of damaged lines;
- and local translation

must be checked against Gadotti before those occurrence records can be promoted as edition-current.

## 2. Inana's Descent to the Netherworld — c.1.4.1

Disposition:

LATER_PHILOLOGICAL_CONTROL_IDENTIFIED / NOT_CLASSIFIED_AS_NEW_FULL_CRITICAL_EDITION

ETCSL's own bibliography relies heavily on earlier publications including:
- William Sladek's 1974 dissertation;
- Bendt Alster's 1996 work;
- earlier Kramer and other textual work.

Pascal Attinger published a later dedicated translation/philological study:
- *La descente d'Innana dans le monde infernal (1.4.1)*
- originally placed online in 2019;
- Zenodo V2 states it was updated in 2021.

Source:
- Pascal Attinger, *La descente d'Innana dans le monde infernal (1.4.1)*
  https://doi.org/10.5281/zenodo.4603728

The current pass does not establish that Attinger 2019/2021 is a new full critical edition equivalent in apparatus scope to Gadotti 2014.

Therefore the correct project label is:

LATER_PHILOLOGICAL_CONTROL

not:

NEW_CRITICAL_EDITION

Additional currentness signal:
CDLI's composite for Inana's Descent explicitly references both ETCSL and Attinger in its publication history/access layer.

Source:
- CDLI Literary 000343 (Inanna's Descent) composite
  https://cdli.earth/search?atf_transliteration=%7Bd%7Deresz-ki-gal&layout=full&limit=25

Project consequence:

INANA_OCCURRENCES_ETCSL = SEARCHABLE_BASE_WITH_ATTINGER_CROSSCHECK_REQUIRED

Especially high-value targets for revalidation:
- kur at the descent/gate passages;
- Ganzer as palace/place-name;
- repeated me kur-ra / jarza kur-ra passages;
- the final Dumuzi sequence, where textual interpretation has a substantial scholarly history.

## 3. The Death of Gilgamesh — c.1.8.1.3

Disposition:

ETCSL_ALREADY_BUILT_ON_MAJOR_2000_REEDITION / NO_LATER_FULL_EDITION_IDENTIFIED_IN_TARGETED_PASS

ETCSL's bibliography directly uses:

Antoine Cavigneaux and Farouk N. H. al-Rawi,
*Gilgameš et la Mort. Textes de Tell Haddad VI, avec un appendice sur les textes funéraires sumériens*,
Cuneiform Monographs 19 (2000).

That publication is itself a major re-edition:
- it publishes important new fragments from Meturan/Tell Haddad;
- republishes Nippur fragments;
- includes translation and commentary.

Source:
- Cavigneaux / al-Rawi, *Gilgameš et la Mort* (2000)
  https://books.google.com/books/about/Gilgame%C5%A1_et_la_mort.html?id=_60axEdEQn8C

A 2025 University of Hamburg research/public-outreach page still identifies the Cavigneaux/al-Rawi edition as the relevant cuneiform edition for the Sumerian death text.

Source:
- Centre for the Study of Manuscript Cultures, "The funeral of Gilgamesh, the deified hero" (2025)
  https://www.csmc.uni-hamburg.de/publications/mesopotamia/2025-04-25.html

This targeted pass did not identify a later full edition superseding Cavigneaux/al-Rawi 2000.

That is a bounded search result, not proof that no later specialized article has corrected individual readings.

Project consequence:

DEATH_GILGAMESH_ETCSL = SUBSTANTIALLY_GROUNDED_IN_2000_REEDITION

but:

NO_LATER_FULL_EDITION_FOUND != NO_LATER_PHILOLOGICAL_CORRECTIONS_EXIST

The PR #38 gidim / kur / Arali occurrence map remains usable at V1 research level, with consequential lines still requiring direct Cavigneaux/al-Rawi score or later line-specific scholarship when promoted.

## 4. The Death of Ur-Namma — c.2.4.1.1

Disposition:

ETCSL_BUILT_ON_1999_SCORE_EDITION / NO_LATER_FULL_EDITION_IDENTIFIED_IN_TARGETED_PASS

ETCSL's bibliography uses Esther Flückiger-Hawker's 1999 monograph:
*Urnamma of Ur in Sumerian Literary Tradition*.

For *The Death of Ur-Namma*, ETCSL specifically lists pages 93-182 and describes the work as containing:
- score transliteration;
- translation;
- photograph;
- commentary;
- handcopy;
- composite text.

Sources:
- ETCSL bibliography for Ur-Namma A
  https://etcsl.orinst.ox.ac.uk/section2/b2411.htm
- bibliographic control for Flückiger-Hawker 1999
  https://vergil.uni-tuebingen.de/keibi/Record/KEI00013241

CDLI currently exposes a digital Ur-Namma A composite that identifies itself with ETCSL 2.4.1.1 and records a 2014 composite update.

Source:
- CDLI Literary 000386 (Ur-Namma A)
  https://www.cdli.earth/inscriptions/2231690

The CDLI composite is valuable as a current digital access/readback surface.

It is NOT treated here as an independent new critical edition merely because its digital record was updated later.

This targeted search did not identify a later complete score edition superseding Flückiger-Hawker 1999.

Project consequence:

UR_NAMMA_ETCSL = BASED_ON_STRONG_1999_SCORE_CONTROL

and:

CDLI_2014_COMPOSITE != AUTOMATIC_NEW_CRITICAL_EDITION

The PR #38 internal-polysemy result for kur remains high-value because it is visible inside the composition itself, but exact readings should still be bound to the score/manuscript tradition before canonical semantic claims are made.

## 5. Edition-status matrix

| Composition | ETCSL relationship | Later control found | Current project status |
| --- | --- | --- | --- |
| Inana's Descent | searchable composite relying on older textual work | Attinger 2019/2021 philological translation/control | CROSSCHECK_REQUIRED |
| Gilgamesh, Enkidu and Netherworld | searchable composite predating a major later edition | Gadotti 2014 new edition using additional manuscripts | FULL_REVALIDATION_REQUIRED |
| Death of Gilgamesh | ETCSL already uses Cavigneaux/al-Rawi 2000 major re-edition | no later full edition identified in targeted pass | LINE_SPECIFIC_RECHECK_WHEN_CONSEQUENTIAL |
| Death of Ur-Namma | ETCSL uses Flückiger-Hawker 1999 score edition | CDLI updated digital composite; no later full score identified | LINE_SPECIFIC_RECHECK_WHEN_CONSEQUENTIAL |

## 6. Consequence for PR #38 evidence labels

The occurrence map must not have one undifferentiated "verified" status.

Recommended occurrence provenance states:

- ETCSL_DIRECT
- ETCSL_PLUS_LEXICON
- LATER_TRANSLATION_CROSSCHECKED
- CURRENT_FULL_EDITION_CROSSCHECKED
- MANUSCRIPT_VARIANT_CONTROLLED
- ACCESS_SURFACE_NEGATIVE_ONLY

Immediate migration rule:

All c.1.8.1.4 occurrences currently derived from ETCSL remain:
ETCSL_PLUS_LEXICON / CURRENT_FULL_EDITION_CROSSCHECK_PENDING

until Gadotti 2014 is checked line-by-line.

Inana c.1.4.1:
ETCSL_PLUS_LEXICON / ATTINGER_CROSSCHECK_PENDING

Death of Gilgamesh c.1.8.1.3:
ETCSL_DIRECT_WITH_2000_EDITION_LINEAGE / LINE_SPECIFIC_SCORE_CHECK_PENDING

Death of Ur-Namma c.2.4.1.1:
ETCSL_DIRECT_WITH_1999_SCORE_LINEAGE / LINE_SPECIFIC_SCORE_CHECK_PENDING

## 7. Negative-search correction

The PR #38 statement that kurnugi was "not found" remains only:

ACCESS_SURFACE_NEGATIVE_ONLY

A newer edition can:
- normalize spelling differently;
- segment compounds differently;
- restore a damaged lexeme differently;
- add a newly published manuscript.

Therefore absence from ETCSL search must never be promoted to historical absence without edition- and witness-level review.

## 8. Current disposition

SUMERIAN_DEATH_CORPUS_EDITION_CURRENTNESS_V1 =
PASS_WITH_ONE_MAJOR_POST_ETCSL_REEDITION_AND_MULTIPLE_RECHECK_REQUIREMENTS

Most important result:

GADOTTI_2014 creates a real currentness dependency for c.1.8.1.4.

The PR #38 composition map remains useful research state, but the Gilgamesh/Enkidu/Netherworld occurrence set should not be promoted as edition-current until reconciled against the 2014 edition.

For the other three compositions:
- later controls exist;
- ETCSL's textual ancestry is explicitly documented;
- no claim is made that this targeted web pass exhausts every later article, collation, fragment publication, or correction.

No result here modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
