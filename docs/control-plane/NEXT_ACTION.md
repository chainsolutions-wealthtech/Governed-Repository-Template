# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_D_MERGE_PR53_REUPGRADE_EKYC_RESUME_DISCOVERY
STATE = IN_PROGRESS
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Objective

Merge the client-upgrader distribution correction, redistribute the portable Governance Model integrity test to Ekyc, require the client Governance CI to pass fully, then resume the preserved MCP discovery checkpoint.

## Evidence

- Template main before PR #53: `ca8ce60e31a1d5f07fc1293cac54ca29906b7501`.
- Ekyc current HEAD: `bbe20f4406eb794df4d2452161462f945e2d3fc6`.
- Ekyc CI `36620623398`: stale portable Governance Model test detected by governed-upgrade continuity.
- PR #53 RED: `36620804501`.
- PR #53 GREEN: `36620877757`.

## Required sequence

1. require final PR #53 HEAD CI green;
2. reobserve Template main and PR #53 exact HEAD;
3. merge PR #53 under exact-head guard;
4. require source post-merge CI green;
5. reobserve Ekyc exact HEAD;
6. redistribute via `/governed-upgrade-local-entry`;
7. require Ekyc Governance CI fully green;
8. preserve `Ekyc#1` answers and prior 404 evidence;
9. execute the preserved MCP discovery gate;
10. correct the endpoint at the recovery question to `https://mcp.wealthtechinnovations.com/mcp`;
11. rerun read-only discovery and continue C1-13 chronologically.

## Safety boundary

- No direct Ekyc patch.
- Distribute the portable test, not source-only control-plane state.
- Do not recreate baseline/history.
- Runtime writes remain separately approval-gated.
- P12-S6 and GMC remain blocked behind P12-S5.
