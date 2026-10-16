# Sumerian Material Evidence — City / Period Matrix V1

Status: RESEARCH_PACKET / MATERIAL_EVIDENCE_LANE / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #34
- predecessor head: `efe4ab2e39f205ff5bbc6e176be0b4fe1348f480`
- branch: `research/sumerian-material-evidence-v1-20260918`

## Purpose

This packet adds a material-archaeology lane to the Sumerian religion reconstruction so that literary, lexical, and later theological sources do not carry more evidentiary weight than they deserve.

The controlling distinction is:

`TEXTUAL_DIVINE_ASSOCIATION != EXCAVATED_CULT_INSTALLATION != BUILDING_FUNCTION_PROVED`

A structure may be called a temple in excavation history, identified as cultic by inscriptions, associated with a deity by later texts, or interpreted as sacred from plan and finds. Those are different evidentiary routes and must not silently collapse into one another.

Evidence classes used here:
- `MATERIAL_EVIDENCE`
- `PRIMARY_TEXT`
- `HISTORICAL_RECONSTRUCTION`
- `SCHOLARLY_INTERPRETATION`
- `PROJECT_INFERENCE`
- `UNKNOWN`

## 1. Material-evidence rules

### M1 — Context before label

Legacy names such as "Temple Sounding", "Eanna", "E-abzu", "Temple of Enlil", or "Ibgal" are not all the same kind of evidence.

For each claimed cult building, track separately:
1. excavated architecture;
2. stratigraphic date;
3. inscriptional identification found in or directly tied to the structure;
4. later textual identification;
5. excavator interpretation;
6. modern re-evaluation.

### M2 — Deity attribution requires an attribution route

Allowed attribution routes:
- in-situ or tightly contextualized inscription;
- building inscription demonstrably belonging to the structure;
- strong stratigraphic continuity plus historically controlled textual identification;
- explicit excavator identification supported by published evidence.

Not enough by itself:
- city patron known from literature;
- much later god list;
- modern site-tour convention;
- resemblance to another temple plan.

### M3 — Monumental does not automatically mean cultic

Large mudbrick architecture may be:
- temple;
- palace;
- administrative complex;
- platform;
- terrace;
- fortification;
- storage;
- mixed-use institution;
- or unresolved.

### M4 — Literary theology cannot repair archaeological gaps

If archaeology has not located a temple, literary evidence that a city had a patron deity does not create one archaeologically.

If archaeology finds a monumental building without a secure divine attribution, later theology does not automatically supply the god.

### M5 — Archaeology can falsify inherited simplifications

New excavation may:
- move walls;
- change periodization;
- separate phases formerly conflated;
- downgrade cultic certainty;
- reveal domestic/private cult;
- expose administrative or production contexts alongside monumental sacred architecture.

That is not "contradiction noise"; it is normal evidentiary revision.

---

# 2. City / period matrix

## NIPPUR

### Ur III — Temple of Enlil / Ekur area

Evidence:
- Joint University Museum / Oriental Institute excavations published in *Nippur I*.
- The excavated Temple of Enlil northeast of the ziggurat is reported as apparently built by Ur-Nammu.
- Its plan remained broadly stable through later rebuilding/use into Neo-Assyrian and Neo-Babylonian periods.

Classification:
- architecture: `MATERIAL_EVIDENCE`
- Ur-Nammu construction attribution: `HISTORICAL_RECONSTRUCTION` grounded in excavation/publication
- Enlil identification: high-confidence scholarly identification, but period-specific building phases remain distinct.

Source:
- ISAC, *Nippur I, Temple of Enlil, Scribal Quarter, and Soundings*
  https://isac.uchicago.edu/publications/nippur-i-temple-enlil-scribal-quarter-and-soundings

### Ur III / early Isin-Larsa — private household cult

*Nippur I* reports clear evidence for private chapels in the Scribal Quarter only in levels belonging to the Ur III and early Isin-Larsa periods.

Implication:
- cult activity was not confined to monumental temples;
- "religion = temple institution" is materially incomplete;
- domestic/private religious architecture must be tracked separately from state/city cult.

Classification:
- private chapel architecture: `MATERIAL_EVIDENCE`
- relationship to household practice: `HISTORICAL_RECONSTRUCTION`

Guard:
Do not generalize these Nippur private chapels to every Sumerian city or period.

---

## UR

### Ur III and later sacred precinct — ziggurat and surrounding sacred architecture

Penn Museum's excavation history records Woolley's investigation of the ziggurat and surrounding sacred structures at Ur, including the Temple Precinct of Nanna.

Classification:
- architecture: `MATERIAL_EVIDENCE`
- precinct-wide Nanna attribution: strong historical/epigraphic reconstruction
- individual building function: resolve per structure and phase.

Sources:
- Penn Museum, "The Thrill of Discovery"
  https://www.penn.museum/sites/expedition/the-thrill-of-discovery/
- Penn Museum, "Partners in Search of the Past"
  https://www.penn.museum/sites/expedition/partners-in-search-of-the-past/

### Early Dynastic III — Royal Cemetery

The Royal Cemetery provides major mortuary evidence from mid-third-millennium Ur.

Materially attested:
- large cemetery;
- elite "royal" tomb complexes among many simpler graves;
- rich grave goods;
- differentiated burial practices.

Classification:
- graves / bodies / assemblages / stratigraphy: `MATERIAL_EVIDENCE`
- titles, offices, ritual interpretation: mixed `PRIMARY_TEXT` + `HISTORICAL_RECONSTRUCTION`

Sources:
- Penn Museum, "Ur and Its Treasures"
  https://www.penn.museum/sites/expedition/ur-and-its-treasures/
- Penn Museum, "What Do We Know About the People Buried in the Royal Cemetery?"
  https://www.penn.museum/sites/expedition/what-do-we-know-about-the-people-buried-in-the-royal-cemetery/

Guard:
`ROYAL_CEMETERY != TEMPLE_CULT`

Mortuary practice may intersect with kingship and religion, but cemetery evidence must not be treated as direct evidence for the daily liturgy of Nanna's temple.

### Multiple periods — domestic and neighborhood evidence

Woolley's excavations also exposed houses, workshops, neighborhood shrines, and non-monumental urban contexts.

Implication:
The religious system of Ur cannot be reconstructed only from ziggurat + elite graves.

Source:
- Penn Museum, "City of the Moon"
  https://www.penn.museum/sites/expedition/city-of-the-moon/

---

## GIRSU / TELLO

### Third millennium BCE — Ningirsu sacred district

The modern British Museum Girsu Project is re-excavating the sacred district and temple/sanctuary of Ningirsu using modern documentation methods.

Materially significant features include:
- extensive mudbrick walls;
- architectural elements with pilasters;
- inscribed cones recovered in wall contexts;
- renewed excavation of temple and sanctuary areas;
- administrative-center work at Tablet Hill.

Classification:
- walls / cones / spatial relationships: `MATERIAL_EVIDENCE`
- Ningirsu attribution where inscriptions and structure context converge: strong `MATERIAL_EVIDENCE + PRIMARY_TEXT`

Sources:
- British Museum, Girsu Project
  https://www.britishmuseum.org/research/projects/girsu-project
- British Museum, Tello
  https://www.britishmuseum.org/our-work/international/iraq-scheme/tello

Important methodological value:
Earlier excavations and looting left many Girsu finds with weak archaeological context. The modern project explicitly treats context recovery and re-documentation as a research problem.

That means:
`MUSEUM_OBJECT_FROM_GIRSU != SECURE_BUILDING_CONTEXT`

unless provenance/context is independently established.

### Gudea / Eninnu tradition

Gudea's temple-building texts are extremely important textual evidence for Ningirsu's temple.

But:
- inscriptional/literary temple description is not identical to the excavated architecture;
- architectural reconstruction must bind text to physical phases rather than assume one-to-one correspondence.

Classification:
- Gudea cylinders/text: `PRIMARY_TEXT`
- excavated building: `MATERIAL_EVIDENCE`
- exact text-building phase correlation: `HISTORICAL_RECONSTRUCTION`

---

## LAGASH / AL-HIBA

Lagash and Girsu are separate urban centers within the historical Lagash city-state and must not be collapsed into one site.

### Early Dynastic — temple complexes

Legacy excavations at Tell al-Hiba exposed:
- the Ibgal of Inana;
- the Bagara of Ningirsu;
- extensive Early Dynastic I temple remains;
- an Early Dynastic III administrative complex.

The distinction between temple and administration is archaeologically useful: monumental institutional architecture at Lagash is not one undifferentiated sacred category.

Source:
- Penn Museum, Lagash Archaeological Project
  https://www.penn.museum/research/project.php?pid=219

Classification:
- excavated temple complexes: `MATERIAL_EVIDENCE`
- deity attribution: strong where excavation history and inscriptions/textual controls align
- administrative complex: `MATERIAL_EVIDENCE`, not temple by default.

### Enanatum I / Ibgal control

Recent Lagash work recovered an inscribed clay nail naming Enanatum I in a context below a later flood deposit; Penn notes that Enanatum I oversaw construction of the Ibgal temple of Inana previously excavated at the site.

Source:
- Penn Museum, "Partners in Search of the Past"
  https://www.penn.museum/sites/expedition/partners-in-search-of-the-past/

Classification:
- inscribed nail: `PRIMARY_TEXT + MATERIAL_EVIDENCE`
- connection to Ibgal building history: `HISTORICAL_RECONSTRUCTION`

### Current project correction to elite-monument bias

The current Lagash Archaeological Project deliberately samples:
- craft-production areas;
- domestic housing;
- streets;
- public eateries;
- neighborhoods;
- hydrology and marsh-edge landscape.

Project implication:
A Sumerian religion model derived solely from monumental temples risks overrepresenting royal/elite institutional religion.

Source:
- Penn Museum, Lagash Archaeological Project
  https://www.penn.museum/research/project.php?pid=219

---

## ŠURUPPAK / FARA

### Early Dynastic urban structure

Modern magnetometer work at Fara has:
- confirmed a city wall;
- identified canals within the city;
- mapped a large central building complex interpreted as likely a temple;
- re-georeferenced early twentieth-century excavation trenches.

Source:
- Fassbinder et al., "Revisiting Fara"
  https://doi.org/10.1002/arp.1878

Classification:
- city wall / geophysical anomalies / canals: `MATERIAL_EVIDENCE`
- central building = temple: `SCHOLARLY_INTERPRETATION`, not yet absolute
- deity attribution to Sud: `UNKNOWN` archaeologically unless independently bound.

Critical guard:
The project explicitly began from the problem that texts attest Sud and centralized administration while older excavations had not securely located a palace or temple.

Therefore:

`TEXTS_ATTEST_SUD -> BUILDING_X_IS_SUD_TEMPLE`

is invalid without an archaeological attribution bridge.

### 2022 / 2024 renewed excavation

LMU's Fara project reports modern survey, geophysics, and new excavations designed to clarify houses, official buildings, the town center, and northern urban edge.

Source:
- LMU Munich, FARA Fieldwork
  https://www.en.vorderas-archaeologie.uni-muenchen.de/research/fara-fieldwork/index.html

Implication:
Šuruppak is a live re-evaluation case; building-function labels should remain updateable.

---

## URUK / WARKA

### Late fourth millennium onward — Eanna precinct

The German Archaeological Institute reports long-term excavation of Uruk's central monumental architecture and identifies:
- Eanna sanctuary of Inanna/Ištar;
- Anu sanctuary;
- later Irigal and Bit Resh temples;
- stratified architectural sequences;
- Eanna traceable from the end of the fourth millennium BCE into much later periods.

Sources:
- DAI, Uruk (Warka)
  https://www.dainst.org/en/research/projects/noslug/2604
- DAI, Uruk results
  https://www.dainst.org/forschung/projekte/noslug/2604?tx_wfdaiprojects_projects%5Bsection%5D=results

Classification:
- architectural sequence: `MATERIAL_EVIDENCE`
- named sanctuary attribution: strong scholarly/epigraphic reconstruction
- continuity of "same religion" across all phases: not implied.

Important guard:
Long architectural duration does not equal semantic or ritual continuity.

`SAME_PRECINCT_OVER_TIME != SAME_THEOLOGY_OVER_TIME`

### Research-history bias

DAI explicitly notes that Uruk research focused for decades on building history and only later expanded toward broader cultural-historical interpretation.

Project implication:
Uruk's excellent monumental record may be disproportionately visible because archaeology itself historically privileged architecture.

This should be treated as a source-selection bias, not proof that monumental cult dominated every dimension of lived religion.

---

## ERIDU / ABU SHAHRAYN

Eridu is the highest-value methodological stress test in this matrix because recent work is actively revising the legacy picture.

### Legacy Temple Sounding

The 1940s "Temple Sounding" exposed an 18-level architectural sequence fundamental to Ubaid periodization.

However:
- "Temple Sounding" is a research-history label;
- later terraces were dated partly through indirect/external evidence;
- modern excavation has corrected locations shown on older published plans;
- precise phase/function correlations require renewed stratigraphic control.

Source:
- Quenet et al., "Archaeological Mission at Eridu: the 2022 campaign ... E-abzu monumental complex reconsidered"
  https://doi.org/10.1017/irq.2025.10035

Classification:
- 18-level sequence: `MATERIAL_EVIDENCE`
- every level = Enki temple: do not assume without phase-specific evidence.

### Late Chalcolithic / Uruk-period monumental terraces

The 2022 work identifies white-plastered stepped terraces predating the Ur III ziggurat. Their dating is still partly indirect and the excavators explicitly seek radiocarbon control.

Classification:
- terraces / plaster / stratigraphy: `MATERIAL_EVIDENCE`
- exact date: `HISTORICAL_RECONSTRUCTION`, some phases provisional
- cultic function: phase-specific and not automatic.

### Ur III — E-unir / E-abzu monumental complex

The modern project reconstructs a major Ur III phase in which older terraces were reused in the platform of the ziggurat and the E-abzu precinct was monumentalized.

This is strong material evidence for a major cultic-monumental installation in the Ur III period.

But the same article notes that the excavated area's Early Dynastic and Akkadian phases are absent.

Therefore:
`UR_III_ENKI_PRECINCT != DIRECT_MATERIAL_PROOF_OF_UNBROKEN_EARLY_DYNASTIC_PRECEDENT`

### Royal inscriptions are not excavation proof

The Eridu report explicitly warns that royal epithets/inscriptions can remain ideological or rhetorical and cannot automatically prove concrete royal work at the site.

This is adopted as a project-wide rule:

`ROYAL_BUILDING_CLAIM != MATERIAL_EFFECT_VERIFIED`

unless archaeological context/readback supports it.

---

# 3. Comparative material-evidence table

| City | Period(s) emphasized | Secure material lane | Cultic attribution confidence | Main caution |
| --- | --- | --- | --- | --- |
| Nippur | Ur III–Isin-Larsa | Enlil temple; private chapels | High for Enlil complex; high for chapel function | Do not generalize household chapels across Sumer |
| Ur | ED III; Ur III+ | cemetery; ziggurat/sacred precinct; houses | High for Nanna precinct at broad level | Cemetery evidence is not temple liturgy |
| Girsu | 3rd millennium | Ningirsu temple/sanctuary; inscribed cones; admin center | High where cone/context binds | Old museum finds often have weak context |
| Lagash | ED I–III | Ibgal, Bagara, temples, admin complex, domestic/production zones | Medium-high by structure | Lagash != Girsu; elite architecture bias |
| Šuruppak | ED IIIa and wider 3rd millennium | city wall, canals, probable central official/cult building | Probable, not closed | Sud in texts does not identify a building by itself |
| Uruk | Late 4th millennium onward | Eanna/Anu precinct architecture | High at precinct level | Long duration != unchanged ritual/theology |
| Eridu | Ubaid–Ur III+ | 18-level sounding; terraces; Ur III monumental E-abzu | High for Ur III complex; variable earlier | Legacy "temple" labels and dates require phase-specific recheck |

---

# 4. What this changes in the Sumerian religion model

The literary packet's city-temple-deity network remains useful, but the material lane forces four corrections.

## Correction A — institutional plurality

Material evidence supports not one religious architecture but several overlapping settings:
- monumental temple precincts;
- administrative complexes;
- private chapels;
- cemeteries;
- neighborhood shrines;
- production and habitation zones;
- landscape/waterscape infrastructure.

So:

`SUMERIAN_RELIGION != MONUMENTAL_TEMPLE_SYSTEM_ONLY`

## Correction B — city patron theology is not an excavation shortcut

Patron deities remain historically important, but they cannot be used to pre-label every monumental building in that city.

## Correction C — chronology must attach to architecture, not just deity name

A deity may remain associated with a city over long periods while:
- buildings move;
- precincts expand;
- temples are rebuilt;
- ritual roles change;
- political patrons change;
- older architecture is reused.

Therefore registry claims should bind:
`CITY + BUILDING_PHASE + DATE_RANGE + ATTRIBUTION_ROUTE`

not merely:
`CITY + GOD`.

## Correction D — preservation and excavation bias matter

The archaeological record overrepresents:
- monumental mudbrick architecture that was targeted by excavators;
- spectacular graves;
- inscribed objects;
- sites excavated intensively by major expeditions.

It underrepresents:
- ordinary household practice;
- perishable ritual;
- open-air activity;
- low-status neighborhoods;
- poorly preserved early phases;
- sites damaged by looting or early excavation.

This bias must be modeled explicitly before comparative conclusions are drawn.

---

# 5. Registry design consequence

A future `EXT-SUMERIAN-MATERIAL-EVIDENCE-V1` should not create a generic "temple" edge.

Minimum building/site record fields should include:

- `site_id`
- `city_name`
- `modern_site_name`
- `area_or_building_id`
- `phase_id`
- `date_range`
- `material_context_type`
- `excavation_project`
- `excavation/publication_source_id`
- `function_interpretation`
- `function_confidence`
- `deity_attribution`
- `attribution_route`
- `inscription_context`
- `legacy_label`
- `modern_reassessment_status`
- `preservation_bias_notes`

This prevents a later comparative query from treating "temple at Eridu", "Temple of Enlil", "probable central temple at Fara", and "private chapel at Nippur" as equivalent observations.

---

# 6. Current evidentiary disposition

`MATERIAL_EVIDENCE_LANE_V1 = PASS_WITH_ACTIVE_REASSESSMENT_FRONTIERS`

Strongly supported:
- cult architecture at Nippur, Ur, Girsu, Lagash, Uruk, and Ur III Eridu;
- non-temple institutional and domestic contexts are materially significant;
- Šuruppak's city plan and probable central monumental/cult building can now be modeled without pretending the temple identification is closed;
- modern fieldwork is materially revising legacy excavation assumptions.

Not yet closed:
- complete site-by-site deity attribution;
- pre-Ur III functional continuity at Eridu;
- full household-cult comparison;
- funerary religion across cities;
- material correlates of specific rituals;
- archaeological evidence for inter-city transmission of theological concepts.

No result in this packet changes PR #33's promotion HOLD or authorizes merge/canonical materialization.
