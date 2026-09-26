# CANONICAL ARCHITECTURE — Governed Repository Platform

> Authority ID: `CP-ARCH-001`  
> Authority type: `CANONICAL_TARGET_ARCHITECTURE`  
> Scope: `CONTROL_PLANE_SOURCE_ONLY`  
> Status: `ACCEPTED_TARGET_ARCHITECTURE`  
> Revision: `2`  
> Repository: `chainsolutions-wealthtech/Governed-Repository-Template`  
> Distribution: `SOURCE_ONLY / DO_NOT_COPY_TO_CLIENTS`

## 1. Purpose

This authority defines the durable **target architecture and invariants** of the Governed Repository Platform.

It does **not** define the live current state of implementation. Live state remains in `CURRENT_STATE.md` and machine projections. Execution sequencing remains in `PROGRAM.md`, `TASKS.md`, and `NEXT_ACTION.md`.

The architecture must evolve additively:

```text
PRESERVE
→ REUSE
→ CONNECT
→ EXTEND
→ MIGRATE COMPATIBLY
→ HOLD_FOR_REVIEW when safety cannot be proven
```

Never:

```text
UNKNOWN
→ ASSUME
→ OVERWRITE
```

## 2. Platform identity

The repository is not merely a set of template files. Its target is a multi-repository governance platform:

```text
GOVERNED REPOSITORY PLATFORM
=
Central Governed Control Plane
+ Governance Core
+ Governed Template Distribution
+ Canonical Memory
+ Four Structuring Cases
+ Agent Entry / Session / Work Continuity
+ Evidence / Checkpoints / Handoffs
+ Reconciliation / Non-Regression
+ Future Governance API
+ Future PostgreSQL runtime projection
+ Future Admin Web Application
```

## 3. Four structuring cases + one post-case mode

The canonical structuring cases are:

1. `CREATE_NEW_REPOSITORY`
2. `ADOPT_EXISTING_REPOSITORY`
3. `MAP_EXISTING_PROJECT`
4. `LAB_EVOLUTION`

`CONTINUE_GOVERNED_WORK` is not a fifth structuring case. It is a `POST_CASE_MODE` used once a repository already has exploitable governance.

This distinction must remain consistent across documentation, schemas, relational catalogues, workflows, agent logic, API and future UI.

## 4. Central control plane responsibilities

The central control plane must:

1. receive a governed request;
2. resolve the structuring case or post-case mode;
3. identify target repository and owner scope;
4. verify actual authority;
5. build a chronological path;
6. ask only applicable questions;
7. persist answers and decisions;
8. require evidence;
9. fail closed on contradiction, insufficient authority or invalid evidence;
10. emit a structured handoff;
11. enable a later agent to resume without relying on conversation history.

Principle:

```text
CONTROL PLANE != TARGET REPOSITORY
```

The control plane owns framework orchestration and framework memory. The target repository owns its local project governance and project state.

## 4A. Framework product vs pilot repositories

The framework product is:

`chainsolutions-wealthtech/Governed-Repository-Template`

All generic governance behavior, schemas, automation, tests, canonical architecture, control-plane memory and reusable database model evolve here first.

Pilot/validation repositories such as `Patricked-code/Gouvern` are external case-execution fixtures. They may reveal defects or provide evidence, but they are not the product and do not own framework architecture or roadmap.

Canonical rule:

```text
PILOT REVEALS GENERIC DEFECT
→ FIX TEMPLATE
→ TEMPLATE CI
→ RELEASE/UPGRADE
→ VALIDATE ON PILOT
```

Never:

```text
PILOT PROJECT STATE
→ BECOMES FRAMEWORK SOURCE OF TRUTH
```

## 5. Source/control-plane memory vs client memory

Source-only control-plane memory lives under:

```text
docs/control-plane/
.governance/control-plane-state/
.governance/control-plane-db/
```

It must never leak into instantiated or adopted clients.

```text
SOURCE CONTROL PLANE MEMORY
!=
DISTRIBUTED CLIENT PROJECT STATE
```

Clients receive generic rules, schemas, automation and machine-governance primitives, never another project's history, evidence, business decisions or control-plane source memory.

## 6. CASE 1 — CREATE_NEW_REPOSITORY

Target lifecycle:

```text
CREATE
→ BOOTSTRAP
→ FIRST_AGENT_BOOTSTRAP
→ BUSINESS/PROJECT BASELINE
→ TECHNICAL/INFRASTRUCTURE CHOICES
→ OPTIONAL MCP LINKAGE
→ GOVERNANCE MATERIALIZATION
→ FIRST HANDOFF
→ NORMAL_GOVERNED_ENTRY
→ SECOND FRESH E2E PROOF
→ CASE CLOSURE
```

Known canonical phases remain `C1-00` through `C1-14`.

MCP linkage is optional. If enabled, the owner chooses among:

- `DIRECT_MCP_TOKEN`
- `SSH`
- `BOTH`

Connectivity never grants mutation authority.

A valid first-agent baseline must prevent a later agent from replaying `FIRST_AGENT_BOOTSTRAP`; later agents route through `NORMAL_GOVERNED_ENTRY`.

## 7. CASE 2 — ADOPT_EXISTING_REPOSITORY

Canonical contract:

```text
OBSERVE
→ INVENTORY
→ BASELINE
→ COMPATIBILITY MAP
→ COLLISION ANALYSIS
→ ADOPTION PLAN
→ EXPLICIT ACCEPTANCE
→ ADD COMPATIBLE MISSING BRICKS
→ VALIDATE
→ ATTEST
```

Adoption is additive and plan-first. Existing content and existing authorities must be preserved unless an explicit governed migration says otherwise.

Capability classification:

- `ADD`
- `REUSE`
- `PRESERVE_EXISTING`
- `CONFLICT_HOLD_FOR_REVIEW`
- `SKIP_NOT_APPLICABLE`

Every adoption plan is exact-HEAD bound. If HEAD moves, reobserve and revalidate.

## 8. CASE 3 — MAP_EXISTING_PROJECT

CASE 3 is read-only by default and must distinguish:

```text
CURRENT_ARCHITECTURE = observed facts
TARGET_ARCHITECTURE  = desired design
GAP_MAP              = transformation gap
```

Modes:

- `CURRENT_ONLY`
- `CURRENT_AND_TARGET`

Always distinguish:

- `OBSERVED`
- `DESIRED`
- `UNKNOWN`

CASE 3 is the reusable understanding engine for CASE 2, CASE 4 and governed continuation.

## 9. CASE 4 — LAB_EVOLUTION

Canonical contract:

```text
OBSERVE CANONICAL HEAD
→ CAPTURE BASELINE
→ READ EXISTING GOVERNANCE / ARCHITECTURE / TESTS
→ DEFINE LAB SCOPE
→ OBTAIN EXPLICIT BRANCH/PR AUTHORITY
→ CREATE ISOLATED LAB BRANCH
→ IMPLEMENT ADDITIVELY
→ TEST / COMPARE / RECONCILE
→ OPEN OR UPDATE LAB PR
→ REVIEW NON-REGRESSION
→ MERGE ONLY WHEN ACCEPTED
→ ATTEST CANONICAL POST-MERGE STATE
```

The canonical branch remains source of truth. The lab branch is candidate evolution, never a second durable truth.

## 10. POST-CASE MODE — CONTINUE_GOVERNED_WORK

Normal governed continuation:

```text
NORMAL_GOVERNED_ENTRY
→ load current authorities
→ resolve session
→ resolve role
→ load program/tasks
→ verify authority
→ claim work
→ perform work
→ test
→ validate
→ checkpoint
→ handoff
→ next agent
```

## 11. Entry-routing dimensions

Every agent connection must resolve three distinct dimensions:

```text
ENTRY ACTION      = which macro path?
CONNECTION INTENT = why is the agent here now?
AUTHORITY         = what may it actually do?
```

Intent never creates permission.

Unknown or unresolved routing fails closed.

## 12. Agent roles

The target role model includes at least:

- `INTAKER`
- `SUPERVISOR`
- `CODE_AGENT`
- `REVIEWER`

Roles influence responsibilities and permitted actions but never bypass authority gates.

## 12A. Identity / connection / session separation

Governed arrival must progressively separate:

- `PRINCIPAL` — authenticated external account/identity;
- `AGENT` — acting agent/provider;
- `CONNECTION` — one observed arrival event;
- `SESSION` — governed continuity/resume unit;
- `ROLE` — responsibility model;
- `AUTHORITY` — separately observed permission/mutation envelope.

Target sequence:

```text
CAPTURE PRINCIPAL / ACTOR
→ RESOLVE AGENT
→ CREATE CONNECTION EVENT
→ CREATE OR RESUME SESSION
→ RESOLVE ROLE
→ OBSERVE AUTHORITY
→ RESOLVE ENTRY ACTION
→ RESOLVE CONNECTION INTENT
→ ENTER CHRONOLOGICAL GOVERNED QUESTION/ACTION FLOW
```

Identity and role never create authority. Ambiguous session resolution fails closed.

## 12B. Two-stage automated purpose routing

After identity/session/role/authority resolution on the control-plane source, the system asks one top-level purpose question:

```text
WHY ARE YOU HERE?
├─ WORK_ON_CONTROL_PLANE
└─ APPLY_GOVERNANCE_CASE
```

If `WORK_ON_CONTROL_PLANE`:

```text
WORK KIND
├─ CODE_IMPLEMENTATION
├─ EXECUTE_EXISTING_TASK
└─ ADD_OR_ENRICH_INFORMATION
```

The system then loads source authorities, resolves the current program/task graph, claims or creates the correct governed work item when allowed, asks only missing questions, executes authorized technical actions, validates, checkpoints and hands off.

If `APPLY_GOVERNANCE_CASE`:

```text
CASE
├─ CREATE_NEW_REPOSITORY
├─ ADOPT_EXISTING_REPOSITORY
├─ MAP_EXISTING_PROJECT
└─ LAB_EVOLUTION
```

The selected case then owns the chronological questionnaire/action state machine.

`CONTINUE_GOVERNED_WORK` remains a post-case mode and is not shown as a fifth structuring case.

### Human interaction boundary

The human is not expected to perform technical Git/GitHub/CI/file operations manually.

Human participation is limited to:
- answering required governed questions;
- making choices;
- giving explicit approvals when a gate requires human authorization.

The governed system performs the authorized technical execution automatically.

Automation never bypasses explicit authority, approval, exact-HEAD or fail-closed gates.

## 13. Architecture → program → task lineage

Tasks are not isolated TODOs.

Canonical lineage:

```text
GLOBAL ARCHITECTURE
→ PROGRAM
→ CASE / WORKSTREAM
→ PHASE
→ INTEGRATION SLOT
→ TASK
→ SUBTASK
```

A governed task should be traceable to:

- origin;
- parent;
- dependencies;
- integration slot;
- target architecture;
- authorities;
- agent/session;
- claim/collision domain;
- acceptance criteria;
- tests;
- evidence;
- checkpoint;
- handoff;
- unique next action.

New intakes, defects and owner changes enrich the existing program; they do not replace it with a parallel task list.

## 14. Canonical memory authority categories

The source control-plane memory is organized by role:

### TARGET
- `CANONICAL_ARCHITECTURE.md`
- principles
- invariants
- target capabilities

### CURRENT
- `CURRENT_STATE.md`
- `.governance/control-plane-state/current.json`
- checkpoint projections

### EXECUTION
- `PROGRAM.md`
- `TASKS.md`
- `NEXT_ACTION.md`

### CONTINUITY
- handoffs
- case replay ledgers
- agent activity ledger

### HISTORY
- `DECISIONS_LOG.md`
- `SUIVI.md`
- run events
- evidence
- owner feedback
- supersession history

No single current projection is history.

## 15. Append / supersede / revalidate

History is never silently rewritten.

```text
NEW INFORMATION
→ COMPARE TO CANONICAL MEMORY
   ├─ compatible     → enrich
   └─ contradiction  → HOLD_FOR_REVIEW
```

Decisions and answers evolve by append/supersede. A changed choice invalidates only dependent evidence and phases.

## 16. Owner feedback

Owner feedback is first-class data and may include:

- clarification;
- choice change;
- scope change;
- approval;
- rejection;
- new requirement;
- framework defect indication;
- external dependency issue.

Processing:

```text
OWNER FEEDBACK
→ CLASSIFY
→ IMPACT ANALYSIS
→ RETURN TO EARLIEST AFFECTED PHASE IF REQUIRED
→ INVALIDATE ONLY DEPENDENTS
→ REVALIDATE
```

## 17. Checkpoints and handoffs

A checkpoint must be precise enough to resume deterministically.

A handoff must include at least:

- repository;
- canonical branch;
- observed/subject HEAD;
- case/run;
- phase/checkpoint;
- session;
- role;
- active program;
- current task;
- open claims;
- relevant decisions;
- evidence;
- pending questions;
- permissions and forbidden actions;
- unique next action;
- read-first authorities.

## 18. Exact-HEAD and concurrency

Important mutations are based on an observed HEAD:

```text
OBSERVE HEAD X
→ BUILD PLAN
→ BEFORE WRITE: HEAD == X ?
   YES → continue if all gates pass
   NO  → reconcile first
```

Multi-agent governance must support sessions, claims, collision domains, dependency-safe dispatch, single writer where required and structured handoff.

## 19. Capability model

The platform should progressively be understood as capabilities rather than only files.

Target capabilities include:

- `CAPABILITY_AGENT_ENTRY`
- `CAPABILITY_CANONICAL_MEMORY`
- `CAPABILITY_SESSION`
- `CAPABILITY_PROGRAM`
- `CAPABILITY_TASK_QUEUE`
- `CAPABILITY_CLAIMS`
- `CAPABILITY_CHECKPOINT`
- `CAPABILITY_HANDOFF`
- `CAPABILITY_INTAKE`
- `CAPABILITY_VALIDATION`
- `CAPABILITY_AUTO_BOOTSTRAP`
- `CAPABILITY_RECONCILIATION`
- `CAPABILITY_EXISTING_REPO_ADOPTION`
- `CAPABILITY_PROJECT_MAPPING`
- `CAPABILITY_LAB_EVOLUTION`

A capability should eventually expose detect, compatibility classification, add/reuse, upgrade, validate, repair and reconcile behavior.

## 20. Event history + current projections

The target memory model is lightweight event-sourcing:

```text
APPEND-ONLY EVENTS
→ DETERMINISTIC REDUCER / MATERIALIZATION
→ CURRENT PROJECTIONS
```

Examples of durable events:

- `ARCHITECTURE_AUTHORITY_CREATED`
- `ARCHITECTURE_REVISION_ACCEPTED`
- `CASE_STARTED`
- `QUESTION_ANSWERED`
- `DECISION_ACCEPTED`
- `CHECKPOINT_CREATED`
- `HANDOFF_CREATED`
- `OWNER_FEEDBACK_RECEIVED`
- `TASK_COMPLETED`
- `CASE_COMPLETED`

Current state must be reconstructable from durable authorities/history to the extent defined by the platform contract.

## 21. Canonical relational model and future runtime

Authority hierarchy target:

```text
GIT-VERSIONED GOVERNED AUTHORITIES
+ SQL MIGRATIONS
+ JSON CATALOGUES / SEEDS
+ APPEND-ORIENTED HISTORY
        ↓
DETERMINISTIC RELATIONAL MATERIALIZATION
        ↓
SQLite validation projection
        ↓
future PostgreSQL runtime projection
        ↓
Governance API
        ↓
Admin Web Application
```

PostgreSQL and the future UI must not become opaque independent sources of truth.

## 22. Authority revisioning

Canonical authorities evolve monotonically.

Conceptual model:

```text
authority
  revision 1
    ↓ superseded by
  revision 2
    ↓ superseded by
  revision N
```

Each revision records subject HEAD, content hash, reason, source decision and predecessor.

This avoids silent architectural rewrites.

## 23. Freshness semantics

Never attempt a self-referential `current_head_sha = commit_that_contains_that_sha` loop.

Distinguish:

- `subject_head_sha`: repository state described by a projection;
- `memory_commit_sha`: commit containing the projection, when recorded;
- `freshness`: `CURRENT | STALE | NEEDS_RECONCILIATION | CONFLICT`.

Every agent must reobserve remote HEAD and reconcile freshness before mutable work.

## 24. Non-regression

Always distinguish:

- pre-existing defect;
- introduced regression;
- intended change;
- unknown/unverified state.

Cross-case rule:

```text
PRESERVE
→ REUSE
→ CONNECT
→ EXTEND
→ MIGRATE COMPATIBLY
→ HOLD_FOR_REVIEW
```

## 25. Construction roadmap

The architectural roadmap is:

1. stabilize CASE 1;
2. prove `NORMAL_GOVERNED_ENTRY`;
3. prove the second fresh-repository E2E;
4. close CASE 1;
5. execute/test CASE 2 and enrich its catalogue;
6. execute/test CASE 3 and enrich the model;
7. execute/test CASE 4;
8. reconcile patterns common to all four cases;
9. stabilize the common relational model;
10. strengthen reconciliation / upgrade / repair;
11. expose a Governance API;
12. move runtime projection to PostgreSQL if justified;
13. build the Admin Web Application.

```text
WORKFLOW SEMANTICS FIRST
FRONTEND SECOND
```

## 26. MCP boundary

`Patricked-code/MCP` is independently governed.

From this framework workstream:

- READ / OBSERVE is allowed when required;
- missing capabilities are external intakes;
- no MCP implementation is performed here;
- connectivity never implies mutation authority.

## 27. Source provenance

This authority was distilled additively from the user-supplied V2.8.3 architecture snapshot and integration analysis, then reconciled against the live repository after V2.8.3.

Historical snapshot identity:

- repository: `chainsolutions-wealthtech/Governed-Repository-Template`;
- snapshot HEAD: `892f793a0202cb4f69169001821014f47db45c3f`;
- snapshot template version: `2.8.3`;
- snapshot date: `2026-09-26`.

The snapshot's old live-state values do not supersede newer live Git evidence.

Primary architecture source was Markdown. The PDF is a derived presentation representation, not the primary authority.

## 28. Current execution boundary

This architecture authority enriches canonical knowledge only.

It does not change the current CASE 1 execution gate. The live `CURRENT_STATE.md`, `TASKS.md` and `NEXT_ACTION.md` remain authoritative for the exact active task.
