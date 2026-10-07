# Governance Platform SaaS / Admin Cockpit Programme

> Authority ID: `CP-SAAS-001`  
> Status: `PLANNED_DEPENDENCY_BOUND`  
> Scope: source/control-plane productization and deployment target

## 1. Product objective

Materialize the Governed Repository Platform as a deployable product with:

- a complete autonomous administration cockpit;
- a backend decomposed into governed microservice/service boundaries;
- a complete versioned REST API;
- PostgreSQL runtime projection while Git-versioned authorities remain foundational;
- background workers/event processing where required;
- full audit/evidence/continuity visibility;
- secure operational actions that reuse the existing authority/gate model;
- containerized/server deployment;
- SaaS-ready tenant/isolation model;
- production deployment target:

```text
https://mcp.wealthtechinnovations.com/template
```

The requested host is canonicalized as lowercase DNS host `mcp.wealthtechinnovations.com`; the application base path remains `/template`.

This programme productizes the already governed system. It MUST NOT create a second control plane, second session truth, second question database, or a UI-owned source of truth.

## 2. Dependency rule

Product UI/API work remains downstream of stabilized semantics.

```text
GMC-19
+ RTE-012
+ ARCH-006
+ IDN-006
   ↓
CAP-001..CAP-012
   +
ARCH-008 Governance API
ARCH-009 PostgreSQL projection
ARCH-010 Admin Web Application
IDN-013 Identity/session API/UI
RTE-013 Router API/UI
   ↓
SAA-001..SAA-015
   ↓
production SaaS deployment
```

Registration of this programme does not change the current unique executable task. `P12-S6` remains the only `IN_PROGRESS` global task.

## 3. Product architecture target

```text
Browser / Admin Cockpit
        ↓ HTTPS
Reverse proxy / TLS / base-path routing
        ↓
REST API Gateway / BFF
        ↓
┌────────────────────────────────────────────┐
│ Governed service boundaries               │
│                                            │
│ Identity / Session / Authority Service     │
│ GSCC / Admission / Exposure Service        │
│ GSE Session State Service                  │
│ GACR Continuity Service                    │
│ Programme / Task / Claim Service           │
│ Case / Run / Question Service              │
│ Evidence / Decision / Audit Service        │
│ Repository / Adapter Service               │
│ Knowledge / Infrastructure Service         │
│ Deployment / Upgrade Service               │
└────────────────────────────────────────────┘
        ↓
PostgreSQL runtime projection
+ object/artifact storage where justified
+ GitHub/Git canonical authorities
+ GitHub/provider/server adapters
```

Microservice boundaries may initially share a deployable runtime if that is safer and simpler, but service contracts, ownership and data boundaries must be explicit so they can be split independently. A distributed deployment MUST NOT be introduced merely for fashion or at the cost of transactional/governance correctness.

## 4. Complete REST API target

The backend must expose a versioned API under the product base path, conceptually:

`/template/api/v1/*`

Required resource families include at least:

- `/health`, `/ready`, `/version`;
- `/repositories`;
- `/arrivals`, `/identities`, `/connections`, `/sessions`;
- `/roles`, `/authorities`, `/access-grants`;
- `/gscc`, `/gse`, `/gacr`;
- `/cases`, `/runs`, `/phases`;
- `/questions`, `/answers`;
- `/programmes`, `/tasks`, `/claims`;
- `/decisions`, `/evidence`, `/events`;
- `/checkpoints`, `/handoffs`;
- `/intakes`, `/artifacts`;
- `/knowledge`, `/infrastructure`, `/capabilities`;
- `/adapters`, `/integrations`;
- `/deployments`, `/upgrades`, `/reconciliation`;
- `/audit`;
- `/admin/users`, `/admin/tenants`, `/admin/policies` when SaaS tenancy is enabled.

Mutation endpoints must call the same governed validators used by the underlying runtime. API possession or authenticated login never creates mutation authority.

OpenAPI must be generated/versioned and contract-tested.

## 5. Administration cockpit target

The cockpit must be operational, not a read-only demo.

Minimum views:

1. **Executive Overview**
   - system health;
   - active repositories;
   - active arrivals/sessions;
   - blocked gates;
   - pending owner decisions;
   - failed/stale evidence;
   - deployment status.

2. **Agents / Identity / Sessions**
   - GSCC arrivals;
   - identity correlation;
   - provider facts vs `UNAVAILABLE`;
   - GSE SessionTwins;
   - GACR sessions, leases, liveness, takeover state;
   - role and authority snapshots.

3. **Governance Cases / Runs**
   - CREATE / ADOPT / MAP / LAB;
   - run timeline;
   - current phase;
   - applicable questions;
   - answers and supersessions;
   - owner feedback/revalidation.

4. **Programme / Tasks / Claims**
   - global programme graph;
   - unique executable task;
   - dependencies;
   - collision domains;
   - claims;
   - current/blocked/planned/future status.

5. **Evidence / Decisions / Audit**
   - evidence freshness;
   - decisions and supersession;
   - canonical memory events;
   - audit/event history;
   - exact-HEAD provenance.

6. **Checkpoints / Handoffs / Continuity**
   - reconstructible resume state;
   - next action;
   - takeover/recovery controls;
   - stale/contradictory state warnings.

7. **Repositories / Integrations**
   - repository inventory;
   - provider adapters;
   - GitHub integration;
   - server/MCP capabilities;
   - deployment bindings.

8. **Knowledge / Infrastructure**
   - knowledge-base facts;
   - server/infrastructure observations;
   - freshness/provenance;
   - secret metadata only, never secret values.

9. **Deployment / Runtime Operations**
   - service health;
   - version;
   - migration state;
   - deployment history;
   - upgrade/rollback;
   - backup/restore evidence;
   - logs/metrics links.

10. **Administration / SaaS**
    - users;
    - tenants/workspaces when enabled;
    - role assignment;
    - policy configuration;
    - rate/quota controls if required;
    - feature/version compatibility.

Every mutable control must show the authority/gate being exercised and its expected effect before execution.

## 6. SaaS and tenancy requirements

The deployed product must be SaaS-ready even if first production is operated for one organization.

Required before multi-tenant release:

- tenant/workspace identity;
- tenant-scoped repositories, runs, sessions and evidence;
- strict authorization isolation;
- no cross-tenant state lookup by default;
- tenant-aware audit logs;
- tenant-aware rate/quota policy;
- encryption in transit;
- secrets external to Git/database payloads;
- backup/restore per defined recovery scope;
- data-retention and deletion policy;
- migration/version compatibility contract.

## 7. Security and authority

The web/API layer is a control surface, not an authority generator.

```text
AUTHENTICATION
!= ROLE
!= GOVERNANCE AUTHORITY
!= MUTATION AUTHORITY
```

All sensitive operations remain bound to:
- authenticated principal when available;
- current GSCC/GSE/GACR context;
- exact repository/branch/HEAD where applicable;
- current claim/collision state;
- policy;
- access grant;
- function exposure;
- explicit approval where required;
- auditable evidence.

## 8. Deployment target

Canonical target:

```text
scheme: https
host: mcp.wealthtechinnovations.com
base_path: /template
public_url: https://mcp.wealthtechinnovations.com/template
```

Target deployment must include:
- TLS;
- reverse proxy/base-path routing;
- container/runtime isolation;
- frontend;
- REST API/backend services;
- PostgreSQL when ARCH-009 is accepted;
- workers/background jobs if needed;
- health/readiness probes;
- structured logs;
- metrics/alerts;
- migration strategy;
- backup/restore;
- upgrade/rollback;
- environment/secret injection outside Git;
- CI/CD evidence;
- smoke/E2E validation.

Actual server/DNS/TLS/database mutation remains subject to the existing governed execution engine, server capability availability, exact observed infrastructure state and explicit mutation authority. Registering this target does not itself authorize production mutation.

## 9. Canonical tasks

| ID | Task | Exit gate |
|---|---|---|
| SAA-001 | Freeze SaaS product scope, tenancy model, deployment contract and NFRs | product contract accepted |
| SAA-002 | Define complete REST/OpenAPI v1 resource/action contract | OpenAPI + contract tests accepted |
| SAA-003 | Define backend service/microservice boundaries and ownership | service map + dependency rules accepted |
| SAA-004 | Bind authentication/RBAC to governance role/authority semantics | no auth→authority shortcut; tests pass |
| SAA-005 | Implement PostgreSQL runtime repositories/unit-of-work/migrations | deterministic parity/reconciliation passes |
| SAA-006 | Implement API gateway/backend services and event/background execution | integration suite passes |
| SAA-007 | Define cockpit IA/design system/navigation and admin action contracts | complete screen/action specification accepted |
| SAA-008 | Implement full read/monitor cockpit | all canonical domains observable |
| SAA-009 | Implement governed operational/admin actions | mutable actions pass authority/fail-closed tests |
| SAA-010 | Add audit, observability, security hardening and operational telemetry | security/ops acceptance passes |
| SAA-011 | Package frontend/backend/workers/DB integration for reproducible deployment | build/container/install reproducible |
| SAA-012 | Deploy and validate staging under production-equivalent base-path routing | staging E2E passes |
| SAA-013 | Governed production deployment to `https://mcp.wealthtechinnovations.com/template` | TLS/health/smoke/E2E PASS |
| SAA-014 | Full production acceptance: multi-agent, questions, four cases, continuity, admin ops | acceptance matrix green |
| SAA-015 | Release SaaS platform 1.0.0 with runbooks, backup/restore, upgrade/rollback | reproducible operations + release attestation |

## 10. Definition of done

The product is not complete because a dashboard renders.

Release 1.0.0 requires:
- frontend and backend both deployed;
- API documentation accessible and versioned;
- runtime state reconciles with canonical Git authorities;
- autonomous cockpit covers all core governance domains;
- mutating cockpit actions use real governance gates;
- fresh agent and continuation flows visible end-to-end;
- question/answer/history/resume visible and operational;
- four cases represented correctly;
- GACR continuity/takeover operational;
- staging and production deployment evidence;
- no secrets in Git/logs/API payloads;
- backup/restore tested;
- upgrade/rollback tested;
- observability/alerts operational;
- production URL smoke tested;
- CI/CD and exact release version attested.

## 11. Non-regression

This programme must reuse:
- CP-ARCH-001;
- CP-GOVMODEL-001;
- CP-CAPSULE-001;
- CP-EXECUTION-001;
- CP-AGENT-RELAY-001;
- DATA_MODEL;
- existing question/answer/session/evidence/task databases;
- existing policies and validators.

It must never fork those semantics into frontend-only or backend-only copies.
