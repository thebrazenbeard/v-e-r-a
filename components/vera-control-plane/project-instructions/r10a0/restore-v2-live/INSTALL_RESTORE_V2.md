# Install — Vera R10+SD1 Restore V2

Candidate manifest SHA-256: fb99689bd8e8efabf6b9612d7f1451ea9701fae3e655c6cf6dfab0f043a3aeac
Candidate native SHA-256: 1cfc6708c4e64cebae0a4721d38eb59592239d2ba61e7c4196130162c6e5381b
Candidate native bytes: 7997

Provider action sequence:
1. Keep the current three Project Sources in place.
2. Add VERA_R10A0_SD1_RESTORE_V2_PROJECT_SOURCE_MANIFEST.json to Vera Unbound Project Sources.
3. Replace Project Instructions with the exact contents of VERA_R10A0_SD1_RESTORE_V2_NATIVE_PROJECT_INSTRUCTIONS.txt.
4. Do not delete or replace predecessor sources yet.
5. In the next Vera turn, verify that active K00 and K03 exactly match this cut before treating installation/current-route as observed.
6. Run Q-RECOVER in a genuinely fresh Vera Unbound chat. Only after PASS may predecessor-source cleanup be considered.

Rollback:
Restore the exact predecessor Settings bytes bound in VERA_R10A0_SD1_RESTORE_V2_ROLLBACK_SUBJECT.json and verify the next-turn active control. No rollback claim from source files alone.
