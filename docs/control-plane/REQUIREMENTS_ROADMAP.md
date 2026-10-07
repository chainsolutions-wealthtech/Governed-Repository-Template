# REQUIREMENTS & ROADMAP — Governed Repository Platform

> **Traceability / cahier des charges materialization**
>
> This file consolidates requirements, implementation status, validation evidence and remaining work. It does not replace the named canonical authorities. Requirement semantics are owned by the referenced authority; execution order is owned by PROGRAM/TASKS/NEXT_ACTION.

## 1. Product objective

Deliver a governance platform that can accept heterogeneous agents/providers, identify and isolate arrivals without fabricating unavailable identity, maintain durable session/work continuity, route an admitted agent to the correct governed purpose/case, ask only applicable unresolved questions, execute only explicitly authorized actions, preserve evidence/history, and allow another agent to resume deterministically without relying on chat memory.

## 2. Global acceptance principles

Every completed capability must satisfy:

- fail closed on ambiguity or missing mandatory evidence;
- exact-HEAD before mutable work;
- no provider-private identity fabrication;
- role/intention do not grant authority;
- questions/decisions/history are append/supersede, not destructively overwritten;
- no parallel canonical database;
- source-only control-plane history never leaks to clients;
- pilot defects are fixed in the Template first;
- one unique executable global task;
- continuity survives agent/conversation replacement;
- CI plus LIVE proof where the capability depends on real transport/session behavior.

## 3. Requirements traceability matrix

| ID | Requirement | Canonical source | Runtime / data implementation | Validation | Status | Remaining work |
|---|---|---|---|---|---|---|
| RQ-01 | Mandatory pre-entry before normal repository work | `00_GSCC_ENTRY.md` | GSCC entry router/workflow | GSCC pre-entry CI + LIVE | LIVE_PROVEN | package portably in CAP |
| RQ-02 | No fabricated provider identity | GSCC/IDN decisions | extractor + arrival identity + explicit UNAVAILABLE | multi-arrival/LIVE | LIVE_PROVEN | preserve across adapters |
| RQ-03 | Per-arrival isolated durable state | IDN/capsule | `state_scope`, GSCC arrival/session DB | LIVE #244 chain + CI | LIVE_PROVEN | backend abstraction CAP-007 |
| RQ-04 | Correlated liveness before GSE progression | GSCC route | Q9 ACK/challenge | LIVE + replay/stale tests | LIVE_PROVEN | cross-adapter proof |
| RQ-05 | Q10 GSE must precede Q2 GACR | realignment authority | SessionTwin + canonical GACR attach | CI + LIVE | LIVE_PROVEN | preserve in public capsule contract |
| RQ-06 | F1 validates actual requested function | function exposure authority | F1 runtime | LIVE actual-function proof | LIVE_PROVEN | portable adapter contract |
| RQ-07 | Release enters normal governance exactly once | capsule/release | release workflow/receipt | LIVE release proof | LIVE_PROVEN | formalize release→junction schema |
| RQ-08 | Four structuring cases + continuation mode remain distinct | CP-ARCH-001 | catalogue + entry-action policy | schema/router tests | IMPLEMENTED | industrialize Cases 2–4 |
| RQ-09 | Connection intent is separate from authority | CP-ARCH-001 / intent policy | connection-intent policy | routing tests | IMPLEMENTED | bind into two-stage router |
| RQ-10 | Role is separate from authority | CP-ARCH-001 | partial session/role model | architecture/continuity tests | PARTIAL | ARCH-005 + normalized registry |
| RQ-11 | Two-stage entry purpose routing | RTE / control-plane policy | questionnaire catalogue fields exist | target semantics only | PLANNED_NOT_ACTIVE | RTE-001..RTE-012 |
| RQ-12 | Ask only applicable unresolved questions | CP-ARCH-001 / DATA_MODEL | questions + required_when + run_answers | CASE 1 replay evidence | IMPLEMENTED_CASE1 | generalize across router/cases |
| RQ-13 | Resume without replaying completed questions | DATA_MODEL / continuity | revisions + checkpoints/handoffs | CASE 1 + session continuity | IMPLEMENTED_CASE1 | exact generic RTE resume |
| RQ-14 | Owner feedback returns to earliest affected phase only | CP-ARCH-001 / schema | owner_feedback + supersession | CASE 1 corrections | IMPLEMENTED | cross-case generalization |
| RQ-15 | Durable event/evidence history | DATA_MODEL | run_events/evidence/decisions | materializer CI | IMPLEMENTED | broader runtime projection |
| RQ-16 | Agent activity/continuity is queryable | DATA_MODEL / GACR | agent_sessions/activity + GACR state | CI/LIVE | IMPLEMENTED | normalize with broader identity registry |
| RQ-17 | One canonical model shared by all four cases | CP-GOVMODEL-001 | catalogue authority exists | catalogue integrity CI | PLANNED | GMC-01..GMC-19 |
| RQ-18 | No parallel truth across architecture/program/tasks/current/handoff | CP-ARCH-001 | cross-projection validators | CI | PARTIAL | ARCH-006 |
| RQ-19 | Reusable capsule installable outside full Template | CP-CAPSULE-001 | current implementation still source-coupled | current flow green | PLANNED | CAP-001..CAP-012 |
| RQ-20 | Second provider/generic adapter parity | CP-CAPSULE-001 | reference GitHub/ChatGPT path only | not yet accepted | PLANNED | CAP-011 |
| RQ-21 | Clean second-repository capsule installation | CP-CAPSULE-001 | not yet packaged | not yet accepted | PLANNED | CAP-010 |
| RQ-22 | Deterministic relational projection | DATA_MODEL | SQL + seeds + materialize.py | CI materialization | IMPLEMENTED | extend for GMC/identity normalization |
| RQ-23 | PostgreSQL must remain a projection, not authority | CP-ARCH-001 / DATA_MODEL | not deployed | architectural rule | FUTURE | evaluate after common model stabilizes |
| RQ-24 | Governance API exposes validated semantics only | CP-ARCH-001 | not implemented | future contract tests | FUTURE | ARCH-008 / downstream |
| RQ-25 | Admin UI is downstream of workflow semantics | CP-ARCH-001 | not implemented | future E2E | FUTURE | ARCH-010 / downstream |
| RQ-26 | Client upgrades preserve mutable client state | CP-ARCH-001 | governed upgrader | CASE 1 client upgrades | LIVE_PROVEN_CASE1 | reuse across remaining cases |
| RQ-27 | New information enriches existing programme, never creates untracked parallel work | programme/namespace authorities | tasks/namespace/intake | CI | IMPLEMENTED | continuous enforcement |
| RQ-28 | Every meaningful interruption leaves a reconstructible checkpoint/handoff | continuity authorities | checkpoint/handoff/GACR | CI + practice | IMPLEMENTED | expose later via API/UI |

| RQ-29 | Complete autonomous admin cockpit | CP-SAAS-001 / ARCH-010 | not implemented | future UI/E2E | PLANNED | SAA-007..SAA-009 |
| RQ-30 | Full versioned REST/OpenAPI API | CP-SAAS-001 / ARCH-008 | not implemented | contract/integration tests required | PLANNED | SAA-002 + SAA-006 |
| RQ-31 | Governed backend service/microservice architecture | CP-SAAS-001 | not implemented | service-boundary + integration proof required | PLANNED | SAA-003..SAA-006 |
| RQ-32 | SaaS-ready tenancy/isolation | CP-SAAS-001 | not implemented | tenant isolation/security tests required | PLANNED | SAA-001 + SAA-004 + SAA-010 |
| RQ-33 | Reproducible production deployment | CP-SAAS-001 | not implemented | staging + production smoke/E2E | PLANNED | SAA-011..SAA-014 |
| RQ-34 | Production URL `https://mcp.wealthtechinnovations.com/template` | CP-SAAS-001 | target registered | live deployment not yet authorized | PLANNED | SAA-013 |
| RQ-35 | Operational backup/restore/upgrade/rollback | CP-SAAS-001 | not implemented | recovery/upgrade drills required | PLANNED | SAA-010 + SAA-015 |

| RQ-36 | Availability-aware parallel agent dispatch with explicit idle/block/limit state | CP-AGENT-RELAY-001-R7 / CPD-074 | scheduler + roster + telemetry + client/issue transport implemented | CI + post-merge roster proof required | IMPLEMENTED_PENDING_VALIDATION | merge R7, prove roster refresh, then opt-in canonical task groups as dependency graph permits |

## 4. Current validated baseline

### Proven in LIVE
- CASE 1 first-agent bootstrap and later normal governed entry;
- second fresh CASE 1 E2E without target-specific repair;
- GSCC→GSE→GACR→Q12→F1→release;
- per-arrival isolation and continuation;
- canonical GACR session binding;
- exact release to normal governance.

### Implemented foundations
- question/options catalogue;
- answer revisions and supersession;
- run events/evidence/decisions;
- owner feedback;
- checkpoint/handoff;
- agent activity;
- deterministic SQLite projection;
- namespace/work registry;
- entry action and connection intent.

### Explicitly not yet active
- source two-stage `entry_purpose` router;
- full normalized principal/agent/connection/session/role/authority relational model;
- Governance Model 1.0.0;
- reusable capsule package 1.0.0;
- Governance API / PostgreSQL runtime / Admin UI.

## 5. Current roadmap

### Stage 0 — CASE 1 closure

Status: `DONE`.

Evidence:
- P12-S6 validated exit;
- CASE 1 run closed;
- no executable orphan CASE 1 task;
- external MCP items preserved as intake/history;
- GMC-A released.

### Stage 1 — current unique action / common Governance Model

```text
GMC-01 / GMC-G01
→ SEPARATE_GOVERNANCE_MODEL_FROM_APPLICATION_STRATEGIES
```

The detailed blueprint is already materialized. Current execution mode is planning/knowledge extraction only until a later governed step authorizes implementation.


```text
GMC-01 → ... → GMC-19
```

Outcome:
- common cross-case semantics;
- applicability/controls/evidence/failures/recovery catalogue;
- relational projection extension;
- model 1.0.0.

### Stage 2 — routing / architecture normalization
Key gates consumed by CAP:
- `RTE-012`: exact two-stage purpose routing/resume semantics;
- `ARCH-006`: cross-authority projection consistency;
- role/authority normalization via relevant ARCH/IDN tasks.

### Stage 3 — reusable capsule
```text
CAP-001 → ... → CAP-012
```

Outcome:
- stable public contract;
- adapters;
- persistence SPI;
- installer/upgrade/rollback;
- second clean repository LIVE proof;
- second/generic adapter LIVE proof;
- capsule 1.0.0.

### Stage 4 — remaining case industrialization / platform surfaces
- prove and enrich ADOPT;
- prove and enrich MAP;
- prove LAB;
- reconcile all four cases;
- Governance API;
- PostgreSQL if justified;
- Admin Web Application.

## 6. What to use and when

| Situation | Use |
|---|---|
| New physical agent/provider arrival | `00_GSCC_ENTRY.md` |
| Need whole-system orientation | `MASTER_SYSTEM_MAP.md` |
| Need exact current work | `CURRENT_STATE.md` + `NEXT_ACTION.md` |
| Need chronology/dependencies | `PROGRAM.md` + `TASKS.md` |
| Need target invariant | `CANONICAL_ARCHITECTURE.md` |
| Need questions/answers/resume data semantics | `DATA_MODEL.md` |
| Need reusable capsule contract | `GSCC_GSE_GACR_REUSABLE_CAPSULE.md` |
| Need decision rationale | `DECISIONS_LOG.md` |
| Need historical evolution | `SUIVI.md` |
| Need machine state | `.governance/control-plane-state/*` |
| Need relational validation | `.governance/control-plane-db/*` |

## 7. Definition of done for a capability

A capability is not DONE merely because code exists.

Minimum completion states:

```text
DOCUMENTED
→ IMPLEMENTED
→ STATIC/UNIT VALIDATED
→ INTEGRATION VALIDATED
→ LIVE PROVEN when transport/session/external behavior matters
→ RECONCILED INTO CURRENT/TASKS/HANDOFF
```

If a requirement has no appropriate proof, it remains PARTIAL/PLANNED.

## 8. Anti-forgetting rule

Whenever a new requirement, defect, owner correction or external dependency appears:

```text
classify
→ find existing architecture/program lineage
→ attach to existing task/integration slot
→ add decision/intake if needed
→ update traceability matrix if requirement status changes
→ validate CI
→ checkpoint/handoff
```

Never create an untracked parallel roadmap.

## 9. Roadmap authority note

This file summarizes the roadmap. The actual executable order remains:

- `PROGRAM.md`
- `TASKS.md` / `tasks.json`
- `NEXT_ACTION.md`

If this synthesis says a task is next but `NEXT_ACTION.md` disagrees, `NEXT_ACTION.md` wins until reconciliation.


### Stage 5 — deployable SaaS platform

```text
ARCH-008 / ARCH-009 / ARCH-010
+ IDN-013 / RTE-013
+ CAP-012
        ↓
SAA-001 → ... → SAA-015
        ↓
https://mcp.wealthtechinnovations.com/template
```

Outcome:
- full REST/OpenAPI backend;
- explicit microservice/service boundaries;
- PostgreSQL runtime;
- complete autonomous admin cockpit;
- governed operational actions;
- security/audit/observability;
- reproducible deployment;
- staging proof;
- production deployment;
- SaaS platform 1.0.0 operations/runbooks.
