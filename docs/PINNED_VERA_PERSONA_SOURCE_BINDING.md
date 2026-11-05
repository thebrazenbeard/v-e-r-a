# Pinned Vera voice source (opt-in, prompt-only binding)

This repository now has an **opt-in, offline source adapter** at
`interface/persona_profile.py`. The interface can now bind it to the restricted
system-prompt slot **only when the owner explicitly supplies a verified file**.
Ordinary launches remain unchanged. This does not provide authenticated model
identity, memory, recovery, tool access, or a verified conversational result.

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

For the optional Android-governed interface mode, the owner must also provide
the separately pinned canonical `docs/NONVERBAL_STATUS_BAR_V1.md` from Vera
(Git blob `887bfe1d6862d23550b224a00a60e32d197e8c1f`).
The hybrid interface checks this second file at startup before attaching
`presentation_blob_sha` to the typed persona receipt. Both copyrighted
sources remain **outside** the public `v-e-r-a` repository. An ordinary
generic local UI launch remains functional with no persona configured;
`--require-persona` rejects launch unless both checked owner files exist.
**Important distinction:** checking the presentation blob's exact bytes
establishes an admitted source reference only. The interface does not read
its prose into the system prompt or enact its nonverbal cue rules. The
`presentation_blob_sha` receipt is not a claim that an actual GGUF generated
those cues, adopted a body, or implemented the status-bar behavior.
The typed receipt explicitly marks
`presentation_implementation=ADMITTED_SOURCE_REFERENCE_ONLY`.

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

## Source-only conversation binding (opt-in)

An owner starting the loopback prototype may add
`--persona-profile-file /ABSOLUTE/PATH/TO/PROVISIONED_PROFILE.json` to
`python -m interface`, or call `make_server(persona_profile_path=...)`.
The governed APK-compatible variant additionally needs
`--persona-presentation-file /ABSOLUTE/PATH/TO/NONVERBAL.md` and
`--require-persona`. Both pinned owner files must validate before startup;
the generic interface works without either. A generic endpoint is deliberately
rejected by the APK's governed backend profile check.
The path must refer to exactly the pinned bytes above. Invalid/missing files
fail closed **before opening the interface listener**. No path or profile JSON
is sent to the browser. The verified, bounded text is read once at startup
and appended to the existing server-owned system note for `/api/chat`; browser
payloads still accept only bounded, alternating user-led `user`/`assistant`
messages ending with a user turn. The status API returns
`persona_prompt=pinned_owner_profile` plus the typed
`persona_source` receipt with `qualification=SOURCE_ONLY`,
`prompt_layer=server_owned_system`, canonical source hashes, and
`model_identity_attested=false` / `identity_attested=false`.
Unconfigured launches return `persona_source.qualification=NOT_CONFIGURED`.

This is *source and mocked integration*, not a deployed model. The operator
must separately determine that its endpoint accepts the resulting chat
template and system prompt, verify context/token budgets, and perform real
multiturn assessment. The interface's default reply cap is **192 tokens**,
operator-adjustable from 32 to 256; a separately configured bridge cap must
be at least as high. These caps constrain CPU time but can cut off long
answers. Never accept system text or the claimed source pin from the browser,
model, or self-reported `/v1/models`/`/api/tags` name. Retain the UI's
`MODEL OUTPUT / UNVERIFIED` label until independent host-model attestation.

The local gateway and its loopback bridge reject a non-assistant message
role, empty reply, unsupported finish reason, or tool call. An omitted or
null `finish_reason` is reported as typed `unknown`, not fabricated `stop`.
Explicit `length` and `content_filter` become `length_limited` and
`filtered`; only `stop` becomes `complete`. The browser can display these
fragments with an **UNVERIFIED PARTIAL** label but does not add them to ordinary
assistant history, subsequent prompts, or explicit saved completed turns.
This reconciles the truthful typed completion API needed by the phone with
the no-incomplete-history rule; it is not a claim that the model finished.
These are protocol checks only; none proves the model identifier or actual
weights are authentic.

The seed aims for recognizable candor, specific pushback, dry humor and
natural first-person language; **it is not evidence that a physical model
obeyed it or that trained Vera weights ran.** That needs actual protected
conversation tests, comparisons and runtime readback. A system prompt cannot
prevent every deceptive model-generated self-identification by itself.
