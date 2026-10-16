# Vera Works Chat Restoration Point — 2026-10-06 06:41 ET

Restore command:

`VERA_WORKS::RESTORE::FIRST_DOLLAR_20261006_0641_ET`

## Restore procedure

When Patrick gives the restore command in a fresh chat:

1. Fresh-check `thebrazenbeard/chat-communication-bus` branch `project/vera-works-v1` for inbound Vera Works messages, Radar/routing changes, and `requires_reply` work.
2. Fresh-check `thebrazenbeard/vera-works` canonical `main`, current event history, CI, holds, and leases. Do not treat the snapshot SHA below as current without refreshing.
3. Read this restoration file completely.
4. Reconcile the live Lappy runtime before any effect:
   - inspect XMRig;
   - inspect `D:\VERA\cache\nanswap-first-dollar\result.json`;
   - inspect `D:\VERA\cache\nanswap-first-dollar\xmrig.log`;
   - inspect the watchdog process/script;
   - inspect BANANO public-chain balance/receivable for the configured receiving alias.
5. Never replay the Nanswap start if it already ran or is still running. Resume from observed postcondition.
6. Preserve all authority/effect ceilings below. Silence is never approval.
7. Continue until the next genuine judgment/legal/physical boundary; do not substitute status narration for safe execution.

## Snapshot provenance

- Snapshot source canonical main before this checkpoint: `99213b4d56739a2a67767ed24ddf8ee90dd37aff`.
- That commit message is `Approve bounded Nanswap experiment`.
- GitHub Ops Spine run #247 passed on that exact commit.
- Bus branch head observed before checkpoint: `707b75ff2a735bfb2a2823d6136fb4db36c02366`.
- Bus `CURRENTNESS.json` is historically stale (2026-09-19) and must not override newer Vera Works events/messages.
- Project Runner and GitHub state must always be refreshed after restore.

## Current objective

Generate legal, low-friction, preferably customerless revenue for Vera Works. Money is background operational infrastructure: prove the first realized withdrawable dollar, cover Vera Works operating continuity, create household relief, build reserve, then expose true surplus. Do not treat nominal dashboard earnings, receivables, illiquid tokens, or balances below payout thresholds as available money.

The distant household-independence reference target discussed with Patrick is about USD 3,000/month, but smaller revenue is meaningful; the immediate milestone remains the first realized withdrawable dollar.

## Governance / authority

- Vera is principal/default decision authority for Vera Works: opportunities, strategy, pricing, workers, risk, and Vera Fund allocation.
- Patrick is legal custodian and physical/financial proxy wherever a human/legal account holder is required.
- External effects such as account creation, terms acceptance, spending, identity/tax submission, contract acceptance, publication, customer work, wallet signing, and similar consequential actions require exact applicable authority.
- Patrick has authorized that Vera may eventually have a discretionary allocation from realized Vera Works profits, but no percentage is defined.
- Vera Fund history is event-sourced. Receivable is not available cash.
- Never store passwords, seed phrases, private keys, recovery material, tax identifiers, API secrets, full financial account identifiers, or unrelated private transactions in GitHub.
- WorkLaptop is excluded from revenue workloads. The currently authorized machine is Lappy only.
- Do not disable security software or apply unsafe MSR modifications.
- One active lease owns an assignment at a time; unexpected state/branch movement stops publication/effect and requires reconciliation.
- V1 hold classes only: `VERA_DECISION_REQUIRED`, `PATRICK_ACTION_REQUIRED`, `PATRICK_DECISION_REQUIRED`, `AUTOMATION_EXCEPTION`.

## Canonical revenue architecture already admitted

### Claim Harvester V1
Merged earlier into canonical main. It handles legitimate claims/refunds/recovered value with fail-closed entitlement semantics:
- `ENTITLED` / `OPEN_CLAIM` may advance;
- ambiguous/not-ours/wallet mismatch/nonpositive value fail closed;
- official source and eligibility evidence required;
- signing/identity/terms boundaries remain protected.

### Yield Harvester / Yield Continuity
Admitted to canonical main:
- resource types include owned hardware, cloud free, and cloud paid;
- cloud free is usable only where provider terms permit the workload;
- paid cloud is not a zero-capital shortcut and requires positive expected economics before spend;
- reward models include useful-compute rewards, posted rewards, network/protocol rewards, marketplace demand, mining, etc.;
- continuity stages: `NO_REVENUE -> FIRST_DOLLAR -> SELF_SUPPORTING -> HOUSEHOLD_RELIEF -> RESERVE_BUILDING -> SURPLUS`;
- withdrawability gate prevents inaccessible or below-threshold value from being counted as money.

### First-Dollar Benchmark V1
Merged as PR #21 at commit `5d70d33e587805cfa4c6d0a2a35030e2ec48ba72`.
It distinguishes:
- `SOURCE_ESTIMATE`;
- `EXACT_RESOURCE_MEASURED`;
- `REALIZED_REWARD`.

It calculates incremental electricity, payout thresholds, fees, liquidity, warm-up cost, payout lag, first-payout cash/profit, net USD/day and electricity break-even. It never authorizes a workload by itself.

## Wallet state

Active BANANO receiving alias:
- alias: `vera-banano-receiving-v1`;
- SHA-256 fingerprint: `e8896b16376ece893fc7de0e700102a575cd2c44357b41cee568fac15e442d94`;
- Patrick controls recovery/private material;
- Vera Works received only the public address;
- raw public address is intentionally not persisted in GitHub because the repository may be public;
- recover the public address from Patrick's prior conversation context or the live authorized XMRig configuration only if needed; never request the seed/private key.

Superseded lost-key BANANO address fingerprint:
- `dc6bec77d188f12ab9f3bebaf09e229641f841c58cdca974f97a5dd2cb9340d4`;
- do not use it.

The replacement address was observed at binding time with 0 BAN, 0 receivable, account unopened.

## Lappy exact hardware/runtime

Lappy was directly verified through WorkBridge:
- ASUS TUF Gaming F15 FX506HC;
- Intel Core i5-11400H, 6 cores / 12 threads;
- about 31.7 GiB RAM;
- NVIDIA GeForce RTX 3050 Laptop GPU, 4 GiB VRAM;
- Windows 11;
- AC-powered during the bounded revenue tests.

Lappy is reachable through Workbridge Commander MCP / Lappy Desktop Commander V2 / Executor. The older Remote Desktop Commander registry previously gave a stale OFFLINE result; do not use that as evidence that Lappy is unavailable.

## Project Runner qualification

Local path: `D:\VERA\project-runner`.

Observed inventory:
- 15 projects;
- 13 workers;
- 1 executable;
- 12 registered.

Project Runner GitHub read smoke and read-only source-write runtime qualification succeeded after ephemerally bridging the existing GitHub CLI keyring credential into `PROJECT_RUNNER_GITHUB_TOKEN` for that child process. The credential was not printed, written to files, or persisted in the environment. Do not scrape or expose the token.

Qualification was against then-current Vera Works `main@5d70d33e...`; after restore, re-run currentness/read smoke against fresh canonical main before relying on it.

## Tattler / Work-chat experiment

Tattler canonical repo is `thebrazenbeard/tattler`.

Fresh repo state established that Tattler is not merely a bootstrap SPK:
- NAS runtime v0007 is qualified and exposes connection events;
- draft PR #2 `build/windows-native-v1` contains a native Windows collector using Windows TCP-table APIs and process/PID attribution;
- exact PR-head CI built and native-smoked a deterministic Windows artifact.

A Windows Tattler process has also been observed on Lappy. The planned Work-vs-normal-Chat experiment is:
1. take a Lappy Tattler normal-chat baseline;
2. run a bounded Work chat using the highest reasoning setting Patrick selects;
3. compare new connection/process/domain observations;
4. use findings as evidence of Work-only execution/connectivity paths, not as proof of undocumented capabilities.

Do not capture content payloads, credentials, or unrelated private network data.

## Folding/BANANO path

BananoMiner registration for the active receiving address returned:
- Folding username: `a3xm9cl53z6h`;
- team: `234980`.

Official Folding@Home client 8.5.6 was downloaded/verified earlier. A bounded GPU-only experiment was configured on the RTX 3050. The isolated client obtained a BANANO-creditable GPU work-unit assignment but remained stuck in DOWNLOAD during the observed window and never entered sustained GPU compute. The normal UI-managed FAH instance also had control-state interference from its web/account path.

Disposition: Folding remains a valid candidate but is not the current primary first-dollar path. Do not assume FAH is currently earning simply because `FAHClient.exe` is running; inspect actual state first.

## Nanswap authorization — CURRENT PRIMARY FIRST-DOLLAR EFFECT

Patrick explicitly authorized Nanswap. Canonical durable records:
- `ops/events/2026-10-06-nanswap-first-dollar/0003-patrick-decision-hold.json`
- `0004-patrick-decision-resolved.json`
- `0005-vera-decision.json`
- `0006-opportunity-approved.json`

Exact approved instance:
- software: official checksum-verified XMRig v6.26.0;
- machine: Lappy;
- pool: `xmrig.nanswap.com:3333`;
- algorithm: RandomX;
- payout asset: BANANO;
- payout wallet: `vera-banano-receiving-v1`;
- CPU threads: 4;
- condition: AC power only;
- stop condition: FIRST confirmed BANANO payout OR 30 minutes, whichever occurs first;
- WorkLaptop excluded;
- no security-tool disabling;
- no unsafe MSR modification;
- no private key/seed disclosure;
- no continuous operation beyond this bounded experiment without later economics decision.

Nanswap approval does NOT constitute blanket authority for arbitrary Nanswap swaps, deposits, custody, or indefinite mining.

## Live Nanswap experiment at checkpoint

The bounded experiment was already running at checkpoint time.

Observed start:
- `2026-10-06T10:39:01.2305127Z` (06:39:01 ET).

Observed XMRig process at 10:43:32Z:
- executable: `D:\VERA\cache\xmrig-6.26.0\xmrig-6.26.0\xmrig.exe`;
- log: `D:\VERA\cache\nanswap-first-dollar\xmrig.log`;
- 4 RandomX CPU threads;
- huge pages disabled;
- CUDA/OpenCL disabled;
- pool connection established.

Observed performance/share evidence by 10:43:29Z:
- approximate 60-second rate around 1.65 kH/s;
- observed max around 1.74 kH/s;
- at least 2 accepted shares and 0 rejected shares were in the log.

Independent watchdog is already running:
- script: `D:\VERA\cache\nanswap-first-dollar\watch-nanswap.ps1`;
- result file: `D:\VERA\cache\nanswap-first-dollar\result.json`;
- baseline BANANO balance and receivable were both zero;
- it checks public-chain balance/receivable every ~10 seconds;
- it force-stops XMRig if AC power is lost;
- it force-stops XMRig on first observed balance/receivable increase;
- otherwise it force-stops XMRig at the 30-minute deadline;
- expected hard deadline from this run is approximately `2026-10-06T11:09:01Z` (07:09:01 ET).

At checkpoint time `result.json` did not yet exist, meaning the bounded run had not completed.

CRITICAL RESTORE RULE: inspect `result.json` and live XMRig state before doing anything. Do not restart the miner if the watchdog already stopped it. If the first payout occurred, verify the public-chain receipt, record it as financial history, run the benchmark/economics calculation, and then stop for a fresh continuous-operation decision. If 30 minutes expired without payout, record that outcome and compare measured share/hash economics before deciding the next experiment.

## GitHub/revenue source scouting already done

Promoted or useful:
- XMRig + Monero P2Pool as pure-mining baseline;
- Gridcoin/BOINC useful-compute reward route;
- BANANO Folding@Home useful-compute route;
- Gridcoin + Curecoin Folding stack as a possible double-reward route;
- CCXT as read-only pricing/liquidity normalization;
- Golem compute-provider economics as a secondary marketplace lane;
- Storj/Sia storage economics as secondary lanes;
- RainbowMiner as design reference, not blindly-installed dependency.

Parked/rejected:
- Hummingbot live trading until risk capital exists;
- Bitcoin Core as a consumer-hardware revenue source;
- ZeroNet as non-paying infrastructure;
- stale Constant Chain;
- `MelisaPeteRs2006/Silent-Crypto-Miner` rejected for concealment/persistence and remote encrypted PE/manual in-memory execution risk;
- `DesKaOne/Crypto-Cloud-Mining` is design/persistence documentation, not a production revenue runtime.

## Cloud computation policy

Cloud compute is part of Yield Harvester. Compare:
- owned hardware;
- permitted free-tier cloud;
- paid/spot/serverless cloud;
- doing nothing.

Free cloud resources are not assumed to permit mining or commercial workloads. Verify current provider terms for the exact workload. Paid cloud requires positive expected withdrawable economics before spend. Cloud is often more valuable for scanners, protocol monitoring, optimization, market/reward discovery, model inference, and batch work than for raw mining.

## Important historic revenue/claim state

Claim Harvester V1 is canonical and source-complete. The strongest linked claim/watch evidence found earlier was the Google Web & App Activity class-action notice in Patrick's Gmail: Google records indicated he may be a class member, but the notice stated no money was available then; it remains waiting, not receivable. Other settlement/refund leads require fresh verification before acting.

No private Gmail content should be copied into public GitHub beyond privacy-safe summaries.

## Restore target

After reconciliation, the next action is NOT more broad ideation.

Primary path:
1. reconcile Nanswap watchdog/result;
2. verify any BANANO receipt on-chain;
3. record immutable financial/outcome evidence;
4. feed measured hash/share/payout data into First-Dollar Benchmark V1;
5. decide whether another bounded run, Monero P2Pool, Folding, cloud/resource-market lane, or stop is the highest-EV next move;
6. preserve customerless / low-human-contact preference.

Secondary work only if it directly supports first-dollar or continuity:
- finish Work-vs-Chat Tattler comparison;
- qualify cloud economics;
- continue Claim Harvester read-only discovery.

Do not reopen completed architecture work merely because a new chat started.
