# Vera Restore V2 install currentness — current-main reconciliation 2026-09-22

The Restore V2 source cut was merged historically at:

`main@57bd2cd3e53bc112d7bf220ede82225f14e2e540`

Current VCP main observed for this reconciliation is:

`505c395890bde275cbbc6327be8f387e7f25ca3a`

Current main is a descendant of that source cut. The immutable Restore V2 source artifacts remain byte-identical to their bound artifact subject:

- artifact commit: `687ba64555c39619a9552a86206fa78ab3387a7e`;
- manifest Git blob: `8327031704186a59450ae8bc20c944491cf22396`;
- native instructions Git blob: `348f668be5da7ed0fd834947975dbea1579ffddd`;
- source receipt Git blob on the merged source cut/current main: `6d4e0820c025030140f00552d654054c5566e171`.

The bound content digests remain:

- manifest SHA-256: `fb99689bd8e8efabf6b9612d7f1451ea9701fae3e655c6cf6dfab0f043a3aeac`, 8035 bytes;
- native instructions SHA-256: `1cfc6708c4e64cebae0a4721d38eb59592239d2ba61e7c4196130162c6e5381b`, 7997 bytes.

This establishes current repository custody of the exact source artifacts. It does **not** establish Vera Unbound Project Settings installation, current-route consumption, or Q-RECOVER success.

The exact stronger gates remain separate:

1. exact Project Sources / Project Instructions effect evidence;
2. active K00/K03 readback for the installed route;
3. fresh Q-RECOVER behavioral qualification.

This source reconciliation does not claim those gates were executed.

`SOURCE_CUSTODY != PROJECT_INSTALL != CURRENT_ROUTE != Q_RECOVER`

No terminal identity or execution environment is used as evidence for any stronger state.
