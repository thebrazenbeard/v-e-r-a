# Independent local-model review of unified Vera prototype — 2026-10-28

Native ChatGPT `collaboration.spawn_agent`/delegation was **not available** in
this session. The following are real local Ollama **model review calls**, not
native ChatGPT child agents, independent software builds, or proven adversarial
attacks. All were invoked in isolated local processes with read-only briefs
and **no files, secrets, tools or deployment permissions**.

| Reviewer scope | Actual model/device | Response |
| --- | --- | --- |
| Systems Architect — try to falsify composability | `qwen3:8b` / Lappy | complete, `done_reason=stop` |
| Security Red Team — attack credentials/scope | `vera-local:latest` / Lappy | complete, `done_reason=stop` |
| STM/privacy — cross-device memory scope | `qwen3:1.7b` / VERA-NODE-1 | complete, `done_reason=stop` |
| UI/accessibility/release | `gemma3:1b` / VERA-NODE-1 | truncated, `done_reason=length` |

## Findings reconciled against observed source

**FAILS for full shared-memory claim**: both Android and Windows share one
encrypted journal *database* and infer through the same Lappy service, but
the browser's 8788 transcript vault remains distinct. The gateway uses a
single bearer token and client-supplied session IDs to choose prior turns.
There is no independently qualified authenticated device/principal-to-session
access check. A shared token authorizes the endpoint, not a particular
conversation. A separate session ID per client is useful for segregation but
not a security principal. No history-read endpoint has been admitted.

**SURVIVES narrow proof:** a native Windows client can compile with installed
.NET 10, call the same local gateway as Android, and elicit a live
response-only model answer using the gateway's encrypted STM journal. Negative
SDK contract checks prove redirects, auth failure, invalid roles and unexpected
authority are rejected; they do **not** prove per-device authentication.

**UNKNOWN**: GUI rendering/accessibility in an actual interactive Windows
session; Windows app restart/resume behavior; Android integration after
future token and identity changes; Tauri installer build; Linux runtime;
governed day-30 retention, private DeepMemoryStorage handoff and delete
propagation; cross-device session ownership and recall.

### Red-team corrections

The local security model proposed arbitrary **7-day key rotation** and a
**1-day journal retention cap**. Neither duration is a verified user policy
or grounded in installed STM source, and the latter conflicts with the
user's 30-day review direction. **Reject these arbitrary numbers.** Design
rotation and an authenticated owner-specified retention policy instead.
It also warned about **WebView XSS in the WinForms prototype**, but this
prototype has no WebView or HTML interpreter. Its untrusted model reply is
rendered as plain RichTextBox content. Navigation/XSS controls will be
mandatory if a future Tauri WebView host is implemented.

## Unresolved release blockers

1. Introduce per-device, revocable gateway credentials and server-attested
   owner-to-session access control; test wrong-device reads and token replay.
2. Evaluate STM v0.5/v0.6 PRs against the current phone journal and the
   operator's actual retention policy, before exporting to DeepMemoryStorage.
3. Add an authenticated, scoped history/rejoin API with provenance and
   deletion correction semantics; preserve old Android compatibility only
   behind explicit migration gates.
4. UI smoke with real Windows desktop (window/title, keyboard, resize,
   screen-reader, theme), phone Wi-Fi-to-cellular transitions, reboot recovery.
5. Implement a Tauri 2 comparison in a separate branch, build a real signed
   installer, then measure RAM/cold start against this working .NET control.

Source/demo PR is intentionally **draft** and existing 8788 UI, 18777 gateway,
Tailscale Serve, STM database and canonical main remain unchanged.
