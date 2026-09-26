# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_12_J_B_COMPLETE_PORTABLE_INTENT_FIXTURE
STATE = IN_PROGRESS
```

## Objective

Complete the **framework product** connection-intent self-test fixture so it is fully portable when executed from an already-baselined client.

Product repository:

`chainsolutions-wealthtech/Governed-Repository-Template`

## External validation evidence

V2.8.5 was applied through the governed control-plane upgrade path to the current CASE 1 pilot:

- previous pilot HEAD: `3a1b7689be5aa38b4b6fdb6456526e618f9b0dd5`
- upgraded pilot HEAD: `17f852c19ac8c5d26f40d3508338ce9c221697c8`
- upgrade version reported: `2.8.5`
- control-plane upgrade run: `36274976355`
- pilot CI run: `36275001208` → FAILED at `test_connection_intent.py`

## Root cause

The V2.8.4 fixture isolated work-items, claims, sessions and canonical-memory state but still inherited instantiated client values for:
- project profile;
- infrastructure intent;
- repository-local first-agent state;
- MCP binding;
- access plan;
- workflow model.

The synthetic `auto_bootstrap.py` therefore did not represent a true template-source fixture on an already-baselined client.

## Required Template fix

1. reuse the same generic fixture semantics already proven by `test_bootstrap_consistency.py`;
2. reset only the temporary copied test fixture;
3. preserve the real client state untouched;
4. surface subprocess stdout/stderr on fixture failures;
5. run full Template CI;
6. release the next Template version only if green;
7. re-apply via governed exact-HEAD pilot upgrade.

No direct pilot patching is permitted.
