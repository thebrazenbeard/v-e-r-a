# Vera local interface V1 — shipped source boundary

## Why this lives in `v-e-r-a`

The repository's default branch was a source registry, not an interface. The
new `interface/` module is an independent application surface alongside that
registry. It does not modify the 44 mirror branches, their pins, canonical
repositories, or unmerged integration Draft PR #1.

## Executable seam

```
same-machine browser (untrusted text)
    | Same-Origin + fresh session header
    v
interface.server : 127.0.0.1 (response-only; opt-in local transcript vault)
    | fixed localhost HTTP URL; installed-model allowlist
    v
Ollama on this machine (model response only)
```

- `python -m interface [--port 8765] [--ollama-url http://127.0.0.1:11434]`
- `GET /api/session`: fresh per-process token, readable only by same-origin code.
- `GET /api/models`: current installed model names from Ollama `/api/tags`,
  only after a valid same-origin session header.
- `GET /api/status`: reports disconnected privileged subsystems, also session-gated.
- `POST /api/chat`: normally accepts exactly `model` and bounded user/assistant `messages`.
  Strict Origin, Host, session, JSON, model-name and body-size gates precede
  inference. An explicit system note denies tools/memory/external effects; no
  tool specs are passed to the model, and any tool-call response fails closed.

The session token deters cross-origin browser requests. It is **not** Windows
account authentication, a credential for network exposure, or an attested
person identity. Do not bind the server to a non-loopback address or expose it
via a public reverse proxy. Model-serving logs remain outside this app's
privacy guarantee. UI conversation exists in current tab memory only.

## Optional owner-pinned conversational behavior — source-only

The canonical Vera behavior JSON is **not redistributed in this repository**.
It belongs to the owner-governed, source-available `thebrazenbeard/vera`
repository. A generic launch has no pinned persona and reports
`persona_source.qualification=NOT_CONFIGURED`. The owner can explicitly
provide the exact checked and licensed JSON through
`--persona-profile-file /ABSOLUTE/OWNER/PROFILE.json`; see
`docs/PINNED_VERA_PERSONA_SOURCE_BINDING.md`. The startup path checks its
SHA-256 against the pinned canonical digest before creating a listener.
`--require-persona` is the explicit governed interface mode. It also
requires separately owner-provisioned, Git-blob-hash-verified
`--persona-presentation-file /ABSOLUTE/OWNER/NONVERBAL.md`, and **fails
closed** if either source is absent or changed. This does not make a
model's weight identity attested.

Once accepted, `interface/persona_profile.py` constructs a bounded
server-owned voice specification. The caller cannot change the system role,
and `/api/status`/`/api/chat` return a typed
`persona_source.qualification=SOURCE_ONLY` receipt including canonical
profile hash, verified presentation blob hash, and `identity_attested=false`.
The governed APK requires this exact two-source receipt and rejects generic
`NOT_CONFIGURED` mode without claiming an external model failure.
It tells the model to speak naturally
in first person through Vera's configured interface, while distinguishing
that behavior from proof of authenticated Vera weights. An unverified local
model must not claim a continuously lived or trained Vera identity.

The gateway accepts only bounded, strictly alternating user-led
`user/assistant` turns ending in `user`. Both the upstream bridge and
gateway reject non-assistant upstream messages and empty replies.
`response_completion_status` reports `complete`, `length_limited`,
`filtered` or `unknown` without forging an upstream stop. Only `complete`
is admitted into the browser's ordinary assistant history; incomplete or
unverified fragments are displayed separately and cannot be replayed into
later context or explicitly saved as finished assistant turns.

Conversation is still ephemeral unless explicitly saved. **Server-side vault
recall/injection** requires both `recall_saved:true` and the private vault
capability; it supplies a separately sourced, quoted `user` message, never
the persona system role. The operator can also explicitly **Restore** text
into the browser UI; if then sent as ordinary chat history, those restored
turns have no server-side vault recall receipt, and should not be misread as
verified memories. **Visible message history in a request remains usable
transient context**; the model must not feign amnesia about preceding supplied turns.
Unrecalled *earlier sessions* must not be presented as personal memory;
a quoted user conversation is not imported knowledge or a weight
update. Deleting the saved transcript blocks further recall at the gateway.
This does not erase a still-open browser's conversation, model-server logs,
snapshots, or backups. These are API/security properties validated with mocks,
not guarantees that an arbitrary model is immune to prompt injection embedded
in quotations.

**Physical-model boundary:** Earlier reports of local conversation quality
belong to different seed/host checkpoints. This owner-file integration has
only deterministic mock tests until a separately leased and physically
verified GGUF is assessed. Source pins, self-reported model IDs and tests do
not establish voice quality, identity continuity, or model provenance.

## Memory and real-world scope are integration capabilities, not impossibilities

An unaugmented model does not independently retain chat history or acquire
external observations. This is a limitation of the current execution contract,
**not** proof that persistent memory, observation, or authorized action cannot
be engineered into the surrounding system. An earlier local-model response
incorrectly described these as categorically impossible. The gateway now
distinguishes *not connected in this session* from *technically impossible*.

Minimum admission requirements before adding an adapter:

1. **Memory:** explicit opt-in capture, source and timestamp, confidence and
   possible contradiction, scoped retrieval, retention/deletion controls,
   authenticated ownership, and a separate audit trail. Do not silently
   remember every utterance or treat recalled text as truth.
2. **Observation:** named device/source, timestamp and freshness, operator
   permission, typed data contract, and read-time failure status. A model's
   inference is not a verified sensor measurement.
3. **Action:** narrowly granted capability, human or established authority,
   confirmation for protected effects, actual execution receipt, and later
   reconciliation. Proposals and language about action are not action.

In this v1, all three status fields are `not_connected` and none of the
adapter permissions exist. The immediate future seam is provenance-tagged,
read-only retrieval from a qualified memory provider; persistent writes and
external effects must be qualified separately.

## Intended architecture across nodes (not deployed by V1)

1. A dedicated trusted host authenticates the operator and conversation; it
   does not derive person identity from a model message or Portal's `HUMAN` label.
2. A named model registry records actual node, provider, model ID and
   endpoint provenance. Lappy/VN1/VN2 must each be independently discovered.
   Remote model hops require an authenticated transport and allowlisted service
   identity; **raw LAN Ollama exposure is out of scope**.
3. Portal may select an advisory route; Pre-Active remains the single durable
   task/execution owner; Empathy may supply admitted ephemeral response framing;
   Volition owns persistent wants. Neither the interface nor a model result
   grants an effect or creates autonomous work.
4. The UI may later display task state and reconciled effect receipts, but it
   must distinguish queued/running/completed from verified external effect.
   An explicit, authenticated human approval is required for protected actions.

Unmerged [v-e-r-a Draft PR #1](https://github.com/thebrazenbeard/v-e-r-a/pull/1)
is an advisory source-level CLI, **not** a trusted interface control endpoint.
Before it is callable from the interface, qualify exact checked-out code,
including untracked Python import-tree integrity, real Portal/Vera-Mono tests,
and authenticated runtime authority; never expose it directly to a browser.

## Qualification and limits

`python -m unittest discover -s tests -v` uses a temporary local fake model
HTTP server to check strict model/Origin/Host/session validation, absent tools,
forged authority-field rejection, duplicate-JSON refusal, HTML-safe rendering,
and existing component materialization. It does not test remote model routing,
person-scoped Empathy, task execution, or deployed Lappy service state.

"New conversation" aborts the browser request and prevents late old replies
from appearing in a cleared conversation. It does **not** claim to cancel
already-running model computation on the backend.

## Experimental opt-in local transcript vault (not deployed by V1)

The interface can now be launched with **both** `--memory-db` and
`--memory-secret-file` to enable a separate, operator-unlocked AES-256-GCM
encrypted transcript vault. Install the opt-in dependencies in
`requirements-vault.txt` in its own environment first. Neither has a default. The obsolete
`--acknowledge-plaintext-vault-risk` argument remains a deprecated no-op for
launch-script compatibility; it cannot disable encryption or private-file checks.
With either path missing, storage remains
disabled and `/api/status` reports `durable_memory=not_connected`.

The secret file must be a private operator-supplied, high-entropy ASCII token
(at least 32 characters). The vault rejects Unix mode bits exposing the file to
other users; on Windows it requires the `pywin32` inspection backend and denies
files whose DACL grants access outside the owner/current user/SYSTEM/Administrators,
and it rejects writable access by other identities on the immediate parent
directory. Unix checks require owner-only file access, the current effective
user as file owner, and no group/world-writable immediate parent.
Files with unknown or unsupported ACL entries fail closed. The browser never writes it to localStorage, and the
gateway never sends it to Ollama. The operator enters it in the UI for
explicit **Save recent**, **Restore**, or **Remove active saved entry** actions. The vault
stores at most 12 bounded, alternating user/assistant messages in local SQLite;
it does not automatically capture chat or infer long-term facts. Saved content
includes a timestamp, source label, and SHA-256 integrity check over ciphertext,
and its active
row can be removed. **Removal is not secure erasure:** old data may survive in
SQLite freelists/journals/WAL, filesystem snapshots, cloud sync, and backups.
SQLite's `secure_delete=ON` is enabled per connection as a best-effort reduction
of page-level remnants; it does not make removal forensic erasure or control
other retained copies.
The server records save/remove event types without transcript text.

**Typed provenance receipt:** Save, authenticated read, explicit model-time
recall, and removal expose a `source_classification` receipt with
`kind=user_conversation`, `origin=operator_saved_browser_transcript`,
`consent=explicit_operator_save`, and
`retention=until_explicit_operator_delete`. Its two negative flags state
`imported_knowledge=false` and `trained_weights_modified=false`. These are
claims about this narrow local operation, not attestations of person or model
identity. Imported knowledge and neural weight updates are distinct source
categories and **have no write path in this vault**. The existing audit
`operator_save`/`operator_delete` transaction and ciphertext storage remain the
single owner; this receipt creates no second ledger. No time-based expiration
is implemented: the active row remains until deliberate operator deletion,
subject to the documented backup/forensic-erasure limits.

Restoration is a conscious operator action. Restored messages are unverified
text and may be included by that operator in a later model request as ordinary
conversation history; they are not new model weights, consciousness evidence,
fresh observations, authenticated memories, or authorized actions.

**Explicit model-time recall (experimental local seam):** The operator may
select *Use saved context on Send* in the browser after entering the private
vault key. Only then may `/api/chat` accept an exact `recall_saved:true` flag
alongside one fresh user question. The server must authenticate the separate
`X-Vera-Vault-Key` on **that very request**, read the current saved revision,
and pass the stored transcript as a quoted, unverified user-context message
alongside the current question in one lower-trust user turn, without creating
adjacent duplicate user roles that some chat templates reject.
The browser session token alone can never retrieve or inject private text.
The response identifies the source label, save time, revision, and content
digest, never the bearer secret. Ordinary chat does not read the vault. A
deleted/empty entry fails closed with 409; the server does not silently fall
back to stale browser history. The toggle intentionally replaces unsaved tab
context for that single model call (apart from the new question). Content
larger than the bounded recalled-context limit is refused; use manual Restore
for such cases. An already in-flight model call cannot retract text the server
previously transmitted before a later Delete completed.
Removing a saved row also clears this browser tab if its conversation was
Restored from the vault **or a model reply used explicit saved context**, so
ordinary follow-on chat does not unknowingly retransmit the derived text.
Changing the entered vault credential (even to another nonempty value) likewise
clears derived tab history and cancels a pending private recall locally. Late
responses are ignored, but an already transmitted model request cannot be
retracted from the model runtime.
Other tabs, prior completed model calls, and manually retyped copies are
outside that guarantee.

The local fake-model integration regression demonstrates save → interface
restart → source-attributed recalled request → changed deterministic mock
answer → delete → no later recall. This is **software-path verification**, not
evidence a pretrained model learned or an actual Ollama endpoint ran. A live
checkpoint needs a distinct bounded real-model, same-owner, restart and
delete/no-recall demonstration with independent execution receipts.

This is **not** a qualified general-purpose durable-memory service: active
transcript bytes are encrypted using a fresh 96-bit random nonce per save, a
per-database scrypt salt derived from the operator secret, and authenticated
encryption bound to the saved revision. The SQLite file contains encrypted
text, not plaintext or plaintext hashes. Wrong keys and legacy plaintext
database rows are rejected; there is **no automatic unsafe migration**.
The ciphertext hash is not an authenticity signature, no multi-person identity
exists, and there is no separate tamper-resistant audit or backup/retention
authority. Restrict the DB and secret path using host ACLs; do not put them in
Git, cloud sync, shared drives, or a network-exposed UI. The Windows ACL code
has not been independently tested on Lappy. **At-rest protection is not
forensic erasure, protection against a compromised running account, or
proof of true operator identity.** Rolling back the entire SQLite database
to an earlier valid snapshot also remains possible without an external
monotonic audit anchor; revisional AAD only stops partial ciphertext replay.
An **optional, limited external rollback witness** may be enabled with
`--memory-rollback-anchor /separate/private/highwater.json` alongside the vault
arguments. The witness is an owner-private, HMAC-authenticated revision and
ciphertext fingerprint file in a **different protected directory** from the
SQLite database. Its MAC key is domain-separated from the vault's existing
per-database salted scrypt output; it **does not** create a fast HMAC oracle
from the raw operator credential. It advances before database commit, and a restored database
with a stale revision or different ciphertext then fails closed on startup,
read, save, and delete. The path must belong to a separate trusted backup
boundary: keep it out of the vault's automatic sync, snapshot, and restore
jobs. If enabling the witness for an existing vault, an operator must perform
a separately reviewed fresh-vault migration; the software intentionally refuses
to invent a witness for existing data. Newly anchored databases persist a
`vault_anchor_policy` requirement: restarting the same database without the
witness argument is refused, instead of silently disabling rollback checking.
This marker is in SQLite and **is not itself tamper-resistant**; rolling back
the whole database to a pre-marker image is outside the guarantee.
Loss or tampering of the witness also
refuses the vault, not silently resets its revision. A crash between updating
the witness and committing the SQLite transaction may leave the vault locked;
recover only after investigating authoritative backups and keys, not by lowering
the witness to match an older database.

**Crucial limit:** this protects against *database-only* rollback, not a
whole-device/whole-backup restore, malicious action under the operator identity,
reinstallation with both an old database and old witness, or reintroduction of
an old decryption secret. Windows witness filesystem durability and ACL
behavior have not been qualified on Lappy. The feature is not a hardware
monotonic counter, key-shredding service, forensic erasure, or a claim that
deleted ciphertext cannot be recovered from historical copies. The included
regressions intentionally demonstrate both database-only refusal **and**
whole-pair rollback recovery of old text.
Vault mutations use an incrementing SQLite revision, checked inside each
transaction. The browser serializes vault operations per tab; concurrent tabs
or delayed requests with an outdated revision receive HTTP `409` and must
explicitly reload before retrying. A removal advances the revision even when
the slot is empty, so a delayed pre-removal Save cannot silently revive an
entry. It does not prevent a *new, explicitly authorized* Save made against
the subsequent revision, and does not constitute forensic erasure.
For sensitive data, independent Windows ACL and authenticated ownership
qualification remain deployment prerequisites. This local code has not been installed over the
currently running Lappy process.

The model gate currently serializes generation (one in-flight request), limits
input messages to 12/16,000 characters, and uses a 90-second socket timeout
(**not** a guaranteed wall-clock deadline for a trickling upstream response). There
is no generation cancellation/streaming API in V1; those require separately
verified client abort and backend cleanup semantics.

The loopback server permits at most 16 simultaneous HTTP request threads and
sets an 8-second inbound socket inactivity timeout plus a 12-second absolute
deadline for reading a POST body. Connections above the cap are closed without
spawning worker threads; an authenticated client that stalls or slowly drips
its declared POST body receives HTTP 408. Header parsing still relies on the
socket inactivity timeout, so a sufficiently slow header stream may occupy one
of the 16 slots; these bounds reduce but do not eliminate local denial-of-service
risk and do not authenticate other local OS processes.

## Rollback

Stop the `python -m interface` process. No daemon, scheduler, saved prompts,
Pre-Active database, or external action is registered or modified by this app.
Rollback of this UI source is independent from the component snapshot registry.
