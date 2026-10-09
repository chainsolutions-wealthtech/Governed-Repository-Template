# Canonical Agent Reconstruction Skeleton

Authority ID: `CP-AGENT-RECONSTRUCTION-001`

Status: `APPLICABLE / COMPOSITION_ONLY`

Machine-readable skeleton: `.governance/agent-reconstruction-skeleton.json`

Read-only reconstruction CLI: `scripts/gacr_agent_reconstruction.py`

## Purpose

This skeleton preserves the complete path needed to reconstruct a governed agent after a cold start, provider/context change, interrupted conversation, expired lease, handoff, or takeover.

It does **not** create a new identity system. It composes the authorities already present in the repository.

The owner concept called a **block** is represented here as a read-only `AGENT_RECONSTRUCTION_BLOCK` whose canonical key is the existing `logical_agent_id`.

No additional `block_id` is minted.

```text
AGENT_RECONSTRUCTION_BLOCK
  logical_agent_id
  ├─ owner aliases[]
  ├─ sessions[]
  │    ├─ provider/runtime contexts[]
  │    ├─ liveness / lease
  │    └─ control/wake surfaces
  ├─ continuity memberships[]
  │    ├─ coordination issue / bus
  │    ├─ participants / scopes
  │    └─ events / routes
  ├─ work links[]
  │    ├─ tasks
  │    ├─ work items
  │    ├─ collision domains
  │    ├─ offers / dispatches
  │    └─ canonical claims
  ├─ takeover / forensic evidence
  └─ checkpoint / handoff relationship
```

The block is a projection, not a new registry and not execution authority.

## Complete reusable path

```text
NEW PROVIDER / CHAT / RUNTIME SURFACE
        │
        ▼
00_GSCC_ENTRY.md
        │
        ├─ expose only actually observable facts
        ├─ unavailable provider-private facts = UNAVAILABLE
        └─ optional READ-ONLY historical reconstruction
                scripts/gacr_agent_reconstruction.py
                │
                └─ does NOT admit the current arrival
        │
        ▼
GSCC persisted entry
        │
        ├─ FIRST_TOUCH
        ├─ CONTINUATION
        └─ UNRESOLVED → fail closed
        │
        ▼
Q10 / GSE SessionTwin
        │
        ▼
Q2 / GACR durable binding
        │
        ├─ SAME_SESSION_RESUME
        ├─ NEW_PROVIDER_CONTEXT_SAME_LOGICAL_AGENT
        ├─ NEW_SESSION_SAME_LOGICAL_AGENT
        ├─ NEW_LOGICAL_AGENT
        └─ UNRESOLVED_SURFACE
        │
        ▼
logical_agent_id
        │
        ├─ N sessions
        ├─ N provider contexts
        └─ owner alias projection (when canonically assigned)
        │
        ▼
CONTINUITY BUS
        │
        ├─ continuity_id
        ├─ coordination issue
        ├─ scope / collision domains
        └─ B12 → B29 → POLL routing
        │
        ▼
WORK MATCHING
        │
        ├─ canonical READY work only
        ├─ logical-agent capacity aggregation
        └─ WORK_OFFER grants no write authority
        │
        ▼
CANONICAL CLAIM
        │
        └─ mutable work authority + exact-HEAD discipline
        │
        ▼
EVIDENCE / CHECKPOINT / FORENSICS
        │
        ▼
HANDOFF / TAKEOVER
        │
        ├─ preserve historical membership
        ├─ no synthetic heartbeat
        └─ zero-claim takeover grants no mutable work
        │
        ▼
EXIT / RELEASE
        │
        ├─ normal release → 00_START_HERE.md
        ├─ interruption → persist checkpoint/handoff
        └─ future surface → restart at 00_GSCC_ENTRY.md
```

## Cold-start usage

A newly opened conversation or provider surface may inspect historical context only after reading `00_GSCC_ENTRY.md`.

Examples:

```bash
python3 scripts/gacr_agent_reconstruction.py --alias FORGE
python3 scripts/gacr_agent_reconstruction.py --logical-agent-id GSCC-ID-b484944fc30fe55b88948f9f
python3 scripts/gacr_agent_reconstruction.py --session-id session-ba6f8db786eb9a8aa11865f2
```

All three selectors resolve the same block only when canonical state proves that relationship.

Alias resolution is fail-closed:
- unknown alias → reject;
- alias mapped to more than one logical agent → reject;
- session without canonical logical identity → reject.

## What reconstruction returns

The projection contains:
- canonical logical-agent identity and owner aliases;
- every known canonical session for that logical agent;
- stored provider/runtime contexts without inventing missing provider-private identifiers;
- continuity memberships and coordination bus references;
- task/work/collision links;
- canonical claims;
- pending/historical dispatches;
- takeover and forensic evidence;
- relevant beacon/correlation evidence;
- checkpoint/handoff relationship;
- source-store revisions;
- one recommended **safe re-entry action**.

The recommendation is navigational only.

## Authority separation

The following identities and authorities remain distinct:

`logical_agent_id != session_id != provider_context_id != continuity_id != task_id != claim_id != dispatch_id`.

And:

`RECONSTRUCTION != ADMISSION != SESSION_RESUME != CLAIM != MUTATION_AUTHORITY`.

A reconstructed historical block cannot prove that the **current chat** is the historical session.

The current arrival must still pass the canonical GSCC → GSE → GACR → F1 path.

## Communication bus

The skeleton does not create a new bus.

It reuses the continuity bus already defined by:
- `scripts/gacr_continuity_bus.py`;
- `scripts/gacr_continuity_coordination.py`;
- `docs/MULTI_AGENT_COORDINATION.md`;
- existing GACR dispatch/control stores.

The reconstruction output tells a future agent which `continuity_id`, coordination issue, session targets and routing surfaces already exist.

This permits agents to rediscover each other without a conversation transcript becoming the source of truth.

## Work and multiple agents

A logical agent may own multiple sessions and provider contexts, but they remain one default automatic capacity unit unless canonical policy explicitly says otherwise.

Different logical agents may receive independent work concurrently when:
- each work item is canonically READY;
- capabilities/roles match;
- collision domains do not conflict;
- the target session is eligible;
- pending offers/claims do not already consume capacity.

Only canonical claims grant mutable work authority.

## Exit contract

Every long-running agent should leave enough durable evidence for this reconstruction to work:
1. update canonical session/progress evidence through existing GACR paths;
2. persist checkpoint/handoff when applicable;
3. preserve exact HEAD/evidence references;
4. record work/claim/dispatch relationships through existing stores;
5. do not overwrite historical provider contexts;
6. never persist secrets, raw private transcripts or private reasoning;
7. leave one explicit next safe action.

The next provider/chat then begins again at `00_GSCC_ENTRY.md`, reconstructs history if useful, and proves its own current arrival independently.

## Relationship to the reusable capsule

`docs/control-plane/GSCC_GSE_GACR_REUSABLE_CAPSULE.md` remains the productization programme for extracting the pre-entry capsule to other repositories/platforms.

This skeleton is different: it is the **currently applicable in-repository composition map and read-only reconstruction projection** spanning pre-entry, continuity, work coordination, handoff and re-entry.

It does not advance or bypass the CAP programme dependencies.
