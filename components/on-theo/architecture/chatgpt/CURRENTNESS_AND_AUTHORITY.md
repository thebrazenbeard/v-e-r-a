# Currentness and Authority

## Canonical currentness

GitHub is authoritative for:
- branch/ref state;
- commit history;
- pull requests;
- source/research artifacts;
- repository-governed conclusions.

Before a state-sensitive action, fresh-read the relevant ref.

If a remembered SHA differs from the live SHA:
1. stop treating the remembered state as current;
2. inspect the divergence;
3. preserve newer work;
4. bind any new action to the live head.

## Human authority

Patrick retains authority for:
- merge;
- force push;
- branch deletion;
- history rewrite;
- repository visibility or permissions;
- credentials;
- deployment;
- paid compute;
- publication or other protected effects.

Research branch writes and draft PR updates are allowed when Patrick asks to
continue/build/research/save and the tool surface permits them, but they do not
create canonical merge authority.

## Verification

Distinguish:
- commit created;
- branch ref updated;
- PR updated;
- test executed;
- review passed;
- merged;
- deployed.

Never collapse these states.
