# Sumerian Death-Corpus Occurrence Provenance Overlay V1

Status: RESEARCH_CONTROL / COMPLETE_OVER_TARGETED_V1_SET / REVIEW_REQUIRED

This overlay assigns an explicit evidence ceiling to every one of the 25 lexical occurrence records created in the targeted death-corpus map.

The problem it solves is simple: a line seen in ETCSL, a line confirmed in a current CDLI composite, a line aligned to a physical witness, and a line inherited through a specific Me-Turan reconstruction are not the same kind of evidence.

The overlay therefore keeps two independent dimensions:

1. Evidence state — what has actually been read back for the occurrence.
2. Currentness state — what later edition, philological control, score, or witness alignment still remains unresolved.

## Coverage

The overlay covers exactly 25 occurrence IDs:
- Inana's Descent: 7
- Gilgamesh, Enkidu and the Netherworld: 7
- The Death of Gilgamesh: 4
- The Death of Ur-Namma: 7

No mapped occurrence is omitted and no new occurrence is added to the set.

## Strongest witness-aligned subset

The strongest V1 records currently include:
- Inana line 73 Ganzer;
- Inana lines 74-75 kur gate language;
- Inana line 119 kur with witness variation;
- Inana line 120 Ganzer;
- Gilgamesh/Enkidu line 166 Ganzer + kur;
- Gilgamesh/Enkidu lines 178-179 kur/Ganzer retrieval pair;
- Gilgamesh/Enkidu line 292 gidim;
- Gilgamesh/Enkidu line 303 gidim-a-ni with variant syntax.

These records have direct aligned-witness support on current CDLI score surfaces.

That does not make all of them edition-current in the strongest possible sense. The Gilgamesh/Enkidu records still retain the Gadotti 2014 full-edition dependency, and Inana retains the Attinger philological crosscheck.

## Composite-only or currentness-limited records

The overlay deliberately leaves several records below witness-aligned status:
- Inana lines 98-99 remain ETCSL-direct/current-recheck-pending because they were not separately upgraded in the targeted score pass.
- Gilgamesh/Enkidu line 224 remains pending full-edition/current recheck.
- Ur-Namma records remain current-composite confirmed because witness-alignment readback was unavailable in this runtime.

This is the evidence ceiling, not a defect to hide.

## Version-specific Death of Gilgamesh records

All four original occurrence records from The Death of Gilgamesh are now explicitly tagged ME_TURAN_VERSION:
- gidim line 38;
- gidim line 39;
- kur line 39;
- Arali line 166.

The current CDLI Nippur composite does not independently witness-align those lines and currently reports zero aligned witnesses overall.

The stronger Me-Turan reconstruction remains valid research evidence through the ETCSL / Cavigneaux-al-Rawi edition lineage, but it must not be mislabeled as current Nippur-composite or witness-aligned evidence.

## Ur-Namma and internal polysemy

Ur-Namma's occurrence set remains especially useful because the current CDLI composite independently confirms the central semantic control:
- line 65 uses kur geographically/for foreign land;
- line 73 onward uses kur in the death-realm domain.

Those records are composite-level, not witness-aligned, but the internal contrast is direct and current.

## Governing rule

The project should never ask merely, "Is this occurrence verified?"

It should ask:
- verified where?
- against which textual version?
- at what evidentiary layer?
- with which currentness dependency still open?

The overlay makes those questions machine-readable.

## Current disposition

SUMERIAN_DEATH_OCCURRENCE_PROVENANCE_V1 = COMPLETE_OVER_TARGETED_25_WITH_MIXED_EVIDENCE_CEILINGS

Nothing in this overlay modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
