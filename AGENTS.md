# V-E-R-A repository instructions

Scope: contributors and coding agents working on `thebrazenbeard/v-e-r-a`.
This is a public source registry and a bounded local UI, **not** the installed
VeraOS runtime or the authority for other repositories' source decisions.

## Source and authority

- Read accepted `main`, relevant source/tests and open draft heads before
  changing contracts. Keep accepted behavior distinct from proposals, mock tests,
  CI results and actual host observations. A documented capability is not a
  running or qualified service.
- Treat upstream component repositories as their respective source owners.
  `components.json` pins and mirror branches do not grant permission to edit,
  replace or silently refresh another component. Preserve provenance and the
  materializer's refusal to overwrite or accept unreviewed drift.
- `D:\VERA` is the authorized Windows ecosystem root; `C:\VERA` is obsolete.
  Do not guess host paths, installed services, tunnel URLs or device status.
- Keep every operation at **$0** unless Patrick freshly authorizes a cost.
  No paid provisioning, billing enrollment or surprise hosted dependencies.

## Local UI and model boundary

- Preserve `127.0.0.1`-only service/model routing, strict Host/Origin checks,
  bounded JSON/request sizes, per-launch session gating, model-message role
  validation and default-deny external effects. Do not expose the UI or raw
  model service on LAN/public tunnels without a separate qualified design.
- `X-Vera-Session` protects the browser's local UI session. It is **not** a
  verified person, Windows principal, VeraOS task permission, memory-consent
  grant or protected-effect capability. Do not trust browser-supplied SID,
  principal or permission headers as host authority.
- The separately provisioned model bridge's two private bearer files protect
  inference transport only. Neither file authorizes VeraOS tasks, memory,
  identity, consent or external action. Keep secrets out of source, process
  arguments, logs, browser responses and model prompts; use verified host-owned
  custody and distinct capabilities for separately privileged reads.
- Persona pins configure source-checked behavior, not model identity or a
  Windows logon. `SOURCE_ONLY` and `identity_attested=false` must remain honest.
  Do not redistribute owner-private profile or presentation source.
- No VeraOS status/task/effect bridge is admitted by a browser session alone.
  A future read-only projection needs verified host-owned issuer, actual caller
  principal mapping, consent/receiver privacy, freshness/revocation, narrowly
  scoped output and fail-closed runtime tests. Protected effects additionally
  require a separate broker, explicit permission and durable receipt.

## Privacy, tests and changes

- Never commit credentials, private conversations, autobiographical material,
  local transcript vault records, model weights or unlicensed source. Consent,
  ownership and revocation are enforced by host mechanisms, not model wording.
- Keep source, test-double evidence and physical host probes labeled separately.
  Synthetic HTTP tests do not prove live GGUF inference or resident VeraOS.
- Work in isolated branches/worktrees when touching active PR lines. Implement
  bounded, reversible changes and test the impacted seam. The source suite is
  `python -m unittest discover -s tests -q`; report pass/fail/skip counts and
  exact source commits. Include hostile cases for authority, privacy and
  recovery changes. No unauthorized merge, deployment, deletion, restart,
  credential/ACL change or external effect.
- Consult an authorized Blotter's last 20 entries and append truthful task
  checkpoints only when the actual authorized interface is available. Do not
  fabricate continuity or route around an unavailable boundary.
