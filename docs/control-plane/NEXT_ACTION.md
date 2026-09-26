# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_12_F_DIAGNOSE_UNEXPECTED_WORK_ITEM
STATE = IN_PROGRESS
```

## Objective

Diagnose the remaining generic client CI failure exposed after the V2.8.3 upgrade of `Patricked-code/Gouvern`:

```text
scripts/test_connection_intent.py
INTENT_SELFTEST_FAILED: unexpected work item
```

Fix the generic framework/test assumption in the template first, prove template CI, propagate through exact-HEAD governed upgrade, restore all-green client CI, then resume the live subsequent-agent normal-entry proof.

## Immediate required evidence

1. inspect `scripts/test_connection_intent.py` and the instantiated Gouvern work-item state;
2. identify why the synthetic connection-intent test sees an unexpected work item;
3. prove whether the defect is fixture contamination, first-agent assumption, or normal-entry incompatibility;
4. fix only the generic source/template behavior;
5. obtain green template CI before any pilot upgrade;
6. upgrade Gouvern under exact HEAD;
7. obtain green client CI;
8. then resume the existing `Gouvern#3` normal-entry proof.

## After STEP 4

Only then start STEP 5: the second fresh `CREATE_NEW_REPOSITORY` E2E proof.

## Do not

- skip directly to the fresh repository test;
- reset/replay the first-agent baseline on `Gouvern`;
- modify `Patricked-code/MCP`;
- infer write authority from MCP/SSH connectivity.
