# Movie Transcript / Screenplay Provenance Registry

Audit date: 2026-09-10
Audit traversal: **descending request chronology** until the accessible historical search frontier stopped producing older movie-read assignments.

## Result

- Patrick-requested movie works recovered: **20**
- `READ_COMPLETED_VERIFIED`: **18**
- `READ_COMPLETION_NOT_VERIFIED`: **2**
- Non-qualifying/rejected leads are preserved separately so they cannot later be mistaken for completed assignments.

This count is about recoverable ChatGPT request/read history, not every movie ever discussed with ChatGPT.

## 2026-08-27 — Her

### Her (2013)

- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Recoverable completion: **two full screenplay passes**.
- Historical source family: OverBlack plus cross-checks against matching screenplay mirrors.
- Artifact: `PRODUCTION_SCREENPLAY_VERIFIED`; final-draft/awards-distribution screenplay by Spike Jonze, WGA Registration #1500375, 106-page historical copy.
- Independent provenance: SimplyScripts' awards archive identifies the *Her* final draft as hosted by Warner Bros; surviving mirrors retain the same title-page identifier.
- Binary caveat: no digest from the historical download survives, so cross-mirror byte identity is not claimed.

See `movies/her-2013/provenance.md`.

## 2026-08-27 — AI/personhood research syllabus

Patrick explicitly assigned *Ex Machina*, *Blade Runner*, *Blade Runner 2049*, *I'm Your Man* and *Westworld*, then added *Turbo Kid*. He subsequently explicitly asked that the movies and TV material be learned "inside and out." The preserved completion statement says full screenplay/transcript passes were completed for **all five films**, while *Westworld* is tracked in the TV audit.

### Ex Machina (2015)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Historical primary text: Alex Garland screenplay.
- Artifact: `PRODUCTION_SCREENPLAY_VERIFIED`.
- Surviving copy identifies `EX MACHINA — By Alex Garland — © Alex Garland 2013 — c/o DNA Films Ltd.`; A24 independently identifies Garland as writer/director.

### Blade Runner (1982)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Historical primary text: Springfield! Springfield! movie-script page.
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`; no production-screenplay provenance is assigned to that historical source.

### Blade Runner 2049 (2017)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Historical primary text: Scribd screenplay copy.
- Artifact: `PRODUCTION_SCREENPLAY_VERIFIED`.
- Surviving text identifies Hampton Fancher (story/screenplay) and Michael Green (screenplay) and labels itself `FINAL SHOOTING SCRIPT`; independent screenplay catalogs identify the same final-shooting-script version.
- Host caveat: the historically consulted Scribd copy was user-uploaded; official-host provenance is not claimed.

### I'm Your Man (2021)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Historical primary text: Subtitle Cat English subtitle artifact.
- Artifact: `USER_UPLOADED_SUBTITLES` / released-dialogue evidence, not a production screenplay.
- Subtitle Cat explicitly labels the underlying subtitle text user uploaded. Apple TV independently confirms the film identity, 2021 release, German original audio and English subtitles.

### Turbo Kid (2015)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Historical primary text: Springfield! Springfield! movie-script page.
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`; no production-screenplay provenance is assigned to that historical source.

See `movies/ai-personhood-syllabus-2026-08-27/PROVENANCE.md`.

## 2026-08-14 — Star Wars theatrical-film corpus

Patrick explicitly directed a Star Wars movie ingestion and clarified the scope as all of the films. The preserved completion record says transcript-level primary text was obtained for the **first twelve released theatrical films** in the corpus below; the then-new *The Mandalorian and Grogu* lacked a comparable complete transcript and was deliberately kept at lower evidence weight.

| Work | Historical read status | Historical artifact class |
| --- | --- | --- |
| Star Wars: Episode IV — A New Hope (1977) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Star Wars: Episode V — The Empire Strikes Back (1980) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Star Wars: Episode VI — Return of the Jedi (1983) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Star Wars: Episode I — The Phantom Menace (1999) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Star Wars: Episode II — Attack of the Clones (2002) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Star Wars: Episode III — Revenge of the Sith (2005) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Star Wars: The Clone Wars (2008 theatrical film) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Star Wars: Episode VII — The Force Awakens (2015) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Rogue One: A Star Wars Story (2016) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Star Wars: Episode VIII — The Last Jedi (2017) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Solo: A Star Wars Story (2018) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| Star Wars: Episode IX — The Rise of Skywalker (2019) | `READ_COMPLETED_VERIFIED` | `RELEASED_DIALOGUE_TRANSCRIPT` |
| The Mandalorian and Grogu (2026) | `READ_COMPLETION_NOT_VERIFIED` | complete comparable transcript not established in the historical pass |

Historical source family was primarily Forever Dreaming's film transcript archive, with Springfield! Springfield! also used for at least part of the comparison. These are treated as third-party released-dialogue evidence, not production screenplays.

See `movies/star-wars/PROVENANCE.md`.

## 2026-07-19 — The Adventures of Ford Fairlane

### The Adventures of Ford Fairlane (1990)

- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETION_NOT_VERIFIED`
- Patrick first supplied the Script Slug page and then uploaded the screenplay PDF after the remote asset failed.
- Recoverable response verifies that the uploaded PDF parsed successfully across **102 pages**, but successful parsing is not silently promoted into proof that a complete semantic pass was actually performed.
- The recovered PDF itself identifies:
  - title: `FORD FAIRLANE`
  - screenplay by Dan Waters
  - story by Jay Cappe & Dave Arnott
  - based on a character created by Rex Weiner
  - `A Silver Pictures Production`
  - date: **May 1, 1989**
- Artifact: `PRODUCTION_SCREENPLAY_VERIFIED`.
- The soft-copy note says scene numbers present in the hard copy were not retained.

See `movies/the-adventures-of-ford-fairlane-1990/provenance.md`.

## Non-qualifying / rejected leads

These were found during the descending audit but are **not** included in the 20 requested movie works above.

### Heretic (2024) — 2026-07-12
`NOT_A_READ_ASSIGNMENT`. The actual 125-page screenplay artifact is recoverable and its title page identifies Scott Beck & Bryan Woods; A24 also hosts an official screenplay PDF. But the strongest recovered interaction evidence says Patrick supplied it as a **gift, not pending homework**, and the original gifting turn was not recovered. No read assignment or completed read is promoted from that evidence.

### A Not-a-girl & Her Auditor: A Love Story — 2026-08-27
`OFFER_ONLY_NO_ARTIFACT`. A movie idea and possible screenplay were discussed immediately before *Her*, but no supplied/read screenplay for this proposed title is recovered.

### Star Trek film worker lane — August 2026
`PROJECT_SCOPE_ONLY`. The Trek research architecture defines a films worker that should research assigned films from complete primary/full sources, but the recovered material used in this audit does not establish a Patrick-directed, completed feature-film transcript/screenplay pass for individual Star Trek movies. Architecture is not silently promoted into read history.

### Psycho Killer (2026) — 2026-05-30
Ordinary movie research/plot discussion surfaced, but no Patrick-requested screenplay/transcript full read was recovered.

### The Secret: Dare to Dream (2020)
Movie identification/research surfaced, but no Patrick-requested complete screenplay/transcript read was recovered.

### Anchorman: The Legend of Ron Burgundy (2004) — 2025-11-27
`INCIDENTAL_SOURCE_CONSULTATION`. Script-O-Rama was consulted during an exact quote/timestamp investigation. No full transcript read was assigned or completed. Script-O-Rama describes its text as a dialogue transcript transcribed from the screenplay and/or viewings, so it is not treated as a production screenplay.

## Exhaustion / coverage boundary

The audit searched the recoverable conversation-export sequence `conversations-000.json` through `conversations-010.json`, the older combined `chat.html`, Vera Project/Library exports and passdowns, known script/transcript-provider traces, and targeted title/source searches. Reverse-time searches repeatedly converged on the qualifying clusters above. No older movie-read assignment surfaced behind the 2025 Anchorman incidental lookup.

That establishes an **accessible-evidence exhaustion frontier**, not metaphysical proof that deleted, inaccessible, unindexed, or never-exported chats contained no other request. Any newly recovered historical source can reopen this registry without overwriting the provenance of the present cut.
