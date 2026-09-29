# CONTROL PLANE CURRENT STATE

> Source-only authority for `chainsolutions-wealthtech/Governed-Repository-Template`.
> This file is not project-state content for repositories generated from the template.

## Identity

- Repository: `chainsolutions-wealthtech/Governed-Repository-Template`
- Role: `CENTRAL_GOVERNANCE_CONTROL_PLANE`
- Canonical branch: `main`
- Template baseline before this self-governance migration: `2d51b21f266726624ec7ac16072ccca4623b9b4a`
- Template version: `2.8.6`
- V2.7.0 release subject HEAD: `d11b72956e68526edf9b17aec472163a4e49a585`
- Source-state revision: `24`

## Current framework program

- Active macro case: `CREATE_NEW_REPOSITORY`
- Canonical program issue: `#12`
- Current case checkpoint: `STEP_5_SECOND_FRESH_REPOSITORY_E2E`
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

- Framework product V2.8.6 is released; Template Governance CI run `36275324940`: PASS.
- Canonical `main` observed before the Governance Model catalogue enrichment: `76fae0dc132ef7e91e659c4dad44cd3522d2c8c4`.
- STEP 4 subsequent-agent proof is complete: `Patricked-code/Gouvern#4` reached `NORMAL_GOVERNED_ENTRY` / `LOCAL_HANDOFF_READY` on exact pilot HEAD `671774dfc8e8be8eac2b50d5fb8f0928591694b3` with no baseline/session/work duplication.
- The Governance Model Catalogue programme is accepted canonical backlog but dependency-bound behind CASE 1 closure; it is not an executable bypass.

## Unique next action

`C1_13_C_MERGE_PR52_REUPGRADE_EKYC_RESUME_DISCOVERY`

## Latest proof

- Template Governance CI run `36275324940`: PASS.
- V2.8.6 release subject: `02173120acfa3941e84bf69c89dac0e8d74b47ce`.
- Post-release canonical main observed: `76fae0dc132ef7e91e659c4dad44cd3522d2c8c4`.
- Complete portable connection-intent fixture: PASS.
- New canonical knowledge enrichment: `CP-GOVMODEL-001` accepted, execution gate unchanged.

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

## Canonical target architecture

- Authority: `docs/control-plane/CANONICAL_ARCHITECTURE.md`
- Authority ID: `CP-ARCH-001`
- Status: `ACCEPTED_TARGET_ARCHITECTURE`
- Structuring cases: `CREATE_NEW_REPOSITORY`, `ADOPT_EXISTING_REPOSITORY`, `MAP_EXISTING_PROJECT`, `LAB_EVOLUTION`
- Post-case mode: `CONTINUE_GOVERNED_WORK`
- Target architecture is distinct from live current state.
- Current execution remains CASE 1 / C1-12 with unique next action `C1_12_F_DIAGNOSE_UNEXPECTED_WORK_ITEM`.


## Framework product boundary

- Product/framework repository: `chainsolutions-wealthtech/Governed-Repository-Template`.
- Framework evolution, generic automation, schemas, tests, canonical architecture and reusable memory/database model are implemented here first.
- `Patricked-code/Gouvern` is an external CASE 1 validation pilot only.
- Pilot state can reveal generic defects but never becomes the framework source of truth or implementation target.
- Generic defect fixed in Template V2.8.4: connection-intent self-test fixture contamination by instantiated client work-items.
- V2.8.4 release subject HEAD: `608d29318d1b2df199e4ec304c4e2fe7bfb94263`.
- Next step is external CASE 1 pilot validation only; no generic implementation moves to the pilot.


## V2.8.4 candidate — portable connection-intent self-test

- Product repository: `chainsolutions-wealthtech/Governed-Repository-Template`.
- Generic defect diagnosis: DONE.
- Root cause: `scripts/test_connection_intent.py` inherited real instantiated-client work/session state.
- Fix: synthetic self-test fixture resets only test profile/work-items/claims/sessions/canonical-memory state before bootstrap.
- Real client project state is not modified by the test.
- Product fix status: `C1-12-G DONE`, `C1-12-H DONE`.
- Active sub-task: `C1-12-I_VALIDATE_V2_8_4_ON_CASE1_PILOT`.
- Pilot validation repository example: `Patricked-code/Gouvern` — external validation only after Template CI/release.


## V2.8.4 release attestation

- Framework product release: `2.8.4`.
- Release subject HEAD: `608d29318d1b2df199e4ec304c4e2fe7bfb94263`.
- PR #33 Governance CI: PASS.
- Portable connection-intent self-test: PASS in Template CI.
- Product/pilot boundary: ACTIVE.
- Current next action: validate the released Template on an external CASE 1 pilot.


## V2.8.5 candidate — dynamic governed client upgrader

- Product repository: `chainsolutions-wealthtech/Governed-Repository-Template`.
- Pilot validation exposed a framework distribution gap before any pilot mutation.
- Prior upgrader hard-coded V2.8.3 and omitted the V2.8.4 portable connection-intent self-test surface.
- Client CI also attempted unconditional source-only control-plane DB materialization.
- V2.8.5 candidate derives the upgrade version from the Template manifest, synchronizes the required static governance/runtime/test surface, preserves mutable client state, and makes source-only DB materialization skip cleanly on clients.
- Active task: `C1-12-I-A_FIX_DYNAMIC_CLIENT_UPGRADER`.
- External pilot mutation remains blocked until Template CI/release passes.


## V2.8.6 candidate — complete portable intent fixture

- V2.8.5 governed external pilot upgrade succeeded at pilot HEAD `17f852c19ac8c5d26f40d3508338ce9c221697c8`.
- External pilot Governance CI run `36275001208` failed only in `scripts/test_connection_intent.py`.
- Root cause: synthetic intent test still inherited bootstrap-influencing client baseline state outside work/session stores.
- V2.8.6 resets project-profile, infrastructure-intent, local-entry, MCP binding, access-plan and workflow-model inside the temporary test copy in addition to profile/work/claims/sessions/canonical-memory.
- Real pilot/client state remains untouched.
- Subprocess failures now expose captured stdout/stderr.
- Active task: `C1-12-J-B_COMPLETE_PORTABLE_INTENT_FIXTURE`.


## V2.8.6 release attestation

- Framework product release: `2.8.6`.
- Release subject HEAD: `02173120acfa3941e84bf69c89dac0e8d74b47ce`.
- Template Governance CI run `36275324940`: PASS.
- Complete portable connection-intent fixture: PASS.
- Real client/pilot state mutation by self-test: NONE.
- Current next action: governed exact-HEAD re-upgrade of the external CASE 1 pilot.

## Governance Model Catalogue programme accepted

- New source-only authority: `CP-GOVMODEL-001` at `docs/control-plane/GOVERNANCE_MODEL_CATALOGUE.md`.
- Purpose: make the central Governance Model independently enumerable, versioned, comparable and reusable before CREATE/ADOPT/MAP/LAB consume it.
- Decisions: `CPD-025` through `CPD-027`.
- Programme: `GMC-01..GMC-19`, grouped into phases `GMC-A..GMC-G`.
- Relational status: `PENDING_SCHEMA_EXTENSION`; the existing control-plane database/materializer will be extended, not replaced.
- Priority: dependency-bound behind `P12-S6`; current unique action remains `C1_12_J_C_RELEASE_AND_REUPGRADE_CASE1_PILOT`.
- Observed canonical main before this enrichment: `76fae0dc132ef7e91e659c4dad44cd3522d2c8c4`.

## Governance Model Catalogue merge attestation

- PR #39: MERGED.
- Merge subject HEAD: `6fb12122d5a0812f6ceca063b1d7af13511003bc`.
- Governance CI run `36284616415`: PASS.
- `CP-GOVMODEL-001`: ACTIVE canonical source knowledge.
- `GMC-01..GMC-19`: canonical dependency-bound backlog.
- Detailed governance-model registry schema/materialization: still `PENDING_PROJECTION` by design.
- Unique executable action remains `C1_12_J_C_RELEASE_AND_REUPGRADE_CASE1_PILOT`.


## PR #42 post-merge integrity reconciliation

- Canonical main reobserved: `2c70fc82aed4fa8f7eebb7f49b2573e6c57e9e59`.
- PR #42 is merged, but two review threads remain unresolved.
- P1: GMC artifact `consumed_by` metadata diverged from the already reciprocal group artifact-dependency contracts and global dependency edges; 68/85 artifacts were affected.
- P2: CPD-029 enriched the normative Governance Model contract while `CP-GOVMODEL-001` remained at revision R1.
- Additional same-surface continuity drift: relational repository HEAD and source checkpoint/handoff projection were stale.
- Framework correction task inserted: `C1-12-J-C-A`.
- External CASE 1 pilot mutation is blocked until this Template correction passes Governance CI and is merged/attested.
- `C1-12-J-C` remains the parent pilot objective and will resume after this correction.


## PR #43 integrity correction merged and attested

- PR #43 merged to canonical `main`.
- Merge subject HEAD: `113c50aa765ae886cd7a085637b8d5dbb5c2766b`.
- Governance CI run `36289874574`: PASS.
- GMC projection integrity gate: PASS — 19 work packages, 174 atomic tasks, 85 planned knowledge artifacts, 100 artifact dependency edges, Governance Model revision R2.
- Canonical relational materialization: PASS.
- PR #42 P1/P2 review threads: resolved after the fix merged.
- `C1-12-J-C-A`: DONE.
- External pilot mutation gate is reopened only through the original chronological task `C1-12-J-C`.
- Unique next action restored: `C1_12_J_C_RELEASE_AND_REUPGRADE_CASE1_PILOT`.


## V2.8.6 pilot revalidation reconciled

- Source canonical main reobserved before reconciliation: `dc2c1d5244aa11eaa9d4486edb5d3a1cc166ed6f`.
- Pilot `Patricked-code/Gouvern` current main: `671774dfc8e8be8eac2b50d5fb8f0928591694b3`.
- Pilot upgrade commit message: `governance: upgrade repository-local setup to v2.8.6`.
- Pilot manifest confirms Template version `2.8.6`.
- Pilot Governance CI run `36275524530`: SUCCESS on the exact current pilot HEAD.
- All Governance CI steps passed, including connection-intent routing and governed-upgrade HEAD continuity.
- Therefore `C1-12-J-C` and parent `C1-12-J` are DONE.
- The V2.8.6 upgrade must not be replayed.
- `C1-12-K` is now IN_PROGRESS.
- Unique next action: `C1_12_K_RERUN_GOUVERN_ISSUE_3`.

## C1-12-K machine-start transport correction

- A live machine local-start request for `Patricked-code/Gouvern` was accepted by the source Control Plane from historical governed request `#4` under exact pilot HEAD `671774dfc8e8be8eac2b50d5fb8f0928591694b3`.
- No target local-entry issue was created, so pilot state did not advance.
- Generic root cause: the source `governed-control-plane.yml` minted `local-start-token` with `permission-contents: read`, while GitHub repository dispatch requires `Contents: write`.
- Corrective sub-task: `C1-12-K-A`.
- RED proof: Governance CI `36292333079` failed exactly on the new local-start permission regression test.
- GREEN proof: Governance CI `36292388479` passed after the minimal permission correction.
- Pilot mutation remains prohibited until this Template correction is merged.
- After merge, `C1-12-K` remains the unique executable task and must retry the machine local-start on the reobserved exact pilot HEAD.

## C1-12 / STEP 4 completion attestation

- Source main observed before reconciliation: `4e7b6354f301ea1f3cb7261def738d9c1dca64b3`.
- Pilot remained at `Patricked-code/Gouvern@671774dfc8e8be8eac2b50d5fb8f0928591694b3`.
- Governed machine start produced `Patricked-code/Gouvern#4`, request `LOCAL-000004`.
- Entry mode: `NORMAL_GOVERNED_ENTRY`.
- Final local-entry status: `LOCAL_HANDOFF_READY`, revision `6`.
- First-agent baseline remained `3806a2c4f3a40aca28d34a00a77b2ad1be3e80f0`.
- Sole first-agent session remained `LOCAL-000002-S1`.
- `WORK-PROJECT-001` remained `READY`; claims remained empty.
- Pilot Git HEAD did not move during the proof.
- `C1-12-K/L/M/N/O/P`: DONE.
- `P12-S4`: DONE.
- Unique next action: `P12_S5_SECOND_FRESH_REPOSITORY_E2E`.
- STEP 5 must use a second clean repository and must not reuse Gouvern's migration/history as proof.


## C1-13 / STEP 5 live corrective gate

- Second fresh repository: `Patricked-code/Ekyc`.
- Central governed request: `chainsolutions-wealthtech/Governed-Repository-Template#49`.
- Fresh target local-entry: `Patricked-code/Ekyc#1`.
- Target HEAD before any corrective propagation: `b6be4b96306a765efd6bbd20727f02d5ef17553d`.
- Business baseline and technical choices progressed normally through runtime policy.
- MCP discovery run `36294979599` failed with `HTTP 404: Not Found`.
- Diagnosis: after a retryable HTTP 404 the generic local-entry state exposed only `/local-execute` and could not reopen `mcp_endpoint`; retrying would reproduce the same invalid endpoint.
- Generic corrective task: `C1-13-A`.
- Pilot/target status: `FROZEN_GENERIC_FRAMEWORK_DEFECT`; no target-specific patch permitted.
- PR #50 RED CI: `36295172971` — only the new recovery expectation failed.
- PR #50 GREEN CI: `36295231828` — full Governance CI PASS after minimal recovery-state fix.
- Template main reobserved before correction: `13d98a2fa35e3dec4aec1fb4ae27f58c177f2297`.
- PR #50 merged and was distributed to `Ekyc`; the governed upgrade then exposed a second generic client-CI portability defect.
- Parent `P12-S5` remains IN_PROGRESS; `P12-S6` and GMC execution remain blocked.


## C1-13-B client CI portability gate

- PR #50 merged on Template main at `dbe0014784362393c8cfbb02ce7810d483cf2bb7`.
- Post-merge source Governance CI `36295619581`: PASS.
- Governed local-entry upgrade on `Patricked-code/Ekyc`: `2ece8cff98258f7c40cf7b7383ceb5c026db9639`.
- Open local-entry `Ekyc#1` was migrated to the new exact HEAD with business/setup answers preserved.
- Ekyc Governance CI `36295714554`: FAIL only at the local-entry self-test.
- Exact failure: client test attempted to open source-only `.github/workflows/governed-control-plane.yml`.
- Generic corrective task: `C1-13-B`.
- PR #51 RED: `36295815960`.
- PR #51 functional GREEN: `36295850914`.
- Correction: guard source-only control-plane assertions behind the `.template-source` marker; do not distribute the source-only workflow to clients.
- Ekyc remains frozen; no client-specific patch is permitted.
- Unique next action: `C1_13_B_MERGE_PR51_REUPGRADE_EKYC_RESUME_DISCOVERY`.


## C1-13-C Governance Model client portability gate

- PR #51 merged at `0a4a9961565d53a872d6eb62ad3f4afadbb11d6e`; source post-merge CI `36296114629`: PASS.
- Governed Ekyc re-upgrade: `dd5a2664c4422ab14fc7131a77e5c2df0e0356a0`; `Ekyc#1` migrated to revision 25.
- Ekyc CI `36296169271`: all portable/client tests PASS through governed-upgrade continuity, then FAIL only at Governance Model projection integrity.
- Root cause: that test loaded source-only `.governance/control-plane-state/governance-model-*.json` in a client repository.
- Corrective task: `C1-13-C`.
- PR #52 RED `36296258279` → GREEN `36296295586`.
- Correction: source-only Governance Model integrity test exits successfully on clients without `.template-source`.
- Target remains frozen; no target-specific patch.
- Unique next action: `C1_13_C_MERGE_PR52_REUPGRADE_EKYC_RESUME_DISCOVERY`.
