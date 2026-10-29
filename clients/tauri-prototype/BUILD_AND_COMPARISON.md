# Vera Tauri 2 Windows spike — build and honest .NET comparison

Based on Vera Desktop WinForms source PR #17 at exact head
`3f8a3157d9903005317e2fa3306479698f2fe285`.

## Delivered source and local build

- Tauri 2 / Rust local-only frontend with **no network, filesystem,
  shell or browser plugins exposed through WebView**. The *Rust host*
  reads the existing local bearer at request time; only Rust makes
  outbound HTTP to `127.0.0.1:18777`, with redirects and proxy-from-env
  disabled. No external URLs or remote web content, and the frontend
  uses `textContent` for untrusted model output.
- Original user-provided Vera wallpaper and icon. CSP, one app window,
  bounded local models and response-only chat commands, error/draft UI.
- Built under an isolated Rust toolchain:
  `D:\VERA\toolchains\tauri-rust-20261028`.
  Installed MSVC compiler and WebView2 runtime already present.
  `npm run tauri -- build --no-bundle` succeeded, Rust 1.99.1,
  Tauri 2.12.5. A subsequent `npm run tauri -- build` produced
  an **NSIS unsigned setup exe** (~2.02 MiB).
- The project includes reproducible package and Cargo lockfiles; only
  source, lockfiles and small assets should be committed. Neither
  binaries, toolchain, Rust cache nor user tokens are Git source.
- **This prototype still targets the legacy phone gateway V1.**
  Secure V2 device/session code lives separately in Vera APK PR #12;
  real owner-verified provisioning, persistent device identity and
  memory retrieval **are not integrated into this Tauri build**.
  It MUST NOT claim complete cross-platform secure memory.

## Comparison from same Lappy (2026-10-28)

| Method | .NET WinForms | Tauri 2 |
| --- | --- | --- |
| Source | Vera Desktop PR #17 | This branch |
| Windows release compile | ~2.2 sec with installed .NET | ~6m 12s initial Rust release (cache cold) |
| Installer | framework-dependent publish directory, no installer | NSIS setup exe, **unsigned** |
| Main executable size | 162,304 B | 9,249,280 B |
| Installer size | not built | ~2.02 MiB |
| Process run in Executor noninteractive session | stays alive but MainWindowHandle 0 | exits code 101: WebView2 WindowsError 0x80070578 invalid window handle |
| UI cold-start/time-to-interaction | **UNKNOWN** | **UNKNOWN** |
| Process memory fairness | benchmark 3× WinForms 55–58 MB after 3 s; headless WindowHandle 0 | not comparable: process exits before 3 s |
| Remote inference | .NET SDK V1 actual `vera-local` response verified | Rust source built; interactive IPC/inference **not qualified** |

Executable/window benchmark script: `benchmarks/compare.ps1`.
CSV generated on Lappy at
`D:\VERA\VeraDesktopPreview\comparison-20261028.csv`.
The noninteractive environment cannot create a WebView2 window. Neither
WinForms' noninteractive process memory nor Tauri's exit supports a fair
interactive GUI memory/startup claim. Run both from an authorized
logged-in Windows desktop and measure OS process tree/WebView2 children,
cold startup, CPU, RAM, input and reconnect before selecting a winner.

## Build from source on Lappy

```powershell
$base = 'D:\VERA\toolchains\tauri-rust-20261028'
$env:CARGO_HOME = "$base\cargo"
$env:RUSTUP_HOME = "$base\rustup"
$env:PATH = "$env:CARGO_HOME\bin;$env:PATH"
cd D:\VERA\v-e-r-a-tauri-20261028\clients\tauri-prototype
npm.cmd ci
npm.cmd run tauri -- build
```

The NSIS installer is not code-signed and must be treated as a local
experimental artifact. No automatic deployment, trusted publisher
claim, autostart, or production route modification has occurred.

Official references:
https://v2.tauri.app/start/prerequisites/
https://v2.tauri.app/security/capabilities/
https://v2.tauri.app/distribute/windows-installer/
