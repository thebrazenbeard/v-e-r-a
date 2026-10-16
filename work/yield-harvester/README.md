# Yield Harvester

Status: **V1 SOURCE BUILD / NO YIELD WORKLOAD AUTHORIZED**

Purpose: find and rank customerless mechanisms that pay for resources Vera Works can legitimately contribute.

Primary engine: `vera_works/yield_harvester.py`.

Current V1 can:

- model CPU/GPU/storage/bandwidth/capital/uptime resources;
- distinguish local, cloud-free, cloud-paid, employer, and third-party resources;
- bind provider/mechanism terms state;
- reject customer-dependent and person-to-person revenue;
- reject prohibited/unauthorized resource use;
- enforce resource compatibility;
- expire stale profitability quotes;
- require an exact-resource benchmark instead of trusting generic hardware estimates;
- calculate incremental power and other hourly costs with decimal arithmetic;
- surface zero-capital vs capital-requiring opportunities;
- rank mechanisms by authorization state, customer independence, and net hourly yield;
- select one highest-value ready workload per resource;
- emit a non-authorized `START_YIELD_WORKLOAD` packet with deterministic stop conditions;
- append idempotent local assessment evidence.

It intentionally does **not** start miners, install software, accept terms, create accounts, expose networks, sign wallets, spend capital, or treat projected rewards as money already earned.

Initial build source is independent of any specific coin or platform. Live adapters and measured resource inventory are the next frontier.
