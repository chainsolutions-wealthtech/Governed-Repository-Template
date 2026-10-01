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
- Source-state revision: `26`

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

`C1_13_H_VALIDATE_PERSISTENT_MCP_CAPABILITY_SNAPSHOT`

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


## C1-13-D upgrader distribution gate

- PR #52 merged at `ca8ce60e31a1d5f07fc1293cac54ca29906b7501`; source post-merge CI `36620454972`: PASS.
- Governed Ekyc upgrade: `bbe20f4406eb794df4d2452161462f945e2d3fc6`.
- Ekyc CI `36620623398`: local-entry tests PASS; upgrade-continuity self-test detected that the client still held the stale Governance Model integrity test.
- Root cause: `control_plane_upgrade_local_entry.py` did not include `scripts/test_governance_model_integrity.py` in `static_paths`.
- Corrective task: `C1-13-D`.
- PR #53 RED `36620804501` → GREEN `36620877757`.
- Correction distributes the portable test only; source control-plane state remains excluded.
- Target remains frozen; no target-specific patch.
- Unique next action: `C1_13_D_MERGE_PR53_REUPGRADE_EKYC_RESUME_DISCOVERY`.


## C1-13-E external MCP TLS blocker

- PR #53 merged at `7b8cf2193514efd8f3fe8ce635b0d21abfe53639`; source post-merge CI `36621351173`: PASS.
- Governed Ekyc upgrade produced `87c28f4fd4e36aa3d65cfc384309a054c1640e4c`.
- Ekyc Governance CI `36621490571`: PASS across the complete client suite.
- Preserved MCP discovery retry `36621624763` failed with `SSL: CERTIFICATE_VERIFY_FAILED ... certificate has expired`.
- This is an external MCP dependency, not a Template/client portability defect.
- Transport `BOTH` is also blocked because the GitHub-OIDC SSH certificate broker is served through the same HTTPS host.
- External intake created: `Patricked-code/MCP#201`, intake only.
- P12-S5 remains active but externally blocked; P12-S6/GMC stay blocked.

## Owner-feedback reconciliation — discovery configuration is not execution authority

Owner feedback reclassified the apparent TLS blocker as downstream evidence, not the correct immediate next action.

Ekyc#1 already preserves the business/setup answers through `runtime_mutation_policy=EXPLICIT_APPROVAL_FOR_SCOPED_WRITE`. Those answers describe the intended configuration. They do not authorize an immediate MCP network call.

New generic corrective task: `C1-13-E-A`.

Required additive invariant:

```text
ANSWER / CONFIGURATION
!=
EXECUTION AUTHORITY

CONFIGURE DISCOVERY
→ PRESENT READ-ONLY DISCOVERY PLAN
→ EXPLICIT APPROVAL
→ ONLY THEN CREDENTIAL PROVISIONING / NETWORK DISCOVERY
```

The previously observed MCP TLS failure and `Patricked-code/MCP#201` remain preserved evidence. Ekyc remains frozen until the generic Template correction is merged and distributed.

The adaptive questionnaire is additive to the existing governance and Loop Engineering: answers and fresh observations enrich the project/resource model and prepare existing work-items/dependencies; no parallel governance or task engine is introduced.

## V2.8.7 Ekyc approval-gate attestation

- Template PR #55: MERGED.
- Merge subject: `8b3a1ac4abf250820558ba873110581f8607a2b3`.
- Post-merge Governance CI `36637371154`: PASS.
- Governed Ekyc upgrade: `a6b0c99cc8d90a1d5cbaf4d6288d52b995e596c6`.
- Ekyc Governance CI `36637639375`: PASS.
- Ekyc#1 migrated without answer loss to `WAITING_FOR_DISCOVERY_APPROVAL / MCP_DISCOVERY_APPROVAL`, revision 29.
- Prior TLS evidence is archived; current discovery evidence is null.
- `C1-13-E-A`: DONE.
- Unique next action: obtain explicit owner approval for the concrete read-only Ekyc discovery plan. No MCP call is authorized before that approval.

## Authorized Ekyc discovery confirms external TLS blocker

The owner explicitly approved the concrete read-only MCP discovery plan. The governed command was dispatched under exact HEAD `a6b0c99cc8d90a1d5cbaf4d6288d52b995e596c6`.

Target run `36638780542` reached the discovery step and failed with:

```text
SSL: CERTIFICATE_VERIFY_FAILED
certificate has expired
```

Ekyc#1 is now revision 31 with `mcp_discovery_approved=true`, status `MCP_DISCOVERY_FAILED_RETRYABLE`, phase `MCP_DISCOVERY`. The baseline-write step was skipped.

This means the earlier authority defect is closed and the TLS condition is now a genuine external dependency. MCP intake `Patricked-code/MCP#201` remains open and independently confirms remediation is not complete.

## TLS remediation confirmed; MCP endpoint corrected

Fresh live evidence supersedes the prior external TLS blocker:

- MCP Governed Deploy `36625479517`: PASS.
- GitHub OIDC read-only MCP evidence `36642167257`: PASS.
- Ekyc retry `36642689845` reached the HTTPS service and returned `HTTP 404 Not Found`, proving the previous certificate failure is no longer the blocking condition.

The 404 exposed a configuration fact already present in MCP architecture: the MCP endpoint is `/mcp`, not the host root. The central governed command corrected Ekyc from `https://mcp.wealthtechinnovations.com/` to `https://mcp.wealthtechinnovations.com/mcp`.

Because an endpoint change is material, V2.8.7 correctly invalidated the previous discovery approval. Ekyc#1 is now revision 33 at `WAITING_FOR_DISCOVERY_APPROVAL / MCP_DISCOVERY_APPROVAL`.

`Patricked-code/MCP#201` is retained as historical evidence only; no new intake or MCP mutation was created.

## Reapproved /mcp discovery — direct PASS, signed SSH profile mismatch

The owner explicitly reapproved the corrected read-only plan. Ekyc run `36644247227` proved the direct MCP path end-to-end:

- MCP initialize: PASS;
- protocol: `2025-06-18`;
- server: `wealthtech_ssh_bridge 0.1.0`;
- `ping`: PASS;
- `get_project_context`: PASS;
- `list_domains_s1`: PASS;
- `list_domains_s2`: PASS;
- `get_write_tools_context`: PASS.

The combined BOTH result failed only because the stored SSH profile `mcp.wealthtechinnovations.com:22/root` differs from the authenticated broker-signed S1 target `212.227.212.33:22/root`.

This is a generic recovery gap: the state machine currently exposes blind retry instead of reopening the SSH profile. `C1-13-G` fixes that in the Template first.

Owner feedback also adds `C1-13-H`: the source Control Plane must maintain a persistent, refreshable MCP capability image and derive case/tool/operation planning from it for the existing Loop Engineering. This is complementary source memory, not a second governance engine.

## Persistent MCP capability image — C1-13-H candidate

The signed-SSH recovery is now proven on Ekyc. V2.8.8 was merged and propagated; the refreshed local state reopened `Q_SSH_PROFILE_RECOVERY`, consumed authenticated broker evidence, and returned to a renewed discovery-plan approval gate at revision 38 without applying the baseline.

The active framework work is now `C1-13-H`.

New source-only authority:

- human: `docs/control-plane/MCP_CAPABILITY_MODEL.md`;
- machine: `.governance/control-plane-state/mcp-capability-snapshot.json`;
- refresher: `scripts/control_plane_mcp_capability_snapshot.py`;
- refresh workflow: `.github/workflows/mcp-capability-refresh.yml`;
- authority ID: `CP-MCP-CAP-001`.

The capability snapshot is a persistent last-known image, not a credential or execution grant. It records MCP identity/protocol, catalogue/resource metadata, server logical IDs, capability surfaces, provenance/digests, case/tool planning candidates and required authority classes. Public persistent state intentionally excludes server connection coordinates and secret values.

Refresh is event/need based. The Template has standing authority for these read-only refreshes, but any server/MCP mutation still requires its normal scoped authority. A pre-mutation live refresh is mandatory.

The relational projection remains `PENDING_PROJECTION_GMC_INTEGRATION` by design; no second database or parallel Loop Engineering engine is introduced.

## C1-13-H capability-first MCP memory complete

C1-13-H is DONE.

The Control Plane now keeps a persistent MCP implementation image behind stable capability semantics. It does not use the raw catalogue as the questionnaire.

Canonical planning chain:

```text
PROJECT REALITY / CASE
→ unresolved requirement
→ stable capability
→ current MCP surface
→ candidate tool
→ required authority
→ prepared operation
→ existing Loop Engineering
```

Canonical question resolution:

```text
fresh direct repository observation
→ fresh persisted project memory
→ prior owner decision
→ authorized MCP read-only discovery
→ ask owner only if still unresolved or a genuine decision
```

Evidence:

- #63: CLOSED UNMERGED after semantic QA.
- #65: merged `07b1f073c6ba5c9c5038efcd0f0e61c2271e73cf`; post-merge CI `36652171736` PASS.
- #66: CLOSED UNMERGED after authority/scope QA.
- #67: merged `662072891a66046ca07bb7e356ed4bf2345a12be`; post-merge CI `36652640862` PASS.
- final refresh `36652696942`: PASS.
- #68: canonical snapshot merged `6c293a809df15b85fe40685b3a0f6a3508e1ee4d`; post-merge CI `36652771078` PASS.
- current MCP image: 135 tools, 2 resources, zero unclassified tool surfaces.
- generic filesystem/web/TLS mutations remain explicitly absent rather than invented.
- project-specific MCP tools do not masquerade as generic project capabilities.
- MCP operational-write authority is distinct from scoped server mutation authority.

CASE 1 now returns to Ekyc#1 revision 38 at the explicit approval gate for the materially corrected BOTH discovery plan.

## Owner correction — BOTH is not coupled execution

Owner clarification supersedes the previous immediate C1-13-I approval request.

`BOTH` means DIRECT and SSH are both configured as eligible governed routes. It does not mean every discovery must run both.

The old implementation in `scripts/mcp_repository_discovery.py` executed DIRECT and then SSH whenever `mcp_transport=BOTH`. On Ekyc, this incorrectly converted an authorized DIRECT PASS into a whole-discovery failure because the alternate SSH profile mismatched.

Generic corrective task `C1-13-I-A` is active. The framework is being changed to `DUAL_READY_SMART_ROUTING`, with one selected route per operation and independent alternate-route readiness.

No new Ekyc network call is required to recover the already-authorized DIRECT evidence.

## Adaptive choice-question planning enrichment

A source-only choice-question catalogue has been added as additive planning knowledge.

It preserves the current CASE 1 execution checkpoint and does not bind a new runtime engine.

The catalogue defines 34 one-at-a-time choice questions across identity/topology, governance posture, infrastructure, domain/network, runtime/data, delivery/operations, MCP/access, authority/security and quality/recovery.

Fresh observations resolve factual questions before owner interaction. Dynamic choices are generated from observed repositories/servers/domains/paths/runtimes/databases. AfricaFunds is captured as an ADOPT_EXISTING replay fixture; Ekyc-like fresh creation is captured as a CREATE_NEW fixture.

Runtime binding remains deferred to small future AQI slices and the existing GMC/Loop Engineering chronology.

## Persistent reusable knowledge model

The Control Plane now has a source-only knowledge model `CP-KNOWLEDGE-001`.

Purpose: agents should reuse what the Control Plane already knows instead of repeatedly rediscovering the same stable facts.

The model separates stable governance/provider/project knowledge from volatile operational evidence and requires provenance plus freshness semantics before reuse.

This is planning/memory enrichment only. It does not change the current CASE 1 executable task, grant execution authority or create another runtime engine.

## Governed execution engine

`CP-EXECUTION-001` is implemented source-only as the execution adapter for the existing Loop Engineering model.

Coverage:
- 15 server/production intents;
- 10 identity/credential/secret lifecycle intents;
- 14 GitHub administration/delivery intents;
- 39 total registered intents.

The engine validates authority, exact target HEAD, MCP capability/tool/project scope, live MCP tool argument contracts and secret-free package rules before side effects.

GitHub operations are implemented with allowlisted REST builders and post-operation verification. Server operations run through MCP bindings only. Missing generic MCP write surfaces remain fail-closed blockers.

No Ekyc mutation and no Patricked-code/MCP mutation is included in this implementation.

## Project execution DAG and Loop binding

The governed execution layer now includes a source-only project-level compiler.

A complete project specification can expand into an ordered DAG spanning GitHub environment/secrets, server directory/port, domain/vhost/TLS, database/credentials, runtime/service, repository binding, deployment, observability, backup and final production attestation.

The Loop adapter evaluates package readiness against the current execution registry and MCP capability snapshot and releases only one eligible node at a time.

Missing MCP production capabilities remain blockers. The current CASE 1 action remains Ekyc domain-binding resolution.

## Bounded server identity/secret mechanism mapper

`KBI-04K` is implemented source-only.

The Control Plane can now build a safe S1/S2 credential-mechanism matrix from the canonical identity model and MCP capability snapshot, and can execute bounded read-only probes when a current MCP token is supplied.

The live result stores only safe status/shape/digest metadata; raw responses and secret values are discarded. Live S1/S2 observation is still pending and the current CASE 1 action remains unchanged.

## Persistent S1/S2 identity-secret facts

`KBI-04N` is implemented source-only.

Validated KBI-04K server identity/secret observations can now be stored as revisioned canonical facts with provenance and freshness. Mechanism classifications are recomputed from canonical source authorities before persistence, and probe results are reduced to safe metadata/digests only.

The relational Control Plane schema is extended to 1.4.0 with `server_identity_secret_facts`.

The initial state remains `NOT_COLLECTED`; no live S1/S2 secret metadata has been persisted yet. CASE 1 remains at Ekyc domain-binding resolution.

## Governed S1/S2 identity-secret facts refresh

`KBI-04O` is implemented source-only.

The Control Plane now has an event/need-based workflow that can run the bounded KBI-04K read-only S1/S2 observation, validate/persist the KBI-04N safe facts under exact revision, materialize the existing relational projection, and open a governed PR when safe metadata changes.

The workflow persists no secret values, raw MCP responses or server connection coordinates and grants no production authority.

Live refresh remains pending until this workflow is merged and invoked from canonical `main`. CASE 1 remains at Ekyc domain-binding resolution.

## KBI-04O live-refresh correction

First canonical-main refresh run `36844233362` proved live read-only MCP collection and safe-fact persistence, then stopped before Git persistence because the persistence unit test incorrectly depended on source revision 0.

Corrective task `KBI-04O-A` is active. No live observation entered canonical state and no server mutation occurred.

## KBI-04O live refresh proven

The first production-like read-only knowledge refresh is now complete and canonical.

Evidence:

- KBI-04O workflow merge #84: `7edffed0594cb0a2f5e54605f21c6348fd60f3fd`;
- first live run `36844233362`: collection/persistence PASS, validation stopped on a unit-fixture defect before Git persistence;
- KBI-04O-A fix PR #85 merge: `30b99b1f9cb0c824c90218078d9c2c2d18a4c6e5`;
- second live run `36844701817`: PASS;
- generated safe-facts PR #86 at `0504b454a778377421d578e9022c2c103f4abe61`;
- PR #86 Governance CI `36844736669`: PASS;
- PR #86 merge: `b665fba88d276b9efb636a894e53d890344b2faa`;
- post-merge Governance CI `36844997332`: PASS;
- canonical facts state: revision 1, 17 facts, `PARTIAL_BOUNDED_METADATA`.

Persisted evidence contains no secret values, raw MCP payloads, server connection coordinates or execution authority.

Observed mechanism result remains explicit: ephemeral SSH OIDC minting is implemented; several generic production capabilities remain modelled gaps, including TLS change, secret provisioning, database change, DNS change and runtime mutation. No automatic MCP intake was created.

CASE 1 is unchanged: Ekyc remains at `C1-13-I-B / Q_DOMAIN_BINDING`.

## C1-13-I-B-A — fresh-project server-before-domain correction

Live Ekyc state and the source implementation were reconciled against the owner's required question order.

Finding: Ekyc is a `NEW_EMPTY_PROJECT` with `UNKNOWN_TO_DISCOVER` infrastructure, successful read-only discovery on both S1/S2 domain inventory tools, no existing project/domain binding, but the legacy runtime currently asks `Q_DOMAIN_BINDING` directly.

Generic correction `C1-13-I-B-A` is active in the Template. The v2.8.25 candidate adds production-server selection before domain planning, reuses selected-server discovery evidence and migrates the open local-entry state through the governed upgrader.

Ekyc itself remains unchanged until Template CI/merge.

## P12-S5 second fresh E2E complete

The fresh Ekyc validation path has now reached its required subsequent normal-entry handoff.

Evidence:

- Ekyc baseline commit: `3e889a2bdac78312ebcc7e31d1388ead65c9fceb`;
- repository state: `PROJECT_BASELINE_READY`;
- first-agent session: `LOCAL-000001-S1`;
- `WORK-PROJECT-001`: `READY`, not executed;
- Ekyc#2 request `LOCAL-000002`: `NORMAL_GOVERNED_ENTRY`;
- final state: `LOCAL_HANDOFF_READY`, revision 6;
- Ekyc HEAD unchanged by the normal-entry proof;
- no baseline/session/work duplication;
- no target-specific repair;
- no S1/domain/DNS/Plesk/TLS mutation.

`P12-S5` is DONE. The unique next action is `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE`. GMC-A remains blocked until CASE 1 closure passes.

## Canonical namespace/work collision guard

`CP-NAMESPACE-001` is implemented source-only.

It registers the canonical ID namespaces, derives definitions from their existing authorities, and fails CI on duplicate or ambiguous canonical definitions.

The historical duplicate `CPD-041` has been reconciled additively: the domain-planning decision is now `CPD-047`; `CPD-048` records the registry decision.

This strengthens multi-agent safety but does not replace claims, collision domains, exact-HEAD guards or single-writer execution.

## GACR agent continuity relay

`CP-AGENT-RELAY-001` is implemented as a generic reusable runtime candidate in Template v2.8.29.

It extends the existing session/claim model with heartbeat, leases, stall detection, standby offers and exact-HEAD guarded takeover.

The implementation does not change the unique CASE 1 programme action and grants no execution authority by itself.
