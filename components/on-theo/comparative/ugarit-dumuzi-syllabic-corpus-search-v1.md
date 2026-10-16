# Ugarit Dumuzi Syllabic-Corpus Search V1

Status: RESEARCH_PACKET / BOUNDED_CORPUS_SEARCH / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #71
- predecessor head: 89920c8e281b97a2806708a21c16e0115f884f64
- branch: research/ugarit-dumuzi-syllabic-corpus-search-v1-20260918

## Purpose

The transmission ladder now treats Dumuzi-specific scholastic exposure at Ugarit as a positive gate because RS 20.123+ / P332950 directly preserves Dumuzi.

This pass asks whether the accessible Ugarit syllabic/cuneiform corpora preserve a second controlled Dumuzi occurrence.

## Search surfaces

Targeted searches covered:
- ORACC AEMW/Ugarit transliterated Middle Babylonian material;
- ORACC DCCLT Ugarit lexical texts and Weidner-list source surfaces;
- CDLI-indexed Ugarit/Ras Shamra material;
- Dumuzi spelling variants including DUMU.ZI, dumu-zi, dumu-zid, du-mu-zi and Tammuz;
- Ras Shamra / Ugarit publication-name combinations.

## Result

The only controlled direct Dumuzi divine-name occurrence recovered in this targeted V1 search remains:

RS 20.123+ / Ugaritica 5, 137 / P332950,
reverse ii 7.

That row preserves:
- Mesopotamian Dumuzi;
- Hurrian du-mu-zi;
- lost Ugaritic-equivalent field.

No second Ugarit syllabic tablet with a controlled Dumuzi divine-name occurrence was recovered in this pass.

Recommended status:

UGARIT_DUMUZI_SYLLABIC_CORPUS =
ONE_CONTROLLED_POSITIVE_WITNESS_IN_TARGETED_V1_SEARCH.

This is not:

P332950_IS_HISTORICALLY_THE_ONLY_DUMUZI_TEXT_AT_UGARIT.

## Dadmiš false-positive control

Searches around older Hurrian/Ugaritic scholarship surface Dadmiš/Tadmiš.

Dadmiš must not be counted as a second Dumuzi hit merely because older glossaries discuss the names near one another.

On P332950 itself:
- Dumuzi occurs at reverse ii 7;
- Šuzianna / Tadmiš / Dadmišu occurs separately at column iii 15'.

They are separate lexical rows.

Therefore:

DADMIS_SEARCH_HIT != SECOND_DUMUZI_OCCURRENCE.

This correction matters because broad web searches can collapse neighboring glossary entries or duplicate traditions.

## Month-name route

The search also tested Tammuz/Duʾuzu month-name queries in current Ugarit digital surfaces.

No controlled Ugarit month-name occurrence was recovered that could be used as a separate Dumuzi-specific source in this pass.

Because the month-name indexes were not fully readable through every digital route, this remains only a bounded search non-hit and is not promoted to an absence claim.

## Evidence ceiling

Strong:
- P332950 is a physical Ugarit lexical witness containing Dumuzi.
- its Dumuzi row is independently indexed by current lexical resources.

Bounded negative:
- no second controlled Ugarit syllabic Dumuzi divine-name witness recovered in the targeted accessible corpus.

Not justified:
- no other Dumuzi text ever existed at Ugarit;
- no unpublished fragment contains Dumuzi;
- no damaged or unindexed occurrence exists;
- P332950 was unique in antiquity.

## Effect on the transmission ladder

Gate G05 remains:

DUMUZI-SPECIFIC UGARIT EXPOSURE = PASS.

But its current evidence breadth is narrow:

KNOWN_CONTROLLED_UGARIT_DUMUZI_WITNESSES_IN_V1 = 1.

Gate G08 remains:

DUMUZI DEATH/RETURN NARRATIVE AT UGARIT = NOT ESTABLISHED.

A single lexical witness proves specific scholastic knowledge, not narrative transmission.

## Current disposition

UGARIT_DUMUZI_SYLLABIC_CORPUS_SEARCH_V1 =
P332950_POSITIVE
+
NO_SECOND_CONTROLLED_HIT_IN_TARGETED_SEARCH
+
HISTORICAL_UNIQUENESS_NOT_PROVEN.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
