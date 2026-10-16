# Ugarit Dumuzi Direct Scribal Attestation V1

Status: RESEARCH_CORRECTION / DIRECT_SCRIBAL_ATTESTATION / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #55
- predecessor head: 118bd970361f0fa47290f979341f3092722b011e
- branch: research/ugarit-dumuzi-direct-attestation-v1-20260918

## Correction target

PR #55 correctly established general Mesopotamian literary and scholastic exposure at Ugarit, but stated that V1 had not identified a Dumuzi/Tammuz source at Ugarit.

A direct Ugarit attestation has now been identified.

That older statement is too broad and is superseded.

## 1. Physical artifact

Ugaritica 5, 137
=
RS 20.123+
=
CDLI P332950
=
NMSD 05294.

Current CDLI metadata:
- provenience: Ugarit / Ras Shamra;
- Middle Babylonian;
- clay tablet;
- lexical text;
- primary publication: Nougayrol 1968, Ugaritica 5, no. 137;
- linked to the Weidner God List tradition.

This is a physical Ugarit scribal artifact, not merely a later comparative reconstruction.

## 2. Direct Dumuzi row

The Ugarit Weidner-list witness preserves, reverse column ii line 7:

Sumerian/Mesopotamian column:
dDUMU-[ZI]

Hurrian column:
du-mu-zi

Ugaritic-equivalent column:
broken / not preserved.

ePSD2 independently indexes the same line:

d dumu-[zid] = du-mu-zi [...]
(Ugaritica 5, 137 r ii 7).

Disposition:

DUMUZI_NAME_AT_UGARIT =
DIRECT_MATERIAL_AND_TEXTUAL_ATTESTATION_HIGH.

## 3. What kind of evidence this is

The artifact is lexical/scholastic.

It therefore establishes:

- Ugaritic scribes or scribal institutions had direct access to a learned Mesopotamian god-list tradition containing Dumuzi;
- the Dumuzi divine name was present in a Ugarit school/lexical context;
- Dumuzi-specific Mesopotamian religious vocabulary reached Ugarit.

This is stronger than:
GENERAL_MESOPOTAMIAN_CONTACT_ONLY.

It upgrades:

SPECIFIC_DUMUZID_SOURCE_CONTACT_AT_UGARIT

from:
NOT_ESTABLISHED

to:
DIRECT_SCHOLASTIC_NAME_ATTESTATION.

## 4. It is not a Dumuzid narrative

The text is not:
- Inana's Descent;
- Dumuzi's Dream;
- a Dumuzi lament;
- a death/return narrative;
- a cultic ritual text;
- a Baal/Dumuzi comparative text.

Therefore:

DUMUZI_NAME_AT_UGARIT
!=
DUMUZI_DEATH_RETURN_MYTH_AT_UGARIT.

No narrative proposition transfers from the Mesopotamian Dumuzi corpus merely because the god's name occurs in a lexical list.

## 5. Ugaritic equivalent is not preserved

The trilingual Ugarit version of the Weidner God List commonly supplies:
- a Mesopotamian entry;
- a Hurrian equivalent;
- a Ugaritic equivalent.

At the Dumuzi row, however, the Ugaritic-equivalent column is broken.

Thus the surviving artifact does not establish:
- which Ugaritic deity, if any, was equated with Dumuzi;
- whether Baal was equated with Dumuzi;
- whether a local Ugaritic Dumuzi cult existed;
- whether the Ugaritic scribes considered Dumuzi identical with any specific local god.

Control:

LOST_UGARITIC_EQUIVALENT
!=
BAAL_EQUIVALENT.

## 6. Hurrian Dumuzi form is preserved

The Hurrian column preserves:
du-mu-zi.

This is important for diffusion history because the Ugarit trilingual god-list tradition itself participates in a Mesopotamian-Hurrian-Ugaritic scholastic environment.

But the form appears to carry Dumuzi's name across columns rather than independently proving a local Hurrian narrative tradition in this artifact.

Therefore:

HURRIAN_COLUMN_DUMUZI =
SCHOLASTIC_EQUIVALENCE_ATTESTATION

not:
INDEPENDENT_HURRIAN_DUMUZI_MYTH_PROOF.

## 7. Carrier model upgrade

The transmission model can now distinguish three levels.

### General capacity
Akkadian literature and cuneiform school material physically present at Ugarit.

Status:
SUPPORTED.

### Dumuzi-specific scholastic exposure
A Ugarit lexical tablet directly preserves the Dumuzi name.

Status:
SUPPORTED.

### Dumuzi death/return narrative exposure
A Dumuzi myth, ritual, or death-return composition at Ugarit.

Status:
NOT ESTABLISHED.

### Ilimilku-specific Dumuzi exposure
Evidence that Ilimilku himself read or used RS 20.123+ or another Dumuzi source.

Status:
NOT ESTABLISHED.

### Baal textual dependence
Evidence that the Baal Cycle borrowed from a Dumuzi composition.

Status:
NONE ESTABLISHED.

## 8. Bounded search for local cult/literary occurrence

A targeted V1 search was run across:
- current ORACC Ugarit materials;
- CDLI Ugarit records;
- KTU/Ugaritic-oriented web results;
- Dumuzi/Tammuz spelling variants.

The positive result is the lexical-school attestation above.

No independently controlled alphabetic-Ugaritic Dumuzi/Tammuz narrative, ritual, or offering-list occurrence was established in this targeted pass.

This is a search-state result only.

It must not be promoted to:

"Dumuzi was absent from Ugaritic religion."

Recommended status:

LOCAL_UGARITIC_DUMUZI_CULT_OR_NARRATIVE =
NOT_FOUND_IN_TARGETED_V1_SEARCH /
HISTORICAL_ABSENCE_NOT_PROVEN.

## 9. Effect on the earlier PR #55 claim

Superseded statement:

"no Dumuzi/Tammuz literary source has been identified at Ugarit"

Corrected statement:

"Direct Dumuzi-specific scholastic exposure is attested at Ugarit in RS 20.123+ / P332950, but no Dumuzi death-return literary composition, local cult text, or Ilimilku-specific use has yet been established."

This is a material improvement in carrier evidence.

## 10. Transmission consequence

The Dumuzid -> Baal transmission model now becomes:

CHRONOLOGY:
compatible.

REGIONAL CONTACT:
supported.

UGARIT MESOPOTAMIAN LITERARY CONTACT:
supported.

UGARIT DUMUZI-SPECIFIC SCHOLASTIC EXPOSURE:
supported.

DUMUZI DEATH/RETURN NARRATIVE AT UGARIT:
not established.

ILIMILKU DUMUZI ACCESS:
not established.

DIRECT DUMUZID -> BAAL DEPENDENCE:
none established.

This raises the plausibility of contact while leaving lineage unproven.

## 11. Current disposition

UGARIT_DUMUZI_DIRECT_ATTESTATION_V1 =
PASS_FOR_DUMUZI_SPECIFIC_SCRIBAL_EXPOSURE
/
NO_PASS_FOR_NARRATIVE_OR_CULT_TRANSMISSION

Strong:
- RS 20.123+ is a physical Ugarit lexical tablet;
- Dumuzi is directly preserved on r ii 7;
- Hurrian du-mu-zi is preserved;
- the Ugaritic equivalent at that row is lost.

Not established:
- Baal = Dumuzi equivalence;
- local Dumuzi cult;
- Dumuzi myth at Ugarit;
- Ilimilku-specific use;
- direct Baal dependence.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
