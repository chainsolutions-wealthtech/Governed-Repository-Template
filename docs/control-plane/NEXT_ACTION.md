# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = P12_S5_SECOND_FRESH_REPOSITORY_E2E
STATE = IN_PROGRESS
```

## Objective

Execute STEP 5 / C1-13: create and validate a **second clean disposable repository** from the current governed Template and prove the full CREATE_NEW_REPOSITORY lifecycle from zero without relying on the historical `Patricked-code/Gouvern` migration path.

## Completed prerequisite

STEP 4 / C1-12 is complete:

- pilot: `Patricked-code/Gouvern`;
- exact pilot HEAD: `671774dfc8e8be8eac2b50d5fb8f0928591694b3`;
- machine local entry: `Gouvern#4`;
- request: `LOCAL-000004`;
- mode: `NORMAL_GOVERNED_ENTRY`;
- final status: `LOCAL_HANDOFF_READY`, revision 6;
- first-agent session `LOCAL-000002-S1` preserved;
- `WORK-PROJECT-001` preserved;
- no duplicate baseline/session/work;
- no target Git mutation during normal-entry proof.

## Required sequence

1. reobserve Template `main` and current canonical programme before any creation;
2. choose/create a second **fresh disposable repository**, distinct from `Patricked-code/Gouvern`;
3. start from current Template state, not from migrated pilot history;
4. execute the full governed lifecycle:
   `CREATE → BOOTSTRAP → FIRST_AGENT → PROJECT BASELINE → OPTIONAL MCP LINK → transport/discovery only if selected → DOMAIN when applicable → SETUP → APPLY_BASELINE → HANDOFF → NORMAL ENTRY`;
5. preserve owner choices exactly; MCP linkage may be declined and must not be invented;
6. require uninterrupted governed execution with no target-specific repair;
7. require all CI/attestations green;
8. persist complete evidence before advancing to `P12-S6`.

## Safety boundary

- Do not reuse `Gouvern` as the second fresh repository.
- Do not replay the completed Gouvern normal-entry proof.
- Do not patch the fresh target directly to hide a framework defect.
- If a generic framework defect appears, stop target mutation and fix the Template first.
- Do not close CASE 1 until STEP 5 passes and evidence is reconciled.
- GMC implementation remains dependency-bound behind `P12-S6`.
