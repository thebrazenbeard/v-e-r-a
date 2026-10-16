# First-Dollar Benchmark V1

This harness answers a narrow question:

On this exact owned machine, does a candidate revenue workload produce enough withdrawable value to justify its electricity, delay, and friction?

It does not start a miner, Folding@Home, BOINC, provider node, trading bot, storage host, or any other workload.

## Evidence ladder

SOURCE_ESTIMATE is discovery evidence only. It may use a current reward calculator, network statistic, or published payout formula. It can rank what should be benchmarked next, but can never authorize execution.

EXACT_RESOURCE_MEASURED means the exact owned resource has been observed under the candidate workload and has benchmark evidence. It can support a later authorization decision but does not itself authorize continuous operation.

REALIZED_REWARD means an exact-resource observation is also bound to actual reward-receipt evidence. This is the strongest economics evidence, but the harness still emits authorization_state=NOT_AUTHORIZED.

## Economics

The harness separates baseline system draw from workload draw and charges only the incremental electricity attributable to the workload:

incremental_kWh/day = (workload_watts - baseline_watts) * hours_per_day / 1000

Gross cash value is reduced by a configurable liquidity ratio before fees. The output includes:

- gross USD/day;
- incremental power cost/day;
- explicit platform and other costs;
- payout threshold and cycle length;
- payout fee per cycle and amortized per day;
- net USD/day and net USD/30d;
- estimated days to first payout including warmup and payout lag;
- first-payout cash value;
- first-payout net profit after operating costs;
- electricity break-even price.

All monetary math uses Decimal.

## Current first-dollar use

The intended first comparisons are:

1. BANANO through Folding@Home;
2. Gridcoin + Curecoin Folding reward stack;
3. Monero through XMRig + P2Pool.

Resource-provider marketplaces such as Golem or storage/bandwidth networks remain secondary until their setup, demand, payout, and exposure costs are competitive.

Private wallet material, account credentials, household financial details, and unrelated machine data do not belong in benchmark records. Public receiving addresses should also be omitted unless an adapter genuinely requires one.

The open HOLD-FIRST-DOLLAR-0001 remains authoritative. This harness does not resolve it.
