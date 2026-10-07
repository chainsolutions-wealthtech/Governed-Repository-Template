# GSCC → GSE → GACR Reusable Capsule Productization

Authority ID: `CP-CAPSULE-001`

Status: `PLANNED_DEPENDENCY_BOUND`

## Purpose

Turn the LIVE-proven pre-entry chain:

```text
ARRIVAL
→ GSCC First Touch
→ Q1/Q3/Q4/Q5/Q8/Q9
→ Q10 / GSE
→ Q2 / GACR
→ Q6/Q7/Q11/Q12
→ F1
→ RELEASED_TO_NORMAL_GOVERNANCE
→ 00_START_HERE.md
```

into a reusable, versioned module that can be installed in repositories or agent platforms outside the full Governed-Repository-Template implementation.

The module MUST preserve the semantics already proven in LIVE acceptance. Productization is extraction and packaging, not a rewrite of the governance model.

## Programme dependency

The capsule productization programme is **downstream**, not parallel, to the global governance programme.

The completed `IDN-006` LIVE proof is the functional baseline. Productization execution remains blocked until the global model, routing and cross-authority consistency work that defines the post-capsule junction is stabilized.

```text
P12-S6 DONE
   ↓
GMC-19 DONE          governance model 1.0.0 / cross-case semantics
   +
RTE-012 DONE         two-stage purpose routing + exact resume semantics
   +
ARCH-006 DONE        cross-authority consistency enforcement
   +
IDN-006 DONE         LIVE GSCC→GSE→GACR→F1→release proof
   ↓
CAP-001
   ↓
...
   ↓
CAP-012
```

This prevents CAP from competing with `GMC-A` when `P12-S6` closes.

Registering or refining this programme does not change the unique executable action. Until every upstream dependency is satisfied, every `CAP-*` item remains `PLANNED`.

## Stable invariants

The reusable capsule MUST preserve all of the following:

1. one controlled arrival has one isolated GSCC arrival identity;
2. provider-private identity is supplied-only and is never fabricated;
3. unavailable facts remain explicit `UNAVAILABLE`;
4. two arrivals cannot collapse merely because actor, model or repository match;
5. continuation reuses only an exact/strongly correlated prior arrival;
6. state persistence is scoped per arrival;
7. Q9 requires a correlated ACK and fresh challenge response;
8. Q10/GSE precedes Q2/GACR;
9. GACR remains the durable continuity/session authority;
10. mutation authority is distinct from identity, admission, access and exposure;
11. F1 validates the actual requested governed function;
12. release to the normal repository workflow occurs only after exact F1 correlation;
13. ambiguity, stale evidence, conflicting identity or failed gates fail closed;
14. secrets, raw transcripts and private reasoning are never persisted.

## Mandatory post-capsule junction

The reusable capsule does **not** replace the repository's governed work router. Its terminal release hands the same arrival into the existing post-entry junction.

Canonical composition:

```text
ARRIVAL
→ GSCC
→ GSE
→ GACR
→ Q12
→ F1
→ exact RELEASE
→ 00_START_HERE.md
→ POST-CAPSULE JUNCTION
     │
     ├─ WHO / ROLE
     │    INTAKER | SUPERVISOR | CODE_AGENT | REVIEWER
     │
     ├─ AUTHORITY SNAPSHOT
     │    observed separately from role
     │
     ├─ CONNECTION INTENT
     │    OBSERVE | CONTEXT_INTAKE | INFORMATION_INTAKE
     │    | WORK_REQUEST | CODE_CHANGE | REVIEW | INFRASTRUCTURE
     │
     └─ ENTRY PURPOSE
          ├─ WORK_ON_CONTROL_PLANE
          │    ├─ CODE_IMPLEMENTATION
          │    ├─ EXECUTE_EXISTING_TASK
          │    └─ ADD_OR_ENRICH_INFORMATION
          │
          └─ APPLY_GOVERNANCE_CASE
               ├─ CREATE_NEW_REPOSITORY
               ├─ ADOPT_EXISTING_REPOSITORY
               ├─ MAP_EXISTING_PROJECT
               └─ LAB_EVOLUTION
```

The following dimensions MUST remain distinct:

`IDENTITY != ROLE != AUTHORITY != CONNECTION_INTENT != ENTRY_PURPOSE != WORK_KIND/CASE != ENTRY_ACTION != MUTATION_AUTHORITY`.

Existing lower-level entry-action policy remains authoritative for repository-local routing. In particular:
- `CONTINUE_GOVERNED_WORK` remains a valid existing governed-entry action;
- it is **not** a fifth structuring case;
- `UNKNOWN` on intent or entry action fails closed;
- role never grants authority;
- intent never grants authority;
- mutation requires its own applicable authority/gates.

The capsule release handoff must preserve or reference, without fabrication:
- `arrival_ref` / GSCC identity;
- GSE SessionTwin reference;
- canonical GACR session id;
- role classification and provenance when resolved;
- authority snapshot and provenance;
- exact repository/branch/HEAD;
- Access Grant / Q12 evidence;
- F1 exposure receipt;
- release receipt;
- unresolved junction fields as explicit `UNKNOWN` / `UNAVAILABLE`.

The post-capsule router then asks or resolves only the **missing** declaration needed for the current arrival. It must not replay First Touch or recreate the GACR session.

## Target module boundary

```text
capsule/
├── core/
│   ├── gscc/
│   ├── gse/
│   ├── gacr/
│   └── f1/
├── contracts/
├── persistence/
├── adapters/
│   ├── github/
│   └── generic/
├── install/
├── migrations/
├── tests/
└── docs/
```

This is a target packaging boundary, not permission to relocate working code before the CAP sequence authorizes it.

## Adapter contract

The core must not depend directly on one provider implementation. Adapters supply only the facts and actions they can legitimately expose.

Required adapter surfaces:

- provider/agent observation;
- repository observation;
- transport/control ingress;
- persistence backend;
- durable session binding;
- function-exposure integration;
- release target.

Provider adapters may expose different field sets. The core normalizes them through the canonical evidence/status model and never invents missing provider-private facts.

## Canonical tasks

| Task | Objective | Dependency | Exit gate |
|---|---|---|---|
| CAP-001 | Define reusable capsule boundary and public contract | GMC-19 + RTE-012 + ARCH-006 + IDN-006 | scope/non-goals/invariants + post-capsule junction contract accepted |
| CAP-002 | Inventory core vs Template/GitHub-specific coupling | CAP-001 | complete coupling map |
| CAP-003 | Freeze versioned public schemas and interfaces, including release→junction handoff | CAP-002 | compatibility-tested contract set preserving role/authority/intent/purpose separation |
| CAP-004 | Extract reusable core layout without semantic change | CAP-003 | existing LIVE path remains regression-green |
| CAP-005 | Define provider/repository/persistence/session adapter SPI | CAP-004 | reference adapter interface tests pass |
| CAP-006 | Refactor current GitHub/ChatGPT path into reference adapter | CAP-005 | same LIVE behavior through adapter |
| CAP-007 | Abstract persistence while preserving current SQLite/artifact implementation | CAP-006 | backend contract + current backend parity |
| CAP-008 | Add installer/upgrader/rollback/version compatibility mechanics | CAP-007 | clean install + upgrade + rollback tests |
| CAP-009 | Build portability/security/fail-closed regression matrix | CAP-008 | complete invariant matrix green, including post-release junction routing invariants |
| CAP-010 | Install on a second clean repository without full Template dependency | CAP-009 | fresh/continuation/multi-arrival LIVE proof plus correct handoff into agent-role/purpose junction |
| CAP-011 | Add and LIVE-prove a second/generic provider transport adapter | CAP-010 | cross-adapter semantic parity |
| CAP-012 | Release reusable capsule 1.0.0 and register it as a consumable component | CAP-011 | versioned release + docs + reproducible install |

## Acceptance criteria for 1.0.0

CAP-012 cannot be marked DONE until all of these are demonstrated:

- current Governed-Repository-Template flow remains green;
- second repository installation succeeds without importing source-only project memory;
- fresh arrival succeeds;
- same-arrival continuation succeeds;
- two simultaneous/different arrivals remain isolated;
- missing provider-private identity does not cause fabrication;
- Q9 replay/stale/mismatch tests fail closed;
- Q10→Q2 ordering is enforced;
- exactly one durable GACR session is bound for a successful arrival;
- Q12 and F1 remain function/authority bounded;
- release is exact-head and exact-session correlated;
- installer is idempotent;
- upgrade preserves runtime state;
- rollback does not silently destroy durable identity/session evidence;
- second adapter preserves the same core state-machine semantics.

## Downstream consumers

The reusable capsule is expected to feed:

- `IDN-013` future API/UI identity/session exposure;
- `RTE-013` future router API/UI;
- cross-case CREATE / ADOPT / MAP / LAB industrialization;
- future external repositories or agent platforms that need the same governed pre-entry capsule.

These downstream consumers do not become executable merely because CAP is registered.
