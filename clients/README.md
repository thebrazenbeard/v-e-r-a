# Vera unified desktop prototype — 2026-10-28

This branch contains a **working Windows-native prototype** built with
WinForms/.NET 10 and a **portable .NET 10 gateway client**. It is intentionally
a build-time control experiment against the Council's favored Tauri 2 path.
No Rust toolchain or Tauri application is installed by this branch.

The client uses the *same live response-only Lappy gateway* as Android,
without duplicating Ollama access or storing a second plaintext transcript.
It reads the existing operator-owned pairing key from
`%LOCALAPPDATA%\VeraPhoneGateway\pairing-token.txt` **at request time**,
with no tokens in the .exe or Git and no external URL input or proxy use.
It saves only a random 32-character session identifier in
`%LOCALAPPDATA%\VeraDesktop\conversation-id.txt`; the conversation archive
is gateway-side, encrypted when STM is configured, and this app never
auto-exports history.

### Build and exercise on Lappy

```powershell
dotnet run --project clients/checks/VeraGateway.Checks.csproj -- --live
dotnet build clients/windows/VeraDesktop.csproj -c Release
dotnet publish clients/windows/VeraDesktop.csproj -c Release --self-contained false -p:PublishSingleFile=false -o D:\VERA\VeraDesktopPreview\0.1.0
```

Start `D:\VERA\VeraDesktopPreview\0.1.0\VeraDesktop.exe` on Lappy.
The framework-dependent executable requires the installed .NET 10 Windows
Desktop runtime; all files in the publish folder are part of the build.
It is **not** a signed installer, Windows Store package, or production
startup service. Do not copy the single .exe without its runtime config
and companion .dll files.

### Acceptance gates and limitations

The checks use a fake transport to prove allowed paths and auth-header
handling, bound schema, malicious role/identifier refusal, HTTP redirect
refusal and unexpected-authority refusal; `--live` checks the actual
loopback authenticated model list without writing conversation history.
The Windows GUI must additionally be inspected by a human on the actual
desktop before UI acceptance. Deliberately **no** executable is auto-launched
and no existing desktop shortcut, browser UI, gateway or Tailscale route
is replaced.

The source remains a proof of the shared-backend objective, not a decision
that WinForms is the final desktop shell. For durable Windows+Linux+Android
shared presentation, prototype Tauri 2 on an isolated toolchain and compare:
signed installer, cold-start, RAM, accessibility, keyboard, navigation, token
isolation, active model selection, loss/reconnect handling, bundled runtime,
and secure upgrades.

**Important:** The per-device principal/session authorization and
governed STM retention gaps in `contracts/VERA_SHARED_RESPONSE_V1.md`
remain open. Do not merge this into production as a fully unified
memory solution before those are solved.
