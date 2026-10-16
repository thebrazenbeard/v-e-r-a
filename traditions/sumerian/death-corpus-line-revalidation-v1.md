# Sumerian Death-Corpus Line Revalidation V1

Status: RESEARCH_AUDIT / LINE_LEVEL_REVALIDATION / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #39
- predecessor head: 74ce2094ad8e45368bd51f8c559046b8b6f2c763
- branch: research/sumerian-death-line-revalidation-v1-20260918

## Purpose

This pass begins the line-level revalidation required by the edition-currentness audit, concentrating on Gilgamesh, Enkidu and the Netherworld (c.1.8.1.4).

It does not claim complete re-edition against Gadotti 2014. Instead it separates:
- exact occurrences directly confirmed by the current CDLI composite and score;
- occurrences confirmed only at composite level;
- nearby philological disputes identified in later collation/commentary;
- records that remain pending full Gadotti 2014 line-by-line control.

Primary digital control:
- CDLI Literary 000364 composite and score, Q000364
  https://cdli.earth/artifacts/469670
  https://cdli.earth/artifacts/composites-score/Q000364

Edition/currentness controls:
- Alhena Gadotti 2014, Gilgamesh, Enkidu, and the Netherworld and the Sumerian Gilgamesh Cycle
  https://doi.org/10.1515/9781614515456
- Pascal Attinger, Bilgameš, Enkidu et le monde infernal, updated 2019
  https://anarkia333data.center/sites/default/files/2019-04/gilgamesh_enkidu_et_le_monde_infernal_attinger.pdf

## 1. Ganzer / kur pair at lines 166-179

### Line 166

CDLI composite:
abul ganzer igi kur-ra-ka dur2 im-ma-ni-in-gar

Aligned Ur witness P346141:
abul-an ganzer igi kur-ra-ke4 dur2 im-ma-ni-in-gar

Disposition:
WITNESS_ALIGNED_CONFIRMED

This directly preserves Ganzer and kur in one line.

The semantic claim that Ganzer and kur participate in one death-realm scene without being identical lexemes therefore survives current score-level readback.

### Lines 174-179

CDLI preserves the explicit alternation:
- line 174: ellag -> kur
- line 175: e-ke4-ma -> Ganzer
- line 178: retrieval from kur
- line 179: retrieval from Ganzer

The aligned Ur witness P346141 preserves the same paired distinction.

Disposition:
WITNESS_ALIGNED_CONFIRMED

This is stronger than a translation-only parallel because the lexical contrast survives in an aligned physical-witness transcription.

## 2. gidim at line 213

CDLI composite:
gidim ba-an-da-ur4-re-esz

English surface:
the spirits felt insulted by him.

Disposition:
CURRENT_COMPOSITE_CONFIRMED / WITNESS_ALIGNMENT_NOT_SHOWN_FOR_THIS_LINE

Important qualification:
Attinger's later collation discussion disputes the reading/classification around lines 192, 214, 229, and 237, criticizing Gadotti's discussion of udug/gidim and preferring kitim in photographed cases.

That dispute does not directly target composite line 213 as numbered in the current CDLI/ETCSL surface.

Therefore:
- OCC-C1814-L213-GIDIM is not downgraded to error;
- it remains composite-confirmed;
- nearby udug/gidim/kitim loci must not be added to the occurrence registry without manuscript-level control.

## 3. gidim and funerary offerings at line 292

CDLI composite:
gidim lu2 ninda sig10-ge5 nu-tuku ...

Aligned Ur witness P346143:
gidim# lu2 ninda si-ge5 nu#-tuku ...

English:
the ghost/spirit of the person who has no funerary offerings.

Disposition:
WITNESS_ALIGNED_CONFIRMED

This supports the existing occurrence record:
OCC-C1814-L292-GIDIM

and the bounded proposition that the literary text associates a gidim with lack of funerary provisioning.

The witness has damaged/uncertain signs elsewhere in the line, but gidim itself is preserved.

## 4. gidim-a-ni at line 303

CDLI composite:
gidim-a-ni nu-gal2 i-bi2-ni an-na ba-e-e11

Aligned Ur witness P346143:
i-bi2-ni an-na ba-a-e11-am3#? gidim-a-ni ki-a nu-ub-dab5

Disposition:
WITNESS_ALIGNED_CONFIRMED_WITH_VARIANT_SYNTAX

Both composite and aligned witness preserve gidim-a-ni.

The word order and continuation differ, so the semantic record should preserve:
- stable lexical occurrence: gidim-a-ni;
- variant local syntax;
- no claim that the composite wording is the only manuscript form.

## 5. Attinger/Gadotti dispute boundary

Attinger explicitly flags lines 192, 214, 229, and 237 in his numbering as problematic for the udug/gidim distinction and criticizes Gadotti 2014:280 on this point.

Project consequence:

DISPUTED_NEARBY_SPIRIT_SIGN != ALL_GIDIM_OCCURRENCES_UNRELIABLE

The correct response is occurrence-level status, not wholesale normalization.

Current V1 states:
- line 213: CURRENT_COMPOSITE_CONFIRMED
- line 292: WITNESS_ALIGNED_CONFIRMED
- line 303: WITNESS_ALIGNED_CONFIRMED_WITH_VARIANT_SYNTAX
- Attinger-disputed loci: QUARANTINED_PENDING_MANUSCRIPT_CONTROL

## 6. Gadotti 2014 dependency remains real

This pass does not remove the Gadotti 2014 dependency.

Google Books/publisher metadata confirms:
- Gadotti provides a new edition;
- additional manuscripts motivated the edition;
- the volume contains an eclectic text, textual matrix, commentary, and plates.

Therefore full edition-current promotion still requires direct control against Gadotti's edition for all c.1.8.1.4 occurrence records.

This line-revalidation pass only upgrades records for which current CDLI score evidence independently supplies stronger readback.

## 7. Evidence-state vocabulary

Recommended states:

- ETCSL_ONLY
- CURRENT_COMPOSITE_CONFIRMED
- WITNESS_ALIGNED_CONFIRMED
- WITNESS_ALIGNED_CONFIRMED_WITH_VARIANT_SYNTAX
- PHILOLOGICALLY_DISPUTED
- FULL_EDITION_RECHECK_PENDING
- ACCESS_SURFACE_NEGATIVE_ONLY

These states are orthogonal to semantic interpretation.

A line can be:
- lexically confirmed,
- syntactically variant,
- and still semantically disputed.

## 8. Current disposition

SUMERIAN_DEATH_LINE_REVALIDATION_V1 =
PARTIAL_PASS_WITH_WITNESS_LEVEL_UPGRADES_AND_TARGETED_QUARANTINE

Upgraded:
- Ganzer + kur at line 166;
- kur/Ganzer retrieval pair at 174-179;
- gidim at line 292;
- gidim-a-ni at line 303.

Retained with lower ceiling:
- gidim at line 213, composite-confirmed only.

Quarantined:
- nearby spirit-sign loci identified by Attinger as udug/gidim/kitim-sensitive.

Still pending:
- full Gadotti 2014 occurrence-by-occurrence reconciliation;
- complete witness coverage beyond the three CDLI-aligned witnesses;
- extension of line-level currentness control to the other three death compositions.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
