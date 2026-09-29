# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_E_B_REQUEST_EXPLICIT_EKYC_MCP_DISCOVERY_APPROVAL
STATE = WAITING_FOR_OWNER_APPROVAL
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Verified state

- Template v2.8.7 merge: `8b3a1ac4abf250820558ba873110581f8607a2b3`.
- Template post-merge Governance CI: `36637371154` PASS.
- Ekyc governed upgrade: `a6b0c99cc8d90a1d5cbaf4d6288d52b995e596c6`.
- Ekyc Governance CI: `36637639375` PASS.
- Ekyc#1: `WAITING_FOR_DISCOVERY_APPROVAL / MCP_DISCOVERY_APPROVAL`, revision `29`.
- Existing owner answers are preserved.
- Current MCP discovery evidence is null.
- The prior TLS failure is archived in discovery history and is not the active gate.

## Exact discovery plan awaiting approval

```text
operation = READ_ONLY_MCP_DISCOVERY
repository = Patricked-code/Ekyc
transport = BOTH
endpoint = https://mcp.wealthtechinnovations.com/
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

Only an explicit owner approval may advance this plan to credential preparation/network discovery.

## Safety boundary

- Do not infer approval from prior configuration answers.
- Do not contact MCP before explicit approval.
- Do not patch Ekyc directly.
- Do not mutate Patricked-code/MCP from this workstream.
- Preserve the archived TLS evidence.
- P12-S6 and GMC remain blocked behind P12-S5.
