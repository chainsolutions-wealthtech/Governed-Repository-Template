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
| P12-S4 Prove subsequent NORMAL_GOVERNED_ENTRY on external CASE 1 pilot (current pilot: Gouvern) | IN_PROGRESS | P12-S3 | live normal-entry handoff, no baseline reset |
| P12-S5 Second fresh repository E2E | PENDING | P12-S4 | clean uninterrupted lifecycle |
| P12-S6 Close CASE 1 and release next macro case | PENDING | P12-S5 | reconciled final evidence |

## Unique executable task

`P12-S4_PROVE_NORMAL_GOVERNED_ENTRY_ON_GOUVERN`

No later task may become executable before its dependency is complete.

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
| C1-12-I | Validate current framework release on external CASE 1 pilot (current pilot: Gouvern) | ACTIVE_PARENT | validation blocked until Template upgrader can distribute current client surface |
| C1-12-I-A | Make client upgrader version-dynamic and client-CI-safe in Template | DONE | V2.8.5 merged; Template CI PASS |
| C1-12-I-B | Apply current governed Template upgrade to external CASE 1 pilot | DONE | V2.8.5 applied by control plane to `17f852c19ac8c5d26f40d3508338ce9c221697c8` |
| C1-12-J | Obtain all-green external pilot Governance CI | ACTIVE_PARENT | V2.8.5 pilot CI exposed second generic fixture-isolation defect |
| C1-12-J-A | Diagnose V2.8.5 pilot CI failure inside connection-intent synthetic bootstrap | DONE | auto_bootstrap failed because synthetic test still inherited project-profile/infrastructure/local-entry/MCP/access/workflow state |
| C1-12-J-B | Complete portable connection-intent fixture in Template | DONE | V2.8.6 merged; Template CI PASS |
| C1-12-J-C | Release Template fix and re-upgrade external CASE 1 pilot | IN_PROGRESS | apply V2.8.6 through governed exact-HEAD upgrade path |
| C1-12-K | Re-run Gouvern#3 through machine local-entry start | PENDING | depends on C1-12-J |
| C1-12-L | Verify mode = `NORMAL_GOVERNED_ENTRY` | PENDING | depends on C1-12-K |
| C1-12-M | Verify no first-agent baseline/session/work duplication | PENDING | depends on C1-12-L |
| C1-12-N | Persist normal-entry handoff + evidence | PENDING | depends on C1-12-M |
| C1-12-O | Mark C1-12 / STEP 4 DONE and unlock C1-13 | PENDING | depends on C1-12-N |
| C1-12-P | Reconcile canonical relational memory with completed C1-12 evidence | PENDING | depends on C1-12-O |

Current unique executable sub-task: `C1-12-J-C_RELEASE_AND_REUPGRADE_CASE1_PILOT`.

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
