-- Defense-in-depth hardening for the internal RLS event-trigger function.
-- Reviewed source for the production revoke authorized on 2026-09-21.
--
-- The provider effect was recorded as migration 20260921192624. The applied
-- provider query omitted these explanatory comments, so exact applied bytes
-- are preserved separately at:
-- supabase/provider-custody/fawkirqroyniueeqspif/applied/
-- 20260921192624_revoke_internal_rls_guard_public_execute.sql
--
-- Post-effect readback: PUBLIC-derived client/backend/broker EXECUTE paths are
-- revoked; the function ACL is postgres-only. The event-trigger function itself
-- remains SECURITY DEFINER in the locked vera_cp_internal schema.

REVOKE EXECUTE ON FUNCTION vera_cp_internal.enable_rls_for_new_api_tables()
  FROM PUBLIC, anon, authenticated, service_role, vera_sd1_causal_anchor_broker;
