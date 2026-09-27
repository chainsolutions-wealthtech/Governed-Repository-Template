# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_A_MERGE_PR50_UPGRADE_EKYC_RESUME_DISCOVERY
STATE = IN_PROGRESS
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Objective

Complete the generic recovery correction discovered during the second fresh repository E2E, then resume `Patricked-code/Ekyc` at the exact affected MCP discovery checkpoint without replaying the already accepted baseline/setup answers.

## Live evidence

- Template canonical main before correction: `13d98a2fa35e3dec4aec1fb4ae27f58c177f2297`.
- Fresh target: `Patricked-code/Ekyc`.
- Target local-entry: `Ekyc#1`.
- Target HEAD: `b6be4b96306a765efd6bbd20727f02d5ef17553d`.
- Failed target run: `36294979599`.
- Failure: `HTTP 404: Not Found` during MCP discovery.
- Generic defect: retryable failure did not permit correcting `mcp_endpoint`.
- PR #50 regression RED: `36295172971`.
- PR #50 correction GREEN: `36295231828`.

## Required sequence

1. reobserve Template `main` before merge;
2. require PR #50 head/CI to remain current and all-green;
3. merge PR #50 without force/history rewrite;
4. reobserve merged Template `main`;
5. update `Patricked-code/Ekyc` only through the governed Template/client update path;
6. preserve every accepted `Ekyc#1` answer and the failed discovery evidence;
7. reopen endpoint recovery and use the verified direct MCP route rather than repeating the known-404 root;
8. rerun read-only MCP discovery on the exact upgraded target HEAD;
9. continue C1-13 chronologically only if discovery and subsequent gates pass;
10. keep `P12-S6` blocked until the entire second fresh E2E, including NORMAL_GOVERNED_ENTRY, is proven.

## Safety boundary

- Do not patch `Ekyc` directly to bypass the generic defect.
- Do not restart the fresh repository or recreate its baseline.
- Do not discard the failed discovery evidence.
- Do not infer write authority from `EXPLICIT_APPROVAL_FOR_SCOPED_WRITE`; every scoped runtime write still requires explicit authorization.
- Do not implement MCP-server changes from this workstream.
- GMC remains dependency-bound behind `P12-S6`.
