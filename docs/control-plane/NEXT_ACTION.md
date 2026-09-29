# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_C_MERGE_PR52_REUPGRADE_EKYC_RESUME_DISCOVERY
STATE = IN_PROGRESS
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Objective

Merge the generic Governance Model client-portability correction, redistribute it through the official upgrader, require Ekyc client CI to pass completely, then resume the preserved MCP discovery checkpoint.

## Evidence

- Template main before PR #52: `0a4a9961565d53a872d6eb62ad3f4afadbb11d6e`.
- Ekyc current HEAD: `dd5a2664c4422ab14fc7131a77e5c2df0e0356a0`.
- Ekyc CI `36296169271`: client/local-entry tests PASS; source-only Governance Model test FAIL.
- PR #52 RED: `36296258279`.
- PR #52 GREEN: `36296295586`.

## Required sequence

1. require final PR #52 HEAD CI green;
2. reobserve Template main and PR #52 exact HEAD;
3. merge PR #52 with exact-head guard;
4. require source post-merge CI green;
5. reobserve Ekyc exact HEAD;
6. redistribute via `/governed-upgrade-local-entry`;
7. require Ekyc Governance CI fully green;
8. preserve `Ekyc#1` answers and prior 404 evidence;
9. execute the preserved MCP discovery gate;
10. on the expected 404 recovery question, correct the endpoint to the previously proven route `https://mcp.wealthtechinnovations.com/mcp`;
11. rerun read-only discovery and continue C1-13 chronologically.

## Safety boundary

- No direct Ekyc patch.
- Do not distribute source-only control-plane state to clients.
- Do not recreate the baseline or discard failure evidence.
- Runtime writes remain separately approval-gated.
- P12-S6 and GMC execution remain blocked behind P12-S5.
