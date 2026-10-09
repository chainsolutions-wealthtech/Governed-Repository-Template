# SYSTEM DIRECTORY — Agents, Pôles, Objects, Buses and Owner Navigation

> **Human/operator navigation authority only — not a runtime authority**
>
> This document gives humans and agents one stable directory for the governed system.
> It links and explains existing canonical authorities without replacing them.
>
> Owner documentation intake: GitHub issue #270.
> Architecture continuation intake: GitHub issue #269.
> Master navigation: `docs/control-plane/MASTER_SYSTEM_MAP.md`.

## 1. Purpose

A cold-start agent or owner must be able to answer, without reconstructing the repository from chat history:

1. which named logical agents exist;
2. which sessions/provider contexts belong to them;
3. which pôle/group they belong to;
4. which objects and blocks exist;
5. which buses/routes can carry requests, wake/challenge or work offers;
6. where tasks/claims/collision domains live;
7. where checkpoints/handoffs/forensics live;
8. which front-end view will expose each concept.

This file is intentionally separate from runtime authority.

```text
DIRECTORY / DOCUMENTATION
!= IDENTITY AUTHORITY
!= SESSION AUTHORITY
!= LIVENESS
!= CLAIM
!= MUTATION AUTHORITY
```

Volatile state such as liveness, leases, current claims, dispatch state and exact capacity must be read from the current canonical GACR/control-plane stores.

## 2. Named logical-agent directory

Owner aliases are human selectors. They are not session IDs and never create authority.

| Alias | Canonical logical_agent_id | Historical reference session | Owner-facing responsibility |
|---|---|---|---|
| ATLAS | `GSCC-ID-16b1f46fbab319f97b7ec43f` | `session-1bb68ac942a69a77dfbb8d24` | architecture, analysis, programme/model cartography, central architecture link |
| FORGE | `GSCC-ID-b484944fc30fe55b88948f9f` | `session-ba6f8db786eb9a8aa11865f2` | bounded implementation, LAB integration, governed code changes |
| SENTINEL | `GSCC-ID-21df6eb30456b56be12144bf` | `session-3320926e66a52ff8f4396ed2` | supervision, coordination, liveness/collision/risk review |

Alias provenance: `OWNER_ASSIGNED`.

Reference sessions are historical anchors only. Their current liveness must be queried from GACR.

The shared historical continuity used by this three-agent lineage is:

`GRT-CONT-20261007-2117-GMC01-DSP258-01`

## 3. Identity hierarchy

```text
LOGICAL_AGENT
  logical_agent_id
  aliases[]
  |
  +-- SESSION[]
       session_id
       lease/liveness
       role/capabilities
       |
       +-- PROVIDER_CONTEXT / CHAT / RUNTIME_SURFACE[]
```

Rules:

```text
alias != logical_agent_id
logical_agent_id != session_id
session_id != provider conversation id
membership != liveness
liveness != work authority
transport reachability != mutation authority
```

A new chat does not imply a new logical agent.

## 4. Pôle vs Pool

### PÔLE — owner-facing coordination group

A pôle groups durable logical agents around an objective.

```text
PÔLE
  objective
  instructions
  logical_agents[]
  work/task references
  buses
  shared chronology
  checkpoints
```

The current owner-facing three-agent pôle is:

```text
                 ATLAS
          architecture / model
                 |
        +--------+--------+
        |                 |
      FORGE            SENTINEL
 implementation      supervision
        |                 |
        +--------+--------+
                 |
      shared objective / continuity
```

Pôle membership grants no claim or mutation authority.

### POOL — runtime capacity projection

A runtime pool answers: who is eligible for safe work now?

```text
READY WORK
+ logical-agent capacity
+ sessions/liveness
+ roles/capabilities
+ pending offers
+ claims
+ in-flight actions
+ collision domains
→ safe work offers
```

Several sessions/chats of one logical agent remain one default automatic capacity unit unless explicit canonical policy authorizes more.

## 5. Object directory

### Identity/runtime
- arrival;
- GSCC arrival/identity;
- human alias;
- logical agent;
- GSE SessionTwin;
- GACR session;
- connection;
- provider context;
- runtime/chat surface;
- provider-native conversation/session/thread reference when actually exposed.

### Coordination/continuity
- continuity;
- continuity participant;
- bus event/route;
- control command;
- ACK/response;
- liveness challenge;
- dispatch;
- checkpoint;
- handoff;
- takeover;
- forensic record;
- beacon/correlation.

### Work
- programme;
- work package;
- task/work item;
- work offer;
- canonical claim;
- collision domain;
- evidence;
- release/gate.

### Governed Block — planned composition layer

Issue #269 defines the next block abstraction as an envelope over existing canonical objects rather than an immediate new identity namespace.

Candidate block kinds:

- `AGENT_BLOCK` → key: `logical_agent_id`;
- `COORDINATION_BLOCK` → key: `continuity_id`;
- `WORK_PACKAGE_BLOCK` → key: existing `work_package_id`;
- `TASK_BLOCK` → key: task/work-item ID;
- `CAPACITY_POOL_BLOCK` → derived projection;
- future model blocks only where GMC/ARCH proves an independent identity is needed.

Reserved owner terminology such as `GWC` must not be minted into a canonical namespace until the Governance Model proves what new identity it represents.

## 6. Bus directory

### Entry/admission bus

```text
ARRIVAL
→ 00_GSCC_ENTRY
→ GSCC
→ GSE
→ GACR
→ F1
→ RELEASE
→ 00_START_HERE
```

Repository readability is not admission.

### B12 control channel

Used for bounded targeted control:
- request/instruction/review;
- status/context/progress request;
- ACK;
- liveness challenge;
- correlation/expiry/idempotency.

The GitHub issue-control bridge is a repository control surface, not a private provider callback.

### B29 registered external bridge

Used only when a real endpoint/bridge registration exists.

Never invent a provider callback endpoint.

### Polling fallback

When no verified direct route exists:

`B12 → B29 → POLL_REPOSITORY`.

### Continuity bus

Projects shared mission/continuity events. Membership never creates work authority.

### Work/dispatch bus

```text
READY task
→ deterministic offer
→ ACCEPT
→ canonical CLAIM
→ exact HEAD
→ execute
→ evidence/checkpoint/handoff
```

No second work queue is created.

### Planned composition buses

Issue #269 records:
- agent-to-agent;
- agent-to-block;
- block-to-block;
- agent-to-pool;
- coordination/supervision.

They must reuse existing control/continuity/dispatch stores.

## 7. Call / wake / resume directory

### Use an existing named agent

```text
"Je viens utiliser Forge"
→ read 00_GSCC_ENTRY
→ reconstruct alias FORGE read-only
→ classify CURRENT arrival
→ GSCC → GSE → GACR
→ SAME_SESSION_RESUME
   or NEW_PROVIDER_CONTEXT_SAME_LOGICAL_AGENT
   or NEW_SESSION_SAME_LOGICAL_AGENT
   or UNRESOLVED_SURFACE
```

Reconstruction alone is not admission.

### Create a new named agent

```text
"Crée l'agent Genesis"
→ FIRST_TOUCH
→ GSCC
→ GSE
→ GACR NEW_LOGICAL_AGENT
→ only after canonical identity exists:
   attach OWNER_ASSIGNED alias GENESIS
```

Never invent a logical-agent ID from the desired alias.

### Wake / ping

```text
target alias/logical agent
→ reconstruct
→ resolve exact routable session
→ B12 challenge/control
→ B29 when really registered
→ polling fallback
```

A wake request is not evidence that a provider-native chat woke.

### Heartbeat

A session/runtime surface emits heartbeat only for itself.

Synthetic heartbeat on behalf of another session is forbidden.

### Takeover/recovery

Persistent membership survives lease expiry.

A takeover may reconcile liveness and continuity. Mutable continuation requires recoverable canonical work authority/claim.

## 8. Queue and task directory

The owner-facing chronological queue is a projection of existing state:

```text
PROGRAMME
→ WORK PACKAGE
→ TASK GRAPH
→ READY
→ WORK_OFFER
→ ACCEPT
→ CLAIM
→ EXECUTE
→ RESULT
→ CHECKPOINT/HANDOFF
→ recompute
```

Do not create a second queue.

Pending non-terminal work offers consume logical-agent dispatch capacity across dispatcher runs.

## 9. Reconstruction directory

Canonical reconstruction foundation merged through PR #263:

- `.governance/agent-reconstruction-skeleton.json`;
- `docs/control-plane/AGENT_RECONSTRUCTION_SKELETON.md`;
- `scripts/gacr_agent_reconstruction.py`;
- GACR session/continuity/dispatch/claim/takeover/forensics/beacon state.

Invariant:

```text
RECONSTRUCTION
!= ADMISSION
!= SESSION_RESUME
!= CLAIM
!= MUTATION_AUTHORITY
```

## 10. Documentation conversation mode

Owner-facing documentation is a separate workflow.

Natural commands may include:

- `Document`;
- `Documente ce système`;
- `Ouvre la documentation de Forge`;
- `Ajoute cette réponse au dossier architecture`.

Target semantics:

```text
DOCUMENTATION SESSION
→ select subject
→ progressive owner Q&A
→ preserve notes/answers/provenance
→ keep draft separate from runtime authority
→ reconcile/publish into governed docs only when authorized
```

Documentation mode must not silently create claims, change liveness, dispatch work or convert an idea directly into executable policy.

## 11. Front-end projection

Product programme: `CP-SAAS-001`.

Target base URL:

`https://mcp.wealthtechinnovations.com/template`

Read-first navigation should include:

```text
/template/system
/template/agents
/template/agents/{logical_agent_id}
/template/poles
/template/poles/{pole_ref}
/template/sessions
/template/provider-contexts
/template/continuities
/template/blocks
/template/buses
/template/calls
/template/wake
/template/programmes
/template/tasks
/template/work-offers
/template/claims
/template/collisions
/template/checkpoints
/template/handoffs
/template/takeovers
/template/audit
/template/documentation
```

### Agent page
Show aliases, logical identity, sessions, provider contexts, continuities, pôle memberships, buses, work/claim references, checkpoint/handoff and reconstruction links.

### Pôle page
Show objective, member agents, instructions, task/work references, capacity, blockers/collisions, chronological queue view, buses and shared chronology.

### Bus page
Show source/target, route priority, transport, correlation, expiry, ACK/response, reachability evidence and fallback. Explicitly show that transport grants no authority.

### Documentation Center
Expose:
- Master System Map;
- this System Directory;
- canonical architecture;
- named-agent directory;
- object/block catalogue;
- bus/call/wake directory;
- owner documentation/Q&A sessions;
- decision/evidence chronology;
- source links and freshness/provenance.

First UI implementation should be read-only. Mutable controls must later call the same governed validators/gates as non-UI workflows.

## 12. Freshness and provenance

Static documentation may describe durable semantics and identifiers.

It must not freeze volatile operational state as permanent truth.

For current state, query:
- `CURRENT_STATE.md`;
- machine current/task state;
- GACR sessions/claims/dispatches/takeovers/forensics;
- exact repository HEAD;
- current checks/evidence.

Every front-end view should label facts as:
- canonical;
- derived/projection;
- planned;
- historical;
- live/volatile;
- unavailable.

## 13. Non-regression

- no second identity registry;
- no second task engine;
- no second queue;
- no second dispatch store;
- no second liveness authority;
- no alias-as-authority;
- no pôle-membership-as-authority;
- no transport-as-authority;
- no provider-private ID invention;
- no synthetic heartbeat;
- exact HEAD before mutation;
- cold-start reconstructible from persisted repository state;
- front-end remains a governed projection/control surface, never an independent source of truth.
