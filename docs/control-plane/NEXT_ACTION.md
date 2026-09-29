# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_E_A_IMPLEMENT_EXPLICIT_MCP_DISCOVERY_APPROVAL_GATE
STATE = FRAMEWORK_CORRECTION_REQUIRED
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Why this supersedes the TLS wait as the immediate action

Owner feedback established that Ekyc's MCP setup answers were configuration/preparation choices, not authorization to execute network discovery.

The prior TLS failure `36621624763` and intake `Patricked-code/MCP#201` remain preserved evidence, but they are downstream of an earlier missing authority gate.

## Required correction

1. keep all current Ekyc#1 answers;
2. add `MCP_DISCOVERY_PLAN` presentation;
3. require explicit `mcp_discovery_approved=true` before credential provisioning or network discovery;
4. make endpoint correction invalidate prior discovery approval;
5. migrate legacy/pre-approval discovery state back to the approval gate while archiving evidence;
6. validate the Template;
7. only after merge, re-upgrade Ekyc through the governed Template path;
8. resume Ekyc at the explicit discovery approval gate, not at TLS retry.

## Additive architecture rule

```text
ANSWER / OBSERVED FACT
→ PROJECT MODEL
→ RESOURCE REQUIREMENTS
→ GAP CLASSIFICATION
→ PREPARED WORK-ITEMS / DEPENDENCIES / AUTHORITIES
→ EXISTING LOOP_ENGINEERING
```

No parallel governance, task engine, or replacement workflow is authorized.

## Safety boundary

- Do not patch Ekyc directly.
- Do not mutate `Patricked-code/MCP` from this workstream.
- Do not bypass TLS.
- Do not discard the prior TLS evidence.
- Do not advance P12-S6 or GMC while P12-S5 is open.
