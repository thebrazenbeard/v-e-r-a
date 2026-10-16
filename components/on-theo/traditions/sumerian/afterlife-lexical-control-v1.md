# Sumerian Afterlife Lexical Control V1

Status: RESEARCH_PACKET / SEMANTIC_CONTROL / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #36
- predecessor head: de5f1f0c88b49fb4c654eb87e25c021396957b0a
- branch: research/sumerian-afterlife-lexicon-v1-20260918

## Purpose

This packet constrains the English gloss "underworld" by separating source-language terms that are not semantically interchangeable.

Core rule:

ONE_ENGLISH_GLOSS != ONE_SUMERIAN_LEXEME != ONE_STABLE_CONCEPT

Primary lexical control is ePSD2 / ORACC. Literary context remains necessary because dictionary sense inventories do not determine the meaning of every occurrence mechanically.

Terms in scope:
- gidim
- kur
- arali
- ganzer
- kurnugi

## 1. gidim

ePSD2:
- 169 total attestations in the full lexical entry;
- attested from Early Dynastic IIIa and IIIb through Ur III, Old Babylonian, and later periods;
- sense: "spirit of a deceased person, ghost";
- Akkadian lexical equivalence: etemmu.

Source:
https://oracc.museum.upenn.edu/epsd2/o0028131

Important result:

GIDIM_SEMANTIC_CORE = DECEASED_PERSON_GHOST/SPIRIT

This is much more stable than the topographic vocabulary.

The existence of gidim in Early Dynastic and Ur III evidence means the category is not merely a first-millennium invention.

But:
- later ritual systems involving ghosts cannot be back-projected wholesale;
- lexical continuity does not prove unchanged ritual practice;
- gidim must not be collapsed with demon terms such as udug.

Control:

GIDIM != GENERIC_SUPERNATURAL_BEING

and:

GIDIM_LEXEME_CONTINUITY != RITUAL_SYSTEM_CONTINUITY

## 2. kur

kur is highly polysemous.

ePSD2 early-literary data explicitly gives:
- "(foreign) land, country";
- "mountain(s)";
- "underworld".

In the cited early-literary subset:
- 20 instances total;
- 18 are classified as mountain(s);
- 1 as foreign land/country;
- 1 as underworld.

Source:
https://oracc.museum.upenn.edu/epsd2/earlylit/o0032654

This makes a global replacement rule such as:

kur = underworld

invalid.

Instead:

KUR = CONTEXT-SENSITIVE LAND/MOUNTAIN/FOREIGN-REGION/UNDERWORLD LEXEME

depending on text, syntax, genre, period, and collocation.

Critical consequence:
A comparative study that searches every kur occurrence as "underworld" will manufacture false evidence.

Examples of required controls:
- distinguish geographic mountain/foreign-land uses;
- distinguish cosmic/topographic underworld uses;
- preserve compound forms separately;
- do not infer an underworld concept from the sign KUR alone.

## 3. arali

ePSD2 gives arali as:
"earth, land; underworld".

Full entry:
- 81 instances;
- 73 classified as earth/land;
- 8 classified as underworld;
- attested from Early Dynastic IIIb and Ur III through Old Babylonian and later periods.

Source:
https://oracc.museum.upenn.edu/epsd2/cbd/sux/o0024401.html

Especially important:
the Ur III administrative subset lists arali as "earth, land" in the surviving examples.

Source:
https://oracc.museum.upenn.edu/epsd2/admin/ur3/cbd/sux/summaries.html

Therefore:

ARALI != UNDERWORLD_BY_DEFAULT

The underworld sense is real, but minority in the full lexical entry and must be established contextually.

Later lexical associations connect arali with:
- erṣetu, earth;
- arallû, netherworld;
- "house of death";
- burial place.

Those associations show a semantic field around earth/death/burial/netherworld, not a single timeless gloss.

Control:

ARALI_SENSE = CONTEXT + PERIOD + GENRE

## 4. ganzer

ganzer is substantially more underworld-specific in the surviving lexical corpus.

ePSD2:
- 24 instances;
- 18 classified as netherworld/underworld/door to the underworld;
- 6 as earth/land;
- surviving attestations begin in the Old Babylonian period in the current entry.

Source:
https://oracc.museum.upenn.edu/epsd2/cbd/sux/o0027881.html

Lexical associations include:
- "gate of the earth";
- Irkalla;
- Dannina;
- Kanisurru;
- earth/netherworld terminology.

This explains why literary translations can render Ganzer as the netherworld or an underworld entrance.

But the chronology matters:

GANZER_SURVIVING_CORPUS = OLD_BABYLONIAN_AND_LATER

Therefore an Old Babylonian Sumerian literary occurrence cannot by itself prove that the same lexeme or semantic package operated identically in Early Dynastic spoken/religious language.

Control:

GANZER = STRONG_NETHERWORLD_TERM_IN_SURVIVING_OB+ CORPUS

not:

GANZER = TIMELESS_PAN-SUMERIAN_UNDERWORLD_NAME

## 5. kurnugi

ePSD2 treats kurnugi as a netherworld noun:
- 7 instances;
- 100 percent assigned to netherworld in the current lexical entry;
- attested from Old Babylonian onward in the surviving corpus.

Source:
https://oracc.museum.upenn.edu/epsd2/o0032704

This is more semantically specific than bare kur.

Important methodological rule:

KUR != KURNUGI

A compound or fixed expression must not be decomposed and then treated as equivalent to every occurrence of its component lexeme.

Later bilingual lexical material associates kurnugi with Akkadian earth/netherworld expressions, including a "land/earth of no return" equivalence in lexical tradition.

But:
- lexical bilinguals are evidence for scribal semantic mapping;
- they are not transparent windows into every earlier historical usage.

## 6. Semantic hierarchy

The V1 semantic control is:

### Person-category
gidim
- deceased person's ghost/spirit
- comparatively stable semantic core
- early attestations exist

### Broad spatial/topographic term
kur
- mountain
- foreign land/country
- underworld in some contexts
- extremely unsafe to normalize globally

### Earth/death/underworld field
arali
- predominantly earth/land in ePSD2
- underworld in a minority of contexts
- burial/death associations appear in lexical tradition

### More specific underworld/gate term
ganzer
- strongly associated with underworld/gate semantics
- surviving corpus Old Babylonian and later

### Fixed underworld term
kurnugi
- strongly netherworld-specific
- surviving corpus Old Babylonian and later

## 7. Translation controls

Do not silently translate all of the following as the same conceptual noun:

kur
arali
ganzer
kurnugi

Even when English "underworld" is acceptable in context, retain the Sumerian lexeme in the semantic registry.

Recommended display form:

English gloss [source lexeme]

Examples:
- underworld [ganzer]
- underworld [arali]
- netherworld [kurnugi]
- kur [contextually underworld]

This prevents English translation from erasing distinctions before comparison.

## 8. Diachronic controls

The lexical corpus is uneven.

Old Babylonian material dominates several literary and lexical entries.

Therefore:

ATTESTATION_FREQUENCY != HISTORICAL_USAGE_FREQUENCY

and:

FIRST_SURVIVING_ATTESTATION != FIRST_HISTORICAL_USE

But equally:

LATER_ATTESTATION != EVIDENCE_OF_EARLIER_USE_WITHOUT_SUPPORT

The project should state only:
- what periods are actually attested;
- what semantic range the current corpus supports;
- where continuity is inference rather than direct evidence.

## 9. Implications for the funerary packet

The funerary packet should now distinguish:
- gidim when discussing the dead as ghosts;
- ganzer/kurnugi/arali/kur when discussing spatial or cosmological location;
- specific text-level wording before abstracting to "the underworld."

This blocks a common error:

"the Sumerian underworld" as though every source uses one standardized noun and one standardized cosmology.

A safer formulation is:

"one or more Sumerian literary representations of the realm/location of the dead, using multiple overlapping source terms whose semantic ranges differ."

## 10. Comparative-religion consequence

These terms must not be compared directly to:
- Hebrew Sheol;
- Greek Hades;
- Egyptian Duat;
- Christian Hell;
- Buddhist Naraka;
- generic "land of the dead";

until each side is independently reconstructed at the proposition and lexeme level.

Similarity of English translation is not semantic identity.

Control:

SAME_TRANSLATION != SAME_CONCEPT != TRANSMISSION

## 11. Registry design

A lexical-semantic record should include:
- lexeme;
- normalized form;
- written form(s);
- period;
- corpus;
- source locator;
- ePSD sense;
- local contextual gloss;
- collocation/compound;
- semantic confidence;
- whether the use is literal, geographic, cosmological, metaphorical, or unresolved;
- whether an English translation collapses multiple source lexemes.

For compounds:
- record the compound as its own semantic unit;
- preserve component morphology without assuming compositional equivalence.

## 12. Current disposition

SUMERIAN_AFTERLIFE_LEXICON_V1 = PASS_WITH_CONTEXT_AND_DIACHRONY_CONTROLS

Strong:
- gidim is a robust term for ghost/spirit of a deceased person;
- kur is irreducibly polysemous and cannot globally mean underworld;
- arali has real underworld uses but is predominantly earth/land in the ePSD2 entry;
- ganzer is strongly underworld/gate oriented in surviving Old Babylonian and later evidence;
- kurnugi is strongly netherworld-specific in surviving Old Babylonian and later evidence.

Open:
- composition-level semantic analysis of each occurrence;
- historical phonology and etymology;
- regional variation;
- relation among literary, administrative, ritual, and lexical-list usage;
- pre-Old-Babylonian history of ganzer/kurnugi.

No result here modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
