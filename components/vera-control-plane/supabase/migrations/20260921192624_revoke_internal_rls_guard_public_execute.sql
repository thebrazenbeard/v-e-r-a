-- Defense-in-depth hardening for the internal RLS event-trigger function.
REVOKE EXECUTE ON FUNCTION vera_cp_internal.enable_rls_for_new_api_tables()
  FROM PUBLIC, anon, authenticated, service_role, vera_sd1_causal_anchor_broker;