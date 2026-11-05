# Vera local GGUF model bridge (source-only; no deployment)

`interface.loopback_model_bridge` offers a localhost-only HTTP compatibility
bridge between Vera's existing UI gateway and a separately running local
llama.cpp/KoboldCPP **OpenAI-compatible** server. It creates no server process,
downloads no model, uses no paid service, and has no write authority.

Once an operator has independently installed, verified, and started a local
model endpoint, discover its exact model ID with `GET /v1/models` and health
with `GET /health`. Example command (replace both values with verified facts):

```sh
python -m interface.loopback_model_bridge \
  --upstream http://127.0.0.1:11435 \
  --model-id EXACT_ID_FROM_UPSTREAM_V1_MODELS \
  --port 11439
```

The command above is an **example**, not a claim that port 11435 or any
particular Vera model is installed or compatible. Point the existing Vera UI
gateway's model URL to `http://127.0.0.1:11439`. It discovers the model through
`GET /api/tags` and sends chat to `POST /v1/chat/completions`.

The bridge checks upstream `/health` and exact `/v1/models` identity on every
discovery and chat request; a missing/swapped model, timeout, redirect, or
malformed reply fails closed. It accepts only bounded non-streaming text chat;
no tools, remote hosts, arbitrary HTTP routes, or upstream metadata are
forwarded. It binds `127.0.0.1` only, with a bounded request concurrency limit.
The bridge **and** UI gateway separately reject an upstream message whose
`role` is not exactly `assistant`, or whose response content is empty. An
upstream `role=system` text with `finish_reason=stop` therefore cannot be
relabelled as Vera's completed assistant speech by the bridge.
It requires a literal localhost Host header, denies cross-origin requests,
and expires slow request headers or partial bodies within 12 seconds even if
the client trickles data. Upstream timeout is capped at 75 seconds, leaving
time inside the existing UI gateway's 90-second limit. A disconnected client
will not be retried, although a chat already submitted upstream cannot be
guaranteed cancelled without a runtime-specific cancellation API. The bridge
preserves verified `stop`, `length`, or `content_filter` completion reasons.
If the upstream omits `finish_reason` or explicitly supplies `null`, the bridge
preserves that uncertainty. It must **not** manufacture `stop`; the Vera UI
gateway reports an `unknown` completion state instead of claiming a finished
answer. Unsupported completion reasons remain errors. In the browser,
`length_limited`, `filtered`, and `unknown` text is visibly marked
`LOCAL MODEL / UNVERIFIED PARTIAL` and deliberately **not** appended to the
assistant conversation history or subsequent model requests. It remains
visible to the operator as an unverified fragment, but cannot be promoted by
the UI into a saved completed assistant turn. The next question forms a new
coherent user-led context without inventing the omitted assistant answer.
All upstream transactions now use a monotonic **total wall-clock** deadline
over connection, response headers, and response body, plus bounded response
bytes. This also closes the upstream socket if a model server trickles bytes
faster than a normal idle-read timeout would expire. Separate mock regressions
exercise 16 simultaneous body-drip chats and trickling response headers.

**Identity limitation:** the live model ID is *self-reported by the upstream*.
This check does not authenticate the physical GGUF file, hash, version, or
loaded weights. A trustworthy deployment requires separate weight-provenance
and actual inference readback against the chosen physical model. The bridge
cannot establish that a local process is an official Vera model.

**State separation:** model weights belong to the operator-managed inference
server; conversation history remains under Vera's existing explicit local
transcript controls. Retrieved knowledge/memory and governed plastic state
are not connected to this bridge and cannot be written through it. Every
health response declares `effect_authority: false`; the host adapter's
`effect_authority=false` boundary remains unchanged. Restarting the bridge
does not delete or update model weights or persisted UI transcripts; it also
does not acquire persistent memory merely by restarting. No external effects
are exposed.

Mock protocol verification (no model weights or real inference):

```sh
python -m unittest discover -s tests -p 'test_loopback_model_bridge.py' -v
python -m unittest tests.test_three_process_loopback_smoke -v
node --test tests/test_vault_ui_state.mjs
```

The second test launches **three genuine, independently bound subprocesses**
on ephemeral localhost ports: a deterministic synthetic OpenAI-compatible
upstream, this bridge, and the real Vera UI gateway. It verifies 192-token
requests, source-owned persona metadata, multi-turn alternation, truthful
completion, and rejection of non-assistant or empty model replies through
actual HTTP. It terminates its own processes. The synthetic upstream is a
protocol test double; no GGUF inference or host-substrate qualification occurs.

**Stack integration HOLD (2026-11-05):** GitHub Draft PR #24 was updated to
`22b7dbbff1b1407a7d8fdc604a5182da8f7c10dc` after Draft PR #25
branched from `f5da5991a32135c3d6812f1eb4c4f46221e747da`. PRs
#25→#28 are therefore **not** an integrated descendant of the latest #24.
PR #24's owner-provisioned, pinned `--persona-profile-file` opt-in contract,
licensing rationale, and fail-closed incomplete-output behavior materially
conflict with PR #25–28's source-vendored, always-on persona and typed
`complete|length_limited|filtered|unknown` response contract. A passing
test against either independent head does **not** qualify their combination.
Before merge, a distinct reviewed integration branch must preserve #24's
non-redistribution policy and opt-in verified owner source, #28's strict
inbound user-led alternation, both layers' strict outbound assistant-role
validation, and the typed completion fields expected by the governed APK.
Incomplete text must never be ordinary completed chat history. The eventual
live model still needs a separate host lease and behavioral evaluation.

## Bounded local end-to-end operator smoke (not executed here)

Run all three processes in the **same trusted Windows or Linux/WSL network
namespace** for the simplest loopback configuration. On WSL, do not assume a
Windows-host `127.0.0.1` endpoint is reachable without checking actual WSL
network forwarding. Every example below uses loopback only; never replace it
with `0.0.0.0` to make the prototype work.

1. Start an already installed, separately verified GGUF inference engine
   (llama.cpp or KoboldCPP) with its **OpenAI-compatible HTTP endpoint** bound
   to `127.0.0.1:11435`, a model source independently verified by hash, a
   bounded context, and no other shared service displaced. Engine-specific
   flags vary; this repository does not launch the engine or attest its
   model weights. Verify `GET http://127.0.0.1:11435/health` and
   `GET http://127.0.0.1:11435/v1/models` first.
2. Take the **exact** `data[].id` from that live models response. Then, in a
   separate terminal in this repository:

   ```sh
   python -m interface.loopback_model_bridge \
     --upstream http://127.0.0.1:11435 \
     --model-id EXACT_ID_FROM_UPSTREAM \
     --port 11439
   ```

3. In another terminal, start the local UI gateway, with its source-pinned
   Vera persona and bounded CPU reply budget:

   ```sh
   python -m interface \
     --port 8765 \
     --ollama-url http://127.0.0.1:11439 \
     --max-response-tokens 192
   ```

4. Open `http://127.0.0.1:8765/` in the same host context. Ask three
   consecutive questions with one correction. Verify that later model
   requests carry only coherent, bounded user-led conversation; that status
   identifies a configured persona rather than an attested model identity;
   and that missing upstream completion metadata is reported as `unknown`.
   A green mock test or a self-reported model ID does **not** prove live
   conversational quality.

5. Optional durable transcript: stop the UI process and relaunch it with
   `--memory-db OWNER_PRIVATE_PATH` plus `--memory-secret-file
   OWNER_PRIVATE_SECRET_PATH` (and an optional separately protected
   `--memory-rollback-anchor`). Create those files using owner-private
   filesystem permissions; never paste the vault key into a shell history,
   URL, log, or issue. Explicit Save, Restore, authenticated Recall and
   Delete are separate user choices. Saving a transcript does not update
   model weights or grant it identity authority. A Delete cannot erase old
   backups or the text still visible in another active conversation.

Stop all three test processes when finished; nothing here installs a daemon,
publishes a listener, or requires a paid service.
