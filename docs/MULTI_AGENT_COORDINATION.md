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
