-- Defense-in-depth: any future table created in an API-facing schema
-- starts with RLS enabled. The internal guard function itself is not exposed.

CREATE SCHEMA IF NOT EXISTS vera_cp_internal AUTHORIZATION postgres;
REVOKE ALL ON SCHEMA vera_cp_internal FROM PUBLIC, anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA vera_cp_internal
  REVOKE ALL ON TABLES FROM anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA vera_cp_internal
  REVOKE ALL ON SEQUENCES FROM anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA vera_cp_internal
  REVOKE ALL ON FUNCTIONS FROM anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA vera_cp_internal
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

CREATE OR REPLACE FUNCTION vera_cp_internal.enable_rls_for_new_api_tables()
RETURNS event_trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
DECLARE
  obj record;
BEGIN
  FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands()
  LOOP
    IF obj.object_type IN ('table', 'partitioned table')
       AND obj.schema_name IN ('public', 'vera_cp_api') THEN
      EXECUTE format('ALTER TABLE %s ENABLE ROW LEVEL SECURITY', obj.object_identity);
    END IF;
  END LOOP;
END;
$$;

DROP EVENT TRIGGER IF EXISTS vera_cp_enable_rls_on_new_api_tables;
CREATE EVENT TRIGGER vera_cp_enable_rls_on_new_api_tables
  ON ddl_command_end
  WHEN TAG IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
  EXECUTE FUNCTION vera_cp_internal.enable_rls_for_new_api_tables();