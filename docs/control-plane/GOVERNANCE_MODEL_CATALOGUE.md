# CANONICAL GOVERNANCE MODEL CATALOGUE

> Authority ID: `CP-GOVMODEL-001`  
> Authority type: `CANONICAL_GOVERNANCE_MODEL_CATALOGUE_PLAN`  
> Scope: `CONTROL_PLANE_SOURCE_ONLY`  
> Status: `ACCEPTED_TARGET_MODEL_CATALOGUE_PLAN`  
> Revision: `1`  
> Repository: `chainsolutions-wealthtech/Governed-Repository-Template`  
> Distribution: `SOURCE_ONLY / DO_NOT_COPY_TO_CLIENTS`

## 1. Purpose

The central governance model is the reference object. Repositories are targets where the model is instantiated, compared, mapped, extended or validated.

Canonical separation:

```text
GOVERNANCE MODEL
  -> architecture
  -> concepts
  -> domains
  -> capabilities
  -> components
  -> objects / fields / relationships
  -> contracts
  -> rules
  -> states / transitions
  -> workflows
  -> controls / gates
  -> authorities
  -> evidence
  -> failures / recoveries
  -> implementation mappings
  -> tests
  -> dependencies

APPLICATION STRATEGIES
  -> CREATE_NEW_REPOSITORY
  -> ADOPT_EXISTING_REPOSITORY
  -> MAP_EXISTING_PROJECT
  -> LAB_EVOLUTION
```

The four structuring cases consume the model. They do not define a parallel model.

## 2. Existing reusable foundation

The catalogue extends the existing control-plane memory. It does not create a second database or competing source of truth.

Existing source-only foundation:
- `.governance/control-plane-db/001_schema.sql`
- `.governance/control-plane-db/002_agent_activity.sql`
- `.governance/control-plane-db/003_canonical_authorities.sql`
- `.governance/control-plane-db/catalog.json`
- `.governance/control-plane-db/runtime-seed.json`
- `.governance/control-plane-db/materialize.py`
- `docs/control-plane/DATA_MODEL.md`
- `docs/control-plane/CANONICAL_ARCHITECTURE.md`

Canonical storage direction:

```text
Git-versioned governed authorities
+ versioned JSON catalogue/seed
+ additive SQL migrations
        ↓
existing deterministic materializer
        ↓
SQLite validation projection
        ↓
future PostgreSQL runtime projection
        ↓
future Governance API
        ↓
future Admin Web Application
```

No mutable database binary becomes canonical. No duplicate governance-memory subsystem is allowed.

## 3. Canonical anatomy

Every reusable governance element must be traceable through:

```text
DOMAIN
→ CAPABILITY
→ COMPONENT
→ OBJECT
→ FIELD / RELATIONSHIP
→ CONTRACT
→ STATE
→ TRANSITION
→ WORKFLOW
→ CONTROL
→ GATE
→ AUTHORITY
→ EVIDENCE TYPE
→ FAILURE / RECOVERY
→ IMPLEMENTATION ARTIFACT
→ TEST
→ DEPENDENCY
```

A component is not a file. A file is an implementation artifact for one or more components.

## 4. Canonical registries to materialize

The relational catalogue must eventually represent, at minimum:
1. Domain Registry
2. Capability Registry
3. Component Registry
4. Object Registry
5. Field Registry
6. Relationship Registry
7. State Registry
8. Transition Registry
9. Workflow Registry
10. Control Registry
11. Gate Registry
12. Authority Registry
13. Evidence Type Registry
14. Failure Registry
15. Recovery Registry
16. Implementation Registry
17. Test Registry
18. Dependency Registry

These are views of one governance model, not 18 independent sources of truth.

## 5. Semantic comparison contract

Repository comparison is semantic, not filename-only.

Canonical classifications:

- `PRESENT_EXACT`
- `PRESENT_EQUIVALENT`
- `PRESENT_PARTIAL`
- `ABSENT`
- `CONFLICT`
- `OBSOLETE`
- `UNKNOWN`
- `NOT_APPLICABLE`

Canonical actions:

- `PRESENT_EXACT -> REUSE`
- `PRESENT_EQUIVALENT -> MAP_REUSE`
- `PRESENT_PARTIAL -> EXTEND`
- `ABSENT -> ADD`
- `CONFLICT -> HOLD_FOR_REVIEW`
- `OBSOLETE -> MIGRATE_COMPATIBLY`
- `UNKNOWN -> DISCOVER`
- `NOT_APPLICABLE -> SKIP`

Comparison must be able to descend through domain, capability, component, object, field, control and test.

## 6. Applicability contract

Not every governance component is mandatory for every project.

Canonical applicability classes:

- `MANDATORY`
- `OPTIONAL`
- `CONDITIONAL`
- `NOT_APPLICABLE`

The applicable model is resolved before CREATE or ADOPT materialization.

## 7. Hierarchical work programme

This programme is accepted into canonical backlog now, but it must not replace the current unique executable CASE 1 task. Execution begins only when its dependencies allow it.

### Phase A — Establish the central model boundary

- `GMC-01` Separate central model from application strategies.
- `GMC-02` Define the canonical anatomy/metamodel and stable identifiers.

### Phase B — Inventory and normalize the model

- `GMC-03` Inventory and normalize all governance domains.
- `GMC-04` Inventory all capabilities per domain.
- `GMC-05` Decompose capabilities into reusable components.
- `GMC-06` Inventory objects, fields and relationships.

### Phase C — Formalize behaviour and assurance

- `GMC-07` Inventory state machines.
- `GMC-08` Inventory legal/illegal transitions.
- `GMC-09` Inventory controls and their PASS/FAIL semantics.
- `GMC-10` Inventory gates and STOP/GO/HOLD semantics.
- `GMC-11` Inventory evidence types and freshness/validity rules.

### Phase D — Bind the abstract model to the implementation

- `GMC-12` Map model elements to current implementation artifacts.
- `GMC-13` Build the global dependency graph and installation order.
- `GMC-16` Materialize the canonical registries in the existing relational model using the next additive migration and existing materializer.

### Phase E — Build reusable comparison machinery

- `GMC-14` Build the semantic model-to-repository comparison contract/engine.
- `GMC-15` Extend comparison to object/field/control/test level.

### Phase F — Make the Control Plane consume the model

- `GMC-17` Make the central Control Plane load and validate the canonical governance model.
- `GMC-18` Rebind CREATE / ADOPT / MAP / LAB to the shared model and applicability engine.

### Phase G — Cross-case validation and release

- `GMC-19` Execute cross-case validation, reconcile common patterns, close gaps and freeze the first complete Governance Model release.

## 8. Detailed execution requirements for GMC-01..GMC-19

### GMC-01 — Model / strategy separation
- classify every current authority, rule, workflow and artifact as model-level, application-strategy-level, runtime/execution-level or projection;
- detect rules currently embedded only inside one case;
- move generic semantics into the model without changing current runtime behaviour;
- prove the four cases reference rather than redefine common semantics.

### GMC-02 — Canonical anatomy
- define identifiers and contracts for domain/capability/component/object/field/relationship/state/transition/workflow/control/gate/evidence/implementation/test/dependency;
- define cross-reference rules;
- add validation for invalid or dangling references.

### GMC-03 — Domains
- observe the live repository and establish the factual domain list;
- preserve provenance to source files;
- distinguish implemented, partial, planned and future domains.

### GMC-04 — Capabilities
- enumerate capability inputs, outputs, preconditions, dependencies, applicability and status;
- associate each capability with domains and components.

### GMC-05 — Components
- define each component responsibility and interfaces;
- identify duplicates, overlaps, missing components and partial implementations.

### GMC-06 — Objects / fields / relationships
- enumerate governed objects and schemas;
- map fields, types, cardinality, mutability, allowed values and authority;
- map object relationships and integrity constraints.

### GMC-07 — States
- enumerate stateful objects and all initial/intermediate/terminal/error/unknown states;
- define evidence required to claim each state.

### GMC-08 — Transitions
- define FROM/TO, trigger, actor, authority, preconditions, action, postconditions, evidence, failure and recovery;
- catalogue forbidden transitions.

### GMC-09 — Controls
- extract controls from Markdown, JSON, schemas, Python and workflows;
- assign stable IDs;
- record scope, severity, PASS/FAIL, failure behaviour, implementation and tests.

### GMC-10 — Gates
- formalize write, dispatch, bootstrap, adoption, infrastructure, deployment, merge and attestation gates;
- map required controls and fail-closed behaviour.

### GMC-11 — Evidence
- formalize evidence types, producers, subjects, freshness, invalidation and retention;
- distinguish evidence type from concrete evidence record.

### GMC-12 — Implementation mapping
- map abstract model elements bidirectionally to current Markdown, JSON, schema, Python, workflow, SQL and test artifacts;
- detect unimplemented components and orphan artifacts.

### GMC-13 — Dependency graph
- build dependencies across domains, capabilities, components, workflows, controls, gates, artifacts and tests;
- calculate integration order and detect cycles.

### GMC-14 — Semantic comparator
- compare model semantics against target repository observations;
- emit canonical compatibility classification, gap, risk, action and evidence;
- never classify solely from filenames.

### GMC-15 — Fine-grained comparison
- compare object fields, aliases, constraints, lifecycle, authority and proof semantics;
- support `PRESENT_EQUIVALENT` for structurally different but functionally equivalent implementations.

### GMC-16 — Canonical relational materialization
- add the next additive SQL migration for governance-model catalogue tables;
- extend versioned JSON catalogue/seed as needed;
- extend the existing `materialize.py`;
- add schema/foreign-key/reference validation;
- never add a second database/materializer.

### GMC-17 — Control Plane integration
- add Governance Model authority loading and version selection;
- validate the model before case dispatch;
- persist model version used by each future case run.

### GMC-18 — Rebind the four cases
- CREATE: applicability -> instantiate -> verify -> attest;
- ADOPT: inventory -> semantic comparison -> gap/conflict -> additive integration -> verify;
- MAP: observe -> semantic mapping -> gap map, read-only;
- LAB: model/current baseline -> candidate -> compare -> regression -> release.

### GMC-19 — Cross-case release
- finish and test CASE 2, CASE 3 and CASE 4 against the shared model;
- reconcile patterns common to all four cases;
- complete identity/session and two-stage routing integration where required by the model;
- establish Governance Model version `1.0.0` only after cross-case evidence is complete;
- keep PostgreSQL/API/Admin UI downstream of workflow/model stabilization.

## 9. Priority and dependency policy

Current execution priority is unchanged:

```text
C1-12-J-C
→ remaining C1-12 normal-entry proof
→ P12-S5 second fresh repository E2E
→ P12-S6 close CASE 1
→ Governance Model Catalogue execution
→ CASE 2 / CASE 3 / CASE 4 using the shared model
→ cross-case reconciliation
→ Governance Model 1.0.0
→ PostgreSQL / Governance API / Admin UI
```

Knowledge capture for this authority is allowed now and is not considered a bypass of CASE 1 gates.

## 10. Existing planned work absorbed, not duplicated

The existing `ARCH-*`, `IDN-*` and `RTE-*` backlogs remain valid.

They are integrated as dependencies or sub-workstreams:
- `ARCH-004..007` feed assurance/model validation;
- `IDN-001..012` feed identity/authority/session model completeness;
- `RTE-001..012` feed entry/routing model completeness;
- `ARCH-008..010` remain downstream future API/PostgreSQL/UI work.

No duplicate parallel backlog is created.

## 11. Completion definition

The catalogue is complete only when the system can answer from versioned authorities, without relying on conversation history:

- what the governance model contains;
- where every component is implemented;
- which controls protect it;
- which tests prove it;
- how components depend on one another;
- which parts apply to a target repository;
- what a target already has exactly/equivalently/partially;
- what is absent, conflicting, obsolete or unknown;
- what may safely be added without destroying existing behaviour;
- in what order integration must occur;
- what evidence proves successful integration.

## 12. Execution blueprint

The 19 catalogue items are work packages, not atomic tasks.

Detailed mission decomposition is maintained in:

`docs/control-plane/GOVERNANCE_MODEL_EXECUTION_BLUEPRINT.md`

with machine projection:

`.governance/control-plane-state/governance-model-execution-blueprint.json`

The blueprint defines, for every group:

- mission/objective;
- research questions;
- exact source surfaces and search patterns;
- atomic tasks;
- expected results;
- storage targets;
- evidence;
- DONE/HOLD criteria;
- downstream consumers.

It is `PLANNING_ONLY`: it prepares implementation but does not authorize registry/schema/SQL/comparator/runtime creation.

## 13. Output-driven work-package contract

The catalogue execution programme is a knowledge-production pipeline, not a list of status flags.

For every work package:

```text
validated task dependency
+ validated artifact dependency
+ satisfied evidence dependency
+ exit controls PASS
= downstream unlock
```

Results are modeled as persistent versioned knowledge artifacts with:
- stable artifact ID;
- producer work package;
- validation state;
- provenance requirement;
- planned initial version;
- downstream consumers;
- append/supersede/revalidate history.

The detailed authority is `docs/control-plane/GOVERNANCE_MODEL_EXECUTION_BLUEPRINT.md` and its machine projection.

The final GMC-G19 assembly must include the complete Domain / Capability / Component / Object / Field / Relationship / State / Transition / Workflow / Control / Gate / Authority / Evidence Type / Failure / Recovery / Implementation / Test / Dependency registries plus Applicability / Comparison / Integration / Release contracts.

Governance Model `1.0.0` is forbidden until the final assembly separately proves completeness, consistency, reference integrity, implementation traceability, test coverage, evidence coverage, dependency integrity, reusability and compatibility with CREATE / ADOPT / MAP / LAB.
