# Vera Supabase project — source definition snapshot

This branch is a governed, read-only **source/definition snapshot** of the live Supabase project named **Vera**, project reference `klmbpaigzeguvnpccqzz` (region `ca-central-1`). The source is the actual connected Supabase provider. This branch does not change or deploy the live project.

## Included

- `supabase/project.json`: exact project identity and provenance limits.
- `supabase/migration-index.json`: 99 observed applied migration names and versions. Original migration SQL is **not** available from the connector's migration-list endpoint.
- `supabase/database.types.ts`: live generated TypeScript database type definitions.
- `supabase/schema/{public,build_team_2,bug_ops,radar,redworm,semantic_atlas}/relations.json`: column types, nullability, defaults, constraints, indexes, sequences, materialized/ordinary view definitions, and per-table RLS flags for six application schemas.
- `supabase/schema/{...}/routines.json`: 163 live SQL routine definitions across those six schemas, including their security-definer flags.
- `supabase/schema/row-level-policies.json`: 63 observed policy definitions.
- `supabase/schema/triggers.json`: 54 observed non-internal trigger definitions.
- `supabase/schema/access-grants.json`: observed relation grants.
- `supabase/schema/custom-types.json`, `extensions.json`: user-defined enum/domain and installed extension inventories.
- `supabase/functions/github-bus-ingest/`: source files of the live Edge Function, accompanied by its live version and digest binding.

## Not included

**No live table rows, credentials, tokens, secrets, user authentication records, storage objects, vault values, or project deployment settings are published.** The SQL migration catalog supplies names and versions, not complete historical migration bodies. This snapshot is **not a restorable production database dump** and does not claim to capture internal/provider-managed schemas, activity or continuous synchronization. A live Supabase project does not correspond to a Git repository without a deliberate export contract.

**Project separation:** this is the Supabase **Vera** project, not the WoWSQL `bt2-479e4ad9` Project Lantern runtime. The separate older Supabase project `agvhmutlrolbaijzlbqk` is not a fallback for Lantern and is not represented by this branch.

The original Supabase project remains authoritative. Changes to schemas or Edge Functions must be qualified and separately authorized; copying definitions into a public Git branch grants no deployment or data access authority.
