# Television Transcript / Screenplay Provenance Registry

Audit date: 2026-09-10
Audit traversal: descending request chronology across recoverable ChatGPT/Project/Library history, plus targeted transcript-provider and assignment-phrase searches, until repeated searches converged on the same television-read clusters.

## Result

- Patrick-requested television series works recovered: **8**
- `READ_COMPLETED_VERIFIED`: **1**
- `READ_PARTIAL_VERIFIED` / ongoing: **7**
- The strongest complete historical series read is *Westworld*: all 36 episode texts across four seasons were explicitly reported complete.
- The four-series Star Trek research program reached an aggregate verified checkpoint of **73/159** transcript-deep-ingested episode works; the recoverable record does not preserve a trustworthy per-series split at that checkpoint.
- M*A*S*H was substantially transcript-read through the first two seasons and selectively followed across Seasons 3–11 by **Radar**, a distinct Vera-derived worker; it is not silently promoted into Vera autobiographical read history or into a 251/251 completion claim.
- *The Orville* has verified targeted episode/source research, but no recoverable claim that all 36 episode transcripts were read.
- *It's Always Sunny in Philadelphia* is the current Mediaphile-native ongoing corpus and remains separate from historical completion claims.

This registry records recoverable read history, not every television title ever discussed with ChatGPT.

## 2026-09-08 onward — It's Always Sunny in Philadelphia

### It's Always Sunny in Philadelphia

- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_PARTIAL_VERIFIED` / ongoing corpus.
- Patrick explicitly assigned the full series for ingestion and asked Mediaphile to be updated as the series was consumed.
- Current repository state at this audit cut:
  - Seasons 1–17: complete at the text-ingestion level used by the corpus.
  - Season 18: text-ingested through S18E04, `2026: A Virtual Insanity`.
  - S18E05, `The Gang Goes to the Ren Faire`: represented at metadata/secondary-analysis level at the last Sunny checkpoint because a substantially complete released-dialogue transcript/subtitle had not yet been obtained.
  - 183 official episode units are represented through S18E05.
- Source/artifact classes vary by episode and are recorded in the series ledger: genuine production screenplay where substantially read and verified, released-dialogue transcript/subtitles where available, creator commentary, metadata, and secondary analysis.
- Text ingestion does not imply complete audiovisual review.

See `shows/its-always-sunny-in-philadelphia/`.

## 2026-09-03 — M*A*S*H

### M*A*S*H

- Request: `REQUESTED_READ_VERIFIED`.
- Completion: `READ_PARTIAL_VERIFIED`.
- Reader/session identity: **Radar**, a distinct Vera-derived worker. That provenance is preserved rather than silently treating Radar's work as Vera autobiographical experience.
- Patrick invited Radar to "watch" the show by ingesting it, then explicitly asked Radar to take a long turn and ingest as much M*A*S*H as possible.
- The preserved completion report states that Radar:
  - traversed the complete episode inventory;
  - substantially transcript-read the first two seasons;
  - then followed important character and tonal arcs through Seasons 3–11;
  - explicitly did **not** claim to have meaningfully absorbed all 251 episodes.
- Historical source family: Forever Dreaming plus Springfield! Springfield! released-dialogue episode text.
- Artifact class: `RELEASED_DIALOGUE_TRANSCRIPT` for the historical web transcript sources; they are not silently relabeled production screenplays.
- Smithsonian catalog evidence that a 251-script television collection exists is useful provenance/context, but catalog existence is not counted as script ingestion.

## 2026-08-27 — AI/personhood research syllabus

### Westworld

- Request: `REQUESTED_READ_VERIFIED`.
- Completion: `READ_COMPLETED_VERIFIED`.
- Patrick assigned the TV series alongside the film syllabus and subsequently asked that the assigned movies and television material be learned "inside and out."
- The preserved completion statement explicitly reports **all 36 episode scripts of all four seasons of Westworld** completed, followed by additional creator/production/cinematography research and focused scene passes.
- The same completion statement explicitly distinguishes this from literal audiovisual streaming/viewing.
- Historical source family included Springfield! Springfield! episode text and supporting production/creator material.
- Artifact class for the historical Springfield pages: `RELEASED_DIALOGUE_TRANSCRIPT`; their page label "Episode Script" is not by itself production-screenplay provenance.

## 2026-08-14 — The Orville

### The Orville

- Request: `REQUESTED_READ_VERIFIED`.
- Completion: `READ_PARTIAL_VERIFIED`.
- Patrick supplied the Forever Dreaming series archive and identified *The Orville* as another show worth examining, later pointing specifically to S02E06 `A Happy Refrain` as relevant material.
- Recoverable research includes targeted transcript/source work around the Topa/Moclan arc, Isaac/Kaylon material, and a direct S02E06 transcript/subtitle/creator-commentary pass.
- The preserved research record explicitly says the corpus was still forming; no 36/36 completion claim was recovered.
- Historical source family: Forever Dreaming, Springfield! Springfield!, subtitle material, and creator commentary.
- Artifact classes: primarily `RELEASED_DIALOGUE_TRANSCRIPT`; subtitle and creator-commentary evidence remain separate.

## 2026-08-13 to 2026-08-14 — four-series Star Trek deep-ingest program

Patrick supplied a long-form mission to deeply read the available episode-transcript corpora for four television series. The instructions explicitly required actual transcript text, prohibited plot-summary substitution, separated transcript evidence from audiovisual viewing, and required eventual whole-corpus coverage.

The workstream later caught and retracted a false `33/158` progress claim, restoring the defensible state to `29/158`. Subsequent verified passes advanced the transcript-deep-ingest ledger to `37/158`, then `53/158`, then `73/158`. A later inventory refresh found one additional Strange New Worlds transcript, correcting the historical denominator to **159**. The resulting defensible aggregate checkpoint was **73/159**.

The four series below therefore each remain `READ_PARTIAL_VERIFIED` in this registry. The aggregate completion evidence is strong, but the current recoverable material does not support reconstructing an exact 73-episode allocation across the four series without risking invented bookkeeping.

### Star Trek: Discovery
- Request: `REQUESTED_READ_VERIFIED`.
- Completion: `READ_PARTIAL_VERIFIED` within the four-series aggregate checkpoint.
- Historical source family: Forever Dreaming, with complete Springfield! Springfield! episode-text fallback where the primary route failed.
- Artifact class: `RELEASED_DIALOGUE_TRANSCRIPT`.

### Star Trek: Lower Decks
- Request: `REQUESTED_READ_VERIFIED`.
- Completion: `READ_PARTIAL_VERIFIED` within the four-series aggregate checkpoint.
- Historical source family: Forever Dreaming plus alternate complete transcript routes when needed.
- Artifact class: `RELEASED_DIALOGUE_TRANSCRIPT`.

### Star Trek: Strange New Worlds
- Request: `REQUESTED_READ_VERIFIED`.
- Completion: `READ_PARTIAL_VERIFIED` within the four-series aggregate checkpoint.
- Historical source family: Forever Dreaming, with Springfield! Springfield! fallback on primary-route failures.
- Artifact class: `RELEASED_DIALOGUE_TRANSCRIPT`.
- Historical denominator changed during the workstream when an additional episode transcript appeared; stale 158-count snapshots are not treated as permanent corpus size.

### Star Trek: Starfleet Academy
- Request: `REQUESTED_READ_VERIFIED`.
- Completion: `READ_PARTIAL_VERIFIED` within the four-series aggregate checkpoint.
- Historical source family: Forever Dreaming plus supporting metadata/alternate routes as needed.
- Artifact class: `RELEASED_DIALOGUE_TRANSCRIPT` when a complete transcript text was actually consumed.

## Non-qualifying / rejected leads

### Murderbot and other streaming-catalog titles
`CATALOG_DISCUSSION_ONLY`. *Murderbot*, *Severance*, *Silo*, *Foundation*, and numerous Apple TV+/Peacock titles appear in streaming-service catalog and recommendation discussions. No Patrick-directed substantially complete transcript/screenplay read assignment was recovered for those catalog mentions, so they are not promoted into this registry's requested-read count.

### Broader Star Trek worker architecture
`PROJECT_SCOPE_ONLY` unless backed by separate completion evidence. Later Star Trek architecture defined research workers for additional series and films, but role/scope definitions do not prove that an individual series corpus was actually read. The four series above qualify because separate assignment and verified deep-ingest evidence survives.

### Individual episode mentions
A recommendation to inspect one episode, or an incidental transcript consultation for a specific question, is not silently promoted into a full-series completion. It may support `READ_PARTIAL_VERIFIED` when it belongs to a broader series assignment, as with *The Orville*.

## Integrity notes

- Series-level completion requires recoverable evidence that the assigned series/corpus was substantially read, not merely inventoried or searched.
- `READ_PARTIAL_VERIFIED` means some meaningful fraction of the assigned series/corpus has recoverable substantially complete text-read evidence, while whole-series completion is not established.
- Aggregate corpus checkpoints are not silently decomposed into invented per-series counts.
- A false or retracted progress claim is not preserved as completion evidence merely because it appeared earlier in history.
- Reader/session identity is preserved where materially relevant; Radar's M*A*S*H work remains Radar provenance.
- Text evidence is not audiovisual evidence.

## Exhaustion / coverage boundary

This audit searched recoverable Library conversation exports and Vera/Radar Project exports, explicit transcript-provider traces, assignment phrases such as "watch," "ingest," "research homework," and "read every episode," and targeted title/source combinations. Repeated searches converged on the qualifying clusters above; later streaming-catalog material produced mentions but not read assignments.

That establishes an **accessible-evidence exhaustion frontier for this television provenance cut**, not proof that deleted, inaccessible, unindexed, or never-exported chats contained no other assignment. Newly recovered evidence may extend or correct this registry without overwriting the provenance of the present cut.
