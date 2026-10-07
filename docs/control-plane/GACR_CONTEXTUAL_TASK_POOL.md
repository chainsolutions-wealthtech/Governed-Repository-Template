# GACR R8 — Contextual Continuous Task Pool

Authority: `CP-AGENT-RELAY-001-R8`  
Decision: `CPD-075`

## Objective

Extend R7 capacity-aware dispatch into a continuous source/client task pool that can:

1. derive ready work from existing canonical authorities;
2. form collision-free parallel waves;
3. attach method/history/evidence context to each task;
4. match only explicitly available compatible agents;
5. require acceptance + exact HEAD + claim;
6. preserve traces continuously;
7. requeue responsive interrupted work with checkpoint/handoff;
8. recover abrupt interruptions using existing GACR forensics/takeover;
9. allow a successor to continue the same task without guessing what the predecessor did.

## No second task authority

R8 does not copy the programme into a new canonical queue.

Source Control Plane:
- high-level programme/task truth: `.governance/control-plane-state/tasks.json`;
- GMC atomic truth: `.governance/control-plane-state/governance-model-execution-blueprint.json`;
- pool projection: `.governance/control-plane-state/gacr-task-pool.json`.

Governed client:
- work truth: `.governance/work/work-items.json`;
- pool projection: `.governance/agent-relay/task-pool.json`.

Claims/dispatches remain existing GACR stores.

## Continuous cycle

The existing scheduled relay runs every ten minutes and on governed relay events:

```text
observe sessions/capacity
→ R7 work offers
→ R8 derive contextual pool
→ enrich offers with context
→ derive source-control-plane offers
→ activate accepted offers only at exact HEAD
→ refresh pool
→ persist only semantic state changes
```

## Parallel waves

A wave may contain multiple tasks only when their collision domains do not intersect.

If a task has no explicit source-control-plane collision metadata, R8 defaults current GMC atomic tasks to:

`control-plane:<work-package>:serial`.

That default is deliberately conservative. Future blueprint tasks can declare narrower domains to unlock real parallelism, but R8 never invents independence.

## Continuity packet

Each task includes:
- identity/source/parent;
- purpose and work kind;
- dependencies;
- collision domains;
- capability/authority/role requirements;
- canonical read-first references;
- work-package method/search order;
- evidence/done/hold criteria;
- claim history;
- prior dispatch history;
- takeover history;
- interruption forensics;
- checkpoint/handoff references;
- trace contract.

This packet is safe coordination metadata. Raw prompt/chat text and private reasoning are forbidden.

## Unfinished work

### Responsive interruption

If an agent detects:
- provider rate limit;
- provider quota exhaustion;
- context limit;
- waiting for input;
- dependency blocker;
- voluntary handoff;

it must preserve checkpoint/handoff/evidence and relinquish the claim. The same canonical task returns to `READY`, and the next context packet includes the previous claim/handoff trail.

### Abrupt interruption

If an agent disappears:
- claim remains attached to predecessor;
- GACR liveness progresses to stall;
- forensics captures last completed/in-flight action and safe resume point;
- task becomes `RECOVERY_READY`;
- takeover uses existing exact-HEAD reconciliation;
- successor receives the accumulated history;
- no in-flight action is replayed blindly.

## Role-aware source dispatch

Control-plane blueprint tasks are not sent to generic qualification sessions.

Current aliases normalize:
- `IMPLEMENTER` → `CODE_AGENT`;
- `CODER` → `CODE_AGENT`;
- `CONTINUATION-SUPERVISOR` → `SUPERVISOR`.

Eligibility remains role + capabilities + observed authorities + collision availability + capacity. Role alone grants nothing.

## Claim contract

R8 source claims live in the existing source GACR claim store.

A claim means:
- exclusive collision-domain ownership for coordination;
- explicit task/session association;
- exact HEAD at activation.

A claim does **not** mean:
- business approval;
- mutation authority;
- F1 bypass;
- access grant;
- policy bypass.

## Current programme integration

At R8 design time, the global programme is:

`GMC-01 / GMC-G01`.

Its first atomic task `GMC-G01-T01` is eligible for projection because it has no atomic dependency, but it must only be offered to a compatible declared agent. Later GMC-G01 tasks remain blocked until their explicit predecessor is complete.

This GACR evolution is a cross-cutting coordination capability. It does not mark GMC atomic tasks complete and does not widen GMC implementation authority.

## Acceptance

R8 is accepted only if CI proves:
- dependency-safe projection;
- collision-free wave formation;
- incompatible roles rejected;
- contextual packet present;
- acceptance without HEAD cannot claim;
- exact-HEAD acceptance can claim;
- duplicate active claim prevented;
- voluntary handoff/requeue preserves trace history;
- stalled predecessor becomes recovery-ready with takeover/forensics;
- no secret/transcript/private-reasoning persistence;
- client upgrade preserves local runtime pool/history.
