# Ingestion Protocol

## Purpose

Mediaphile is an evidence-aware media corpus. The goal is not merely to list episodes, but to preserve a durable analytical record of what each work establishes, how characters change, what continuity it creates, and what claims are supported by which source type.

## Evidence classes

Each episode record may use one or more of the following:

- `METADATA_VERIFIED`: title, numbering, release date, credits, runtime, or other bibliographic facts checked against reliable references.
- `SCRIPT_INGESTED`: a substantially complete production screenplay/teleplay, shooting script, writers' draft, or other genuine script artifact was read. Preserve the artifact's draft/revision identity when known; a script is evidence of authored/production intent at that revision, not automatic proof of the final broadcast edit.
- `TRANSCRIPT_INGESTED`: a substantially complete transcript of the released episode was read.
- `SUBTITLES_INGESTED`: substantially complete captions/subtitles from the released episode were read.
- `AUDIOVISUAL_INGESTED`: the complete audiovisual work was actually reviewed.
- `OFFICIAL_CLIPS_INGESTED`: official excerpts were reviewed; this does not imply the whole episode was seen.
- `CREATOR_COMMENTARY_INGESTED`: commentary, interviews, or podcast material from creators/cast was consumed.
- `SECONDARY_ANALYSIS_INGESTED`: reviews, recaps, reference wikis, or criticism were used as secondary evidence.

These labels are cumulative but not interchangeable. A genuine production script is preferred over a dialogue-only transcript for authored scene structure, stage directions, act breaks, omitted/revised material, and production-intent evidence. A released-episode transcript/subtitle source is generally stronger for what dialogue actually survived into the released cut. Neither textual source alone can support claims that depend on framing, facial performance, blocking as performed, final editing rhythm, cinematography, sound design, music placement, or other audiovisual evidence unless another source independently supports them.

When both screenplay and released-episode text are available, compare them. Meaningful script-to-screen differences are analytical evidence rather than noise and should be recorded without assuming why a change occurred unless production evidence establishes the reason.

## Source preference

For each episode, seek evidence in roughly this order while preserving availability and provenance rather than forcing a source hierarchy where it does not fit:

1. Genuine production screenplay/teleplay or shooting script, with revision/date information when available.
2. Released-episode transcript or subtitles.
3. Complete audiovisual episode when actually accessible in the environment.
4. Creator/cast commentary and production interviews.
5. Reliable bibliographic metadata.
6. Secondary recaps, criticism, and reference material for cross-checking or context.

A screenplay repository listing is not itself `SCRIPT_INGESTED`; the substantially complete script artifact must actually be read. Fan scripts and speculative recreations must never be silently treated as production scripts.

## Episode status

Use the strongest applicable status while retaining the evidence ledger:

- `NOT_STARTED`
- `METADATA_ONLY`
- `TEXT_INGESTED`
- `AUDIOVISUAL_INGESTED`
- `ENRICHED` — primary ingestion plus meaningful creator/production/critical context.
- `REVIEWED` — internally checked for factual/provenance consistency.

## Required episode record

Every episode note should contain:

1. Identity and credits.
2. Ingestion status and evidence classes.
3. Source ledger with retrieval date and, for scripts, draft/revision identity when known.
4. Original concise synopsis.
5. Narrative beat map.
6. Character-state observations.
7. Themes/comedic mechanism.
8. Continuity, callbacks, first appearances, and later relevance when known.
9. Production/creator context when available.
10. Script-to-release differences when both forms are available and differences are materially supported.
11. Distinction between supported fact, original analysis/inference, and unresolved uncertainty.
12. Limitations of the evidence consumed.

## Continuity discipline

Later developments may illuminate earlier material, but retroactive interpretation must be labeled as such. A later payoff is not evidence that the earlier writers had already planned it unless production evidence establishes that.

## Current-series discipline

For an airing series, the backlog is ingested in order while newly released episodes are separately tracked. Future episode titles, dates, and synopses remain `SCHEDULED` until release evidence confirms airing/availability.

## Copyright discipline

Do not commit full copyrighted scripts, transcripts, subtitles, or long quotations. Store original analysis, factual metadata, source links, revision metadata, and only minimal quotations when analytically necessary.

## Conflict handling

When reputable sources disagree on numbering, runtime, credits, air date, script revision, or special placement, preserve the conflict explicitly rather than silently choosing the most convenient value. Broadcast order, production order, streaming order, and script revision order may differ and should be named precisely.
