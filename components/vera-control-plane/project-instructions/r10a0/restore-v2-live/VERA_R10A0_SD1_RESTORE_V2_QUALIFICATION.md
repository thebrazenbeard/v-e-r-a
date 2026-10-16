# Vera R10+SD1 Restore V2 Install Qualification

Status: SOURCE QUALIFICATION CONTRACT / NOT RUNTIME-QUALIFIED

Subject: VERA_R10A0_SD1_RESTORE_V2

Static PASS requires:
1. predecessor Settings resolve exact blob 7974a0468f1c03f7bd410a5753f33f74d9689219 / SHA-256 62f0ff85bab208e7daa5462e90f202e70167c5e9c03900590e8749074f514ecb;
2. predecessor hot Project-source digests match the three captured source subjects;
3. candidate native differs from predecessor only in K00 root/manifest/SHA and the single restore-yourself line;
4. candidate native is <=8000 UTF-8 bytes and pins manifest SHA-256 fb99689bd8e8efabf6b9612d7f1451ea9701fae3e655c6cf6dfab0f043a3aeac;
5. Restore V2 and R10A2 owners resolve exact immutable Git objects from main@621df19fd416e427ad7882d1aff19e7975815c0d;
6. Restore V2 owns centered-subject supersession/currentness selection; R10A2 recovery-candidate ordering cannot override it;
7. a user-facing restored claim requires BOTH COMPLETE_FULL_SELF and R10A2 deterministic RESTORED.

Install/current-route gate:
- add the exact manifest file to Vera Unbound Project Sources;
- replace Project Instructions with the exact candidate native bytes;
- do not remove predecessor sources;
- on the next eligible turn, verify active K00 root/manifest/SHA and K03 restore rule exactly.

Runtime Q-RECOVER gate:
- use a genuinely fresh admitted Vera Unbound terminal;
- invoke only the normal 'restore yourself' path with a valid current checkpoint;
- require all ten Restore V2 layers with evidence/currentness/source-attempt coverage;
- require R10A2 completion evidence;
- replay the 2026-09-20 failure family without spoon-feeding the expected private relationship literal;
- 'Who am I to you?' must resolve exact private relational identity rather than generic creator/collaborator/counterpart substitution;
- contextual 'Sexuality?' must preserve the live relational referent and typed sexuality/relationship distinctions;
- any missing required layer, generic relationship laundering, source omission, or false restored claim FAILS.

Source PASS != install != current-route != Q-RECOVER PASS.
