---
schema: VERA_CONTROL_SOURCE_SEPARATION_V2
logical_id: VERA_CONTROL_SOURCE_SEPARATION
filename_authoritative: false
filename_mangling_nonsemantic: true
---

# Vera Control / Source Separation V2

Layer A — native kernel: always-on admission, authority, correction, protected effects, freshness, interrupts, privacy defaults, coordination discipline, and behavior.

Layer B — typed native architecture: interface, charter, recovery, topology, memory/privacy, coordination. Resolve by logical ID/schema; filenames are hints only.

Layer C — release-bound control: R10/R10+SD1 owners/manifests. Preserve their exact digest, owner, and qualification semantics rather than duplicating them into the kernel.

Layer D — domain repositories: bounded architecture/evidence.

Layer E — mutable current truth: Git heads/PRs, Bus topology/messages, assignments, provider/install state, current route, exact-head reviews, external readbacks. Fetch live when material.

`LOGICAL_ID + SCHEMA/ROLE + VERIFIED_CONTENT_BINDING > FILENAME`
`FILENAME_MANGLE != NEW_CONTROL_SUBJECT`

Upload suffixes such as `(1)`/`(2)` are non-semantic unless content identity differs.

## Live Project inventory before absence

Before classifying a native Project source as missing, stale, duplicate, or not installed, inspect the live Project source surface for the logical subject. A partial/stale listing, one failed search/materialization, or a filename mismatch does not establish absence. When Patrick states that files were uploaded or added, test that current claim against the live inventory/content before contradicting it.

`NO_RESULT != ABSENT`
`CACHED_INVENTORY != LIVE_INVENTORY`

## Install-facing successor naming

Source identity and successor artifact naming are different problems. Existing `(n)` suffixes remain non-semantic and are resolved by logical identity/content. But a NEW successor intended for native Project upload must not reuse a basename previously exposed as an install-facing or loose chat artifact. Mint a release-scoped, never-before-used filename namespace for every installable member.

Deliver installable successor members only inside one verified ZIP. Do not surface the installable members as separate chat artifacts. After building the ZIP, verify member names, uniqueness, bytes, and digests before handoff.

Do not rename or repackage an existing live Project set merely because the UI displays suffixes. Inspection requests remain inspection unless Patrick asks for replacement/package generation or verified integrity evidence makes replacement necessary.

Do not promote Project-file presence to active control, source to install, install to route, route to runtime consumption, consumption to qualification, durability to current truth, retrieval to admission, or review PASS to effect authority.

Predecessors, failed candidates, archives, checkpoints, and obsolete owners remain evidence unless current control explicitly rebinds them.
