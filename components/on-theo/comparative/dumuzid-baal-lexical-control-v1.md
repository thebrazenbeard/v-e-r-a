# Dumuzid / Baal Death-Return Lexical Control V1

Status: RESEARCH_PACKET / CROSS-LANGUAGE_LEXICAL_CONTROL / REVIEW_REQUIRED

Successor subject:
- predecessor PR: #50
- predecessor head: 8aabf5571246ca772ef6954c2470ee9d6f33e208
- branch: research/dumuzid-baal-lexical-control-v1-20260918

## Purpose

The Dumuzid/Baal transmission lane already distinguishes:
- chronology;
- contact;
- narrative mechanics;
- direct carrier evidence.

This packet adds another guard:

PLOT_SIMILARITY != SHARED_LEXICAL_FORMULA.

The comparison is intentionally narrow:
- Akkadian A.1146 Dumuzi death/return wording;
- Ugaritic Baal death and renewed-life wording.

It does not claim that lexical difference disproves all historical influence.
It does block a stronger claim that the surviving texts preserve one shared death-return formula.

## 1. A.1146: killing is agentive

A widely cited reconstruction of A.1146 lines 39-44 contains:

idakkushu

from Akkadian daku, "to kill."

The current ORACC Akkadian lexical resources classify daku as KILL, with kill as the dominant attested sense in several corpora.

The A.1146 reconstruction is commonly translated:

"they kill him."

Important semantic feature:

DUMUZI_DEATH_A1146 =
AGENTIVE_KILLING_CONSTRUCTION.

The form describes others acting upon Dumuzi.

This is not merely a stative statement:
"Dumuzi is dead."

Because the A.1146 passage is damaged, the exact form remains reconstruction-controlled rather than autoptically secure in this project.

## 2. A.1146: return is iterative

The same reconstructed passage contains:

ittanar

from Akkadian taru, "turn / return."

Current ORACC Akkadian lexical data attests iterative/continuative forms such as:
- ittanar / ittanar-type forms;
- senses including "come back repeatedly," "continually turn back," and "return."

The common A.1146 translation:
"he always comes back"

therefore reflects an iterative or repeated-return value, not the lexical verb "to rise."

Control:

A1146_RETURN =
REPEATED_RETURN / COMING_BACK

not:

LEXICAL_VERB_RESURRECT.

## 3. Akkadian daku and taru are semantically ordinary verbs

Neither root is intrinsically a technical "dying-and-rising god" formula.

daku:
- kill;
- defeat in some contexts.

taru:
- turn;
- return;
- come back;
- restore/bring back in derived/transitive contexts.

Therefore:

DAKU + TARU
!=
FIXED_RESURRECTION_IDIOM

unless a specific corpus establishes such an idiom.

A.1146's theological/mythic force comes from the Dumuzi referent and the surrounding comparison, not because the verbs themselves lexically mean "die and resurrect."

## 4. Baal's death is expressed differently

The Ugaritic Baal Cycle reports Baal's death with the paired expressions:

mt aliyn b'l
hlq zbl b'l ars

commonly translated along the lines of:
- "Mighty/Victorious Baal is dead";
- "the Prince, Lord of the Earth, has perished."

The Ugaritic lexical roots differ from A.1146:

mt:
death / die

hlq:
perish.

Current Ugaritic lexical resources independently classify:
- mt as DIE / DEATH;
- hlq as PERISH.

Thus:

BAAL_DEATH =
DEAD/DIE + PERISH STATE/EVENT LANGUAGE

rather than A.1146's:
"they kill him."

## 5. Baal's renewed-life wording is also different

KTU 1.6 III describes the recognition of Baal's renewed presence with:

hy aliyn b'l

and a parallel existence statement concerning the Prince, Lord of the Earth.

Mark S. Smith notes that the dream-vision calls Baal:

hy, "alive"

and that this has often been taken as evidence of Baal's return to life/resurrection.

The wording is therefore life/existence language:

BAAL_RETURN =
ALIVE / EXISTS / REAPPEARS

not:

UGR_VERB_RETURN cognate to A.1146 taru.

This is a major lexical control.

## 6. The surviving formulations are not a shared phrase

A.1146:
- others kill Dumuzi;
- Dumuzi repeatedly returns.

Baal Cycle:
- Baal is dead / has perished;
- later Baal is alive / exists / reappears.

At the proposition level both can support:
DEATH -> RENEWED_PRESENCE.

At the wording level:

AGENTIVE_KILL + ITERATIVE_RETURN
!=
DEAD/PERISHED + ALIVE/EXISTS.

Therefore:

SHARED_DEATH_RETURN_SEMANTICS
!=
SHARED_FORMULA.

## 7. What lexical difference can and cannot prove

Lexical difference weakens claims of:
- direct formula borrowing;
- translation-calque dependence;
- one preserved phrase transmitted from Mari to Ugarit.

It does NOT by itself disprove:
- broader mythic influence;
- oral transmission;
- ritual influence;
- adaptation into local vocabulary;
- shared regional mythologem.

An adapted tradition can change all of its words.

Therefore the correct inference is bounded:

LEXICAL_IDENTITY_EVIDENCE_FOR_DIRECT_DEPENDENCE = ABSENT_IN_V1.

## 8. Narrative mechanics remain independently different

This lexical result reinforces, but does not replace, the prior causal comparison.

Dumuzid tradition:
- substitution;
- galla captors;
- handing over;
- escape;
- sister alternation;
- repeated return language at Mari.

Baal tradition:
- Mot as antagonist;
- reported death/perishing;
- divine mourning;
- Mot confrontation;
- later alive/existence recognition;
- restoration of kingship/rain order.

The lexical and narrative differences point in the same direction:

DIRECT_TEXTUAL_DEPENDENCE_NOT_DEMONSTRATED.

## 9. Beware English harmonization

English translations make the two traditions look more alike than the source language necessarily does.

A translator may summarize both as:
- "dies";
- "returns";
- "rises";
- "comes back to life."

But the source-level constructions differ.

Project rule:

COMPARE_SOURCE_LEXEMES_BEFORE_ENGLISH_MOTIF_LABELS.

## 10. Current disposition

DUMUZID_BAAL_LEXICAL_CONTROL_V1 =

SEMANTIC_PARALLEL_REAL
+
LEXICAL_FORMULA_IDENTITY_NOT_FOUND
+
DIRECT_CALQUE_DEPENDENCE_NOT_ESTABLISHED
+
BROADER_INFLUENCE_STILL_POSSIBLE

Strong controls:
- A.1146 killing = daku reconstruction;
- A.1146 returning = iterative taru reconstruction;
- Baal death = mt / hlq;
- Baal renewed life = hy / existence-reappearance language.

Evidence boundary:
A.1146 remains a damaged text reconstructed through scholarship; the lexical analysis inherits that ceiling.

Next frontier:
- recover A.1146's exact damaged signs around idakkushu / ittanar from a line edition if technically possible;
- isolate Ugaritic KTU 1.6 III exact morphology and parallelism in a current critical edition;
- compare Mari ritual-movement verbs such as usherib "I caused to enter" against Baal reappearance language;
- only then test whether any translation/calque route is linguistically plausible.

No result modifies PR #33's HOLD, authorizes merge, or establishes canonical materialization.
