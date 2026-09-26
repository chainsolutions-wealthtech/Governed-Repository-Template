# CONTROL PLANE CURRENT STATE

> Source-only authority for `chainsolutions-wealthtech/Governed-Repository-Template`.
> This file is not project-state content for repositories generated from the template.

## Identity

- Repository: `chainsolutions-wealthtech/Governed-Repository-Template`
- Role: `CENTRAL_GOVERNANCE_CONTROL_PLANE`
- Canonical branch: `main`
- Template baseline before this self-governance migration: `2d51b21f266726624ec7ac16072ccca4623b9b4a`
- Template version: `2.8.3`
- V2.7.0 release subject HEAD: `d11b72956e68526edf9b17aec472163a4e49a585`
- Source-state revision: `8`

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

## Current blockers

- `Patricked-code/Gouvern` is upgraded to V2.8.3 at `3a1b7689be5aa38b4b6fdb6456526e618f9b0dd5`.
- Governance validation: PASS.
- Bootstrap consistency self-test: PASS.
- Governance CI still fails at `scripts/test_connection_intent.py`.
- Exact failure: `INTENT_SELFTEST_FAILED: unexpected work item`.
- C1-12 normal-entry proof issue exists as `Patricked-code/Gouvern#3`, but its first start attempt was refused by the human actor authorization gate and no governed state advanced.


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

## V2.8.0 memory freshness reconciliation

- Current canonical main HEAD observed before this reconciliation: `2ad88338fc3f02efbbf2c5e0572dd0a1754701fd`.
- CASE 1 step-1 wording reconciled to the adaptive MCP contract: MCP optional; if linked, DIRECT/SSH/BOTH are owner choices.
- Relational runtime seed and machine current-state HEAD reconciled to the observed main HEAD.
- Active workflow checkpoint remains `C1-12 / STEP_4_PROVE_NORMAL_GOVERNED_ENTRY_ON_GOUVERN`.

## C1-12 live chronology

- 18:10 UTC — pilot issue `Patricked-code/Gouvern#3` created for subsequent-agent NORMAL_GOVERNED_ENTRY proof.
- First start attempt refused because the repository actor authorization gate did not recognize current admin/maintain/write permission; no governed state advanced.
- V2.8.1 / PR #25 added exact-HEAD machine local-entry start via `/governed-local-start`.
- Gouvern upgraded to `0aaa276c75f5fe46cacaf9c636ddbad65ca66ee1`; client CI exposed policy synchronization regression.
- V2.8.2 / PR #26 synchronized current control-plane policy into upgraded clients while preserving `GOVERNED_TARGET_CLIENT`.
- Gouvern upgraded to `11563779839f149a762f883b3690ffa7541d77ac`; client CI exposed bootstrap fixture contamination by instantiated project state.
- V2.8.3 / PR #27 made bootstrap self-tests portable by resetting only synthetic fixture project-profile/infrastructure values.
- Gouvern upgraded to `3a1b7689be5aa38b4b6fdb6456526e618f9b0dd5`.
- Current remaining failure: `INTENT_SELFTEST_FAILED: unexpected work item`.
- Active CASE 1 phase remains `C1-12`; no transition to C1-13 is allowed until client CI and live normal-entry proof are green.
