# VeraOS ↔ V-E-R-A UI admission boundary — source-only HOLD

**Cross-repository review inputs (2026-11-05):**

- Accepted `v-e-r-a` main `4c02f06e3c7fcccec3c681cb94cc087f1049235d`.
- `v-e-r-a` Draft PR #30 `7f8346b1328e8b4e3f172d1c1e10ad5738cb7d89`
  (stacked on unfinished local GGUF/persona/continuity proposals).
- Accepted `vera-os` main `31b66b6ff317eb981c4bd8fcc4ae6e5db1d21adf`.
- `vera-os` Draft PR #74 `048da7c59d72dbbbe718b48d1bda91460e0fda8b`
  (WSL test surface; no installed host bridge).

These are source observations, not claims of currently installed services.

## Present boundary

The V-E-R-A local browser session token establishes a bounded same-origin UI
session only. It is not a Windows logon credential, verified human identity,
OS authorization token, VeraOS consent grant, or WSL task authority. Owner-pinned
persona material in Draft #30 produces `qualification=SOURCE_ONLY` and
`identity_attested=false`; it is behavior configuration, not a Windows principal.
Draft #30's newly paired upstream/bridge-client model bearer files independently
limit access to the local inference transport; neither bearer authorizes VeraOS
status, tasks, memory admission, or protected effects.
The model bridge and text may neither authorize protected effects nor directly
rewrite VeraOS state. The current UI status correctly reports `response_only`
and unrelated privileged runtimes `not_connected`.

VeraOS Draft #74's WSL IPC response is a same-Linux-UID local development
result (bounded task/event counts, `production_authority=false`). Its `SO_PEERCRED`
observation is not a Windows logon SID or authenticated bridge. The Windows
named-pipe source prototype has no qualified real read/impersonation or trusted
issuer; its request shape and 128-hex fields prove no authorization. A browser
must not shell out to `wsl.exe`, call that Unix socket or infer identity from
localhost merely because the interface runs on the same Windows machine.

## Qualified bridge prerequisite, not implemented here

Before the UI exposes even read-only VeraOS status, the runtime side must
provide an owner/issuer-authenticated, fresh and narrowly scoped projection;
bind the exact Windows principal/session to a consented VeraOS owner; and
independently enforce receiver privacy and revocation. A distinct host-owned
capability must authorize the read. A UI session token alone is insufficient.

An eventually admitted projection needs a typed source revision, source host,
issued-at/expiry interval, explicit `production_authority=false` where
appropriate, a verified principal/consent scope and a server-side freshness
gate. It should expose only privacy-reviewed bounded state (for example
aggregate counts), never filenames, prompt content, secrets, audit details, or
unreviewed user memory. An action path would require a separate protected-effect
broker, explicit approval and durable receipt, not an extension of a GET token.

No protocol is declared *implemented* by this document. Avoid introducing
untrusted data adapters that accept a caller-provided `verified=true` boolean,
arbitrary JSON signatures, or a UI-borne authorization header as proof.

## Executable negative gates

`tests/test_veraos_admission_boundary.py` starts only its own disposable
loopback HTTP interface without a model endpoint and tests:

1. Forged SID/principal/grant headers do not promote `/api/status` beyond
   `response_only` or create runtime principal/effect claims.
2. Browser-session authorization does not manufacture VeraOS status, task or
   effect endpoints (all return 404).
3. `/api/chat` rejects injected task/effect/principal keys before model I/O.
4. Private goal reads still need their separate capability; session alone is
   rejected.

This is an honest integration **HOLD** and regression fence, not a live
VeraOS status panel or an API implementation. Merge/deploy, native named-pipe
execution, Windows ACL/service changes, model loading or private-memory
ingestion remain outside this scope and require separate authorization.
