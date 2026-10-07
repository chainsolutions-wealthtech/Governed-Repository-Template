# CONTROL PLANE CURRENT STATE

> Source-only authority for `chainsolutions-wealthtech/Governed-Repository-Template`.
> This file is not project-state content for repositories generated from the template.

## Identity

- Repository: `chainsolutions-wealthtech/Governed-Repository-Template`
- Role: `CENTRAL_GOVERNANCE_CONTROL_PLANE`
- Canonical branch: `main`
- Template baseline before this self-governance migration: `2d51b21f266726624ec7ac16072ccca4623b9b4a`
- Template version: `2.8.27`
- V2.7.0 release subject HEAD: `d11b72956e68526edf9b17aec472163a4e49a585`
- Source-state revision: `48`

## Current programme

- Active programme: `GOVERNANCE_MODEL_CATALOGUE`.
- Active work package: `GMC-A / GMC-G01`.
- Previous macro case: `CREATE_NEW_REPOSITORY` — `DONE`.
- CASE 1 closure decision: `CPD-073`.
- CASE 1 checkpoint: `CREATE_NEW_REPOSITORY_CASE_COMPLETE`.
- `P12-S1..P12-S6`: `DONE`.
- `GMC-01`: `IN_PROGRESS`.
- Detailed work package: `GMC-G01`.
- First atomic task available to the next operation: `GMC-G01-T01`.
- GMC implementation authority remains false; the released mode is planning/knowledge extraction only.

## Current control-plane hardening

State: `SELF_GOVERNED`.

Required boundary remains:

```text
SOURCE CONTROL PLANE MEMORY
!=
DISTRIBUTED TEMPLATE PROJECT STATE
```

## External dependency boundary

`Patricked-code/MCP` remains independently governed.

From this programme:
- READ / OBSERVE is allowed when required for evidence;
- external MCP needs remain intake/history;
- no MCP implementation is performed here without separate MCP-program authorization.

Preserved CASE 1 external references include:
- `Patricked-code/MCP#192`;
- `Patricked-code/MCP#201` (historical remediated external TLS dependency).

## Current blockers

None for CASE 1 closure.

GMC-G01 must still fail closed on contradictory/missing authority or provenance according to its blueprint.

## Unique next action

`GMC_01_SEPARATE_GOVERNANCE_MODEL_FROM_APPLICATION_STRATEGIES`

Execution authority:
- planning/knowledge extraction: released;
- Governance Model implementation mutation: not yet authorized by this closure;
- CAP/SaaS programmes: still dependency-bound.

## Latest proof

- CASE 1 second fresh E2E: PASS.
- Gouvern subsequent normal entry: PASS.
- Ekyc fresh baseline: `3e889a2bdac78312ebcc7e31d1388ead65c9fceb`.
- Ekyc subsequent `NORMAL_GOVERNED_ENTRY`: `LOCAL_HANDOFF_READY`.
- historical parent `C1-13-I-B` reconciled through children `A..G`.
- no executable CASE 1 task remains orphaned.
- relational CASE 1 run: `DONE`, active phase count target: zero.
- next programme released: `GMC-A / GMC-G01`.

## Historical record below

The sections below preserve earlier candidate/release chronology. Any historical “current/next” wording in those sections is superseded by the authoritative current snapshot above.

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

## GACR post-merge attestation

- Process: `GACR — Governed Agent Continuity Relay`.
- Authority: `CP-AGENT-RELAY-001`.
- Template version: `2.8.29`.
- PR #98: MERGED.
- Merge commit: `0d0c595be7f6833bb36778a0cdac46c82abbd2ab`.
- Post-merge Governance CI `36915276875`: PASS.
- GACR regression test: PASS.
- Existing CASE 1 priority remains unchanged: `P12-S6`.

## GACR v2.8.30 source-boundary attestation

- Authority: `CP-AGENT-RELAY-001`.
- Boundary decision: `CPD-050`.
- Template version: `2.8.30`.
- PR #100: MERGED.
- Merge commit: `d894d29eca6fcc2a1784c459e9e3ddac672b3515`.
- Post-merge Governance CI `36916456136`: PASS.
- Source Control Plane GACR runtime memory is isolated from distributed client GACR state.
- Programme priority remains unchanged: `P12-S6`.

## GACR R2 — Beacon / Correlator / Dispatcher

Revision authority `CP-AGENT-RELAY-001-R2` is implemented on the current branch and awaiting full CI.

It adds safe GitHub connection telemetry, fail-closed session correlation, target-specific standby dispatch, aggregated agent context and an optional external wake bridge contract.

No provider conversation identifier is inferred when absent. No raw GitHub event payload, token, cookie or secret is persisted.

The current programme priority remains unchanged: `P12-S6`.

## GACR R2 post-merge attestation

- Revision authority: `CP-AGENT-RELAY-001-R2`.
- Decision: `CPD-051`.
- Template version: `2.8.31`.
- PR #102: MERGED.
- Merge commit: `abefcfccbf822fa2fcf590e592ad51c767e32937`.
- Post-merge Governance CI `36921331490`: PASS.
- Beacon / Correlator / Dispatcher / Agent Context regression test: PASS.
- Optional external bridge wake contract is installed but remains provider/client dependent.
- Programme priority remains `P12-S6`.

## GACR R3 — Interruption Forensics

Cross-cutting status: `CI_PROVEN`.

- Parent continuity authority: `CP-AGENT-RELAY-001`.
- Previous proven revision: `CP-AGENT-RELAY-001-R2`.
- Candidate revision: `CP-AGENT-RELAY-001-R3`.
- Baseline main: `0d4ca9ff007b88f8fee040ff845ea9a0387d1815`.
- R3 implementation merge: `ada6866efdfe9d2aed2e77171c01ca774a76a885` (PR #104).
- Governance CI `36927683547`: PASS.
- PR #104 post-merge workflow registration run `36927681943`: FAILURE with no jobs.
- Corrective PR #105 merged at `05f49a634e1da46f3da5a016e32499236223ff1d`.
- Corrective candidate CI `36927942003`: PASS.
- Corrective post-merge Governance CI `36928024260`: PASS.
- No new workflow-registration failure is present on corrected main.
- External failure cause is never inferred from missing heartbeat.
- Every generated resume point still requires exact-HEAD reobservation and normal claim/authority gates.
- Programme-level unique next action remains `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE` and is intentionally not executed by this cross-cutting work.

### GACR owner return gate

GACR cross-cutting finalization does not execute the global programme. The canonical global next action remains `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE`, but execution is held until explicit owner OK.

## GACR R4 — Automatic Continuity Attachment

Cross-cutting status: `LIVE_AUTO_ATTACH_PROVEN / CI_PROVEN`.

- Parent authority: `CP-AGENT-RELAY-001`.
- Previous proven revision: `CP-AGENT-RELAY-001-R3`.
- Candidate revision: `CP-AGENT-RELAY-001-R4`.
- Decision: `CPD-053`.
- Baseline main: `75996ee63ae283fd0d6d94549c9746f1bd2ac2bc`.
- Candidate branch: `governance/gacr-r4-auto-attach`.
- A fresh active Conversation Chronicle may act as a provider-independent attachment anchor.
- Missing provider conversation metadata does not block attachment.
- Late explicit provider metadata must enrich the existing connection-bound session without duplication.
- Normal source-main activity invokes auto-attachment; repository automation state-persistence pushes are loop-guarded.
- Programme-level `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE` remains unchanged and is not executed by this cross-cutting work.

### GACR R4 live proof

- PR #109 merged at `4c7db9f0e2e782de147ef316c41086ed0863b49e`.
- Candidate Governance CI `36939255201`: PASS.
- Post-merge Governance CI `36939325620`: PASS.
- GACR push run `36939325451`: PASS.
- Current Conversation Chronicle auto-attached as `session-68c97d4bb1ef71c86444de12`.
- AUTO_ATTACH Beacon `GACR-B-6e9a2275ea04`.
- Correlator `GACR-C-caffb7cb6efd`: `EXACT`.
- Persisted runtime main after auto-attach: `7467bbbca0f554df9d43831588ca03a0d1862c9f`.
- Provider conversation reference remains optional/unavailable; attachment succeeded without invention.
- No recursive auto-attach was observed from repository-automation state persistence.

## GACR R5 — Client Liveness and Trace Emitter

Cross-cutting status: `GENERIC_CORE_COMPLETE / R5_CORRECTION_LIVE_PROVEN / CI_PROVEN`.

- Parent authority: `CP-AGENT-RELAY-001`.
- Previous proven revision: `CP-AGENT-RELAY-001-R4`.
- Candidate revision: `CP-AGENT-RELAY-001-R5`.
- Decision: `CPD-054`.
- Baseline main: `6d6ba0e23d052d563e014e290ba4b32fc88b87db`.
- Candidate branch: `governance/gacr-r5-client-liveness-trace`.
- Generic client emitter transports heartbeat/action/interruption metadata through existing repository-dispatch receivers.
- Client provenance is `CLIENT_EMITTER`, distinct from GitHub Actions transport.
- Wake polling cannot accept takeover.
- Continuous browser/client liveness is not claimed unless the provider host actually invokes or runs the emitter.
- Global programme action `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE` remains unchanged and unexecuted.

### GACR R5 post-merge proof and host boundary

- PR #111 candidate commit: `f63b50cf70bc12b6ef9f37a4cb4a3a61e22fe245`.
- Candidate Governance CI `36941120405`: PASS.
- PR #111 merged at `9b371b45711a9274a0976fe5015d8b19b0315e6c`.
- Post-merge Governance CI `36941216248`: PASS.
- Post-merge GACR run `36941216312`: PASS.
- R4 auto-attachment remained stable: one canonical session `session-68c97d4bb1ef71c86444de12`, no duplicate.
- Third AUTO_ATTACH Beacon: `GACR-B-ff8bedbc4bf2`.
- Third exact correlation: `GACR-C-976bbba3924d / EXACT`.
- Runtime persistence advanced main to `34ceb14a140202ad7b57c9db2700241d50e7460c`.
- R5 client-emitter transport/action/interrupt/wake-poll contracts are CI-proven.
- No persistent client process or direct `repository_dispatch` surface is exposed by the current ChatGPT host in this conversation, so autonomous browser heartbeat is not claimed live here.
- This remaining provider-host instrumentation boundary is external to the generic repository GACR core.
- Global programme action `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE` remains unchanged and unexecuted.

### GACR R5 internal-transport regression correction

- Post-attestation runtime main `0e64a3d2c0f1c99d1aa76f1f25a68d70d425beb2` exposed an invalid second GACR session.
- Canonical conversation session: `session-68c97d4bb1ef71c86444de12`.
- Invalid transport session: `session-cb22a4ed0d9e29eba5383f5d`.
- Defect trigger: Chronicle exceeded the configured freshness window; the internal `Governed Agent Continuity Relay` workflow fell back to GitHub Actions identity and was misclassified as an agent.
- Corrective branch: `governance/gacr-r5-internal-transport-fix`.
- Decision: `CPD-055`.
- Correction: internal GACR workflow may never create a session; no observable external anchor yields a no-op skip; terminal sessions are excluded from live correlation candidates.
- Invalid transport session is preserved but will be `CLOSED / SUPERSEDED`, never deleted.
- R5 cannot return to final-complete status until candidate CI, merge, post-merge GACR no-duplication proof and final attestation pass.
- `P12-S6` remains unchanged and unexecuted.

### GACR R5-A corrective live proof

- Corrective decision: `CPD-055`.
- Corrective PR #113 candidate commit: `1758001e052b923dc50b1e467cc28d5eb528b728`.
- Candidate Governance CI `36942282684`: PASS.
- PR #113 merge: `bfb7b6fb81244f18f1b2c8c1ea82526af0dc2d62`.
- Post-merge Governance CI `36942347934`: PASS.
- Post-merge GACR run `36942347872`: PASS.
- Derived-state persistence main: `173297fee3c6ac55a03ca3787558b063cb85b668`.
- Session records: 2 historical records, exactly 1 active conversation session.
- Canonical active session: `session-68c97d4bb1ef71c86444de12`.
- Misclassified internal-transport session `session-cb22a4ed0d9e29eba5383f5d`: `CLOSED / SUPERSEDED`.
- Beacon revision/count remained `4 / 4`: the corrective merge created no new internal auto-attach Beacon.
- Correlator revision advanced to `5`; terminal session is excluded from live candidates.
- The historical invalid Beacon/correlation is preserved. Its current projection is `PROBABLE`, selected session `null`, candidate only the canonical live session.
- This closes the observed internal-transport duplication regression without extending Chronicle freshness or inventing liveness.
- Generic GACR R1-R5 is complete as repository/runtime/client protocol.
- Provider-host persistent-emitter activation remains a separate external integration boundary and is not falsely reported as live.
- `P12-S6` remains unchanged and unexecuted pending explicit owner OK.

## GACR R6 — provider-host issue bridge candidate

Cross-cutting status: `IMPLEMENTED_PENDING_CI_AND_POST_MERGE_LIVE_PROOF`.

- Authority: `CP-AGENT-RELAY-001-R6`.
- Decision: `CPD-056`.
- Baseline main: `6be9df3f614d178dde6811a66a18c933bf5e6198`.
- Source ingress issue: `#115`.
- Transport: GitHub `issue_comment` with exact `/gacr-host ` prefix.
- Adapter: `scripts/gacr_host_issue_ingress.py`.
- Safety: allowlisted fields/actors/issue only; no transcripts or secrets; comment-ID idempotency; no execution authority.
- Existing GACR R1-R5 semantics remain authoritative.
- Client distribution is included through the governed upgrader.
- Acceptance requires Governance CI PASS, merge, then a real event emitted from the current ChatGPT conversation proving lease renewal + ACTION_TRACE + EXACT correlation + forensics without session duplication.
- Global programme action `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE` remains unchanged and is not executed by this integration slice.

### GACR R6-A — issue-comment rerun reconciliation

A live-review of the first R6 event identified a rerun semantics gap before final attestation.

- Original issue-comment workflow executions are anchored to the event SHA.
- After a successful R6 event, GACR state persistence advances `main`.
- A GitHub rerun of the original attempt would otherwise reconstruct from the older event SHA and only fail later on the exact-HEAD push guard.
- R6-A therefore fetches and checks out the latest default-branch HEAD for `issue_comment` events **before** capturing the base HEAD and evaluating comment-ID idempotency.
- The same comment replay can then resolve as `GACR_HOST_EVENT_ALREADY_PROCESSED` with no state diff and no push.
- Candidate version: `2.8.38`.
- Final acceptance requires candidate CI, merge, a fresh live host event, then rerun of that exact event with successful no-op proof.

### GACR R6-B — portable host inbox boundary

Status: `IMPLEMENTED / CI_PENDING`.

A pre-attestation portability review found that source issue `#115` is runtime-local and must not be distributed to clients.

Correction:
- the generic workflow no longer hard-codes issue `#115`;
- source config retains its exact local issue number;
- governed client upgrades force `host_issue_bridge.issue_number = null`;
- client ingress then uses exact canonical-title validation until a local issue number is bound;
- source issue identity is explicitly non-distributed;
- unit/workflow regression tests cover both source-number and client-title modes.

Candidate Template version: `2.8.39`. The previously proven source live event remains valid; R6-B acceptance requires CI and merge, followed by a fresh source heartbeat proving the exact-number source path still works.

### GACR R6-C — explicit host provider enrichment

Status: `IMPLEMENTED / CI_PENDING / LIVE_PROOF_PENDING`.

Live R6/R6-B evidence confirmed that the canonical session was still labelled `provider = other` because it predated provider-host integration, even though host events explicitly declared `provider = chatgpt`.

R6-C corrects only this attribution gap:
- explicit `chatgpt` may enrich the existing connection-bound generic session without requiring a provider conversation ID;
- session identity is preserved;
- provider conversation reference remains `UNAVAILABLE` unless genuinely supplied;
- conflicting specific providers fail closed;
- host adapter reuses auto-attach/register semantics.

Candidate Template version: `2.8.40`. Acceptance requires CI, merge, then a real ChatGPT-host event proving the canonical session changes from `other` to `chatgpt` with no new session.

## GACR R6 final provider-host integration attestation

Status: `LIVE_PROVEN / CI_PROVEN / INTEGRATED`.

Authority: `CP-AGENT-RELAY-001-R6`. Decision: `CPD-056`. Template version: `2.8.40`.

Validated live chain from the current ChatGPT conversation:

```text
ChatGPT host
→ issue #115 /gacr-host event
→ issue_comment workflow
→ host ingress validator
→ existing canonical GACR session
→ heartbeat / ACTION_TRACE
→ EXACT correlation
→ Interruption Forensics
→ exact-HEAD guarded state persistence
```

Evidence:
- PR #116 / Governance CI `36947562102`: PASS.
- START comment `5943461065` → state commit `69ccfc90c14f2fa02a264c765e31c49c64951635`.
- START Beacon `GACR-B-ddc264dcf74e`; correlation `GACR-C-ea0f04b97de7 / EXACT`.
- PR #117 / Governance CI `36947919754`: PASS.
- COMPLETED comment `5943497457` → state commit `3d258e3c9fdfacd1232fb0a19448594ab452b47f`.
- COMPLETED Beacon `GACR-B-e3e2cf52542f`; forensics shows no in-flight action and outcome PASS.
- Exact rerun of run `36947989601`: `GACR_HOST_EVENT_ALREADY_PROCESSED` + `GACR_NO_STATE_CHANGE`; main unchanged; exactly one Beacon for that comment.
- PR #118 / Governance CI `36948433046`: PASS; source issue number is no longer distributed to clients.
- Portability heartbeat `5943559595` → state commit `371509ac60d1a63c0be7cee8ec8620346210d824`; EXACT correlation preserved.
- PR #119 / Governance CI `36948711458`: PASS.
- Provider enrichment heartbeat `5943592733` → state commit `46a4a3068f0eb28ec3dc1d141cbcf349542a3348`.
- Canonical session remains `session-68c97d4bb1ef71c86444de12`, now `provider = chatgpt`.
- Provider conversation reference remains `null / UNAVAILABLE`; no identifier was invented.
- Total historical sessions remain 2 with exactly 1 active session.
- Correlation remains `EXACT`; no active claim/takeover/dispatch was fabricated.

Automation boundary:
- event-driven provider-host integration is live-proven;
- continuous background heartbeat while no host turn/process exists is **not** claimed because this ChatGPT host exposes no persistent daemon execution surface;
- when a governed host action occurs, AGENTS/R6 require emission through the configured bridge without a human reminder.

Global programme state is unchanged: `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE` remains parked pending explicit owner OK.

## GACR origin realignment registered

- GACR R1-R6 remain preserved as the current implemented baseline.
- Owner has accepted a non-destructive Presence-First realignment plan for the next GACR evolution.
- Human authority: `docs/control-plane/GACR_ORIGIN_REALIGNMENT.md`.
- Machine projection: `.governance/control-plane-state/gacr-origin-realignment.json`.
- Status: `ACCEPTED_PLAN / NOT_YET_EXECUTED`.
- Realignment completion requires a live fresh-agent → automatic observable presence → liveness/progress evidence → stall → second-agent exact-HEAD takeover → continuation proof.
- This registration does not change the current unique executable task `P12-S6_CLOSE_CREATE_NEW_REPOSITORY_CASE`.


## Autonomous GACR programme

- GACR programme authority: `docs/control-plane/GACR_PROGRAM.md`.
- Original-intent authority: `docs/control-plane/GACR_ORIGINAL_INTENT.md`.
- GACR and the global Control Plane programme are distinct workstreams.
- No global task, including `P12-S6`, is a functional dependency of GACR.
- GACR own next action: `GACR-OR-01_REOBSERVE_AND_ATTEST_R6_BASELINE`.
- Original two-limit stop point and BEACON/WATCH/CORRELATOR/DISPATCHER target are now durable canonical memory.
- Global programme state remains unchanged by this GACR registration.


## Owner-authorized IDN identity/session lane — 2026-10-07

Status: `CLOSED / LIVE RELEASE PROVEN`.

The separately authorized control-plane infrastructure lane completed without executing `P12-S6`. The global programme checkpoint remains unchanged and is again the active continuation boundary.

Live-proven invariants:
- distinct GSCC arrival identity per controlled arrival;
- provider-private conversation/session identity remains supplied-only and was not fabricated;
- same-arrival continuation remains deterministic;
- one isolated GSE SessionTwin per GSCC identity;
- Q9 requires correlated ACK before fresh challenge response;
- Q10 precedes durable Q2/GACR binding;
- canonical GACR remains the sole durable continuity authority;
- Q2/Q6/Q7/Q11/Q12 completed on the same connection;
- F1 validated the actual requested function `github_get_repository_state`;
- release to `00_START_HERE.md` is accepted only after the F1 receipt matches the same runtime, connection, GACR session, Access Grant and exact HEAD.

Closure implementation:
- initial implementation PR `#229`;
- live Q10 dispatch correction PR `#239`;
- F1 canonical surface correction PR `#241`;
- explicit F1→normal-governance release PR `#243`, merge `4a71b8c0aa0d2b08462e62d884241fd9b3dd910e`.

Final acceptance:
- issue `#244`;
- runtime `GSCC-RUNTIME-ded6c37f3dc7c3dd634f838e`;
- connection `GSCC-CONN-6d1caad58d77dbd3b164344efc04f6aa`;
- canonical GACR session `session-5bba386248ac4d9c0e05f1a8`;
- F1 workflow `37550409710 = SUCCESS`;
- exposure receipt `GSCC-EXPOSURE-083cf0005955022e1c19d5b8d79264a170e9d9cc7bc898a251339e9b3b92b76f`;
- release workflow `37550477009 = SUCCESS`;
- release comment `6027880258`;
- released HEAD `f768268bf1a3f62c2e6741aecfba20d86545969c`;
- release state `RELEASED_TO_NORMAL_GOVERNANCE`;
- next authority `00_START_HERE.md`.

IDN-006 is complete. The next global programme action is unchanged: `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE`.


## Reusable capsule programme registered — 2026-10-07

- Authority: `CP-CAPSULE-001`.
- Machine tasks: `CAP-001..CAP-012`.
- Status: `PLANNED_DEPENDENCY_BOUND`.
- Existing LIVE-proven capsule baseline: `IDN-006 = DONE`.
- Productization target: reusable/versioned/installable GSCC→GSE→GACR→F1→release module.
- First execution gate: `GMC-19 + RTE-012 + ARCH-006 + IDN-006 = DONE`.
- `P12-S6` closure releases GMC-A, not CAP directly.
- Post-capsule junction is preserved: role/type → authority → connection intent → entry purpose → work kind/case.
- Cross-repository acceptance: required before capsule 1.0.0.
- Second/generic provider adapter acceptance: required before capsule 1.0.0.
- Current unique executable task remains `P12-S6`; this registration creates no parallel execution lane.
