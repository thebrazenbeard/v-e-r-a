-- Reserve a dedicated API schema without exposing it. Nothing receives access
-- until an explicit API contract and RLS policy are reviewed.

CREATE SCHEMA IF NOT EXISTS vera_cp_api AUTHORIZATION postgres;
REVOKE ALL ON SCHEMA vera_cp_api FROM PUBLIC, anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA vera_cp_api
  REVOKE ALL ON TABLES FROM anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA vera_cp_api
  REVOKE ALL ON SEQUENCES FROM anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA vera_cp_api
  REVOKE ALL ON FUNCTIONS FROM anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA vera_cp_api
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;