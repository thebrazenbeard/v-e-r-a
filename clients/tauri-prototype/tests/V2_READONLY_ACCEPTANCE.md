# Vera Desktop V2: Windows delivery and read-only acceptance gate

Source base: `thebrazenbeard/v-e-r-a` Draft PR #19 at
`51bdcdee50df7c220f03aa0e7dff3d0c61daa770`, plus source-hardening Draft
PR #21 at `e7784c60f0acb304e1c0af484a331a3e03555681`. Companion gateway:
`thebrazenbeard/vera-apk` Draft PR #12 at
`9bbcd3f78508200557146bd7adddb74a072ea3aa`, with source-hardening Draft
PR #15 at `ddf3de07cb08ced73c36412226fec973961350d1`.

**This is a source-only qualification aid, not an installation receipt.** The
Tauri config still identifies the app as `Vera Desktop Preview`, version
`0.1.1`, identifier `com.vera.desktop.preview`, NSIS unsigned installer. A
matching title or version string does **not** prove the running process is V2;
the existing V1 preview can present the same visible identity. Old V1 gateway
`:18777` and original Android route must remain untouched.

## Hermetic source test (safe anywhere)

```powershell
cd <authorized-v-e-r-a-source>\clients\tauri-prototype
py -3 -m unittest discover -s tests -p test_v2_readonly_probe.py -v
py -3 tests\v2_readonly_probe.py
```

The second command is **dry-run**: no credential read, no network or model
inference. Tests use in-process fake HTTP responses, synthetic IDs and tokens,
and perform no socket binding or host access.

### Optional read-only Windows process/shortcut inventory

`v2_windows_inventory.ps1` is inert by default. Its `-Inspect` mode is a
local, read-only inventory; it neither provisions a device nor touches the
V1 service, scheduled tasks, files or desktop shortcuts. Run it only in a
separately authorized Windows session:

```powershell
powershell.exe -NoProfile -File .\tests\v2_windows_inventory.ps1
powershell.exe -NoProfile -File .\tests\v2_windows_inventory.ps1 -Inspect -ExpectedClientExe '<reviewed installed Vera exe path>' -ExpectedClientSha256 '<reviewed 64-character installer-extracted exe hash>'
```

The result reports the existence of the authoritative `D:\VERA` root, a
supplied exact executable hash/running-process match, Vera-named desktop
shortcut names, and observed listening addresses for V1 `:18777` and V2
`:18781`. It deliberately **never** reports `releaseQualified=true`: a PID,
binary hash and loopback socket cannot authenticate a V2 gateway service,
establish owner enrollment/consent, verify file ACLs, or prove encrypted
history and interactive GUI work. A missing expected exe/hash also never
passes. It does not read pairing tokens or model/conversation data. The
host-independent contract test checks only source safety properties; a
PowerShell runtime/Windows qualification is still required. Before using
`-Inspect`, parse-check the script with Windows PowerShell's
`System.Management.Automation.Language.Parser.ParseFile` API and run its
default dry-run under the target operating-system version.

## Optional owner-controlled gateway probe (future, separate authorization)

Only after the route owner confirms the dedicated V2 gateway is listening
locally, the scoped host/GPU lease permits read-only checks, and a separately
enrolled **test** device has a revocable credential, run:

```powershell
py -3 tests\v2_readonly_probe.py --probe --root http://127.0.0.1:18781 --token-file <test-device-token-file>
```

- Exactly `GET /v2/models` then `GET /v2/sessions`. No history body, session
  creation, chat, writes, model loading or GPU generation.
- No proxy, redirect, remote host or credential on the command line. Token
  contents are read from a local file at request time and never printed.
- Fail-closed on missing/invalid credential, 401/403, redirect, invalid
  authority marker, malformed JSON, excessive payload, or bad inventories.
- Output is a sanitised JSON result with pass/fail and counts only. No bearer,
  model names, owner IDs, session IDs, conversation text or host paths.
- The gateway endpoint is **not** a substitute for authenticating who owns the
  installed Windows GUI. The probe only checks two read-only API contracts.

**Security caution:** this harness does not inspect the ACL of a supplied
credential file and does not enroll or store platform-secured credentials.
That remains a separate owner-controlled security gate. Do not point it at
Patrick's existing real bearer. Never commit test credentials.

## Windows installation qualification — evidence required

1. **Exact source and binary:** record canonical reviewed Git head, Cargo
   lockfile hash, installer build command/toolchain, packaged NSIS SHA-256,
   unpacked installed EXE SHA-256 and Windows executable `ProductVersion`.
   Compare the running process executable path and SHA-256 to the exact
   reviewed installed binary, not just the desktop shortcut icon/title.
   The unsigned NSIS build must be labeled experimental.
2. **Non-destructive ownership:** inventory all Vera process executable paths,
   services, listening loopback ports, desktop/start-menu shortcuts and
   `TargetPath`/arguments. Get an explicit owner-scoped installation window
   and keep a recoverable V1 backup. Avoid terminating or replacing the
   current V1 process until approved. Do not assert "only one shortcut"
   merely because one desktop `.lnk` was found.
3. **Dedicated route:** verify actual listening PID and process image for
   `127.0.0.1:18781` and demonstrate `:18777` unchanged. Require an
   owner-bound V2 test identity; no credential copying across devices.
4. **Interactive desktop:** launch the exact reviewed binary in the authorized
   logged-in Windows session and verify WebView2 window creation, model list,
   enrollment UI, New chat, session picker, reconnect and error handling.
   The previous noninteractive WebView2 error `0x80070578` is **not** a GUI
   pass. Capture process tree and UI screenshots without credential contents.
5. **V2 behavior:** under a separately approved controlled test session,
   establish fresh server-issued session, persist one **synthetic** turn,
   relaunch, recover the identical encrypted owner history, reject cross-owner
   and revoked device access, and verify no fallback to V1 when an enrolled
   credential is lost or malformed. This requires a different, mutation-authorized
   test plan; the read-only probe cannot certify it.
6. **Release:** repeat tests on the final immutable source/binary hash,
   adversarial review, CI and interactive smoke tests. Only then consider
   installer/shortcut replacement, with rollback and post-install health.

### Known blockers at this source head

- PR #19 and companion V2 gateway PR #12 remain draft/source-only; no evidence
  of a V2 installer installed or durable V2 gateway on Lappy.
- The PR #21 local marker fix prevents fallback when a previously enrolled
  device loses **only** its token. Both bearer and marker remain in the same
  user-controlled profile: deletion of **both** can still permit legacy
  preview selection. Owner-enforced enrollment provenance remains missing.
- WinForms and Tauri preview share obvious product identity (`0.1.1`/preview
  name), making version/title-only field verification unreliable.
- The screenshot showing `Legacy V1 preview` is positive evidence of the
  active old path, not evidence that V2 is broken after installation.
- No source-only test here validates WebView2 interactive runtime, desktop
  shortcuts, encrypted persistence at rest, Android V2 or actual model gain.
