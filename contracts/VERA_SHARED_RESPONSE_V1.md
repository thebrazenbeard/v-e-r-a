# Vera shared response-only gateway contract (V1, SOURCE CANDIDATE)

The currently deployed **Android** interface communicates through Tailscale
HTTPS port 8443 to a Lappy-only gateway on 127.0.0.1:18777. The first
**Windows** prototype calls the exact same gateway on 127.0.0.1:18777,
never opens the LAN port, and therefore shares one inference and encrypted
conversation-journal **service**. The existing browser interface on
127.0.0.1:8788 remains independent and unchanged.

## Wire contract

The network access control is **not** browser Origin or a client-supplied
identity. Requests require the installed `Authorization: Bearer <token>`
over loopback (Windows) or tailnet-only HTTPS (Android). Never publish, log,
hardcode or embed that token in web assets, Git or release metadata.

| Request | Body | Required response |
| --- | --- | --- |
| `GET /v1/models` | none | `{models:[string],node:"local",mode:"response_only"}` |
| `POST /v1/chat` | `{model,messages:[{role,content}],session_id,request_id}` | `{model,reply,node:"local",mode:"response_only"}` |

The gateway retains compatibility with older Android bodies having only
`model,messages`. Message roles are `user` and `assistant` only. Model
name must exist in the installed local inventory. Limits: 32 KiB request,
12 messages, 4096 chars/message, 16K reply, bounded timeouts.

When the optional local STM phone journal is configured, it can append a
successful user/assistant exchange by a unique opaque request ID and load up to
eight recent entries (14 KiB) for the same opaque session. The *client's*
session ID is an identifier, **NOT** proof of caller identity. The model
receives no filesystem/tools/effect authority.

## Trust boundaries and negative findings

1. **The current bearer key is shared by Windows and Android.** The gateway
   does not have per-device credentials, revocation, authenticated principal
   to session authorization, or a history-read endpoint. High-entropy opaque
   session IDs reduce guessing risk but **do not** solve this authorization gap.
   Do not add a cross-device history browser until a real owner principal,
   device binding, scope ACL, revocation and adversarial tests exist.
2. **Shared journal database is not shared open conversation.** Windows uses
   a separate persisted per-install session; Android's app uses its own
   private session. Both can collect history in the same local encrypted
   journal, but their active threads are not merged automatically.
3. **STM v0.1–v0.6 source candidates in separate draft PRs are not installed**
   or the live phone journal implementation. Especially respect verified
   consent, bounded retention and day-30 review before calling any ingestion
   a governed long-term memory system.
4. The existing 8788 browser UI uses a fresh same-origin session header,
   opt-in transcript vault and separate trust boundary. **Do not proxy or
   give that browser token to 18777**; neither token authorizes the other.
5. No public router forwards, Tailscale Funnel, raw Ollama port, arbitrary
   remote URL, programmatic autostart, tool effects or background sync.
6. `/v1/chat` currently sends completed text only, not streamed tokens;
   client UI may show progress but cannot guarantee immediate delivery.

## Admission before permanent architecture

Qualify versioned contract against the exact Android and Windows clients,
negative auth/replay/cross-session tests, encrypted STM retention and
provenance, service restart persistence, and migration of the 8788 browser
interface without weakening its Origin/Host/session protections. Record
explicit source/build/install/runtime evidence separately.
