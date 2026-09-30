# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_H_REFINE_CAPABILITY_FIRST_MAP_THEN_REGENERATE_SNAPSHOT
STATE = FRAMEWORK_SEMANTIC_REFINEMENT
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
BRANCH = governance/refine-mcp-capability-map
```

## Exact resume state

- Template `main`: `fde48fedfcdc1589147c0b3e38507241c18878f1`.
- Refinement branch was created from that exact HEAD and had no changes before this correction.
- Automated live snapshot PR #63 is OPEN and intentionally NOT MERGED.
- PR #63 is technically valid but semantically over-broad: its case maps attach roughly the whole MCP catalogue to each case and its first project-id parser admitted metadata labels such as `path` / `note`.
- Live catalogue evidence remains valid: 135 tools, 2 resources, catalogue digest `8447f9dcc5078fdc9287068c9a791ab5366cc8f10ead5770f6830ed4aca34f1b`.

## Active correction

1. filter project IDs to actual top-level registry entries;
2. replace case → bulk-tool mapping with:
   `CASE → CAPABILITY → CURRENT SURFACE → TOOL CANDIDATE → AUTHORITY → PREPARED OPERATION`;
3. encode observation-first question resolution;
4. explicitly represent capabilities currently absent from MCP;
5. prepare scoped capability requests only when a concrete operation needs an absent capability;
6. validate RED→GREEN;
7. merge the framework refinement;
8. supersede/close stale snapshot PR #63;
9. rerun `/refresh-mcp-capabilities`;
10. inspect and merge the regenerated capability-first snapshot only after Governance CI.

## Ekyc — separate gate

Ekyc remains:

```text
HEAD = 4d552458afab32df12aaafd6c7290fab6246d96b
Ekyc#1 revision = 38
status = WAITING_FOR_DISCOVERY_APPROVAL
phase = MCP_DISCOVERY_APPROVAL
endpoint = https://mcp.wealthtechinnovations.com/mcp
transport = BOTH
SSH profile = broker-observed corrected profile
current discovery = null
```

The previous approval was invalidated because the SSH target changed materially. Do not execute Ekyc discovery again until the corrected plan is explicitly approved.

## Safety boundary

- Do not merge PR #63 as-is.
- Do not patch Ekyc directly.
- Do not mutate Patricked-code/MCP.
- Do not create a new MCP intake merely because a generic capability is absent.
- P12-S6 and GMC remain downstream of P12-S5.
