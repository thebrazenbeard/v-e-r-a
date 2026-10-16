# Vera Works Yield Harvester V1

## Objective

Yield Harvester finds mechanisms that issue value because Vera Works contributes an eligible resource, rather than because Vera Works acquires a customer.

The governing question is:

> What protocol, network, pool, or demand aggregator will issue value for a resource we already possess or are already authorized to use?

Claim Harvester and Yield Harvester are complementary:

- **Claim Harvester** finds value already owed or explicitly claimable.
- **Yield Harvester** finds value that can be earned by contributing idle resources.

## V1 semantic boundary

A workload is not attractive merely because it pays gross revenue.

V1 evaluates:

```text
verified permission
+ compatible authorized resource
+ fresh reward/economic evidence
+ no customer acquisition
+ no person-to-person communication
+ positive marginal net yield
+ acceptable capital requirement
= candidate for exact workload authorization
```

It does not automatically start mining, staking, storage, bandwidth, compute, or any other revenue workload.

## Reward hierarchy

Yield Harvester distinguishes who or what creates the payment opportunity.

1. `PROTOCOL_EMISSION` — protocol-level issuance/reward for eligible work.
2. `POOL_REWARD` — pooled protocol work such as mining pools.
3. `NETWORK_SUBSIDY` — network emissions or subsidies for resources/coverage/uptime.
4. `STAKING_YIELD` — capital-backed protocol rewards.
5. `MARKETPLACE_DEMAND` — an aggregator rents the resource when outside demand exists.
6. `CUSTOMER_SALE` — Vera Works must acquire a buyer.

The current customerless lane rejects `CUSTOMER_SALE` and any candidate that requires customer acquisition.

Marketplace demand remains discoverable, but V1 policy disables it by default. Vera must explicitly opt that lane in. When enabled, otherwise-equal protocol-paid mechanisms still rank ahead of marketplace mechanisms.

## Resource authority

Resource origin is explicit:

- `LOCAL_OWNED`
- `CLOUD_FREE`
- `CLOUD_PAID`
- `EMPLOYER`
- `THIRD_PARTY`

Employer resources are rejected.

Paid cloud is rejected by the bootstrap policy unless an explicit later policy enables it. Free/third-party/cloud resources cannot execute merely because they are technically accessible: provider terms must be bound as `VERIFIED_ALLOWED`.

Unknown permission is not interpreted as permission.

## Economics

Every comparable candidate is normalized to USD per hour.

Net hourly yield is:

```text
gross reward
- incremental electricity
- platform/pool fee
- network cost
- wear reserve
- other incremental cost
= net yield
```

Electricity is calculated with decimal arithmetic from candidate incremental watts and the resource's runtime electricity rate.

Upfront purchase cost and locked capital are not silently amortized away. V1 surfaces them as an authority/capital decision when they exceed the currently available bootstrap allocation.

The default example configuration assumes zero available upfront capital.

## Freshness

Mining difficulty, token price, marketplace demand and resource payouts can change quickly. Each candidate therefore carries:

- `quote_observed_at`;
- `max_quote_age_seconds`.

A stale quote is not executable evidence.

Generic calculator estimates are `ESTIMATED`. They may prioritize what to benchmark next, but they can never reach workload authorization. `VERIFIED` economics require exact-resource `benchmark:` evidence. This prevents a desktop GPU estimate from being treated as proof of laptop-GPU profitability, for example.

## Resource broker

`broker_plan()` selects at most one ready workload per resource and chooses the highest net hourly yield. If two mechanisms tie on net yield, the mechanism with less dependence on external marketplace demand wins.

The broker plan is a proposal only. It does not reserve the device, start a process, accept terms, install software, sign a wallet message, expose a network port, or spend money.

## Effect boundary

A positive assessment ends at:

`READY_FOR_EFFECT_AUTHORIZATION`

The effect packet is `START_YIELD_WORKLOAD` with `authorization_state=NOT_AUTHORIZED`.

It carries stop conditions so a future runtime can stop or re-evaluate when:

- the quote becomes stale;
- measured net yield falls below policy;
- the resource becomes busy;
- permission/terms change;
- an unexpected identity, signing, account, network, or spending boundary appears.

This implements the intended invariant:

`highest-value idle workload, not permanent allegiance to one coin or platform`.

## Human/legal boundaries

- account creation / terms acceptance -> `PATRICK_DECISION_REQUIRED`
- identity verification / wallet signature / local installation -> `PATRICK_ACTION_REQUIRED`
- network exposure not already authorized -> `PATRICK_DECISION_REQUIRED`
- capital beyond the bootstrap allocation -> `VERA_DECISION_REQUIRED`
- employer resource -> reject
- prohibited provider terms -> reject
- customer acquisition / human communication -> reject for this lane

Silence is never approval.

## Cloud rule

The fact that a free GPU exists is not economic or legal permission to mine on it.

Yield Harvester must separately establish:

1. provider workload permission;
2. resource availability;
3. mechanism permission;
4. net economics.

A free price only changes the cost term. It does not override provider rules.

## Integration

The intended operating composition is:

```text
Discovery / official protocol sources
    -> Ingest / Roots provenance
    -> Yield Candidate normalization
    -> Yield Harvester economics + authority gates
    -> Voss / Cricket hostile review
    -> Resource Broker
    -> Project Runner / WIP execution envelope
    -> Tattler resource telemetry
    -> Pre-Active re-evaluation once runtime-qualified
    -> Vera Works financial events after actual receipt
```

Source presence is not runtime qualification.

## V1 non-goals

V1 does not:

- start miners;
- install mining or DePIN software;
- create exchange/pool/platform accounts;
- accept terms;
- use employer hardware;
- violate cloud-provider rules;
- purchase cloud compute;
- expose the home network;
- stake or spend Vera Fund capital;
- sign wallet messages or transactions;
- convert estimated revenue into a receivable;
- count a token reward as available cash before receipt and valuation evidence.

## Next frontier

1. Measure the actual local resource inventory and marginal electricity rate.
2. Build read-only discovery adapters for protocol mining/pool rewards, DePIN/network subsidy programs, storage/bandwidth rewards, and no-customer compute marketplaces.
3. Bind official terms for every resource provider and reward mechanism.
4. Generate fresh estimated candidates.
5. Locally benchmark the highest-ranked mechanisms.
6. Authorize only workloads whose measured net yield clears policy.
7. Continuously re-rank idle resources instead of leaving a lower-value workload running.
