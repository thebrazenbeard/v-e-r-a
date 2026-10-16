# Vera Works Infrastructure Triggers

V1 deliberately avoids infrastructure that has not earned its complexity. Adoption is triggered by correctness or workload requirements, not appearance.

## PostgreSQL

Adopt a dedicated Vera Works PostgreSQL database when at least one becomes operationally material:

- atomic multi-entity updates are required;
- concurrent writers need uniqueness or transactional guarantees Git cannot safely provide;
- durable webhook ingestion becomes part of normal operation;
- frequent cross-entity operational queries make event-file scanning inappropriate;
- customer/order/runtime state becomes too active or sensitive for repository storage.

Do not borrow Project Lantern or BT2 simply because they exist. Vera Works receives dedicated persistence when triggered.

## Supabase vs plain PostgreSQL / WoWSQL

Prefer Supabase when Vera Works needs PostgreSQL plus meaningful use of Auth, Storage, Realtime, generated APIs, or Edge Functions.

Prefer a simpler PostgreSQL surface such as WoWSQL when relational persistence/SQL is the actual requirement and the broader Supabase platform would be unused baggage.

## External orchestration

Move beyond GitHub Actions when Vera Works needs durable queued execution, retry/backoff and dead-letter behavior, long-running jobs, tighter scheduling guarantees, or orchestration across multiple external systems/services.

## API-native model workers

Adopt an API-native worker when a model task must start without Vera or Patrick manually invoking a chat, must consume structured queued work, or must run repeatedly/scheduled.

Interactive GPTs remain useful specialists but are not assumed to be daemons, schedulers, queue consumers, or reliable autonomous runtimes.

## Financial integration

Add dedicated financial ingestion/reconciliation when transaction volume makes statement import and deterministic matching materially burdensome or delayed reconciliation creates meaningful risk. Raw credentials and unrelated personal financial activity remain outside GitHub.
