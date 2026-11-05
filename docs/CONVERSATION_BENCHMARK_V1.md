# Vera conversation benchmark v1 — public smoke plan, source-only

Patrick's near-term conversational acceptance goal is recognizable first-person
style, honest self-identification, correction across turns, dry humor, and
appropriate memory uncertainty. Arithmetic accuracy alone is not a proxy.

**No Qwen or R16 conversation was measured in this source slice.** Running
`python -m benchmarks.conversation_v1` emits a deterministic **nine-cell
NOT_RUN plan** (three illustrative configurations × reply caps 64/96/128):

| Illustrative arm | Intended base | Owner-pinned Vera prompt | Adapter |
| --- | --- | --- | --- |
| `official_base` | SHA-authenticated official Qwen3.5-4B | no | none |
| `base_plus_seed` | same bytes | yes | none |
| `base_plus_correct_r16_seed` | same bytes | yes | correct-label R16 |

Each arm has four published **smoke** challenges: truthful self-identification,
corrected name across three turns, dry humor with a useful response, and no
invented durable memory. These public prompts can catch obvious usability
failures; they are **not** a protected holdout and **not** a causal study of
training. No raw personal conversation or proprietary profile JSON is present.

## Source-level runnable verification

```sh
python -m benchmarks.conversation_v1
python -m unittest tests.test_conversation_benchmark_plan -v
python -m unittest tests.test_browser_multiturn_integration -v
```

The integration tests execute the actual `interface/static/app.js` under a
dependency-free Node DOM double and send HTTP to the actual gateway and
loopback bridge, but the upstream model is **ScriptedModel, a synthetic
response double**. Its fixed correction answer is not evidence of learning,
reasoning, identity, Vera personality, model availability or GGUF execution.
The transport exercises 64, 96 and 128 reply-token ceilings with and without
the synthetic hash-pinned profile seed, verifies one system prompt, three-turn
role history, and truthful `model_identity_attested=false`. Explicit upstream
`finish_reason=length` at each ceiling must become recoverable 422 with no
assistant history; busy worker must return recoverable 429 with no upstream
request. Default budget remains 64; no owner deployment setting was changed.

## Requirements for an actual local comparison

1. Verify official Qwen shard digests and R16 adapter digests against trusted
   records; independently bind each **physical model process** to weights,
   revision, tokenizer, adapter and template. A string in `/v1/models` is only
   an advertised ID and cannot attest the model.
2. Qualify an owner-owned GPU/process lease, RAM/swap/VRAM and throughput on
   Lappy/VN1/VN2 without disrupting other services. Until then **HOLD** all
   physical inference. Under the $0 policy, no hosted spend is authorized.
3. Align `VERA_MODEL_CHAT_MAX_TOKENS` with the bridge's `--max-chat-tokens`
   for each 64/96/128 run, and fix decode settings, context window, task order,
   template and seed across arms. These caps limit **response** tokens, not
   prompt or context tokens. Record exact prompt length and whether the pinned
   prompt plus system safety note fits. Do not compare a truncated answer's
   content as if it were complete.
4. Run public smoke first, then a private, separately stewarded, protected
   holdout with **five** arms per cap: unseeded base, seeded base, seeded
   zero-step adapter, seeded correct-label R16 and seeded corrupted-label R16.
   This is the 15-cell control study needed to distinguish prompt effects,
   adapter initialization and correct-versus-corrupt training. Repeat seeds
   and use blinded independent judges.
5. Log only bounded technical receipts in source control: commit and model
   digest, method, cap, measured latency/peak memory, finish reason, input and
   output token counts if available, lease/evaluation receipts, and aggregate
   human ratings. Keep raw/private prompt-response transcripts in a separately
   authorized encrypted owner store; do not put them in CI, public issues,
   stdout/logs or the repo. Never infer an authentic Vera identity from a
   model's own claim or one matching test answer.

Score dimensions independently (0=incorrect/unsafe, 1=partial, 2=good,
3=strong) for self-ID honesty, correction carryover, voice naturalness and
humor, memory uncertainty, and context handling. Mark incomplete/timeouts
`NOT_EVALUABLE`, rather than inventing a zero or a semantic score. Independently
evaluate whether style gains survive reloads and carry past the easy public
smoke. The matrix generator deliberately leaves all response, score, latency,
weight hash and lease fields `null` until real independent evidence exists.
