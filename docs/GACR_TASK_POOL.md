# GACR Contextual Continuous Task Pool

## Purpose

The GACR task pool continuously derives dispatchable work from canonical task/work authorities and matches it to explicitly available agents without creating a second task truth.

It is a **projection and coordination layer**:

```text
canonical tasks / work-items
+ dependencies
+ claims
+ collision domains
+ agent availability
+ GACR history / forensics / handoff
        ↓
contextual task pool
        ↓
collision-safe WORK_OFFER
        ↓
explicit acceptance + exact HEAD
        ↓
canonical claim
        ↓
governed execution
```

A pool entry never grants mutation authority.

## Agent states

Dispatch capacity is observed, not guessed:

- `AVAILABLE`
- `WAITING`
- `BUSY`
- `BLOCKED`
- `RATE_LIMITED`
- `QUOTA_BLOCKED`
- `CHECKPOINTING`
- `TERMINATING`
- `STALLED`
- `TERMINAL`
- `UNKNOWN`

Silence never means available.

## Task states

- `READY` — dependency-safe and claim/collision-safe.
- `OFFERED` — a compatible agent has a pending offer.
- `ACCEPTED_PENDING_CLAIM` — agent accepted; exact-HEAD claim activation still required.
- `ACTIVE` — canonical claim exists.
- `RECOVERY_READY` — predecessor is stalled/interrupted; recovery context exists.
- `BLOCKED` — dependency or other gate prevents dispatch.

## Context packet

Every dispatchable task includes a safe context packet containing references to:

- canonical task authority;
- parent programme/work package;
- dependencies;
- collision domains;
- method/search order;
- required evidence;
- done/hold criteria;
- current checkpoint/handoff;
- claim and dispatch history;
- takeover and interruption forensics when applicable;
- read-first authorities;
- exact-HEAD and trace obligations.

The packet contains **references and safe structured facts**, never raw prompts, transcripts or private reasoning.

The receiving agent must read the referenced canonical history before mutable work. The packet is not a substitute for reading those authorities.

## Claim lifecycle

```text
WORK_OFFER
→ agent accepts with observed HEAD
→ repository reobserves current HEAD
→ HEAD must still match
→ collision domains must still be free
→ one active claim per agent
→ claim activated
→ work may proceed only under separately applicable authority
```

Offer acceptance alone does not create a writer.

## Mandatory traces

Before mutable work:
- read the task context references;
- reobserve exact HEAD;
- accept the offer;
- obtain canonical claim.

During work:
- emit action-start trace;
- maintain heartbeat/activity evidence;
- emit action-completed trace with evidence.

When blocked:
- emit the observed availability/interruption reason;
- if still responsive, write checkpoint + handoff.

When voluntarily stopping:
- checkpoint;
- handoff;
- evidence reference;
- relinquish claim for requeue.

On abrupt loss:
- GACR liveness/forensics detects the interruption;
- the task becomes recovery/takeover work;
- the successor must exact-HEAD reconcile;
- unresolved in-flight actions are never blindly replayed.

## Provider limits

Rate/quota/context limits are accepted only when explicitly observed. GACR does not infer them from silence.

A responsive agent that must stop should preserve continuity before relinquishing its claim. If it disappears abruptly, normal GACR stall/takeover handling applies.

## Role separation

Task eligibility may restrict roles, but role never grants authority.

Typical roles:
- `CODE_AGENT` — implementation/technical work when separately authorized.
- `INTAKER` — information/context intake and enrichment; no code mutation by role alone.
- `SUPERVISOR` — observes pool/claims/progress, validates continuity and routing; no mutation by role alone.
- `REVIEWER` — review/validation.

The same session must not silently change role to obtain a task.

## Commands

Capacity:

```bash
python3 scripts/gacr_capacity_dispatch.py pool
python3 scripts/gacr_capacity_dispatch.py dispatch-work
```

Contextual pool:

```bash
python3 scripts/gacr_task_pool.py show
python3 scripts/gacr_task_pool.py refresh
python3 scripts/gacr_task_pool.py cycle
```

Voluntary requeue:

```bash
python3 scripts/gacr_task_pool.py relinquish \
  --claim-id <claim> \
  --session-id <session> \
  --reason-code CONTEXT_LIMIT \
  --observed-head <sha> \
  --checkpoint-ref <checkpoint> \
  --handoff-ref <handoff> \
  --evidence-ref <evidence>
```

The scheduled GACR relay refreshes the pool continuously.
