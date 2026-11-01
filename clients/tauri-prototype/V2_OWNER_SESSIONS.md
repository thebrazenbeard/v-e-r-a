# Vera Desktop V2 session/replay client — isolated source candidate

This source candidate follows Vera Tauri draft PR #19 (observed head
`51bdcdee50df7c220f03aa0e7dff3d0c61daa770`) and combines earlier local
Rust V2 validation (`419e2c75d81c9e8567dc5f37438e5daea2c5bcd7`) with
the model-discovery safeguards from local UI patch (`7bd6a8570b9d77363cf87dab6f3e75bd42441004`).
**It has not been merged, installed, or accepted by the owner.** The original
V2 design extended earlier Vera Tauri PR #18 (head `c9f07b928524b784c946448af31583f84d34169a`)
with a Windows Tauri client for the **separate** Vera V2 device gateway
in Vera APK draft PR #12 (V2 bound to 127.0.0.1:18781, **not deployed**).

## Changed behavior
- Detect `%LOCALAPPDATA%\VeraDesktop\device-v2-token.txt` from Rust only
  (not exposed to JavaScript). The file must be provisioned out of band
  by an authenticated owner-controlled local administrator. This branch
  **does not enroll your actual devices**.
- If the V2 token exists, use only `/v2/models`, `/v2/sessions`,
  `/v2/sessions/{id}/history` and `/v2/chat`. Sessions are server-issued
  and owner-authorized. The desktop has a **New chat** and a session picker;
  reconnect restores encrypted history rather than generating an
  unrelated local conversation ID.
- A V2 failure **never** silently downgrades to the old shared V1 bearer.
  On the first valid local credential observation, Rust persists a companion
  versioned `%LOCALAPPDATA%\VeraDesktop\device-v2-enrolled.marker` using
  exclusive creation and sync. A missing token **with that marker present**
  is a hard enrollment error, not permission to use V1. A damaged token or
  marker likewise fails closed. Only absence of **both** means the client
  treats the profile as never enrolled and offers explicitly labeled legacy
  V1 preview without cross-device history. This marker is nonsecret and is
  not an independently authenticated owner enrollment record.
  Original Android 0.2.3 and Lappy :18777/8443 production routes remain
  unaffected.
- Model output is inserted through DOM `textContent`, not HTML,
  and credentials are confined to the Rust host. The Rust V2 client
  rejects missing authority marker, invalid session identifiers, excessive
  messages, model mismatch and redirects/proxying. The API is loopback only.
- SEND appends the outgoing bubble and clears the composer immediately.
  If the reply is interrupted, status says **delivery uncertain** rather
  than falsely certifying that a write failed. A later **manual** retry of
  identical V2 model, owner session and message during the same desktop
  process reuses the uncertain request ID; changing any of those values
  generates a different ID. No retry is automatic. Owners must **reconnect
  and check V2 history before manually retrying**. In-process gateway dedupe
  is not durable exactly-once protection after a gateway crash/restart.
  When a retrieved owner-scoped history entry carries the **same request ID,
  user text, and model** in the same session, it reconciles the pending
  request, replaces pending UI bubbles with the persisted exchange, and
  clears only an unchanged restored draft. A changed unsent draft is kept.
  Missing or nonmatching entries in bounded history **do not prove the
  request failed** and cannot silently clear the pending identity.

## Source/tests
- This follow-up's source-only UI suite: **13/13 Node/JSDOM tests passed**
  in an isolated scratch checkout, reusing an already installed local JSDOM
  dependency directory. These cover missing-pairing fallback, V2 denial,
  session replay, V1 failure recovery, uncertain V2 request-ID reuse, and
  reconnect reconciliation without automatic retry or draft loss.
  Rust regression sources cover token deletion after enrollment and malformed
  marker state, but **Rust tests have not been executed here** (`cargo` and
  `rustc` unavailable). No remote exact-head CI or Windows live test is claimed.
- Node 24 / JSDOM: **4/4 tests pass**, covering fail-closed V2, history
  retrieval, V2-scoped sends and explicitly labeled legacy mode.
- Rust `cargo test --release --lib`: **2/2 unit tests pass**.
- `npm run tauri -- build --no-bundle`: release compile passed on Lappy
  with isolated Rust 1.99.1 and Tauri 2.12.5.
- Companion V2 gateway PR #12: **34/34 Python tests**, and real
  synthetic `vera-local:latest` same-owner encrypted retrieval,
  cross-owner/revocation rejection and cleanup. STM encrypted
  replay lookup is separate draft PR #12 in the STM repository.
- There is **no Windows GUI acceptance** in the noninteractive Executor
  session: WebView2 previously returned HRESULT 0x80070578. This
  remains a blocking interactive gate. A build is not proof of runtime.

## Honest remaining issues
- No V2 device has been owner-enrolled, no V2 gateway installed as a
  durable service and **no phone V2 client exists yet**.
- The marker and bearer live in the same user-controlled profile. Removing
  **both** defeats the local ever-enrolled signal, and an attacker can mutate
  files or race filesystem checks. Production must require an independent,
  authenticated owner enrollment registry and an owner-approved secure
  provisioner/rotation mechanism; a marker is only defense in depth.
- Uncertain request IDs are **not durable across desktop process restart**;
  server deduplication is in-process only, so even the same ID may produce a
  second inference after a gateway restart. A visible failed response does
  not prove that the first write failed. Require explicit history review.
- Sessions shared by owner become accessible only after separate
  owner-approved per-device credentials and a qualified service.
  Existing V1 conversations are not silently assigned to V2 owners.
- Device token still resides in a local file; production enrollment
  must improve platform-secure credential storage, backup, rotation,
  revocation, audit and machine ACLs before deployment.
- Current concurrency dedupe is in-process; no cross-process/distributed
  exactly-once guarantee. STM's 30-day-to-DMS policy remains source-only,
  not installed retention governance.
- Neither Tauri GUI performance nor installer code-signing is qualified.

Native ChatGPT specialist subagent dispatch was unavailable; test evidence
comes from real Lappy build/unit tools and independent remote probes.
