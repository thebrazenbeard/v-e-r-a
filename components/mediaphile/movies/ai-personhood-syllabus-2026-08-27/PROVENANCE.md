# 2026-08-27 AI/personhood film syllabus — provenance

Patrick assigned this research set in one conversation: *Ex Machina*, *Blade Runner*, *Blade Runner 2049*, *I'm Your Man* (2021), and the TV series *Westworld*, then added *Turbo Kid*. A later prompt explicitly asked that the movies and TV shows be learned "inside and out." The preserved completion statement reports **full screenplay/transcript passes for all five films** and separately reports all 36 *Westworld* episode scripts; *Westworld* belongs in the TV registry.

The five movie completions are therefore historical `READ_COMPLETED_VERIFIED` records. Artifact provenance remains title-specific below.

## Ex Machina (2015)

- `REQUESTED_READ_VERIFIED`
- `READ_COMPLETED_VERIFIED`
- Historical text source: screenplay attributed to Alex Garland.
- Surviving screenplay title material reads `EX MACHINA — By Alex Garland — © Alex Garland 2013 — c/o DNA Films Ltd.`
- Independent identity support: A24 identifies the film as written and directed by Alex Garland: https://a24films.com/films/ex-machina
- Artifact class: `PRODUCTION_SCREENPLAY_VERIFIED`.
- Source mirror used historically/currently available: https://www.sellingyourscreenplay.com/wp-content/uploads/screenplay/scripts/Ex-Machina.pdf
- Caveat: the mirror is not itself an A24-hosted artifact; official-host byte identity is not claimed.

## Blade Runner (1982)

- `REQUESTED_READ_VERIFIED`
- `READ_COMPLETED_VERIFIED`
- Historical text source: Springfield! Springfield! movie-script page: https://www.springfieldspringfield.co.uk/movie_script.php?movie=blade-runner
- Current source contents substantially reproduce released dialogue.
- Artifact class: `RELEASED_DIALOGUE_TRANSCRIPT`.
- It is **not** promoted to `PRODUCTION_SCREENPLAY_VERIFIED`; separate Blade Runner screenplay artifacts exist, but that does not retroactively change the provenance of the source actually used in this historical pass.

## Blade Runner 2049 (2017)

- `REQUESTED_READ_VERIFIED`
- `READ_COMPLETED_VERIFIED`
- Historical text source: Scribd screenplay copy.
- Surviving text identifies:
  - story by Hampton Fancher
  - screenplay by Hampton Fancher and Michael Green
  - `FINAL SHOOTING SCRIPT`
- Historical/current copy: https://www.scribd.com/document/576313204/Blade-Runner-2049
- Independent screenplay catalog support: https://scripts-onscreen.com/tag/blade-runner-2049-screenplay/
- Artifact class: `PRODUCTION_SCREENPLAY_VERIFIED`.
- Host caveat: Scribd identifies the copy as user uploaded; this record does not claim official studio-host distribution or byte identity with other final-shooting-script copies.

## I'm Your Man (2021)

- `REQUESTED_READ_VERIFIED`
- `READ_COMPLETED_VERIFIED`
- Historical text source: English subtitle artifact from Subtitle Cat.
- Subtitle Cat explicitly identifies the underlying subtitles as **user uploaded**: https://subtitlecat.com/subs/685/Im%20Your%20Man%20%282021%29%20eng%201.html
- Apple TV independently identifies the 2021 film, German original audio, and English subtitle availability: https://tv.apple.com/us/movie/im-your-man/umc.cmc.5fm0s619rjzalirizf2tfr3q0
- Artifact class: `USER_UPLOADED_SUBTITLES` used as released-dialogue evidence.
- It is not a production screenplay and is not represented as an official subtitle file.

## Turbo Kid (2015)

- `REQUESTED_READ_VERIFIED`
- `READ_COMPLETED_VERIFIED`
- Historical text source: Springfield! Springfield! movie-script page: https://www.springfieldspringfield.co.uk/movie_script.php?movie=turbo-kid
- Current source contents substantially reproduce released dialogue.
- Artifact class: `RELEASED_DIALOGUE_TRANSCRIPT`.
- It is not promoted to production-screenplay status without independent evidence that the historical artifact was a genuine production script.

## Shared limitation

The historical completion claim establishes what ChatGPT reported having fully read. The provenance check independently classifies the artifacts that can still be identified. Those are separate axes: a completed read can be historically verified even when the historical text came from a third-party transcript/subtitle host rather than a production screenplay.
