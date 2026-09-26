# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = COMPLETE_V2_7_0_SELF_GOVERNED_CONTROL_PLANE
STATE = IN_PROGRESS
```

## Objective

Complete the source-only persistent-memory layer for the control-plane repository.

## Required completion evidence

1. source-only human authorities exist;
2. source-only machine checkpoint/handoff/task projections exist;
3. governance validation requires them in template-source mode;
4. initialization removes source-only directories from generated clients;
5. bootstrap self-test proves those directories do not survive client initialization;
6. source CI is green;
7. V2.7.0 is merged;
8. source state is reconciled to the merged release;
9. resume canonical program #12 at `STEP_4_SECOND_FRESH_REPOSITORY_E2E`.

## Do not

- start the second fresh repository before this migration is green;
- modify `Patricked-code/MCP`;
- overwrite distributed root project-state templates with source-project history.
