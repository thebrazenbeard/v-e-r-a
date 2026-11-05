# VeraOS ↔ V-E-R-A UI admission boundary — source-only HOLD

**Cross-repository review inputs (2026-11-05):**

- Accepted `v-e-r-a` main `4c02f06e3c7fcccec3c681cb94cc087f1049235d`.
- `v-e-r-a` Draft PR #30 `7f8346b1328e8b4e3f172d1c1e10ad5738cb7d89`
  (stacked on unfinished local GGUF/persona/continuity proposals).
- Accepted `vera-os` main `31b66b6ff317eb981c4bd8fcc4ae6e5db1d21adf`.
- `vera-os` Draft PR #74 `019969a21b3c8c763926f1af504cd8b4b43086ae`
  (WSL development/test source and Windows named-pipe prototype; no installed
  host bridge).

These are source observations, not claims of currently installed services. A
separate **REAL_SYSTEM_PROBE** on Lappy (2026-11-05, Blotter #543) used that
exact Draft source for one explicitly authorized, foreground Windows Python
3.14.5, single-use named-pipe `PING`/`PONG` exchange. The server successfully
read the client message, called Win32 `ImpersonateNamedPipeClient`, observed
the kernel client token, matched user SID and authentication LUID to its own
process token, reverted impersonation, and closed the disposable endpoint;
the probe exited 0 in 0.67 seconds. It was an in-memory test harness, not a
service, deployed broker, stored grant, installed client, or independent audit.

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
named-pipe prototype now has one successful, same-logon **native observation**
probe, but no authenticated application protocol, trusted server/issuer custody,
consented owner mapping, replay prevention, independently enforced worker
isolation, or protected-effect grant. Its request shape and 128-hex fields still
prove no authorization. A browser
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
5. Forged `verified=true`, SID/LUID, issuer, and signature-looking headers do
   not promote response-only status to VeraOS authority.
6. Replayed browser-session requests with nonce, expiry and consent claims do
   not create VeraOS status or task endpoints.
7. Caller-provided apparent authorization in a task body or private-read header
   does not create an effect route or bypass private goal capability.
8. With an explicitly configured disposable local transcript vault, plausible
   Windows SID/LUID/issuer/signature/consent headers plus the ordinary browser
   session cannot read, write, or delete records without the distinct vault key;
   the vault remains empty after denied attempts.
9. Browser-originated `conversation/history` and `stm/admit` requests bearing
   consent-looking headers do not create an STM archive-admission endpoint.
10. Percent-encoded, query-extended and proxy-rewrite-shaped VeraOS paths do
    not turn absent task/effect routes into privileged actions.
11. Denied task/effect/STM paths do not invoke the existing local-model list or
    chat backend, as asserted with source-only mocks.

This is an honest integration **HOLD** and regression fence, not a live
VeraOS status panel or an API implementation. Merge/deploy, any additional
native named-pipe host execution, Windows ACL/service changes, model loading or private-memory
ingestion remain outside this scope and require separate authorization.
