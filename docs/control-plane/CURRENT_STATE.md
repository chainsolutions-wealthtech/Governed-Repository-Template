# CONTROL PLANE CURRENT STATE

> Source-only authority for `chainsolutions-wealthtech/Governed-Repository-Template`.
> This file is not project-state content for repositories generated from the template.

## Identity

- Repository: `chainsolutions-wealthtech/Governed-Repository-Template`
- Role: `CENTRAL_GOVERNANCE_CONTROL_PLANE`
- Canonical branch: `main`
- Template baseline before this self-governance migration: `2d51b21f266726624ec7ac16072ccca4623b9b4a`
- Template version entering this migration: `2.6.10`
- Source-state revision: `1`

## Current framework program

- Active macro case: `CREATE_NEW_REPOSITORY`
- Canonical program issue: `#12`
- Current case checkpoint: `STEP_4_SECOND_FRESH_REPOSITORY_E2E`
- CASE 1 pilot `Patricked-code/Gouvern`: baseline/handoff proven
- Pilot baseline commit: `23975e0435e63fb45d7436d1f23ce8ce0a450a5f`
- Pilot local-entry state: `LOCAL_HANDOFF_READY`
- Pilot first governed session: `LOCAL-000002-S1`

## Current control-plane hardening

State: `IN_PROGRESS`

Objective: make the template source obey the same persistent-memory principles that it imposes on generated repositories, without leaking source-project history into clients.

Required boundary:

```text
SOURCE CONTROL PLANE MEMORY
!=
DISTRIBUTED TEMPLATE PROJECT STATE
```

## External dependency boundary

`Patricked-code/MCP` is an independently governed project.

From this framework program:
- READ / OBSERVE is allowed when required for integration evidence;
- missing capabilities become INTAKE items for the MCP program;
- no MCP implementation work is performed here;
- no MCP branch/task/session is created here unless separately authorized by the MCP program.

## Blockers

None for the self-governance migration.

## Unique next action

`COMPLETE_V2_7_0_SELF_GOVERNED_CONTROL_PLANE`
