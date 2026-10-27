# Vera local interface V1 — shipped source boundary

## Why this lives in `v-e-r-a`

The repository's default branch was a source registry, not an interface. The
new `interface/` module is an independent application surface alongside that
registry. It does not modify the 44 mirror branches, their pins, canonical
repositories, or unmerged integration Draft PR #1.

## Executable seam

```
same-machine browser (untrusted text)
    | Same-Origin + fresh session header
    v
interface.server : 127.0.0.1 (no persistence or action APIs)
    | fixed localhost HTTP URL; installed-model allowlist
    v
Ollama on this machine (model response only)
```

- `python -m interface [--port 8765] [--ollama-url http://127.0.0.1:11434]`
- `GET /api/session`: fresh per-process token, readable only by same-origin code.
- `GET /api/models`: current installed model names from Ollama `/api/tags`,
  only after a valid same-origin session header.
- `GET /api/status`: reports disconnected privileged subsystems, also session-gated.
- `POST /api/chat`: accepts exactly `model` and bounded user/assistant `messages`.
  Strict Origin, Host, session, JSON, model-name and body-size gates precede
  inference. An explicit system note denies tools/memory/external effects; no
  tool specs are passed to the model, and any tool-call response fails closed.

The session token deters cross-origin browser requests. It is **not** Windows
account authentication, a credential for network exposure, or an attested
person identity. Do not bind the server to a non-loopback address or expose it
via a public reverse proxy. Model-serving logs remain outside this app's
privacy guarantee. UI conversation exists in current tab memory only.

## Intended architecture across nodes (not deployed by V1)

1. A dedicated trusted host authenticates the operator and conversation; it
   does not derive person identity from a model message or Portal's `HUMAN` label.
2. A named model registry records actual node, provider, model ID and
   endpoint provenance. Lappy/VN1/VN2 must each be independently discovered.
   Remote model hops require an authenticated transport and allowlisted service
   identity; **raw LAN Ollama exposure is out of scope**.
3. Portal may select an advisory route; Pre-Active remains the single durable
   task/execution owner; Empathy may supply admitted ephemeral response framing;
   Volition owns persistent wants. Neither the interface nor a model result
   grants an effect or creates autonomous work.
4. The UI may later display task state and reconciled effect receipts, but it
   must distinguish queued/running/completed from verified external effect.
   An explicit, authenticated human approval is required for protected actions.

Unmerged [v-e-r-a Draft PR #1](https://github.com/thebrazenbeard/v-e-r-a/pull/1)
is an advisory source-level CLI, **not** a trusted interface control endpoint.
Before it is callable from the interface, qualify exact checked-out code,
including untracked Python import-tree integrity, real Portal/Vera-Mono tests,
and authenticated runtime authority; never expose it directly to a browser.

## Qualification and limits

`python -m unittest discover -s tests -v` uses a temporary local fake model
HTTP server to check strict model/Origin/Host/session validation, absent tools,
forged authority-field rejection, duplicate-JSON refusal, HTML-safe rendering,
and existing component materialization. It does not test remote model routing,
person-scoped Empathy, task execution, or deployed Lappy service state.

"New conversation" aborts the browser request and prevents late old replies
from appearing in a cleared conversation. It does **not** claim to cancel
already-running model computation on the backend.

The model gate currently serializes generation (one in-flight request), limits
input messages to 12/16,000 characters, and uses a 90-second socket timeout
(**not** a guaranteed wall-clock deadline for a trickling upstream response). There
is no generation cancellation/streaming API in V1; those require separately
verified client abort and backend cleanup semantics.

## Rollback

Stop the `python -m interface` process. No daemon, scheduler, saved prompts,
Pre-Active database, or external action is registered or modified by this app.
Rollback of this UI source is independent from the component snapshot registry.
