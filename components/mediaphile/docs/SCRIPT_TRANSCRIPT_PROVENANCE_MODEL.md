# Script / Transcript Provenance Model

Mediaphile separates three questions that are easy to collapse:

1. **Did Patrick actually ask ChatGPT to read this work's transcript, subtitles, or screenplay?**
2. **Did the recoverable interaction establish no read, a partial corpus read, or a substantially complete read?**
3. **What exactly was the artifact ChatGPT read or consulted?**

A title mention, project-scope instruction, web-search result, script catalog listing, uploaded file, incidental quote lookup, successful parsing, partial corpus read, and completed full read are different evidence states.

## Request-history states

- `REQUESTED_READ_VERIFIED` — recoverable conversation evidence shows Patrick explicitly requested a screenplay/transcript/subtitle read, ingestion, or equivalent full-work/corpus textual research.
- `READ_PARTIAL_VERIFIED` — recoverable conversation evidence establishes substantially complete reading of some meaningful portion of an assigned multi-work or episodic corpus, while whole-corpus completion is not established. The supported frontier or aggregate checkpoint must be recorded rather than guessed.
- `READ_COMPLETED_VERIFIED` — recoverable conversation evidence records a completed substantially complete read of the assigned work/corpus, not merely an intention, search, download, successful parse, inventory sweep, or partial read.
- `READ_COMPLETION_NOT_VERIFIED` — a relevant artifact/request context exists, but completion of a substantially complete read is not established and the recoverable evidence is insufficient to support `READ_PARTIAL_VERIFIED`.
- `INCIDENTAL_SOURCE_CONSULTATION` — ChatGPT consulted transcript/script material to answer another question; this is not promoted into a Patrick-requested full read.
- `OFFER_ONLY_NO_ARTIFACT` — a screenplay/transcript was proposed or discussed, but recoverable evidence does not show that the artifact was supplied/read.
- `NOT_A_READ_ASSIGNMENT` — recoverable evidence explicitly says the artifact was supplied for another reason, such as a gift, rather than as work to perform.
- `PROJECT_SCOPE_ONLY` — project architecture or a worker role permits/requires future source research, but recoverable evidence does not establish that Patrick assigned or that ChatGPT completed the particular work/corpus read being audited.

## Artifact-provenance states

- `OFFICIAL_DISTRIBUTION_COPY_VERIFIED` — source is directly hosted/distributed by the rights-holder/studio or another primary production source.
- `PRODUCTION_SCREENPLAY_VERIFIED` — artifact is supported as a genuine production screenplay by primary or converging high-quality provenance evidence.
- `RELEASED_DIALOGUE_TRANSCRIPT` — text substantially represents released dialogue but is not established as a production screenplay.
- `USER_UPLOADED_SUBTITLES` — subtitle text is explicitly identified by the hosting service as user uploaded; release alignment may be useful, but official provenance is not established.
- `DERIVED_FAN_TRANSCRIPT` — source explicitly describes itself as a transcription made from viewings and/or another screenplay.
- `CATALOG_ONLY` — a catalog says an artifact exists, but the substantially complete artifact was not itself read.
- `ARTIFACT_IDENTITY_UNRESOLVED` — evidence is insufficient to establish what kind of artifact it was.

## Integrity rules

- A transcript or subtitle file is never silently relabeled as a screenplay.
- A screenplay is not proof of the final released cut.
- A source URL or catalog entry is not proof that ChatGPT substantially read the artifact.
- Successful parsing or page-count access is not silently promoted into semantic full-read completion.
- An inventory sweep is not a corpus read; an episodic series can be `READ_PARTIAL_VERIFIED` without being `READ_COMPLETED_VERIFIED`.
- Aggregate corpus checkpoints are never silently decomposed into per-series/per-season counts that the recoverable evidence does not support.
- Retracted or demonstrated-false progress claims do not count as read evidence.
- Historical assistant claims of a full or partial read count as read-history evidence only when preserved in recoverable conversation records; artifact provenance is verified independently where possible.
- Reader/session identity is preserved where materially relevant; work performed by a distinct admitted worker is not silently promoted into another worker's autobiographical read history.
- Binary identity is not claimed unless a digest or byte-level comparison was actually performed.
- `AUDIOVISUAL_INGESTED` remains separate from all text evidence.
- Corpus assignments are expanded to individual works when the recoverable record defines the corpus sufficiently; incomplete members remain explicitly incomplete.
- Audit coverage is bounded to recoverable ChatGPT history, Project/Library evidence, and currently accessible repositories/sources. Missing, deleted, unindexed, or inaccessible history is recorded as unresolved rather than silently treated as absence.
