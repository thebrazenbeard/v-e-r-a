# Baal Cycle / Ilimilku Attribution Control V1

Status: RESEARCH_PACKET / SCRIBAL_ATTRIBUTION_AND_CYCLE_CONTROL / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #53
- predecessor head: 700f2b6c3a9975fe11db45e1441b339dd0b917d8
- branch: research/baal-ilimilku-attribution-control-v1-20260918

## Purpose

The Baal death/life witness packet established that KTU 1.5 and KTU 1.6 are distinct physical tablets.

This packet asks a related but different question:

How directly is the six-tablet Baal Cycle tied to the scribe Ilimilku?

Core rule:

CYCLE_ATTRIBUTION != SIX_DIRECT_COLOPHONS.

## 1. KTU 1.6 directly names Ilimilku

KTU 1.6 closes with a full colophon naming Ilimilku as scribe.

Current Göttingen Ugaritic work quotes the colophon at KTU 1.6 VI 54-58 and identifies Ilimilku as:
- the scribe;
- the Shubbanite;
- the student/assistant of Attenu;
- connected with high cultic and court officials of Niqmaddu, king of Ugarit.

Disposition:

ILIMILKU_KTU16_DIRECT = PRIMARY_TEXT_HIGH.

This is direct colophon evidence on the KTU 1.6 witness itself.

## 2. KTU 1.4 also directly names Ilimilku

KTU 1.4 preserves a shorter scribal note on the tablet edge.

Standard descriptions summarize the note as identifying:
- Ilimilku as scribe;
- Niqmaddu as king of Ugarit.

Thus:

ILIMILKU_KTU14_DIRECT = PRIMARY_TEXT_HIGH.

KTU 1.4 and KTU 1.6 therefore provide at least two direct Baal-Cycle scribal anchors.

## 3. The other Baal tablets do not all preserve direct Ilimilku colophons

Modern scribal studies distinguish:
- texts with explicit Ilimilku colophons;
- texts recognizably or arguably written in Ilimilku's ductus but without surviving colophons.

Wyatt's survey notes direct colophons on:
- KTU 1.4;
- KTU 1.6;
- KTU 1.16;
- KTU 1.17;
- and KTU 1.179,

while other Baal, Kirta and Aqhat tablets may be attributable by handwriting/ductus rather than explicit surviving colophon.

For the six-tablet Baal Cycle, therefore:

KTU 1.1 / 1.2 / 1.3 / 1.5
do not each independently provide the same direct Ilimilku colophon evidence as KTU 1.4 and 1.6.

## 4. Six-tablet cycle unity is scholarly reconstruction supported by more than colophon

The Baal Cycle is conventionally reconstructed as KTU 1.1-1.6.

Evidence includes:
- narrative continuity;
- shared style and poetic language;
- scribal/ductus comparison;
- KTU 1.4 and KTU 1.6 Ilimilku anchors;
- the KTU 1.6 "of Baal" superscription/heading;
- archaeological and library context.

Pardee describes the longest Ugaritic literary composition as the six tablets of the so-called Baal Cycle.

This is strong literary reconstruction.

But:

SIX_TABLET_CYCLE =
SCHOLARLY_COMPOSITIONAL_UNIT

not:

ONE_PHYSICAL_DOCUMENT.

## 5. Authorship, scribal copying, and recension are different propositions

The Ilimilku colophon establishes scribal identity.

It does not automatically prove:
- Ilimilku invented every narrative motif;
- he was the first author of all underlying traditions;
- all six tablets were composed de novo by him;
- the cycle had no oral or earlier written sources;
- every tablet was copied in one sitting.

Recommended distinctions:

SCRIBE:
Ilimilku directly attested on KTU 1.4 / 1.6.

COPYIST/RECENSOR:
plausible cycle-level scholarly model.

ORIGINAL_AUTHOR_OF_ALL_TRADITION:
not established merely by colophon.

## 6. Niqmaddu context

The KTU 1.6 colophon places Ilimilku in relation to Niqmaddu, king of Ugarit.

This gives a court/elite scribal context for the tablet.

It is historically important for:
- chronology;
- scribal institution;
- circulation setting.

But it does not by itself establish:
- royal commissioning of every line;
- official theological orthodoxy;
- direct political allegory.

## 7. Attribution confidence by tablet

Recommended V1 statuses:

KTU 1.4:
DIRECT_ILIMILKU_COLOPHON.

KTU 1.6:
DIRECT_ILIMILKU_FULL_COLOPHON.

KTU 1.1:
ILIMILKU_CYCLE_ATTRIBUTION_BY_SCHOLARLY_RECONSTRUCTION.

KTU 1.2:
ILIMILKU_CYCLE_ATTRIBUTION_BY_SCHOLARLY_RECONSTRUCTION.

KTU 1.3:
ILIMILKU_CYCLE_ATTRIBUTION_BY_SCHOLARLY_RECONSTRUCTION.

KTU 1.5:
ILIMILKU_CYCLE_ATTRIBUTION_BY_SCHOLARLY_RECONSTRUCTION.

This prevents a common provenance inflation:
"the Baal Cycle is attributed to Ilimilku"
becoming
"every surviving tablet explicitly names Ilimilku."

## 8. Effect on KTU 1.5 -> KTU 1.6 death/life sequence

The death witness is KTU 1.5.
The renewed-life witness is KTU 1.6.

KTU 1.6 directly names Ilimilku.
KTU 1.5 does not preserve the same direct colophon anchor.

Therefore:

BAAL_DEATH_LIFE_SEQUENCE
=
CYCLE_LEVEL_CONTINUITY
+
UNEQUAL_DIRECT_SCRIBAL_ATTESTATION.

This does not materially weaken cycle unity.
It improves provenance precision.

## 9. Transmission implications

For Dumuzid/Baal transmission questions, Ilimilku's scribal identity is not a carrier chain by itself.

To establish direct transmission through Ilimilku would require evidence such as:
- Mesopotamian text access;
- bilingual scribal training;
- identifiable source borrowing;
- lexical or structural dependence beyond generic motif similarity;
- historical network connecting specific source material to his scribal environment.

No such direct chain has been established in V1.

Thus:

ILIMILKU =
TARGET_TRADITION_SCRIBAL_ANCHOR

not:

DUMUZID_TO_BAAL_TRANSMISSION_CARRIER.

## 10. Current disposition

BAAL_ILIMILKU_ATTRIBUTION_CONTROL_V1 =
PASS_WITH_DIRECT_AND_RECONSTRUCTED_LEVELS_SEPARATED

Direct:
- KTU 1.4 Ilimilku note;
- KTU 1.6 full Ilimilku colophon.

Reconstructed:
- Ilimilku attribution across the six-tablet cycle where individual colophons do not survive.

Not established:
- six direct colophons;
- original authorship of every inherited tradition;
- direct Dumuzid source transmission through Ilimilku.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
