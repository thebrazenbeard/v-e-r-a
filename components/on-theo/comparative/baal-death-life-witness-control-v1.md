# Baal Death / Life Physical-Witness Control V1

Status: RESEARCH_PACKET / PHYSICAL_WITNESS_AND_CYCLE_CONTROL / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #51
- predecessor head: 48ca89402a6f685614a1cfd068a278d40c1de0fb
- branch: research/baal-death-life-witness-control-v1-20260918

## Purpose

The Dumuzid/Baal lexical-control lane now distinguishes:
- Akkadian A.1146 wording;
- Ugaritic Baal death vocabulary;
- Ugaritic Baal renewed-life vocabulary.

This packet adds a different distinction:

WORK/CYCLE IDENTITY
!=
PHYSICAL TABLET IDENTITY.

The Baal Cycle's death and renewed-life evidence is distributed across separate clay tablets.

That matters because a synthesis statement such as:

"the Baal Cycle says Baal dies and later lives"

is a valid cycle-level reconstruction.

It is not the same claim as:

"one physical tablet preserves both propositions."

## 1. KTU 1.5 physical witness

The fifth Baal Cycle tablet is:

KTU 1.5
=
RS 2.[022] + RS 3.[565]
=
Louvre AO 16641 + AO 16642.

The Louvre catalogs:
- two joined/associated fragments;
- terracotta/clay;
- alphabetic cuneiform;
- myth / Cycle of Baal;
- Late Bronze II, broadly 1400–1200 BCE;
- discovery at the Ras Shamra acropolis.

The current Göttingen Edition of Ugaritic Poetic Texts corpus index independently maps:
- RS 2.[022] + 3.[565]
- AO 16.641 + 16.642
- KTU 1.5
- CTA 5
- Baalu V.

Disposition:

KTU15_PHYSICAL_WITNESS_IDENTITY = HIGH_CONFIDENCE.

## 2. KTU 1.5 preserves the death announcement

KTU 1.5 VI 8-10 contains the well-known death announcement:

npl lars
mt aliyn bl
hlq zbl bl ars

In standard analysis:
- Baal is found/fallen to the earth;
- Mighty/Victorious Baal is dead;
- the Prince, Lord of the Earth, has perished.

The key source lexemes:
- mt — dead/die;
- hlq — perish.

This proposition belongs physically to the KTU 1.5 witness complex.

Evidence state:

BAAL_DEATH =
KTU15_PHYSICAL_WITNESS_BOUND
+
CRITICAL_EDITION_INTERPRETATION.

## 3. KTU 1.6 is a separate physical witness

The sixth Baal Cycle tablet is:

KTU 1.6
=
RS 2.[009] + RS 5.155
=
Louvre AO 16636.

The Louvre currently catalogs:
- terracotta/clay tablet fragment;
- Ugaritic cuneiform;
- myth / Cycle of Baal;
- Late Bronze II, broadly 1400–1200 BCE;
- discovery at Ras Shamra acropolis / House of the High Priest;
- inventory AO 16636;
- excavation numbers RS 2.[009] and RS 5.155.

The Göttingen corpus index independently maps:
- RS 2.[009] + 5.155;
- AO 16.636;
- KTU 1.6;
- CTA 6;
- Baalu VI.

Disposition:

KTU16_PHYSICAL_WITNESS_IDENTITY = HIGH_CONFIDENCE.

## 4. KTU 1.6 preserves renewed-life recognition

KTU 1.6 III contains El's dream/recognition sequence.

Modern grammatical and philological treatments preserve formulations including:

k hy aliyn bl

"because / indeed Mighty Baal lives / is alive"

and a parallel existence statement involving:
- the Prince;
- Lord of the Earth;
- existence / presence.

Mark S. Smith describes the key word hy as "alive" and treats this as the literary recognition of Baal's renewed life/reappearance.

This proposition belongs physically to KTU 1.6, not KTU 1.5.

Evidence state:

BAAL_RENEWED_LIFE =
KTU16_PHYSICAL_WITNESS_BOUND
+
CRITICAL_EDITION_INTERPRETATION.

## 5. Death and renewed life are cross-tablet

Therefore the strongest provenance model is:

KTU 1.5:
DEATH DISCOVERY / DEATH ANNOUNCEMENT

followed in the cycle by:

KTU 1.6:
MOURNING / MOT CONFLICT / RENEWED-LIFE RECOGNITION / BAAL REAPPEARANCE.

This is a cycle-level sequence across distinct physical objects.

Control:

BAAL_DEATH_RETURN_CYCLE =
CROSS_WITNESS_TEXTUAL_RECONSTRUCTION.

It is not:
SINGLE_WITNESS_CONTINUOUS_EVENT_REPORT.

## 6. KTU 1.5 -> KTU 1.6 continuation is literary, not a physical join

Modern Ugaritic scholarship treats KTU 1.6 as the continuation of KTU 1.5 based on literary/thematic sequence:
- KTU 1.5 ends with Baal found dead and mourning initiated;
- KTU 1.6 continues Anat's mourning and the aftermath.

But the tablets are separately cataloged physical witnesses:
- different excavation numbers;
- different Louvre inventory numbers;
- separate clay artifacts.

Therefore:

TEXTUAL_CONTINUITY != PHYSICAL_CONTINUITY.

This distinction must remain machine-readable.

## 7. Scribal/cycle identity is also separate

KTU 1.6 preserves a colophon associated with Ilimilku.

Modern scholarship uses this and related evidence to reconstruct the six-tablet Baal Cycle as an authored/copied literary corpus.

But:

SCRIBE/CYCLE_RELATIONSHIP
!=
ONE_TABLET.

The project should model at minimum:

SRC-UGARIT-BAAL-CYCLE
  -> WIT-KTU15
  -> WIT-KTU16

with separate passage claims bound to each witness.

## 8. Effect on Dumuzid / Baal comparison

This does not weaken the proposition:
Baal dies and later returns/lives.

It improves its type.

The comparison should now distinguish:

### Dumuzid A.1146
One damaged letter contains a reconstructed kill/return comparison.

### Baal
The death and renewed-life propositions are reconstructed across separate tablets within the Baal Cycle.

Thus the evidence architecture itself differs:
- one epistolary comparison;
- one multi-tablet literary cycle.

This is another reason not to compare only English plot summaries.

## 9. Currentness

The physical inventory identities are strong because:
- Louvre catalog records are current institutional object records;
- the Göttingen Ugaritic poetic-text project independently maps the RS / Louvre / KTU identifiers.

The textual reading still depends on critical-edition scholarship.

No claim of autoptic sign-by-sign collation from the Louvre photographs is made here.

## 10. Current disposition

BAAL_DEATH_LIFE_WITNESS_CONTROL_V1 =
PASS_WITH_CROSS_TABLET_PROVENANCE_CONTROL

High-confidence:
- KTU 1.5 = AO 16641/16642 = RS 2.[022]+3.[565];
- KTU 1.6 = AO 16636 = RS 2.[009]+5.155;
- death announcement belongs to KTU 1.5;
- renewed-life recognition belongs to KTU 1.6;
- cycle synthesis legitimately connects them;
- physical witness identity remains separate.

Key rule:

CYCLE_LEVEL_DEATH_RETURN
!=
SINGLE_TABLET_DEATH_RETURN.

Next frontier:
- register both physical witnesses;
- bind death/alive claims to witness IDs;
- inspect the exact continuity argument and manuscript joins in current Ugaritic editions;
- then compare witness architecture, not just motifs, against Mari and Sumerian corpora.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
