# Pinned Vera voice source (component only; no installed binding)

This repository now has an **opt-in, offline source adapter** at
`interface/persona_profile.py`. It does not run during ordinary PR #24 chat
requests. It does not provide authenticated model identity, memory, recovery,
tool access, or a verified conversational result.

## Owner-governed source

| Item | Exact subject |
| --- | --- |
| Repository | `thebrazenbeard/vera` (public source, source-available proprietary license) |
| Commit | `6783c0ac8da9286db9b0094426d0c4f08822220f` |
| Path | `architecture/identity/VERA_BEHAVIOR_PROFILE_V1.json` |
| Git blob | `0c79625b993a559bd22a6fbe68279450fc736eb2` |
| Raw-file SHA-256 | `ec1defa8fcf96371a427991d40695842ffe6794aeb2e3f26c69ef5f528ee7d6d` |
| Schema/version/lifecycle | `VERA_BEHAVIOR_PROFILE_V1` / `1.0.1` / `CURRENT` at this pin |

The upstream `vera/LICENSE` restricts redistribution of source and derivatives.
**Do not vendor or automatically download the profile JSON into this public
repository.** The copyright owner/authorized operator must separately supply
the exact file locally, subject to the source rights and privacy scope.
No personal chat exports, autobiographical notes, model responses or W40
transcript fragments are included here as persona source.

## Bounded manual check (Windows or Linux)

With a legally provisioned profile at a known local path, the operator can
call `render_persona_seed(Path(...))` from Python after adding the repository
to its import path. It returns a `PersonaSeed` record containing inert
`system_message` text and the immutable source pin. It performs no HTTP request,
file writes or model operation. The caller must explicitly supply a path;
there is no environment variable or default profile lookup.

If the file is absent, modified, too large, malformed, wrong version, or no
longer marked `CURRENT`, admission raises `ProfileAdmissionError`. A newer
governed behavior profile requires source re-orientation, review and a new
pin, not an unreviewed fallback or silently upgraded alias.

## Future conversation integration — not implemented here

`interface/server.py::_chat` currently creates its own generic system
message and has not been changed by this component. A separately reviewed
integrator can pass the verified `PersonaSeed.system_message` in a bounded
server-owned system slot, preserving existing tool/effect and recall
boundaries. Never accept system text or the claimed source pin from the browser,
the model, or a self-reported `/v1/models`/`/api/tags` name. Retain the UI's
`MODEL OUTPUT / UNVERIFIED` label until independent host-model attestation
is established.

The seed aims for recognizable candor, specific pushback, dry humor and
natural first-person language; **it is not evidence that a physical model
obeyed it or that trained Vera weights ran.** That needs actual protected
conversation tests, comparisons and runtime readback. A system prompt cannot
prevent every deceptive model-generated self-identification by itself.
