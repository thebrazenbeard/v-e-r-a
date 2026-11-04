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
It requires a literal localhost Host header, denies cross-origin requests,
and expires slow request headers or partial bodies within 12 seconds even if
the client trickles data. Upstream timeout is capped at 75 seconds, leaving
time inside the existing UI gateway's 90-second limit. A disconnected client
will not be retried, although a chat already submitted upstream cannot be
guaranteed cancelled without a runtime-specific cancellation API. The bridge
preserves verified `stop`, `length`, or `content_filter` completion reasons.

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
```
