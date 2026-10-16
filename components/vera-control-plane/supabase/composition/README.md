# VCP Supabase provider composition

`supabase/migrations/` is the executable reconstruction baseline for the
Vera Control Plane Supabase project. Its baseline identities and bytes must
match the live provider migration ledger exactly.

The three pre-repair alternate-timestamp sources are preserved under
`supabase/drafts/pre-provider-composition-20260922/` for audit only.

Future migrations must advance the bound provider cut and be declared before
they enter the executable directory. Git source, provider application, and
provider readback remain separate evidence/effect domains.
