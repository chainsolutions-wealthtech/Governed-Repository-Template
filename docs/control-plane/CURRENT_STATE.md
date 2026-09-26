# CONTROL PLANE CURRENT STATE

> Source-only authority for `chainsolutions-wealthtech/Governed-Repository-Template`.
> This file is not project-state content for repositories generated from the template.

## Identity

- Repository: `chainsolutions-wealthtech/Governed-Repository-Template`
- Role: `CENTRAL_GOVERNANCE_CONTROL_PLANE`
- Canonical branch: `main`
- Template baseline before this self-governance migration: `2d51b21f266726624ec7ac16072ccca4623b9b4a`
- Template version: `2.8.0`
- V2.7.0 release subject HEAD: `d11b72956e68526edf9b17aec472163a4e49a585`
- Source-state revision: `6`

## Current framework program

- Active macro case: `CREATE_NEW_REPOSITORY`
- Canonical program issue: `#12`
- Current case checkpoint: `STEP_4_PROVE_NORMAL_GOVERNED_ENTRY`
- CASE 1 pilot `Patricked-code/Gouvern`: baseline/handoff proven
- Pilot baseline commit: `23975e0435e63fb45d7436d1f23ce8ce0a450a5f`
- Pilot local-entry state: `LOCAL_HANDOFF_READY`
- Pilot first governed session: `LOCAL-000002-S1`

## Current control-plane hardening

State: `SELF_GOVERNED`

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

`STEP_4_PROVE_NORMAL_GOVERNED_ENTRY_ON_GOUVERN`

## Latest proof

- Governance CI run `36258871067`: `PASS`.
- Source-state validation: `PASS`.
- Instantiated-client bootstrap test: `PASS`.
- Source-only directories absent after client initialization: `PASS`.

## V2.7.0 release attestation

- Release subject HEAD: `d11b72956e68526edf9b17aec472163a4e49a585`.
- Self-governance migration: COMPLETE.
- Client source-memory non-leak proof: PASS.
- Durable source checkpoint/handoff: ACTIVE.
- Canonical framework program #12 may resume.

## Reconciliation note

A post-V2.7.0 continuity review detected that the source checkpoint had compressed canonical program STEP 4 and STEP 5. The durable source state is corrected to preserve the original chronological gates: STEP 4 proves subsequent normal entry on `Gouvern`; STEP 5 is the second fresh repository E2E.
## MCP choice clarification

`BOTH` was the selected transport for the historical `Gouvern` pilot only. The generic `CREATE_NEW_REPOSITORY` route does not mandate MCP linking or `BOTH`. The owner may decline MCP linkage entirely; if linkage is enabled, the transport is selected from `DIRECT_MCP_TOKEN`, `SSH`, or `BOTH`, and subsequent gates adapt to that choice.

## Canonical relational memory

A source-only relational projection is being added in V2.8.0 so all structuring cases can share one reusable data model for cases, phases, questions, activities, decisions, runs, evidence, checkpoints, handoffs, owner feedback, intakes and artifacts.

The current workflow checkpoint does **not** change: CASE 1 remains at `C1-12 / STEP_4_PROVE_NORMAL_GOVERNED_ENTRY_ON_GOUVERN`.

The future admin web application is intentionally deferred until all structuring cases and parcours have been tested and their relational catalogues validated.


## V2.8.0 release attestation

- Release subject HEAD: `4c8d16b5fc71df7923942c5658c21269a0051da3`.
- Canonical relational memory schema: ACTIVE.
- Ephemeral SQLite materialization in Governance CI: PASS.
- Structuring cases registered: 4.
- CASE 1 replay data: ACTIVE.
- Future admin frontend: DEFERRED until all case/parcours validation is complete.
