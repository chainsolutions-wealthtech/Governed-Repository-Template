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
