# MULTI_AGENT_COORDINATION — Generic policy

## Canonical hierarchy

```text
PROJECT
  ↓
PHASE / OBJECTIVE
  ↓
WORK ITEM
  ↓
SESSION
  ↓
ACTION
  ↓
EVIDENCE
  ↓
CHECKPOINT
  ↓
HANDOFF
  ↓
NEXT_ACTION
```

A session never replaces the work item and a work item never replaces project authority.

## Online HEAD is the coordination clock

Before every mutable action, observe the exact online/current HEAD.

If the prepared write was based on another HEAD:

```text
HEAD_MOVED
→ STOP_WRITE
→ REOBSERVE
→ READ_INTERVENING_CHANGE
→ RECONCILE
→ RECOMPUTE
→ VERIFY
→ WRITE
```

Force push, reset-to-old-head and stale overwrite are forbidden.

## Sessions

Only identifiers actually observed may be recorded as provider identifiers.

If a provider conversation identifier is unavailable:

```text
provider_conversation_ref = null
provider_conversation_ref_provenance = UNAVAILABLE
```

Never synthesize a fake provider identifier.

## Connection intent before work claims

A session declares why it is connected before mutable work is dispatched.

```text
OBSERVE / REVIEW
  → no mutable dispatch by default

CONTEXT_INTAKE / INFORMATION_INTAKE
  → intake route
  → no code claim

WORK_REQUEST / CODE_CHANGE
  → eligible for governed dispatch

INFRASTRUCTURE
  → infrastructure discovery
  → governed dispatch only with separate authority

UNKNOWN
  → RESOLVE_CONNECTION_INTENT
```

Intent is a routing fact, not an authorization.

## Work claims

Multiple readers/reviewers are allowed.

Only one writer may own an overlapping collision domain at a time.

Claims are repository coordination records only. They are not server locks, runtime task queues or external authorization.

## Dispatch

A work item may be assigned only when:

1. status is `READY`;
2. dependencies are `DONE`;
3. no foreign active claim occupies one of its collision domains.

Selection is deterministic by priority, sequence and ID.

## Checkpoints and handoff

Meaningful work boundaries should persist a machine-readable checkpoint. A yielding writer releases its claims and writes a handoff with the exact observed HEAD and unique next action.


## Control plane coordination

A Governed Request has one persisted state machine revision at a time. GitHub Actions concurrency serializes updates for a request issue.

Multiple agents may contribute observations/evidence only through the same request state. No agent may skip ahead to a later preparatory action. The next action is determined by the persisted request revision, not by conversation memory.

Once `HANDOFF_READY` is emitted, repository-local session/claim/collision-domain coordination resumes on the target repository.

## GACR — Governed Agent Continuity Relay

GACR is the reusable continuity/failover layer for long-running agent work.

It extends the existing session/claim/checkpoint/handoff model:

```text
SESSION
→ HEARTBEAT / LEASE
→ ACTIVE CLAIM
→ SUPERVISOR SCAN
→ SUSPECTED_STALL
→ STALLED
→ TAKEOVER_READY
→ STANDBY OFFER
→ EXACT-HEAD RECONCILIATION
→ CLAIM TRANSFER
→ CONTINUE
```

A stalled session keeps its active claim until takeover acceptance. This prevents two writers from acting on the same collision domain.

External provider conversation references may be attached only when actually supplied. They are correlation metadata; the governed session ID remains canonical.

An arbitrary browser conversation cannot be universally awakened by GitHub. GACR therefore persists a takeover offer that a standby agent or external orchestrator can consume deterministically.

## GACR source/client boundary

The central Template's GACR runtime records are source-only control-plane memory. Target repositories maintain their own GACR runtime state.

This prevents a conversation, claim or takeover belonging to framework development from leaking into a project created or upgraded from the Template.

## GACR client liveness

R5 distinguishes repository transport from actual client provenance.

A heartbeat arriving through GitHub Actions may still carry `source=CLIENT_EMITTER` when the originating agent/client sent it.

The client emitter may maintain liveness and publish traces, but it never owns claims and cannot accept takeover automatically.

```text
CLIENT_EMITTER
→ heartbeat / trace
→ repository GACR state
→ WATCH / FORENSICS
→ wake poll
→ human/agent exact-HEAD reconciliation
→ takeover-accept
```

If the emitter stops without an explicit interruption signal, WATCH treats the missing heartbeat as absence only; Forensics must not infer a provider or network cause.


## Capacity-aware parallel dispatch

GACR R7 adds a dispatcher view of agents that are actually available for new work.

Use the existing work-item and claim model. Do not create a separate queue.

An agent can be observed as:
- `AVAILABLE` / `WAITING` — eligible if liveness and claim checks pass;
- `BUSY` — current claim or in-flight action;
- `BLOCKED` — explicit dependency/input/context block;
- `RATE_LIMITED` — provider rate limit explicitly observed;
- `QUOTA_BLOCKED` — provider quota exhaustion explicitly observed;
- `STALLED`, `TERMINAL`, `UNKNOWN` — not eligible for new work.

Parallel allocation is legal only for dependency-safe, collision-free work. Two tasks sharing a collision domain are never offered concurrently, even when two agents are idle.

```text
WAITING AGENTS
+ READY TASKS
+ DEPENDENCIES
+ CLAIMS
+ COLLISION DOMAINS
+ CAPABILITIES / ROLE / AUTHORITY
→ SAFE WORK OFFERS
→ ACCEPTANCE
→ CLAIM
→ EXACT HEAD
→ EXECUTE
```

A work offer is a scheduling proposal, not work ownership and not mutation authority.


## R8 — F1-gated declaration-driven dispatch

A connected agent does not enter the new-work pool merely because a GACR session exists.

For the source Control Plane:

```text
GSCC → GSE → GACR → Q12 → F1 → RELEASE
                                  ↓
                         F1_RELEASED beacon
                                  +
                         explicit declaration
                         ROLE + AVAILABILITY
                                  ↓
                         CAPACITY POOL
                                  ↓
                 canonical global task graph
                                  ↓
                      safe WORK_OFFER
                                  ↓
                         ACCEPTANCE
                                  ↓
                            CLAIM
                                  ↓
                         EXACT HEAD
                                  ↓
                          EXECUTION
```

Canonical role behavior:
- `CODE_AGENT` — may receive compatible executable/planning work offers;
- `INTAKER` — contributes context/information through intake routes and is not treated as a code worker merely because it is available;
- `SUPERVISOR` — observes/coordinates pool, blocks, collisions and recovery; mutable execution still requires a compatible claimed task and authority;
- `REVIEWER` — receives review work only when the canonical work item explicitly allows the reviewer role.

The role is a routing attribute, never mutation authority.

The source Control Plane does not dispatch from `.governance/work/work-items.json` when that surface is only generic bootstrap state. It projects the currently released global programme/work package. Unsupported or ambiguous global task state fails closed with no offer.


## Shared continuity coordination projection

GACR may maintain an additive, machine-readable coordination projection keyed by a stable `continuity_id` when several governed sessions contribute to the same long-running objective.

This projection is deliberately **not** a task authority, claim authority, mutation grant, queue, dispatcher or second source of truth.

```text
CANONICAL TASK / AUTHORITY
+ GACR SESSION / CLAIM / COLLISION DOMAIN
+ EXACT HEAD
+ SHARED CONTINUITY PROJECTION
→ SAFE PARALLEL COORDINATION
```

Before a session declares a work scope under a shared continuity ID it must provide:
- the canonical GACR session ID;
- the shared `continuity_id`;
- a receipt/reference proving the latest shared coordination state was read;
- the exact observed repository HEAD;
- an explicit `scope_id`;
- `READ_ONLY`, `WRITE` or `REVIEW` coordination mode;
- explicit collision domains;
- its declared role as routing metadata when known.

The projection enforces:
- a stalled or takeover-ready predecessor cannot silently resume;
- stale HEAD declarations fail closed;
- the same scope cannot be independently occupied by two sessions;
- overlapping `WRITE` collision domains fail closed;
- a foreign active canonical claim on an overlapping collision domain rejects a `WRITE` declaration;
- yielding a coordination scope records a handoff but never transfers or releases a canonical claim.

The stored projection carries explicit negative authority facts:

```text
grants_task_authority = false
grants_claim = false
grants_mutation_authority = false
```

Canonical authority remains in the existing source/program/task/claim/approval gates. The projection only prevents agents sharing a continuity ID from losing the thread or acting on overlapping scopes.

For the source Control Plane, runtime projection state is source-only under `.governance/control-plane-state/`. Instantiated repositories use their repository-local `.governance/agent-relay/` projection. These stores must never be confused or copied as live source runtime state.


## Push-first shared continuity bus

The shared continuity projection may carry bounded model-to-model coordination events. It remains a projection only and does not become a second dispatcher, queue, task authority, session authority or mutation grant.

The delivery preference is:

PUSH-capable external bridge when the target session explicitly advertises EXTERNAL_BRIDGE and a bridge registration exists; otherwise POLL_REPOSITORY fallback.

A continuity event never refreshes another session's heartbeat. ACK/RESPONSE emitted by a session may count only as evidence of that emitting session's own activity.

The derived event lifecycle is:

CREATED/ROUTED -> DELIVERED -> ACKED -> RESPONDED

with failure/recovery states FALLBACK_POLL_REQUIRED, ACK_TIMEOUT and EXPIRED.

The mini-loop only updates derived delivery state and reuses the existing GACR dispatch store. It grants no task, claim or mutation authority. Exact-HEAD and declared continuity scope remain mandatory before emission.


## Early supervision without lease mutation

The continuity mini-loop may emit a derived early-supervision alert when an ACTIVE continuity participant has no fresh session signal for 120 seconds.

This alert is intentionally earlier than the canonical GACR suspected-stall/stalled thresholds. It is observational only:

- it does not change session status;
- it does not shorten, extend or refresh the canonical lease;
- it does not create a claim or task authority;
- it does not trigger takeover;
- it reuses the existing GACR dispatch store;
- it prefers EXTERNAL_BRIDGE only when a real registered bridge exists, otherwise it records POLL_REPOSITORY fallback;
- it is deduplicated until a fresh signal resolves it or canonical GACR liveness state supersedes it.

Canonical STALLED / TAKEOVER_READY remains exclusively owned by existing GACR rules.


## Persistent continuity membership and provider endpoint truth

Continuity membership is durable and must not be conflated with heartbeat freshness.

```text
membership_state = PERSISTENT
liveness_state   = LIVE / QUIET / SUSPECTED_STALL / STALLED / UNREACHABLE / UNKNOWN
```

Lease expiry changes liveness evidence only. It does not delete the canonical GACR session, remove continuity membership, transfer authority or create a new session. A yielded scope also remains part of the durable continuity history. Terminal membership requires an explicit governed terminal/supersession event.

Each continuity participant may carry a derived `provider_endpoint` descriptor. This descriptor is capability-truthful:

- a real registered `EXTERNAL_BRIDGE` is `OBSERVED` and may be used for PUSH;
- a provider-private callback/conversation endpoint that is not exposed is `UNAVAILABLE`;
- ChatGPT's repository-side issue control channel may be recorded as a proven repository control surface when the existing live proof is configured, but it is not misrepresented as a private ChatGPT callback;
- without a real inbound endpoint, wake delivery remains `POLL_REPOSITORY`;
- provider conversation references are persisted only when actually supplied;
- no provider URL, conversation ID or endpoint is synthesized.

The endpoint descriptor is a derived projection of the canonical session/bridge facts. It is not a second endpoint registry or authority source.


## Logical agent, sessions and provider contexts

The continuity projection distinguishes four identities that MUST NOT be collapsed:

```text
logical_agent_id
  -> 1..N canonical GACR session_id
       -> 1..N provider/runtime contexts over time
            -> provider-native conversation/session references only when actually observed
```

The current canonical source for `logical_agent_id` is the existing GACR session
`agent_identity`. The continuity layer only projects and groups that authority; it does
not create a second agent registry or grant claims, task authority, or mutation authority.

A provider context is a typed projection of canonical session facts such as provider,
`provider_conversation_ref`, `client_instance_id`, `connection_ref`, and observable
repository-surface evidence. Its `provider_context_id` is repository-derived and MUST
NOT be represented as a provider-native ChatGPT/Claude/Codex conversation identifier.
Unknown provider-private identifiers remain `UNAVAILABLE`.

This permits `NEW_SESSION_SAME_LOGICAL_AGENT` without implying
`NEW_LOGICAL_AGENT`: multiple sessions with the same canonical `agent_identity` are
grouped under one logical agent while their leases, liveness, claims, collision domains,
and takeover state remain session-scoped.

### Continuity delivery priority

Continuity delivery reuses existing control surfaces in this order:

```text
1. GSCC_CONTROL_CHANNEL (B12; verified repository control transport / SessionEndpoint)
2. EXTERNAL_BRIDGE (B29; only with a real registered bridge)
3. POLL_REPOSITORY (durable final fallback)
```

The GitHub issue control channel is a repository control surface, not a private provider
callback. Continuity requests/instructions/review requests are delivered as bounded
`SUPERVISOR_INSTRUCTION` commands; early supervision uses
`LIVENESS_CHALLENGE`. Neither path grants mutation authority or synthesizes heartbeat.
A fresh challenge response may prove liveness through the existing GACR host-ingress
rules; silence never does.


### Governed creation of another session for the same logical agent

A new stable runtime/chat/provider surface MUST NOT be grouped under an existing
`agent_identity` merely because a client repeats the same agent string.

For a new connection, GACR distinguishes:

```text
same agent_identity claimed + new stable anchor + no canonical continuity proof
→ UNBOUND_ACTIVITY
→ LOGICAL_AGENT_REUSE_REQUIRES_EXPLICIT_CONTINUITY_PROOF

same agent_identity
+ explicit reference_session_id
+ continuity_id
+ exact canonical evidence_ref already present in continuity / forensics / beacon state
+ distinct unowned connection_ref
→ NEW_SESSION_SAME_LOGICAL_AGENT
```

The new session may use another provider or another chat/runtime surface, but it does
not inherit a claim, mutation authority, liveness, lease, or accepted takeover from the
reference session. A stalled/takeover-ready reference remains stalled until the existing
governed takeover/reconciliation machinery explicitly resolves it.

Repository-minted runtime surface identifiers are allowed only as typed repository
identifiers with repository provenance. They MUST NOT be relabeled as provider-native
conversation/session identifiers.


### Identity-resolution result classes and provider-context history

Presence correlation reports an explicit identity-resolution class independently from
the lower-level session operation: `NEW_LOGICAL_AGENT`, `SAME_SESSION_RESUME`,
`NEW_PROVIDER_CONTEXT_SAME_LOGICAL_AGENT`, `NEW_SESSION_SAME_LOGICAL_AGENT`,
or `UNRESOLVED_SURFACE`.

A canonical session may retain multiple `provider_contexts[]`. This is additive
history inside the existing session record, not a new identity registry. Each context
keeps its own connection/runtime surface and, when actually supplied, separate connector
facts such as connector app id, public client id, installation id and connector slug.
Provider-native conversation references remain separate fields and remain `UNAVAILABLE`
when the provider does not expose them.


### Logical-agent capacity aggregation

Capacity dispatch does not treat every canonical session as an automatically independent
worker when several sessions belong to the same logical agent.

The capacity key is derived only from canonical GACR identity evidence:

```text
session.logical_agent_id
or session.agent_identity
→ shared logical-agent capacity key

no canonical logical identity
→ session-local capacity key
```

Provider family, GitHub actor, connector app/installation, repository, continuity ID, or
runtime surface alone never establish logical-agent sameness.

Claims and leases remain session-scoped. However, for automatic work offers, sibling
sessions sharing one canonical logical-agent identity also share the existing automatic
parallel-offer ceiling. An active claim, in-flight action, or non-terminal persisted work offer
(`READY` / `ACCEPTED_PENDING_CLAIM`) on one sibling therefore consumes
logical-agent automatic capacity and cannot be bypassed by opening another chat/runtime
session or by waiting for a later dispatcher run. The same ready work item also cannot
receive a second concurrent pending offer on another logical agent.

Pending offers are read from the existing canonical GACR dispatch store. Terminal or
cancelled offers release this derived capacity; once a canonical claim is activated, the
claim path remains the work authority. Work-offer acceptance revalidates sibling claims,
in-flight activity, and other pending offers before changing offer state.

The dispatcher may still choose the compatible sibling session whose declared
role/capabilities fit a work item; this aggregation grants no claim, mutation authority,
new queue, or provider-level limit inference.


## Owner-assigned logical-agent alias routing

Owner-assigned aliases such as `ATLAS`, `FORGE`, and `SENTINEL` are stable
human-facing labels on the existing logical-agent continuity projection. Their
provenance is `OWNER_ASSIGNED`. They are not session IDs, provider identities,
roles, claims, leases, liveness evidence, or authority tokens.

A fresh provider arrival may carry `logical_agent_alias` only as non-authoritative
entry intent. The canonical route is:

```text
Provider First Touch
  -> GSCC observable packet
  -> GSCC admission / control proof
  -> Q10_GSE retains requested_logical_agent_alias
       resolution = GACR_Q2_REQUIRED
       grants_authority = false
  -> Q2_GACR resolves alias from gacr-continuities.json
  -> exactly one canonical logical_agent_id
  -> canonical sessions + provider/runtime contexts
  -> exact active session only when uniquely routable
  -> remaining Q6/Q7/Q11/Q12/F1 gates
```

The alias never bypasses GSCC or GSE. Unknown aliases fail closed. The same alias
mapped to multiple logical-agent IDs fails closed. A logical agent with multiple active
canonical sessions is `AMBIGUOUS_ACTIVE_SESSIONS` for alias-targeted routing and no
session is selected.

An alias can validate an already correlated session only when that session's canonical
`logical_agent_id/agent_identity` equals the alias resolution. The alias alone does
not prove that a brand-new provider/chat/runtime surface belongs to the logical agent.
Creating another session or attaching an unresolved surface still requires the separate
canonical same-logical-agent proof: reference session, continuity ID, and exact persisted
continuity evidence. Without that proof the host path fails closed as
`LOGICAL_AGENT_ALIAS_SURFACE_UNRESOLVED`.

Continuity commands may target a human alias only after the same resolver returns
`ROUTABLE_EXACT_SESSION`. The bus then routes to the resolved canonical `session_id`
and still applies continuity membership, scope, collision-domain, exact-HEAD, liveness,
B12/B29/polling, ACK, and expiry rules. Supplying both a direct session target and an
alias target is rejected.

Historical `provider_contexts[]` participate in exact session correlation, but
repository-derived provider-context IDs and connector/app/installation evidence are
never promoted to provider-native conversation identity.
