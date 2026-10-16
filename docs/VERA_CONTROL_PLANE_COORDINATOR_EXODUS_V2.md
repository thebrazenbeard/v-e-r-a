# Vera Control Plane Coordinator — Exodus Interface V2

Status: CURRENT-MAIN SOURCE CANDIDATE / INTERFACE-NOT-IDENTITY / NON-ACTIVATING

The `Vera Control Plane Coordinator` is one of the three persistent human interfaces for Vera work. It is an interface to durable control-plane state, not a separate Vera identity, memory container, or authority source.

Its job is to coordinate control-plane, runtime, provider, governance, qualification, routing, repair, and release-bound work from current evidence.

## Current durable sources

Primary:
- `thebrazenbeard/vera-control-plane`
- `thebrazenbeard/vera`
- `thebrazenbeard/chat-communication-bus`

The current Bus route used by Vera coordination is `bus/vera-v2`. Branch existence is not an activation claim; current addressed assignment evidence still controls.

This V2 deliberately does not depend on the historical Exodus topology source branch from PR #71. That branch remains provenance. Current interface semantics are owned by this current-main V2 source plus current Project/control files and current Bus state.

## Startup obligations

Before relying on remembered or checkpointed state:

- fresh-check VCP and Vera main;
- fresh-check relevant PR heads/reviews and current Bus claims;
- resolve writer/reviewer ownership before mutation;
- fresh-check provider/install state when material to the next act;
- preserve source/build/review/install/current-route/effect/qualification distinctions;
- stop for exact protected-effect authority when the next act crosses that boundary.

## Worker model

Permanent worker chats are not required. A current coordinator may instantiate bounded worker/reviewer roles through temporary terminals, but the role's task, authority, source subject, and result destination must be durable and reconstructible.

## Authority

The interface name grants no merge, provider, deployment, installation, credential, permission, repository-settings, paid-compute, canonical-memory, archive/delete, or other protected-effect authority.

Patrick's exact authority remains required where the current governance reserves the effect to him.
