# Vera Desktop V2: Windows delivery and read-only acceptance gate

Source candidate: `thebrazenbeard/v-e-r-a` Draft PR #19 at
`51bdcdee50df7c220f03aa0e7dff3d0c61daa770`. Companion gateway:
`thebrazenbeard/vera-apk` Draft PR #12 at
`9bbcd3f78508200557146bd7adddb74a072ea3aa`.

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
- Existing Tauri `v2_enrolled()` returns false when the token file is lost,
  conflating previously enrolled credential loss with never-paired legacy
  preview; this can undermine the no-silent-downgrade claim. Must be fixed
  and adversarially tested before deployment.
- WinForms and Tauri preview share obvious product identity (`0.1.1`/preview
  name), making version/title-only field verification unreliable.
- The screenshot showing `Legacy V1 preview` is positive evidence of the
  active old path, not evidence that V2 is broken after installation.
- No source-only test here validates WebView2 interactive runtime, desktop
  shortcuts, encrypted persistence at rest, Android V2 or actual model gain.
