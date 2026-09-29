# CONTROL PLANE TASKS

## Completed work package — SG-20260926-001

Objective: V2.7.0 Self-Governed Control Plane.

| Task | Status | Evidence |
|---|---|---|
| SG-001 Define source/client memory boundary | DONE | source-only namespace selected |
| SG-002 Create human source authorities | DONE | `docs/control-plane/*` |
| SG-003 Create machine source projections | DONE | `.governance/control-plane-state/*` |
| SG-004 Enforce source-state validation | DONE | Governance validation contract |
| SG-005 Prevent client leakage | DONE | CI/bootstrap non-leak proof |
| SG-006 Release V2.7.0 and reconcile source checkpoint | DONE | release subject `d11b72956e68526edf9b17aec472163a4e49a585` |
| SG-007 Resume framework program #12 | DONE | program authority restored |

## Active program — CREATE_NEW_REPOSITORY_COMPLETION

| Task | Status | Dependency | Exit evidence |
|---|---|---|---|
| P12-S1 MCP connectivity-choice contract completion | DONE | — | optional MCP linkage + DIRECT/SSH/BOTH choice contract tests + pilot evidence |
| P12-S2 Gouvern MCP discovery | DONE | P12-S1 | PASS/non-degraded discovery |
| P12-S3 Setup approval + APPLY_BASELINE | DONE | P12-S2 | baseline commit + first-agent handoff |
| P12-S4 Prove subsequent NORMAL_GOVERNED_ENTRY on external CASE 1 pilot (current pilot: Gouvern) | DONE | P12-S3 | `Gouvern#4` NORMAL_GOVERNED_ENTRY + LOCAL_HANDOFF_READY; no baseline reset |
| P12-S5 Second fresh repository E2E | ACTIVE_PARENT | P12-S4 | clean uninterrupted lifecycle; current child C1-13-A |
| P12-S6 Close CASE 1 and release next macro case | PENDING | P12-S5 | reconciled final evidence |

## Unique executable task

`C1-13-B_MERGE_PR51_REUPGRADE_EKYC_RESUME_DISCOVERY`

`P12-S5` remains the active parent. No later task may become executable before this inserted corrective gate completes.

### C1-12 discovered sub-tasks

| ID | Task | Status | Evidence / next |
|---|---|---|---|
| C1-12-A | Create subsequent-agent proof issue on Gouvern | DONE | `Patricked-code/Gouvern#3` |
| C1-12-B | Prove initial actor authorization behavior is fail-closed | DONE | start refused; no governed state advanced |
| C1-12-C | Add exact-HEAD machine local-entry start | DONE | V2.8.1 / PR #25 |
| C1-12-D | Synchronize client control-plane policy on governed upgrade | DONE | V2.8.2 / PR #26 |
| C1-12-E | Make bootstrap consistency self-test portable on instantiated clients | DONE | V2.8.3 / PR #27 |
| C1-12-F | Diagnose `INTENT_SELFTEST_FAILED: unexpected work item` | DONE | root cause: self-test inherited real instantiated client work-items |
| C1-12-G | Fix generic connection-intent self-test portability in template | DONE | V2.8.4 merged via PR #33; Template CI PASS |
| C1-12-H | Run template CI and release next compatible version if needed | DONE | V2.8.4 merge `608d29318d1b2df199e4ec304c4e2fe7bfb94263` |
| C1-12-I | Validate current framework release on external CASE 1 pilot (current pilot: Gouvern) | DONE | V2.8.6 pilot revalidation + normal-entry proof PASS |
| C1-12-I-A | Make client upgrader version-dynamic and client-CI-safe in Template | DONE | V2.8.5 merged; Template CI PASS |
| C1-12-I-B | Apply current governed Template upgrade to external CASE 1 pilot | DONE | V2.8.5 applied by control plane to `17f852c19ac8c5d26f40d3508338ce9c221697c8` |
| C1-12-J | Obtain all-green external pilot Governance CI | DONE | V2.8.6 pilot CI `36275524530` PASS |
| C1-12-J-A | Diagnose V2.8.5 pilot CI failure inside connection-intent synthetic bootstrap | DONE | auto_bootstrap failed because synthetic test still inherited project-profile/infrastructure/local-entry/MCP/access/workflow state |
| C1-12-J-B | Complete portable connection-intent fixture in Template | DONE | V2.8.6 merged; Template CI PASS |
| C1-12-J-C | Release Template fix and re-upgrade external CASE 1 pilot | DONE | pilot `671774df...`; CI `36275524530` PASS |
| C1-12-K-A | Correct machine local-start repository_dispatch token permission (`Contents: write`) | DONE | blocks C1-12-K after live dispatch refusal |
| C1-12-K | Re-run Gouvern#3 objective through machine local-entry start | DONE | `Gouvern#4` / run `36292612321` |
| C1-12-L | Verify mode = `NORMAL_GOVERNED_ENTRY` | DONE | `LOCAL-000004` mode confirmed |
| C1-12-M | Verify no first-agent baseline/session/work duplication | DONE | baseline/session/work blob identities unchanged; claims empty |
| C1-12-N | Persist normal-entry handoff + evidence | DONE | `LOCAL_HANDOFF_READY`, revision 6 |
| C1-12-O | Mark C1-12 / STEP 4 DONE and unlock C1-13 | DONE | STEP 4 exit satisfied |
| C1-12-P-A | Remove hard-coded `C1-12` relational active-phase validation | DONE | RED `36293227831`; GREEN `36293287750` |
| C1-12-P | Reconcile canonical relational memory with completed C1-12 evidence | DONE | human/machine/relational projections reconciled |

Current unique executable task: `P12-S5_SECOND_FRESH_REPOSITORY_E2E`.

## Canonical architecture hardening backlog

These tasks preserve target objectives without changing the active CASE 1 execution gate.

| ID | Task | Status | Dependency / note |
|---|---|---|---|
| ARCH-001 | Establish `CP-ARCH-001` canonical target architecture authority | DONE | source-only, revisioned authority |
| ARCH-002 | Add canonical authority/revision registry | DONE | migration `003_canonical_authorities.sql` |
| ARCH-003 | Complete deterministic materializer loaders for already-defined history tables | DONE | additive loader coverage |
| ARCH-004 | Add cross-projection/event-history reducer and reconstruction validation | PLANNED | after active C1-12 blocker |
| ARCH-005 | Formalize role/capability authorization model for INTAKER/SUPERVISOR/CODE_AGENT/REVIEWER | PLANNED | validate through cases |
| ARCH-006 | Strengthen CI cross-checks: manifest ↔ architecture ↔ cases ↔ current/tasks/next/handoff | PLANNED | no parallel truth |
| ARCH-007 | Generate derived PDF from canonical Markdown rather than maintain it manually | PLANNED | derived artifact only |
| ARCH-008 | Expose Governance API over validated semantics | FUTURE | after four case paths stabilize |
| ARCH-009 | Add PostgreSQL runtime projection if justified | FUTURE | Git remains foundational |
| ARCH-010 | Build Admin Web Application as control surface | FUTURE | workflow semantics first |

None of these items supersede the unique executable C1-12 sub-task.


## Identity / connection / session routing backlog

This backlog captures the missing automation required so an arriving agent can be identified, bound to a governed session, assigned a role/authority context, and routed chronologically without manual reconstruction.

| ID | Task | Status | Dependency / note |
|---|---|---|---|
| IDN-001 | Define canonical identity model: PRINCIPAL ≠ AGENT ≠ CONNECTION ≠ SESSION | PLANNED | preserve current session model compatibility |
| IDN-002 | Auto-capture authenticated GitHub actor/login/user-id and repository permission snapshot when available | PLANNED | no permission inference from memory |
| IDN-003 | Add principal registry and stable principal identifiers | PLANNED | GitHub external identity first; extensible to other providers |
| IDN-004 | Add connection-event registry with repository/branch/HEAD/provider/conversation-ref/timestamp | PLANNED | every arrival becomes traceable |
| IDN-005 | Define stable governed session identity/resume rules using strongest available refs | PLANNED | preserve existing stable_session_id semantics |
| IDN-006 | Auto-create or resume governed session after identity capture | PLANNED | fail closed on ambiguity |
| IDN-007 | Bind session to agent role: INTAKER / SUPERVISOR / CODE_AGENT / REVIEWER | PLANNED | role never bypasses authority |
| IDN-008 | Capture authority snapshot separately from identity/role | PLANNED | permission/authority is observed, not assumed |
| IDN-009 | Route chronologically: identity → session → role → authority → entry action → intent → questionnaire/action flow | PLANNED | one applicable question/action at a time |
| IDN-010 | Persist session/connection events and resume history into canonical relational memory | PLANNED | compatible with future Admin UI |
| IDN-011 | Add CI/self-tests for create/resume/ambiguous-session/fail-closed behavior | PLANNED | non-regression gate |
| IDN-012 | Add source-control-plane entry adapter so the template source can use the same identity/session model | PLANNED | source mode remains distinct from client local-entry |
| IDN-013 | Expose identity/session state to future Governance API/Admin UI | FUTURE | only after workflow semantics validated |

These items are architecture/backlog work only. They do not supersede `C1-12-F` as the unique executable task.


## Two-stage agent purpose routing backlog

After identity/session/role/authority resolution, an arriving agent on the control-plane source must enter a two-stage automated purpose router.

### Stage 1 — Why is the agent here?

The system asks exactly one top-level question:

1. `WORK_ON_CONTROL_PLANE` — work on `chainsolutions-wealthtech/Governed-Repository-Template` itself.
2. `APPLY_GOVERNANCE_CASE` — execute one of the four structuring cases.

### Stage 2A — If WORK_ON_CONTROL_PLANE

The system asks the work type:

- `CODE_IMPLEMENTATION` — implement/fix/evolve code or automation;
- `EXECUTE_EXISTING_TASK` — continue an already planned task/subtask/NEXT_ACTION;
- `ADD_OR_ENRICH_INFORMATION` — add/reconcile documentation, decisions, architecture, memory, evidence or structured information.

The system then automatically:
- loads current architecture/program/tasks/next action;
- resolves dependencies/collisions;
- determines applicable role and authority;
- proposes/claims the correct task;
- asks only missing questions;
- performs authorized technical actions itself;
- validates, checkpoints and hands off.

### Stage 2B — If APPLY_GOVERNANCE_CASE

The system asks the case:

1. `CREATE_NEW_REPOSITORY`
2. `ADOPT_EXISTING_REPOSITORY`
3. `MAP_EXISTING_PROJECT`
4. `LAB_EVOLUTION`

After selection, the selected case's governed questionnaire/action state machine takes over chronologically.

| ID | Task | Status | Dependency / note |
|---|---|---|---|
| RTE-001 | Define top-level `entry_purpose`: WORK_ON_CONTROL_PLANE vs APPLY_GOVERNANCE_CASE | PLANNED | after IDN identity/session resolution |
| RTE-002 | Define control-plane work kinds: CODE_IMPLEMENTATION / EXECUTE_EXISTING_TASK / ADD_OR_ENRICH_INFORMATION | PLANNED | source repository path |
| RTE-003 | Define structuring-case selection limited to exactly the 4 canonical cases | PLANNED | CONTINUE_GOVERNED_WORK is not a fifth case |
| RTE-004 | Build automated router from session/role/authority into Stage 1 and Stage 2 | PLANNED | no manual technical steps |
| RTE-005 | Auto-load PROGRAM/TASKS/NEXT_ACTION for WORK_ON_CONTROL_PLANE | PLANNED | preserve unique executable task |
| RTE-006 | Auto-resolve existing task vs new intake/information enrichment | PLANNED | no parallel task list |
| RTE-007 | Dispatch selected governance case to its case-specific questionnaire/state machine | PLANNED | chronology/gates preserved |
| RTE-008 | Persist entry purpose, work kind/case choice, answers and routing events in relational memory | PLANNED | continuous projection contract |
| RTE-009 | Automate authorized Git/CI/workflow actions after answers/approvals | PLANNED | human answers/approves; system executes |
| RTE-010 | Add fail-closed handling for missing/ambiguous purpose, case, task or authority | PLANNED | no inferred mutation authority |
| RTE-011 | Add CI tests for both top-level branches and every case choice | PLANNED | exhaustive router regression matrix |
| RTE-012 | Add resume semantics so reconnecting sessions continue at the exact unanswered question/action | PLANNED | no repeated completed questions |
| RTE-013 | Expose the automated purpose router in future Governance API/Admin UI | FUTURE | frontend after semantics stabilize |

These routing tasks are planned architecture work and do not supersede the current unique executable task `C1-12-F`.

## Active inserted framework correction

### C1-12-J-C-A — PR #42 post-merge GMC integrity reconciliation

Status: `DONE`

Parent: `C1-12-J-C`

Reason:
- unresolved PR #42 P1 review found artifact-consumer metadata inconsistent with dependency contracts/edges;
- unresolved PR #42 P2 review found CPD-029 normative enrichment not represented by a new Governance Model authority revision;
- relational continuity projections on the same surface require reconciliation.

Exit gate:
- all GMC artifact dependency representations reciprocal;
- `CP-GOVMODEL-001-R2` append/supersede revision present;
- CI regression test present and GREEN;
- relational source state/checkpoint/handoff current;
- PR merged and post-merge state attested.

Exit evidence:
- Template PR #43 merged at `113c50aa765ae886cd7a085637b8d5dbb5c2766b`;
- Governance CI run `36289874574`: PASS;
- GMC integrity regression gate: PASS;
- relational materialization: PASS;
- PR #42 P1/P2 review threads: RESOLVED.

The gate is satisfied. `C1-12-J-C` subsequently completed on pilot HEAD `671774dfc8e8be8eac2b50d5fb8f0928591694b3` with Governance CI `36275524530` PASS. Parent `C1-12-J` is DONE and `C1-12-K` is now the unique executable task.

## Queued work package — GOVERNANCE_MODEL_CATALOGUE_COMPLETION

Authority: `CP-GOVMODEL-001`.

Parent dependency: `P12-S6`.

The active unique executable item is now `C1-12-K`.

| Phase | Task | Description | Status | Depends on |
|---|---|---|---|---|
| GMC-A | GMC-01 | Separate central Governance Model from application strategies | PLANNED | P12-S6 |
| GMC-A | GMC-02 | Define canonical anatomy/metamodel and stable IDs | PLANNED | GMC-01 |
| GMC-B | GMC-03 | Inventory and normalize all governance domains | PLANNED | GMC-02 |
| GMC-B | GMC-04 | Inventory capabilities per domain | PLANNED | GMC-03 |
| GMC-B | GMC-05 | Decompose capabilities into reusable components | PLANNED | GMC-04 |
| GMC-B | GMC-06 | Inventory objects, fields and relationships | PLANNED | GMC-05 |
| GMC-C | GMC-07 | Inventory all state machines | PLANNED | GMC-06 |
| GMC-C | GMC-08 | Inventory transitions, forbidden transitions and recovery semantics | PLANNED | GMC-07 |
| GMC-C | GMC-09 | Build exhaustive Control Registry | PLANNED | GMC-08 |
| GMC-C | GMC-10 | Build Gate Registry | PLANNED | GMC-09 |
| GMC-C | GMC-11 | Build Evidence Type/Freshness Registry | PLANNED | GMC-10 |
| GMC-D | GMC-12 | Map abstract model to current implementation artifacts/tests | PLANNED | GMC-11 |
| GMC-D | GMC-13 | Build global dependency graph and installation order | PLANNED | GMC-12 |
| GMC-D | GMC-16 | Extend existing relational memory with canonical model registries using additive migration/materializer | PLANNED | GMC-13 |
| GMC-E | GMC-14 | Build applicability + semantic model-to-repository comparator | PLANNED | GMC-16 |
| GMC-E | GMC-15 | Extend semantic comparison to object/field/control/test level | PLANNED | GMC-14 |
| GMC-F | GMC-17 | Make Control Plane load/version/validate the shared Governance Model | PLANNED | GMC-15 |
| GMC-F | GMC-18 | Rebind CREATE/ADOPT/MAP/LAB to model + applicability + comparison | PLANNED | GMC-17 |
| GMC-G | GMC-19 | Cross-case E2E validation, reconcile common patterns, freeze Governance Model 1.0.0 | PLANNED | GMC-18 |

### GMC integration rules

- Knowledge capture may happen before P12-S6; mutable implementation progression may not bypass the current CASE 1 chain.
- Model inventory is extractive first: observe existing authorities/code/schemas/workflows/tests before declaring gaps.
- Existing `ARCH-*`, `IDN-*`, `RTE-*` tasks remain canonical and are linked into GMC rather than copied.
- PostgreSQL runtime, Governance API and Admin UI remain downstream of GMC-19 and cross-case stabilization.

### GMC work-package execution blueprint requirement

The identifiers `GMC-01` through `GMC-19` are **chronological work packages/groups**, not atomic tasks.

Before implementation of any GMC group, planning must first decompose that group into an execution blueprint.

Each group blueprint must contain:

- `MISSION` — why the group exists;
- `OBJECTIVE` — the concrete result it must obtain;
- `QUESTIONS_TO_RESOLVE`;
- `INPUTS` and `PREREQUISITES`;
- `WHERE_TO_LOOK` — exact repository paths, authorities, JSON policies, schemas, Python scripts/functions, workflows, tests, SQL/catalogue data, decisions, Git/PR history or external evidence to inspect;
- `SEARCH_ORDER` and `SEARCH_METHOD` — keywords, symbols, enums, states, control phrases or semantic patterns to find;
- atomic tasks/subtasks `GMC-Gxx-Tyy`;
- for each atomic task: purpose, inputs, where to look, method, action, classification rules, expected findings, output, output destination, evidence, validation, DONE criteria and BLOCK/HOLD conditions;
- `EXPECTED_RESULTS`;
- `ARTIFACTS` and canonical storage destinations;
- `EXIT_GATE`;
- `OUTPUTS`;
- `CONSUMED_BY` — later groups that reuse those outputs.

Canonical flow:

```text
GMC GROUP
  → mission
  → searches / observations
  → atomic tasks
  → intermediate results
  → controls / validation
  → stored versioned deliverable
  → evidence
  → exit gate
  → output reused by downstream groups
```

A downstream group is unlocked by validated outputs/evidence, not merely because the preceding group number is marked DONE.

The planning target is therefore an **Execution Blueprint** for all 19 groups, likely containing many atomic tasks, before any Governance Model catalogue code, SQL migration, comparator, applicability engine or runtime integration is implemented.

This planning requirement does not change the current unique executable CASE 1 task.

### GMC 19-work-package execution blueprint

The detailed planning authority is:

- `docs/control-plane/GOVERNANCE_MODEL_EXECUTION_BLUEPRINT.md`
- machine projection: `.governance/control-plane-state/governance-model-execution-blueprint.json`

It contains **19 chronological work packages and 174 atomic planning tasks**.

Canonical interpretation:

```text
GMC-Gxx = work package / mission group
GMC-Gxx-Tyy = atomic planning/execution task
```

The chronological chain is:

```text
GMC-G01 → GMC-G02 → GMC-G03 → GMC-G04 → GMC-G05 → GMC-G06
→ GMC-G07 → GMC-G08 → GMC-G09 → GMC-G10 → GMC-G11
→ GMC-G12 → GMC-G13 → GMC-G14 → GMC-G15
→ GMC-G16 → GMC-G17 → GMC-G18 → GMC-G19
```

A downstream group requires validated upstream outputs/evidence. A mere status `DONE` without the expected deliverables does not unlock it.

No task in this blueprint authorizes implementation before the current CASE 1 dependency chain and future write gates permit it.

### GMC dependency dimensions

Every `GMC-Gxx` work package now has three independent dependency dimensions:

```text
TASK_DEPENDENCY
+ ARTIFACT_DEPENDENCY
+ EVIDENCE_DEPENDENCY
→ EXIT CONTROLS PASS
→ DOWNSTREAM UNLOCK
```

A `DONE` status alone is insufficient.

The machine blueprint currently defines:
- 19 work packages;
- 174 atomic tasks;
- 85 persistent/versioned planned knowledge artifacts;
- typed dependency edges;
- explicit exit controls for every group;
- a final `GMC-G19` assembly/release contract.

The artifacts are planning objects only until their producing work packages are executed and validated.


## Current CASE 1 execution — V2.8.6 pilot revalidation complete

### C1-12-J-C / J completion and C1-12-K activation

- `C1-12-J-C`: `DONE`
- `C1-12-J`: `DONE`
- Pilot HEAD: `671774dfc8e8be8eac2b50d5fb8f0928591694b3`
- Pilot Template version: `2.8.6`
- Pilot Governance CI: `36275524530` / `PASS`
- Upgrade replay required: `false`
- `C1-12-K`: `IN_PROGRESS`
- Unique action: `C1_12_K_RERUN_GOUVERN_ISSUE_3`

C1-12-K must resume the existing `Patricked-code/Gouvern#3` proof via exact-HEAD machine local-entry start and may not advance to C1-12-L until the resulting entry is proven to be `NORMAL_GOVERNED_ENTRY`.

### C1-12-K-A machine local-start dispatch correction

- Live `/governed-local-start` was accepted by the source control plane from historical request `#4` under pilot HEAD `671774dfc8e8be8eac2b50d5fb8f0928591694b3`.
- No new pilot local-entry issue was created.
- Root cause: `POST /repos/{owner}/{repo}/dispatches` requires fine-grained `Contents: write`; the source workflow minted the `local-start-token` with `permission-contents: read`.
- Regression proof: PR #47 Governance CI run `36292333079` failed only at `Test repository-local governed agent entry` with the expected permission assertion.
- Fix proof: run `36292388479` passed after changing only the local-start token to `permission-contents: write`.
- Pilot remained unchanged while the generic framework defect was corrected.
- `C1-12-K-A`: `DONE`.
- `C1-12-K`: remains the unique executable task and must now be retried on the exact pilot HEAD.

### C1-12 K→P completion

- `Gouvern#4` was created by exact-HEAD machine local-start at pilot HEAD `671774dfc8e8be8eac2b50d5fb8f0928591694b3`.
- Request `LOCAL-000004` reached `NORMAL_GOVERNED_ENTRY` then `LOCAL_HANDOFF_READY` revision 6.
- Target start run: `36292612321` PASS.
- Answer runs: `36292715800`, `36292741820`, `36292775187`, `36292816422`, `36292850873` PASS.
- First-agent baseline, session `LOCAL-000002-S1`, `WORK-PROJECT-001`, and empty claims were unchanged.
- `P12-S4` is DONE.
- `P12-S5` is now the unique executable task.

### C1-12-P-A relational progression correction

- PR #48 first candidate correctly advanced replay/runtime state to `C1-13`.
- Governance CI `36293227831` failed only because `.governance/control-plane-db/materialize.py` still asserted that the active CASE 1 phase must literally equal `C1-12`.
- The durable invariant is now: exactly one active CASE 1 phase, and it must equal `runs.current_phase_id`.
- Governance CI `36293287750`: PASS, including relational materialization and textual integrity.
- `C1-12-P-A`: DONE.


### C1-13-A MCP endpoint recovery correction

- Parent: `P12-S5 / C1-13`.
- Status: `DONE`.
- Second fresh repository: `Patricked-code/Ekyc`.
- Source governed request: `#49`.
- Target local-entry issue: `Patricked-code/Ekyc#1`.
- Target HEAD: `b6be4b96306a765efd6bbd20727f02d5ef17553d`.
- Failure run: `36294979599`.
- Failure: direct MCP discovery used the accepted root URL and returned `HTTP 404`; the state machine exposed retry only and no longer allowed correcting `mcp_endpoint`.
- Generic defect code: `MCP_DISCOVERY_ENDPOINT_RECOVERY_DEAD_END`.
- Target-specific repair: forbidden; `Ekyc` is frozen.
- TDD RED: PR #50 / Governance CI `36295172971`, failure only on the new endpoint-recovery regression.
- Minimal fix: HTTP 404 reopens `Q_MCP_ENDPOINT_RECOVERY`; correcting the endpoint archives failed evidence, clears the hold, and returns to a clean `MCP_DISCOVERY` gate.
- TDD GREEN: Governance CI `36295231828` PASS across the full governance suite.
- Next: merge PR #50, update the fresh target through the governed Template path, correct the endpoint to the verified MCP route, and resume from MCP discovery without replaying prior answers.


### C1-13-B client local-entry self-test portability

- Parent: `P12-S5 / C1-13`.
- Depends on: `C1-13-A`.
- Status: `DONE`.
- PR #50 merged at `dbe0014784362393c8cfbb02ce7810d483cf2bb7`; post-merge Governance CI `36295619581` PASS.
- Governed client upgrade produced `Patricked-code/Ekyc@2ece8cff98258f7c40cf7b7383ceb5c026db9639` and migrated the open local-entry state without losing answers.
- Ekyc Governance CI `36295714554` failed only because the distributed local-entry self-test tried to read source-only `.github/workflows/governed-control-plane.yml`.
- Generic defect code: `CLIENT_LOCAL_ENTRY_SELFTEST_REQUIRES_SOURCE_ONLY_CONTROL_PLANE_WORKFLOW`.
- The source-only control-plane workflow must remain absent from client repositories.
- PR #51 TDD RED: `36295815960`.
- PR #51 functional GREEN: `36295850914`.
- Fix: source-only token-permission assertions run only when `.template-source` exists.
- Ekyc remains frozen until PR #51 merges and the correction is redistributed through the governed upgrader.


### C1-13-C Governance Model client self-test portability

- Parent: `P12-S5 / C1-13`.
- Depends on: `C1-13-B`.
- Status: `DONE`.
- PR #51 merged at `0a4a9961565d53a872d6eb62ad3f4afadbb11d6e`; post-merge CI `36296114629` PASS.
- Governed Ekyc re-upgrade produced `dd5a2664c4422ab14fc7131a77e5c2df0e0356a0`; `Ekyc#1` migrated to revision 25 with history preserved.
- Ekyc CI `36296169271` passed client/local-entry tests and failed only when the Governance Model integrity test attempted source-only control-plane state.
- Generic defect: `CLIENT_GOVERNANCE_MODEL_TEST_REQUIRES_SOURCE_ONLY_STATE`.
- PR #52 RED: `36296258279`.
- PR #52 GREEN: `36296295586`.
- Fix: Governance Model integrity test skips on clients without `.template-source`; source validation remains mandatory.
- Ekyc stays frozen until PR #52 merges and is redistributed through the governed upgrader.


### C1-13-D upgrader distribution of portable Governance Model test

- Parent: `P12-S5 / C1-13`.
- Depends on: `C1-13-C`.
- Status: `DONE`.
- PR #52 merged at `ca8ce60e31a1d5f07fc1293cac54ca29906b7501`; post-merge CI `36620454972` PASS.
- Governed Ekyc upgrade produced `bbe20f4406eb794df4d2452161462f945e2d3fc6`.
- Ekyc CI `36620623398` failed because the client retained the stale Governance Model integrity test: the upgrader did not distribute the corrected script.
- Generic defect: `UPGRADER_DOES_NOT_DISTRIBUTE_PORTABLE_GOVERNANCE_MODEL_TEST`.
- PR #53 RED `36620804501` → GREEN `36620877757`.
- Fix: add `scripts/test_governance_model_integrity.py` to client upgrader `static_paths`; source-only model state remains excluded.
- Ekyc stays frozen until PR #53 merges and is redistributed.


### C1-13-E MCP TLS external dependency

- Parent: `P12-S5 / C1-13`.
- Depends on: `C1-13-D`.
- Status: `IN_PROGRESS / EXTERNAL_BLOCKER`.
- Ekyc HEAD `87c28f4fd4e36aa3d65cfc384309a054c1640e4c`.
- Ekyc Governance CI `36621490571`: PASS.
- MCP discovery retry `36621624763`: blocked by expired TLS certificate on `mcp.wealthtechinnovations.com`.
- `BOTH` cannot degrade successfully because the SSH certificate broker is HTTPS on the same affected host.
- External intake: `Patricked-code/MCP#201`.
- No MCP code/runtime mutation is authorized from this Template workstream.
- Next: wait for governed MCP TLS remediation/attestation, then retry the preserved Ekyc discovery checkpoint.

### C1-13-E-A explicit MCP discovery authority gate

- Parent: `P12-S5 / C1-13`.
- Depends on: `C1-13-D`.
- Status: `IN_PROGRESS`.
- Blocks: `C1-13-E`, `P12-S5`.
- Generic defect code: `MCP_DISCOVERY_CONFIGURATION_IMPLICITLY_AUTHORIZES_EXECUTION`.
- Owner feedback: answering MCP binding/transport/endpoint/scope/domain strategy/runtime policy must prepare a discovery plan, not execute a network call.
- Required fix: insert an explicit read-only discovery-plan approval gate before credential provisioning and MCP discovery.
- Compatibility: preserve all Ekyc answers, archive any pre-approval discovery evidence, migrate the open issue back to the approval gate through the governed client upgrader, and do not patch Ekyc directly.
- Broader additive contract: questionnaire answers and fresh observations enrich the existing project/resource model and derive future work-items/dependencies/authorities for the existing Loop Engineering; no parallel governance or task engine.
- The TLS failure run `36621624763` and intake `Patricked-code/MCP#201` remain historical/external evidence and become relevant again only after discovery is explicitly approved.

### C1-13-E-B explicit Ekyc discovery approval

- Parent: `P12-S5 / C1-13`.
- Depends on: `C1-13-E-A`.
- Status: `IN_PROGRESS`.
- Gate: `OWNER_APPROVAL_REQUIRED_FOR_READ_ONLY_MCP_DISCOVERY`.
- The exact plan is persisted in `NEXT_ACTION.md`.
- No credential provisioning, MCP call, SSH certificate request or network discovery may occur before explicit approval.
- On approval, dispatch only the approved read-only discovery. Then use its observations to continue the adaptive questionnaire and gap/task preparation.
- On denial or change, preserve all prior answers and re-enter the earliest affected preparation question.
