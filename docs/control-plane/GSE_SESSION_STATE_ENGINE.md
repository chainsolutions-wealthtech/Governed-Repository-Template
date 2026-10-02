# GSE — Governed Session Engine

> Status: implementation candidate on `governance/gse-session-state-engine-v1`.
>
> Integration rule: this tranche is parallel to the canonical GACR realignment programme. It does not close or advance GACR steps 13–24, does not modify live GACR stores, and does not grant takeover or repository mutation authority.

## 1. Role separation

```text
GSCC = transport
GSE  = interpretation
GACR = continuity authority
```

GSE is a pure, deterministic state projection. Given a previous `SessionTwin`, one normalized GSCC event, and a reference clock, it returns a new `SessionTwin`. The engine performs no network access, GitHub API call, webhook handling, filesystem persistence, claim transfer, standby assignment, takeover decision, collision-domain mutation, or repository write-authority decision.

The intended integration direction is:

```text
GSCC event stream
    ↓
GSE reducer / evaluator
    ↓
SESSION_TWIN
    ↓
GACR / Supervisor / other consumers
```

GSE can report that liveness is `LOST`; it cannot decide that GACR must declare `STALLED`, transfer a claim, or permit takeover.

## 2. Frozen common event contract

The engine accepts exactly these event names:

```text
SESSION_ATTACH
SESSION_RESUME
HEARTBEAT
ACTIVITY_STARTED
ACTIVITY_COMPLETED
ACTIVITY_FAILED
TOOL_STARTED
TOOL_COMPLETED
TOOL_FAILED
PROGRESS
BLOCKED
CHECKPOINT
CONTEXT_UPDATE
INTERRUPTION
CHALLENGE_RESPONSE
COMMAND_ACK
```

It understands the observable consequences of command delivery states without sending commands itself:

```text
CREATED
QUEUED
DISPATCHED
DELIVERED
ACKNOWLEDGED
EXECUTING
COMPLETED
FAILED
DECLINED
EXPIRED
CANCELLED
NO_RESPONSE
UNSUPPORTED
```

No event or delivery-state name is renamed by GSE.

## 3. Canonical SessionTwin

Schema identifier:

```text
gse-session-twin/v1
```

The twin preserves independent dimensions instead of collapsing them into one `status = ACTIVE` value:

- `presence`
- `liveness`
- `activity`
- `progress`
- `blockage`
- `loop`
- `control_channel`
- `continuity`

It also carries bounded identity/context facts, explicit timestamps, policy values, and evidence required for deterministic projection and duplicate/order handling.

### 3.1 Presence

States:

```text
PRESENT
KNOWN_NOT_CURRENTLY_OBSERVED
UNKNOWN
TERMINAL
```

Any valid normalized event renews `last_seen_at`; `SESSION_ATTACH` and `SESSION_RESUME` additionally establish liveness evidence. Absence of recent evidence decays `PRESENT` to `KNOWN_NOT_CURRENTLY_OBSERVED`; it never proves disappearance. `TERMINAL` requires an explicit `INTERRUPTION` payload with `terminal=true`, and an older terminal event cannot override a newer resume.

### 3.2 Liveness

States:

```text
ACTIVE
QUIET
SUSPECTED
LOST
UNKNOWN
TERMINAL
```

Fresh evidence can come from `HEARTBEAT`, activity/tool events, `SESSION_ATTACH`, `SESSION_RESUME`, and acknowledged `CHALLENGE_RESPONSE`. The default time policy is configurable and currently projects:

- `ACTIVE`: evidence age <= 300 seconds;
- `QUIET`: > 300 and <= 900 seconds;
- `SUSPECTED`: > 900 and <= 1800 seconds;
- `LOST`: > 1800 seconds.

Hard invariant:

```text
liveness != progress
```

A heartbeat renews liveness but never sets `last_progress_at`.

### 3.3 Activity

States:

```text
ACTIVE
IDLE
QUIET
UNKNOWN
```

`ACTIVITY_STARTED`/`TOOL_STARTED` project `ACTIVE`. Completion/failure events project `IDLE`. A still-active activity with no new activity evidence past the activity quiet threshold becomes `QUIET`.

Hard invariant:

```text
activity != progress
```

Activity may remain `ACTIVE` while progress is `STALE`.

### 3.4 Progress

States:

```text
ADVANCING
STALE
NO_RECENT_PROGRESS_EVIDENCE
BLOCKED_IF_EXPLICITLY_OBSERVED
UNKNOWN
```

Qualifying progress is deliberately narrower than activity. GSE accepts explicit semantic `PROGRESS` changes such as phase/checkpoint/work-item transition, completed-step or next-step references, and explicitly qualified completion evidence. Completion events can also qualify when they carry evidence such as written HEAD movement, commit mutation, pull-request mutation, work-item advancement, or checkpoint advancement.

A simple read, tool invocation, repeated action, or heartbeat does not qualify by itself.

For semantic progress GSE persists only bounded fields such as phase/step/checkpoint/work-item transitions. It does not persist transcript content or private reasoning.

### 3.5 Blockage

States:

```text
NOT_BLOCKED
EXPLICITLY_BLOCKED
SUSPECTED_BLOCKED
UNKNOWN
```

Provenance values used by the engine are compatible with the required categories:

```text
EXPLICIT
OBSERVED
DERIVED
INFERRED
UNKNOWN
```

`BLOCKED` always produces `EXPLICITLY_BLOCKED` with `EXPLICIT` provenance and an allowlisted class:

```text
WAITING_FOR_CI
WAITING_FOR_USER
WAITING_FOR_EXTERNAL_DEPENDENCY
PERMISSION
TOOL_FAILURE
REPOSITORY_STATE
DEPENDENCY
UNKNOWN
```

Three same-signature failures with fresh liveness and no newer qualifying progress may produce only `SUSPECTED_BLOCKED`; this is an inference, never a claim about the agent's mental state.

Hard invariant:

```text
blocked != stalled
```

`STALLED` is not a GSE blockage state. It remains a GACR continuity/watch decision.

### 3.6 Loop detection

Each activity/tool event receives a normalized signature over:

```text
action_type
tool_name
target
relevant_input_digest
repository
branch
observed_head
```

The bounded history detects tail patterns:

```text
AAAA
ABABAB
ABCABCABC
```

Repetition alone is insufficient. `SUSPECTED` requires all of:

- a recognized repeated pattern;
- no qualifying progress after the pattern started;
- effective repository HEAD stable within the pattern window;
- checkpoint stable or absent within the pattern window.

States:

```text
NONE
SUSPECTED
CONFIRMED_BY_EXPLICIT_SIGNAL
UNKNOWN
```

An explicit signal may set `CONFIRMED_BY_EXPLICIT_SIGNAL`, but GSE never infers an agent's psychological or cognitive state.

False-positive protections are tested for repeated file reads, `ABABAB` with HEAD movement, and repetition with checkpoint advancement.

Hard invariant:

```text
loop suspected != stalled
```

### 3.7 Control channel health

States:

```text
REACHABLE
DEGRADED
UNREACHABLE
UNSUPPORTED
UNKNOWN
```

An acknowledged challenge/command response projects `REACHABLE`. One `NO_RESPONSE`/`EXPIRED` projects `DEGRADED`; repeated no-response evidence reaches `UNREACHABLE` at the configured threshold. Explicit `UNSUPPORTED` remains `UNSUPPORTED` and is never conflated with `UNREACHABLE`.

A previously reachable channel ages to `DEGRADED` when ACK freshness exceeds the policy threshold.

Hard invariant:

```text
control unreachable != proof of crash
```

GSE never fabricates `BROWSER_CRASH`, `PROVIDER_TIMEOUT`, or `NETWORK_FAILURE` from silence/no-response.

### 3.8 Continuity completeness

States:

```text
SUFFICIENT
PARTIAL
INSUFFICIENT
UNKNOWN
```

The projection evaluates the availability of:

```text
session identity
repository
task
branch
observed HEAD
last action
checkpoint
last progress
next action/context
```

A claim is retained when supplied but is not required in every workflow. `SUFFICIENT` requires all core identity/repository/task/branch/HEAD facts and at least two resume-oriented facts among last action/checkpoint/last progress/next action. Partial and insufficient states explicitly report missing fields.

Hard invariant:

```text
continuity sufficient != takeover authority
```

This state is advisory only.

## 4. Timestamps

The twin maintains, when supported by evidence:

```text
first_seen_at
last_seen_at
last_activity_at
last_liveness_evidence_at
last_challenge_response_at
last_progress_at
last_checkpoint_at
last_control_ack_at
```

Freshness timestamps use max-time semantics so an older out-of-order event cannot move a newer proof backwards.

## 5. Duplicate and ordering policy

### Duplicate event

Preferred deduplication key is `event_id`; if absent, `message_id` is used. If neither exists a stable digest of normalized event type/time/payload is used as a bounded fallback. A previously seen key is not re-applied, does not advance state/timestamps, and increments only the diagnostic `ignored_duplicate_count`.

### Same message ID

Two events carrying the same `message_id` are treated as the same delivered event even if the later duplicate carries a different timestamp.

### Out-of-order / older event

An event older than `last_applied_event_at` is counted as out-of-order. It may enrich bounded historical evidence, but freshness timestamps are max-monotonic and newer context/state is not overwritten by older evidence. In particular, an older terminal interruption cannot override a newer resume.

## 6. Pure-engine API

Implementation:

```text
scripts/gse/session_state_engine.py
```

Public functions:

```python
new_session_twin(session_id=None)
normalize_event(event)
reduce_event(previous, event, reference_time=None, policy=None)
evaluate_at(twin, reference_time, policy=None)
project(events, reference_time=None, session_id=None, policy=None)
```

The primary reducer contract is conceptually:

```text
previous SessionTwin
+
normalized event
+
reference clock
=
new SessionTwin
```

`evaluate_at` exists so consumers can project time-driven decay without inventing a synthetic event.

## 7. Authority boundaries

GSE does not:

```text
transfer claims
accept takeover
create GACR session authority
assign standby
modify collision domains
grant repository write authority
```

It also has no code path that opens a network connection or writes a GACR store.

The integration owner may later map GSE projections into GACR evidence. That mapping must preserve GACR's existing claim, stall, exact-HEAD, collision-domain, and takeover gates.

## 8. Tests

Test suite:

```text
tests/gse/test_session_state_engine.py
```

The suite covers the required acceptance cases and explicit safety boundaries:

- recent heartbeat + no progress;
- active tool activity + recent semantic progress;
- heartbeat decay through QUIET/SUSPECTED/LOST;
- challenge ACK → REACHABLE;
- challenge UNSUPPORTED → UNSUPPORTED;
- repeated NO_RESPONSE → DEGRADED then UNREACHABLE without fabricated crash cause;
- explicit BLOCKED;
- repeated failures → possible SUSPECTED_BLOCKED;
- AAAA loop detection;
- ABABAB loop detection;
- ABABAB + HEAD movement false-positive prevention;
- repeat + checkpoint advancement false-positive prevention;
- same file read twice false-positive prevention;
- continuity SUFFICIENT/PARTIAL/INSUFFICIENT;
- duplicate event idempotency;
- same-message-id idempotency;
- out-of-order/older evidence handling;
- terminal session semantics and newer resume;
- activity ACTIVE with progress STALE;
- semantic progress redaction boundary;
- absence of GSE authority fields.

All GSE tests use in-memory projections only. They do not write any GACR live store.

## 9. Integration notes

No deviation from the frozen common event/delivery-state names is introduced in this tranche. GSE intentionally does not implement the command-sending surface; it only interprets `CHALLENGE_RESPONSE` and `COMMAND_ACK` consequences. No GSCC code is copied into GSE.

The supervisor/integration tranche should bind the final GSCC normalized event envelope to `reduce_event` and decide where/how a SessionTwin is stored or materialized. That later binding is not implemented here because persistence/transport ownership belongs outside this pure engine tranche.
