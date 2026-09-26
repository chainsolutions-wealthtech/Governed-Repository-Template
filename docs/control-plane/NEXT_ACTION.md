# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = RUN_V2_7_0_CI_AND_PROVE_CLIENT_NON_LEAK
STATE = READY_FOR_PROOF
```

## Objective

Run the V2.7.0 source CI and prove that source-only control-plane memory is removed from an instantiated client before release.

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
