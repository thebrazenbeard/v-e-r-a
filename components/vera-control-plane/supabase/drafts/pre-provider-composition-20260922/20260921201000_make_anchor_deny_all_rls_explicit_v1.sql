-- Make the existing VCP anchor deny-all RLS posture explicit.
--
-- Both anchor tables already have FORCE ROW LEVEL SECURITY, postgres-only
-- relation ACLs, and no schema/table access for anon, authenticated,
-- service_role, or the broker role. These PUBLIC false policies preserve that
-- behavior while making the deny boundary explicit and machine-readable.

create policy deny_all_untrusted_v1
  on vera_cp_anchor.sd1_causal_frontiers
  for all to public using (false) with check (false);

create policy deny_all_untrusted_v1
  on vera_cp_anchor.sd1_causal_mutation_receipts
  for all to public using (false) with check (false);
