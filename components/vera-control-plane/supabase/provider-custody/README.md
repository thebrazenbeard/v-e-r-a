# Vera Control Plane Supabase provider custody

This directory preserves exact SQL recovered from the production Supabase migration
ledger for project `fawkirqroyniueeqspif`.

Two provenance classes are intentionally distinct:

- `EXACT_PROVIDER_SOURCE_RECOVERED`: the provider retained the exact applied SQL,
  but no pre-application Git source was recovered. These bytes are now canonical
  custody for reproducibility, not a claim that Git originally held them.
- `EXACT_DEPLOYED_SOURCE_BYTES_VERIFIED`: deployed SQL was independently matched
  byte-for-byte to an identified Git source artifact.

The machine-readable authority for the current mapping is:

`governance/VCP_SUPABASE_PROVIDER_CUSTODY_V1.json`

Do not rename recovered provider SQL to simulate historical source provenance.
