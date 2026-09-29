# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_F_APPROVE_CORRECTED_MCP_DISCOVERY_PLAN
STATE = WAITING_FOR_OWNER_APPROVAL
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Verified transition

- Template main: `b35db53981cac9cad80ae051e460e08d1fdc3d0d`.
- Ekyc HEAD: `a6b0c99cc8d90a1d5cbaf4d6288d52b995e596c6`.
- TLS remediation is effective: MCP Governed Deploy `36625479517` PASS.
- GitHub OIDC → MCP HTTPS read-only evidence `36642167257`: PASS.
- Authorized Ekyc retry `36642689845` no longer failed on TLS; it reached the service and returned `HTTP 404 Not Found`.
- Root cause: stored MCP endpoint was the host root rather than the MCP path.
- Canonical MCP endpoint is `https://mcp.wealthtechinnovations.com/mcp`.
- Endpoint correction was applied through the governed central command, not by direct target patch.
- Ekyc run `36642777140` advanced Ekyc#1 to revision `33`, status `WAITING_FOR_DISCOVERY_APPROVAL`.
- The previous approval was invalidated automatically because the endpoint changed materially.

## Corrected plan awaiting approval

```text
operation = READ_ONLY_MCP_DISCOVERY
repository = Patricked-code/Ekyc
transport = BOTH
endpoint = https://mcp.wealthtechinnovations.com/mcp
SSH profile = mcp.wealthtechinnovations.com:22 / root
scope = FULL_GOVERNED_MAPPING
domain strategy = DISCOVER_EXISTING_THEN_PROPOSE
runtime mutation policy = EXPLICIT_APPROVAL_FOR_SCOPED_WRITE
tools =
  ping
  get_project_context
  list_domains_s1
  list_domains_s2
  get_write_tools_context
mutation authority = false
secret value exposure = false
```

## Safety boundary

- No new MCP intake or MCP programme mutation is needed for this transition.
- Do not infer approval from the prior root-endpoint plan.
- Do not run discovery before explicit approval of this corrected plan.
- Do not apply the first-agent baseline before discovery completes and the remaining setup gates are reached.
- P12-S6 and GMC remain blocked behind P12-S5.
