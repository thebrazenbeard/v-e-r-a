# Vera Desktop V2 session/replay client — isolated source candidate

This branch extends Vera Tauri PR #18 (head `c9f07b928524b784c946448af31583f84d34169a`)
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
  If no V2 token exists, the application continues to label the **legacy
  V1 preview** explicitly, without offering cross-device history.
  Original Android 0.2.3 and Lappy :18777/8443 production routes remain
  unaffected.
- Model output is inserted through DOM `textContent`, not HTML,
  and credentials are confined to the Rust host. The Rust V2 client
  rejects missing authority marker, invalid session identifiers, excessive
  messages, model mismatch and redirects/proxying. The API is loopback only.
- SEND appends the outgoing bubble and clears the composer immediately.
  If the reply is interrupted, status says **delivery uncertain** rather
  than falsely certifying that a write failed. Owners must check history
  before retransmitting under a new request ID.

## Source/tests
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
