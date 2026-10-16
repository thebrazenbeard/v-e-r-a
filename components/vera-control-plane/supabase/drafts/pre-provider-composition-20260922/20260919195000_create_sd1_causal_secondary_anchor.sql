-- Vera SD1 causal secondary monotonic anchor V1.
-- Control-plane-only provider migration.
--
-- SOURCE ONLY until separately authorized/applied to exact Supabase project
-- fawkirqroyniueeqspif. PROVIDER != CONTROL AUTHORITY.
--
-- Purpose:
--   provide an independently monotonic, append-only CAS frontier that prevents
--   an unprotected Git audit mirror from silently reopening an earlier valid
--   causal-ledger prefix.
--
-- This migration creates no causal responses and does not establish SD1
-- causality. The controller credential receives only two bounded RPCs:
-- read-current-frontier and advance-exactly-one-generation.

CREATE SCHEMA vera_cp_anchor AUTHORIZATION postgres;

REVOKE ALL ON SCHEMA vera_cp_anchor
  FROM PUBLIC, anon, authenticated, service_role;

CREATE ROLE vera_sd1_causal_anchor_broker
  NOLOGIN
  NOSUPERUSER
  NOCREATEDB
  NOCREATEROLE
  NOINHERIT
  NOBYPASSRLS;

-- The PostgREST authenticator may SET ROLE only when presented a separately
-- provisioned/authenticated token naming this exact NOLOGIN role.
GRANT vera_sd1_causal_anchor_broker TO authenticator;

CREATE FUNCTION vera_cp_anchor.sd1_causal_frontier_digest_v1(
    p_chain_head text,
    p_generation bigint,
    p_last_record_digest text,
    p_last_slot_id text,
    p_ledger_schema text,
    p_plan_sha256 text,
    p_predecessor_frontier_digest text,
    p_record_count bigint,
    p_schema text,
    p_witness_store_id text
)
RETURNS text
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
SET search_path = pg_catalog, extensions
AS $fn$
    SELECT encode(
        extensions.digest(
            convert_to(
                '{"chain_head":' || to_json(p_chain_head)::text ||
                ',"generation":' || p_generation::text ||
                ',"last_record_digest":' || coalesce(to_json(p_last_record_digest)::text, 'null') ||
                ',"last_slot_id":' || coalesce(to_json(p_last_slot_id)::text, 'null') ||
                ',"ledger_schema":' || to_json(p_ledger_schema)::text ||
                ',"plan_sha256":' || to_json(p_plan_sha256)::text ||
                ',"predecessor_frontier_digest":' || coalesce(to_json(p_predecessor_frontier_digest)::text, 'null') ||
                ',"record_count":' || p_record_count::text ||
                ',"schema":' || to_json(p_schema)::text ||
                ',"witness_store_id":' || to_json(p_witness_store_id)::text ||
                '}',
                'UTF8'
            ),
            'sha256'
        ),
        'hex'
    );
$fn$;

REVOKE ALL ON FUNCTION vera_cp_anchor.sd1_causal_frontier_digest_v1(
  text,bigint,text,text,text,text,text,bigint,text,text
) FROM PUBLIC, anon, authenticated, service_role, vera_sd1_causal_anchor_broker;

CREATE FUNCTION vera_cp_anchor.sd1_causal_request_digest_v1(
    p_chain_head text,
    p_expected_frontier_digest text,
    p_expected_generation bigint,
    p_frontier_digest text,
    p_generation bigint,
    p_last_record_digest text,
    p_last_slot_id text,
    p_predecessor_frontier_digest text,
    p_record_count bigint,
    p_request_id text
)
RETURNS text
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
SET search_path = pg_catalog, extensions
AS $fn$
    SELECT encode(
        extensions.digest(
            convert_to(
                '{"chain_head":' || to_json(p_chain_head)::text ||
                ',"expected_frontier_digest":' || to_json(p_expected_frontier_digest)::text ||
                ',"expected_generation":' || p_expected_generation::text ||
                ',"frontier_digest":' || to_json(p_frontier_digest)::text ||
                ',"generation":' || p_generation::text ||
                ',"last_record_digest":' || to_json(p_last_record_digest)::text ||
                ',"last_slot_id":' || to_json(p_last_slot_id)::text ||
                ',"operation_id":"sd1.causal.frontier.advance.v1"' ||
                ',"predecessor_frontier_digest":' || to_json(p_predecessor_frontier_digest)::text ||
                ',"record_count":' || p_record_count::text ||
                ',"request_id":' || to_json(p_request_id)::text ||
                '}',
                'UTF8'
            ),
            'sha256'
        ),
        'hex'
    );
$fn$;

REVOKE ALL ON FUNCTION vera_cp_anchor.sd1_causal_request_digest_v1(
  text,text,bigint,text,bigint,text,text,text,bigint,text
) FROM PUBLIC, anon, authenticated, service_role, vera_sd1_causal_anchor_broker;

CREATE TABLE vera_cp_anchor.sd1_causal_frontiers (
    witness_id text NOT NULL,
    frontier_schema text NOT NULL,
    witness_store_id text NOT NULL,
    plan_sha256 text NOT NULL,
    ledger_schema text NOT NULL,
    generation bigint NOT NULL,
    record_count bigint NOT NULL,
    chain_head text NOT NULL,
    last_slot_id text,
    last_record_digest text,
    predecessor_frontier_digest text,
    frontier_digest text NOT NULL,
    request_id text NOT NULL,
    request_digest text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT sd1_causal_frontiers_pk
      PRIMARY KEY (witness_id, generation),
    CONSTRAINT sd1_causal_frontiers_digest_unique
      UNIQUE (witness_id, frontier_digest),
    CONSTRAINT sd1_causal_frontiers_request_unique
      UNIQUE (witness_id, request_id),

    CONSTRAINT sd1_causal_frontiers_witness_exact
      CHECK (witness_id = 'VERA_SD1_CAUSAL_V1'),
    CONSTRAINT sd1_causal_frontiers_schema_exact
      CHECK (frontier_schema = 'SD1_CAUSAL_LEDGER_FRONTIER_V1'),
    CONSTRAINT sd1_causal_frontiers_store_exact
      CHECK (
        witness_store_id =
        'github:thebrazenbeard/vera-control-plane:state/sd1-causal-witness-v1'
      ),
    CONSTRAINT sd1_causal_frontiers_plan_exact
      CHECK (
        plan_sha256 =
        '526f35438c2521d40e7a2bfa145da363e0c5063d2affef27131f9370e08564ba'
      ),
    CONSTRAINT sd1_causal_frontiers_ledger_schema_exact
      CHECK (ledger_schema = 'SD1_CAUSAL_ATTEMPT_LEDGER_V1'),
    CONSTRAINT sd1_causal_frontiers_generation_nonnegative
      CHECK (generation >= 0),
    CONSTRAINT sd1_causal_frontiers_count_matches_generation
      CHECK (record_count = generation),
    CONSTRAINT sd1_causal_frontiers_chain_head_sha256
      CHECK (chain_head ~ '^[0-9a-f]{64}$'),
    CONSTRAINT sd1_causal_frontiers_digest_sha256
      CHECK (frontier_digest ~ '^[0-9a-f]{64}$'),
    CONSTRAINT sd1_causal_frontiers_request_digest_sha256
      CHECK (request_digest ~ '^[0-9a-f]{64}$'),
    CONSTRAINT sd1_causal_frontiers_tail_shape
      CHECK (
        (
          generation = 0
          AND last_slot_id IS NULL
          AND last_record_digest IS NULL
          AND predecessor_frontier_digest IS NULL
        )
        OR
        (
          generation > 0
          AND last_slot_id ~ '^[0-9a-f]{32}$'
          AND last_record_digest ~ '^[0-9a-f]{64}$'
          AND predecessor_frontier_digest ~ '^[0-9a-f]{64}$'
        )
      ),
    CONSTRAINT sd1_causal_frontiers_canonical_digest
      CHECK (
        frontier_digest =
        vera_cp_anchor.sd1_causal_frontier_digest_v1(
          chain_head,
          generation,
          last_record_digest,
          last_slot_id,
          ledger_schema,
          plan_sha256,
          predecessor_frontier_digest,
          record_count,
          frontier_schema,
          witness_store_id
        )
      )
);

ALTER TABLE vera_cp_anchor.sd1_causal_frontiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE vera_cp_anchor.sd1_causal_frontiers FORCE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE vera_cp_anchor.sd1_causal_frontiers
  FROM PUBLIC, anon, authenticated, service_role, vera_sd1_causal_anchor_broker;

CREATE TABLE vera_cp_anchor.sd1_causal_mutation_receipts (
    receipt_id text PRIMARY KEY,
    witness_id text NOT NULL,
    request_id text NOT NULL UNIQUE,
    request_digest text NOT NULL,
    result_status text NOT NULL,
    expected_generation bigint NOT NULL,
    expected_frontier_digest text NOT NULL,
    observed_generation bigint NOT NULL,
    observed_frontier_digest text NOT NULL,
    successor_generation bigint,
    successor_frontier_digest text,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT sd1_causal_receipts_witness_exact
      CHECK (witness_id = 'VERA_SD1_CAUSAL_V1'),
    CONSTRAINT sd1_causal_receipts_id_exact
      CHECK (receipt_id = 'sd1-causal:' || request_id),
    CONSTRAINT sd1_causal_receipts_request_id_shape
      CHECK (request_id ~ '^[A-Za-z0-9._:-]{16,128}$'),
    CONSTRAINT sd1_causal_receipts_request_digest_sha256
      CHECK (request_digest ~ '^[0-9a-f]{64}$'),
    CONSTRAINT sd1_causal_receipts_expected_digest_sha256
      CHECK (expected_frontier_digest ~ '^[0-9a-f]{64}$'),
    CONSTRAINT sd1_causal_receipts_observed_digest_sha256
      CHECK (observed_frontier_digest ~ '^[0-9a-f]{64}$'),
    CONSTRAINT sd1_causal_receipts_status_exact
      CHECK (result_status IN ('APPLIED_VERIFIED', 'REJECTED_STALE')),
    CONSTRAINT sd1_causal_receipts_successor_shape
      CHECK (
        (
          result_status = 'APPLIED_VERIFIED'
          AND successor_generation IS NOT NULL
          AND successor_frontier_digest ~ '^[0-9a-f]{64}$'
        )
        OR
        (
          result_status = 'REJECTED_STALE'
          AND successor_generation IS NULL
          AND successor_frontier_digest IS NULL
        )
      )
);

ALTER TABLE vera_cp_anchor.sd1_causal_mutation_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE vera_cp_anchor.sd1_causal_mutation_receipts FORCE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE vera_cp_anchor.sd1_causal_mutation_receipts
  FROM PUBLIC, anon, authenticated, service_role, vera_sd1_causal_anchor_broker;

CREATE FUNCTION vera_cp_anchor.reject_sd1_causal_anchor_rewrite_v1()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $fn$
BEGIN
    RAISE EXCEPTION 'SD1 causal anchor is append-only; UPDATE/DELETE forbidden'
      USING ERRCODE = '55000';
END;
$fn$;

REVOKE ALL ON FUNCTION vera_cp_anchor.reject_sd1_causal_anchor_rewrite_v1()
  FROM PUBLIC, anon, authenticated, service_role, vera_sd1_causal_anchor_broker;

CREATE TRIGGER sd1_causal_frontiers_append_only
BEFORE UPDATE OR DELETE ON vera_cp_anchor.sd1_causal_frontiers
FOR EACH ROW
EXECUTE FUNCTION vera_cp_anchor.reject_sd1_causal_anchor_rewrite_v1();

CREATE TRIGGER sd1_causal_receipts_append_only
BEFORE UPDATE OR DELETE ON vera_cp_anchor.sd1_causal_mutation_receipts
FOR EACH ROW
EXECUTE FUNCTION vera_cp_anchor.reject_sd1_causal_anchor_rewrite_v1();

INSERT INTO vera_cp_anchor.sd1_causal_frontiers (
    witness_id,
    frontier_schema,
    witness_store_id,
    plan_sha256,
    ledger_schema,
    generation,
    record_count,
    chain_head,
    last_slot_id,
    last_record_digest,
    predecessor_frontier_digest,
    frontier_digest,
    request_id,
    request_digest
)
VALUES (
    'VERA_SD1_CAUSAL_V1',
    'SD1_CAUSAL_LEDGER_FRONTIER_V1',
    'github:thebrazenbeard/vera-control-plane:state/sd1-causal-witness-v1',
    '526f35438c2521d40e7a2bfa145da363e0c5063d2affef27131f9370e08564ba',
    'SD1_CAUSAL_ATTEMPT_LEDGER_V1',
    0,
    0,
    '527ddd4d35e85dfcff56b8c209ba2a6b642c08a18a9d2ae704626e8c78bfe229',
    NULL,
    NULL,
    NULL,
    '7de55cc22b28539c1d4e6934b1790d99c70ecee55ded80d7b698bec61ee249a1',
    'GENESIS',
    encode(
      extensions.digest(
        convert_to('VERA_SD1_CAUSAL_V1_GENESIS_REQUEST', 'UTF8'),
        'sha256'
      ),
      'hex'
    )
);

DO $do$
DECLARE
    v_digest text;
BEGIN
    SELECT frontier_digest
      INTO v_digest
      FROM vera_cp_anchor.sd1_causal_frontiers
     WHERE witness_id = 'VERA_SD1_CAUSAL_V1'
       AND generation = 0;

    IF v_digest IS DISTINCT FROM
       '7de55cc22b28539c1d4e6934b1790d99c70ecee55ded80d7b698bec61ee249a1'
    THEN
        RAISE EXCEPTION 'SD1 causal genesis frontier digest readback mismatch';
    END IF;
END
$do$;

CREATE FUNCTION vera_cp_api.sd1_causal_frontier_read_v1()
RETURNS TABLE (
    witness_id text,
    frontier_schema text,
    witness_store_id text,
    plan_sha256 text,
    ledger_schema text,
    generation bigint,
    record_count bigint,
    chain_head text,
    last_slot_id text,
    last_record_digest text,
    predecessor_frontier_digest text,
    frontier_digest text,
    created_at timestamptz
)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog
AS $fn$
    SELECT
      f.witness_id,
      f.frontier_schema,
      f.witness_store_id,
      f.plan_sha256,
      f.ledger_schema,
      f.generation,
      f.record_count,
      f.chain_head,
      f.last_slot_id,
      f.last_record_digest,
      f.predecessor_frontier_digest,
      f.frontier_digest,
      f.created_at
    FROM vera_cp_anchor.sd1_causal_frontiers AS f
    WHERE f.witness_id = 'VERA_SD1_CAUSAL_V1'
    ORDER BY f.generation DESC
    LIMIT 1;
$fn$;

CREATE FUNCTION vera_cp_api.sd1_causal_receipt_read_v1(
    p_request_id text
)
RETURNS TABLE (
    receipt_id text,
    request_id text,
    request_digest text,
    result_status text,
    expected_generation bigint,
    expected_frontier_digest text,
    observed_generation bigint,
    observed_frontier_digest text,
    successor_generation bigint,
    successor_frontier_digest text,
    created_at timestamptz
)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog
AS $fn$
    SELECT
      r.receipt_id,
      r.request_id,
      r.request_digest,
      r.result_status,
      r.expected_generation,
      r.expected_frontier_digest,
      r.observed_generation,
      r.observed_frontier_digest,
      r.successor_generation,
      r.successor_frontier_digest,
      r.created_at
    FROM vera_cp_anchor.sd1_causal_mutation_receipts AS r
    WHERE r.witness_id = 'VERA_SD1_CAUSAL_V1'
      AND r.request_id = p_request_id
    LIMIT 1;
$fn$;

CREATE FUNCTION vera_cp_api.sd1_causal_frontier_advance_v1(
    p_request_id text,
    p_request_digest text,
    p_expected_generation bigint,
    p_expected_frontier_digest text,
    p_generation bigint,
    p_record_count bigint,
    p_chain_head text,
    p_last_slot_id text,
    p_last_record_digest text,
    p_predecessor_frontier_digest text,
    p_frontier_digest text
)
RETURNS TABLE (
    result_status text,
    stored_result_status text,
    receipt_id text,
    observed_generation bigint,
    observed_frontier_digest text,
    successor_generation bigint,
    successor_frontier_digest text
)
LANGUAGE plpgsql
VOLATILE
SECURITY DEFINER
SET search_path = pg_catalog, extensions
AS $fn$
DECLARE
    v_existing vera_cp_anchor.sd1_causal_mutation_receipts%ROWTYPE;
    v_current vera_cp_anchor.sd1_causal_frontiers%ROWTYPE;
    v_computed_request_digest text;
    v_computed_frontier_digest text;
BEGIN
    IF p_request_id IS NULL
       OR p_request_id !~ '^[A-Za-z0-9._:-]{16,128}$'
    THEN
        RAISE EXCEPTION 'invalid request_id'
          USING ERRCODE = '22023';
    END IF;

    IF p_request_digest IS NULL
       OR p_request_digest !~ '^[0-9a-f]{64}$'
       OR p_expected_frontier_digest IS NULL
       OR p_expected_frontier_digest !~ '^[0-9a-f]{64}$'
       OR p_frontier_digest IS NULL
       OR p_frontier_digest !~ '^[0-9a-f]{64}$'
       OR p_chain_head IS NULL
       OR p_chain_head !~ '^[0-9a-f]{64}$'
       OR p_last_slot_id IS NULL
       OR p_last_slot_id !~ '^[0-9a-f]{32}$'
       OR p_last_record_digest IS NULL
       OR p_last_record_digest !~ '^[0-9a-f]{64}$'
       OR p_predecessor_frontier_digest IS NULL
       OR p_predecessor_frontier_digest !~ '^[0-9a-f]{64}$'
    THEN
        RAISE EXCEPTION 'invalid digest/slot field shape'
          USING ERRCODE = '22023';
    END IF;

    IF p_expected_generation IS NULL
       OR p_generation IS NULL
       OR p_record_count IS NULL
       OR p_expected_generation < 0
       OR p_generation <> p_expected_generation + 1
       OR p_record_count <> p_generation
       OR p_predecessor_frontier_digest <> p_expected_frontier_digest
    THEN
        RAISE EXCEPTION 'invalid successor generation/predecessor relation'
          USING ERRCODE = '22023';
    END IF;

    v_computed_frontier_digest :=
      vera_cp_anchor.sd1_causal_frontier_digest_v1(
        p_chain_head,
        p_generation,
        p_last_record_digest,
        p_last_slot_id,
        'SD1_CAUSAL_ATTEMPT_LEDGER_V1',
        '526f35438c2521d40e7a2bfa145da363e0c5063d2affef27131f9370e08564ba',
        p_predecessor_frontier_digest,
        p_record_count,
        'SD1_CAUSAL_LEDGER_FRONTIER_V1',
        'github:thebrazenbeard/vera-control-plane:state/sd1-causal-witness-v1'
      );

    IF v_computed_frontier_digest IS DISTINCT FROM p_frontier_digest THEN
        RAISE EXCEPTION 'successor frontier digest mismatch'
          USING ERRCODE = '22023';
    END IF;

    v_computed_request_digest :=
      vera_cp_anchor.sd1_causal_request_digest_v1(
        p_chain_head,
        p_expected_frontier_digest,
        p_expected_generation,
        p_frontier_digest,
        p_generation,
        p_last_record_digest,
        p_last_slot_id,
        p_predecessor_frontier_digest,
        p_record_count,
        p_request_id
      );

    IF v_computed_request_digest IS DISTINCT FROM p_request_digest THEN
        RAISE EXCEPTION 'canonical request digest mismatch'
          USING ERRCODE = '22023';
    END IF;

    -- Serialize this exact causal witness before reading its current frontier.
    PERFORM pg_catalog.pg_advisory_xact_lock(
      pg_catalog.hashtextextended('VERA_SD1_CAUSAL_V1', 0)
    );

    SELECT *
      INTO v_existing
      FROM vera_cp_anchor.sd1_causal_mutation_receipts AS r
     WHERE r.request_id = p_request_id;

    IF FOUND THEN
        IF v_existing.request_digest <> p_request_digest THEN
            RETURN QUERY SELECT
              'REQUEST_ID_COLLISION'::text,
              v_existing.result_status,
              v_existing.receipt_id,
              v_existing.observed_generation,
              v_existing.observed_frontier_digest,
              v_existing.successor_generation,
              v_existing.successor_frontier_digest;
            RETURN;
        END IF;

        RETURN QUERY SELECT
          'IDEMPOTENT_REPLAY'::text,
          v_existing.result_status,
          v_existing.receipt_id,
          v_existing.observed_generation,
          v_existing.observed_frontier_digest,
          v_existing.successor_generation,
          v_existing.successor_frontier_digest;
        RETURN;
    END IF;

    SELECT *
      INTO STRICT v_current
      FROM vera_cp_anchor.sd1_causal_frontiers AS f
     WHERE f.witness_id = 'VERA_SD1_CAUSAL_V1'
     ORDER BY f.generation DESC
     LIMIT 1
     FOR UPDATE;

    IF v_current.generation <> p_expected_generation
       OR v_current.frontier_digest <> p_expected_frontier_digest
    THEN
        INSERT INTO vera_cp_anchor.sd1_causal_mutation_receipts (
          receipt_id,
          witness_id,
          request_id,
          request_digest,
          result_status,
          expected_generation,
          expected_frontier_digest,
          observed_generation,
          observed_frontier_digest,
          successor_generation,
          successor_frontier_digest
        )
        VALUES (
          'sd1-causal:' || p_request_id,
          'VERA_SD1_CAUSAL_V1',
          p_request_id,
          p_request_digest,
          'REJECTED_STALE',
          p_expected_generation,
          p_expected_frontier_digest,
          v_current.generation,
          v_current.frontier_digest,
          NULL,
          NULL
        );

        RETURN QUERY SELECT
          'REJECTED_STALE'::text,
          'REJECTED_STALE'::text,
          'sd1-causal:' || p_request_id,
          v_current.generation,
          v_current.frontier_digest,
          NULL::bigint,
          NULL::text;
        RETURN;
    END IF;

    INSERT INTO vera_cp_anchor.sd1_causal_frontiers (
      witness_id,
      frontier_schema,
      witness_store_id,
      plan_sha256,
      ledger_schema,
      generation,
      record_count,
      chain_head,
      last_slot_id,
      last_record_digest,
      predecessor_frontier_digest,
      frontier_digest,
      request_id,
      request_digest
    )
    VALUES (
      'VERA_SD1_CAUSAL_V1',
      'SD1_CAUSAL_LEDGER_FRONTIER_V1',
      'github:thebrazenbeard/vera-control-plane:state/sd1-causal-witness-v1',
      '526f35438c2521d40e7a2bfa145da363e0c5063d2affef27131f9370e08564ba',
      'SD1_CAUSAL_ATTEMPT_LEDGER_V1',
      p_generation,
      p_record_count,
      p_chain_head,
      p_last_slot_id,
      p_last_record_digest,
      p_predecessor_frontier_digest,
      p_frontier_digest,
      p_request_id,
      p_request_digest
    );

    INSERT INTO vera_cp_anchor.sd1_causal_mutation_receipts (
      receipt_id,
      witness_id,
      request_id,
      request_digest,
      result_status,
      expected_generation,
      expected_frontier_digest,
      observed_generation,
      observed_frontier_digest,
      successor_generation,
      successor_frontier_digest
    )
    VALUES (
      'sd1-causal:' || p_request_id,
      'VERA_SD1_CAUSAL_V1',
      p_request_id,
      p_request_digest,
      'APPLIED_VERIFIED',
      p_expected_generation,
      p_expected_frontier_digest,
      v_current.generation,
      v_current.frontier_digest,
      p_generation,
      p_frontier_digest
    );

    RETURN QUERY SELECT
      'APPLIED_VERIFIED'::text,
      'APPLIED_VERIFIED'::text,
      'sd1-causal:' || p_request_id,
      v_current.generation,
      v_current.frontier_digest,
      p_generation,
      p_frontier_digest;
END;
$fn$;

REVOKE ALL ON FUNCTION vera_cp_api.sd1_causal_frontier_read_v1()
  FROM PUBLIC, anon, authenticated, service_role;

REVOKE ALL ON FUNCTION vera_cp_api.sd1_causal_receipt_read_v1(text)
  FROM PUBLIC, anon, authenticated, service_role;

REVOKE ALL ON FUNCTION vera_cp_api.sd1_causal_frontier_advance_v1(
  text,text,bigint,text,bigint,bigint,text,text,text,text,text
) FROM PUBLIC, anon, authenticated, service_role;

GRANT USAGE ON SCHEMA vera_cp_api
  TO vera_sd1_causal_anchor_broker;

GRANT EXECUTE ON FUNCTION vera_cp_api.sd1_causal_frontier_read_v1()
  TO vera_sd1_causal_anchor_broker;

GRANT EXECUTE ON FUNCTION vera_cp_api.sd1_causal_receipt_read_v1(text)
  TO vera_sd1_causal_anchor_broker;

GRANT EXECUTE ON FUNCTION vera_cp_api.sd1_causal_frontier_advance_v1(
  text,text,bigint,text,bigint,bigint,text,text,text,text,text
) TO vera_sd1_causal_anchor_broker;

-- Freeze all direct table paths for the controller/broker role. The two
-- SECURITY DEFINER RPCs above are the entire mutation/readback capability.
REVOKE ALL ON SCHEMA vera_cp_anchor
  FROM vera_sd1_causal_anchor_broker;
REVOKE ALL ON TABLE vera_cp_anchor.sd1_causal_frontiers
  FROM vera_sd1_causal_anchor_broker;
REVOKE ALL ON TABLE vera_cp_anchor.sd1_causal_mutation_receipts
  FROM vera_sd1_causal_anchor_broker;

-- Defensive post-DDL assertions. These fail the migration transaction if
-- canonical genesis or direct broker privileges are not exactly as intended.
DO $do$
DECLARE
    v_genesis_count bigint;
    v_direct_frontier_write boolean;
    v_direct_receipt_write boolean;
BEGIN
    SELECT count(*)
      INTO v_genesis_count
      FROM vera_cp_anchor.sd1_causal_frontiers
     WHERE witness_id = 'VERA_SD1_CAUSAL_V1'
       AND generation = 0
       AND record_count = 0
       AND chain_head =
           '527ddd4d35e85dfcff56b8c209ba2a6b642c08a18a9d2ae704626e8c78bfe229'
       AND frontier_digest =
           '7de55cc22b28539c1d4e6934b1790d99c70ecee55ded80d7b698bec61ee249a1';

    IF v_genesis_count <> 1 THEN
        RAISE EXCEPTION 'SD1 causal genesis exact readback failed';
    END IF;

    SELECT
      has_table_privilege(
        'vera_sd1_causal_anchor_broker',
        'vera_cp_anchor.sd1_causal_frontiers',
        'INSERT,UPDATE,DELETE'
      ),
      has_table_privilege(
        'vera_sd1_causal_anchor_broker',
        'vera_cp_anchor.sd1_causal_mutation_receipts',
        'INSERT,UPDATE,DELETE'
      )
      INTO v_direct_frontier_write, v_direct_receipt_write;

    IF v_direct_frontier_write OR v_direct_receipt_write THEN
        RAISE EXCEPTION 'SD1 causal broker unexpectedly has direct table write privilege';
    END IF;
END
$do$;
