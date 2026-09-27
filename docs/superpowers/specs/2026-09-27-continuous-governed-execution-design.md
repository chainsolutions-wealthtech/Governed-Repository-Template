# Continuous Governed Execution — Design Specification

> Repository: `chainsolutions-wealthtech/Governed-Repository-Template`  
> Date: `2026-09-27`  
> Status: `APPROVED_DESIGN`  
> Scope: architecture/design only  
> Implementation authorized by this document: **NO**  
> Owner review: `APPROVED 2026-09-27`  
> Current live execution gate remains: `C1-12-K_RERUN_GOUVERN_ISSUE_3`

## 1. Purpose

The control plane must allow a connected coding agent to keep working through governed work continuously without requiring a human to manually ask for the next task after every successful step.

The target behavior is:

```text
agent connects
→ identity/session/intent/action/authority resolved
→ next executable task resolved
→ task claimed
→ task executed
→ tests/controls/evidence evaluated
→ result persisted
→ claim released
→ checkpoint persisted
→ queue recomputed
→ next executable task resolved
→ continue
```

The agent continues automatically until a governed stop condition is reached.

This is **continuous governed execution**, not uncontrolled autonomous execution.

## 2. Success criteria

The design is successful only if all of the following become possible after implementation:

1. A coding agent can enter an already governed repository and resume the existing governed session or create one according to current rules.
2. The control plane selects the next task; the agent does not arbitrarily choose work.
3. The selected task is dependency-safe, artifact-safe, evidence-safe, authority-safe, collision-safe and HEAD-safe.
4. The same session can execute multiple tasks sequentially without a human prompt between every task.
5. A completed task automatically causes queue recomputation.
6. A newly unblocked task can be claimed automatically.
7. Work stops fail-closed on approval, authority, evidence, collision, unresolved HEAD movement, external blocker or critical control failure.
8. Session interruption does not destroy continuity; a later agent can resume from versioned repository state.
9. Two agents cannot both mutate the same collision domain at the same time.
10. Existing CREATE / ADOPT / MAP / LAB / CONTINUE_GOVERNED_WORK semantics remain compatible.
11. Existing tests and Governance CI remain green.
12. No current canonical task is bypassed. At the time this design is written, the live task remains `C1-12-K`.

## 3. Current foundation already present

The repository already contains most low-level primitives required for this design.

### 3.1 Session lifecycle

`scripts/governance_agent.py` already provides:

- `session-start`;
- stable session identity;
- session resume;
- intent capture;
- entry-action capture;
- fail-closed ambiguous-session handling;
- last observed HEAD persistence.

### 3.2 Dispatch and claims

The existing `dispatch` flow already provides:

- active-session validation;
- connection-intent mutation gate;
- entry-action routing gate;
- exact HEAD guard;
- dependency checks;
- collision-domain checks;
- deterministic task ordering;
- active claim reuse;
- new claim creation;
- `HEAD_MOVED` refusal.

### 3.3 Continuity

The repository already provides:

- checkpoints;
- handoffs;
- session persistence;
- claim persistence;
- `NEXT_ACTION`;
- canonical task memory;
- source-only control-plane state;
- append/supersede/revalidate memory principles.

### 3.4 Missing layer

What is missing is the orchestration layer that repeatedly composes the existing primitives into one governed loop.

The design therefore **extends the current control plane** rather than replacing it.

## 4. Design principles

### 4.1 Reuse existing primitives

Do not create a second session engine, claim system, task store or canonical memory.

### 4.2 Control plane chooses; agent executes

```text
CONTROL PLANE
→ determines what is executable

AGENT
→ performs the selected execution envelope
```

The coding agent never selects work merely because it looks useful.

### 4.3 Continuous does not mean unlimited authority

`AUTO_CONTINUE=true` never grants authority.

Intent, entry action, role and authority remain separate gates.

### 4.4 Output-driven progression

A task or work package does not unlock downstream work from a status flag alone.

Eligibility may require:

```text
TASK_DEPENDENCY
+ ARTIFACT_DEPENDENCY
+ EVIDENCE_DEPENDENCY
+ EXIT CONTROLS
+ AUTHORITY
+ COLLISION SAFETY
+ EXACT HEAD
```

### 4.5 Fail closed

Unknown or ambiguous authority, identity, state, evidence or dependency never becomes an implicit PASS.

### 4.6 Persistent continuity

The repository, not the conversation, is the durable state.

A new agent must be able to resume from versioned authorities and machine state without needing the previous conversation.

## 5. Proposed architecture

```text
                         AGENT CONNECTION
                                │
                                ▼
                    existing session-start
                                │
                                ▼
                 role / intent / entry action
                                │
                                ▼
                CONTINUOUS EXECUTION CONTROLLER
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
       NEXT EXECUTABLE TASK             RECONCILIATION
             RESOLVER                       SERVICE
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                           TASK GATE
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
        dependencies         authority          collisions
             │                  │                  │
             ├──── artifact/evidence ──────────────┤
             │                                     │
             └──────────── exact HEAD ─────────────┘
                                │
                                ▼
                           AUTO CLAIM
                                │
                                ▼
                       EXECUTION ENVELOPE
                                │
                                ▼
                           CODE AGENT
                                │
                                ▼
                       TASK RESULT CONTRACT
                                │
                                ▼
                    COMPLETION / VALIDATION
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
            PASS                              FAIL / HOLD
              │                                   │
              ▼                                   ▼
      persist result/evidence               persist blocker
      release claim                         checkpoint
      checkpoint                            stop/recover
              │
              ▼
         RECOMPUTE QUEUE
              │
              ▼
          NEXT TASK
              │
              └───────────────────────────────↺
```

## 6. Components

### 6.1 `continuous_governed_execution.py`

Responsibility:

- own the loop;
- call resolver;
- call reconciliation when necessary;
- create/refresh claim through existing claim semantics;
- produce the execution envelope;
- consume the task result;
- invoke completion validation;
- checkpoint after every state-changing boundary;
- recompute and continue;
- stop only on an explicit governed stop condition.

This component must not directly implement task dependency logic already owned by the resolver.

### 6.2 `governed_task_resolver.py`

Responsibility:

- calculate the next executable task;
- preserve deterministic ordering;
- evaluate task dependencies;
- evaluate artifact dependencies;
- evaluate evidence dependencies;
- evaluate upstream exit controls;
- respect existing claims and collision domains;
- prefer resuming the current session's valid claim;
- return a structured reason when no task is executable.

The resolver must be pure enough to test independently from mutation where practical.

### 6.3 `governed_task_completion.py`

Responsibility:

- validate the task result contract;
- validate expected tests and controls;
- validate required artifacts;
- validate required evidence;
- persist task result;
- transition task status only after validation;
- release the active claim;
- persist checkpoint;
- register newly discovered work when allowed by policy;
- return whether queue recomputation may continue.

This component is the missing symmetric operation to `dispatch`.

### 6.4 `governed_reconciliation.py`

Responsibility:

- handle `HEAD_MOVED`;
- detect stale claims/sessions;
- compare the claimed HEAD with current HEAD;
- determine whether the current task is still safe to resume;
- release or supersede stale claims only according to explicit policy;
- never silently discard evidence or claims.

### 6.5 Existing `governance_agent.py`

It remains the low-level control-plane command surface.

The new subsystem should reuse or extract its current primitives rather than fork equivalent logic.

A later implementation plan may choose whether to:

- import reusable functions from `governance_agent.py`, or
- extract shared primitives into a small shared module and preserve existing CLI behavior.

Backward compatibility of existing CLI commands is mandatory.

## 7. Execution policy

Add a source-controlled policy such as:

`.governance/continuous-execution-policy.json`

Conceptual fields:

```json
{
  "schema_version": "1.0.0",
  "auto_continue": true,
  "task_selection": "DETERMINISTIC_GOVERNED",
  "resume_existing_valid_claim_first": true,
  "checkpoint_after_each_task": true,
  "recompute_after_each_completion": true,
  "status_only_unlock_forbidden": true,
  "stop_conditions": [
    "APPROVAL_REQUIRED",
    "NO_EXECUTABLE_WORK",
    "AUTHORITY_BLOCKED",
    "UNRESOLVED_HEAD_MOVED",
    "COLLISION_BLOCKED",
    "EXTERNAL_DEPENDENCY",
    "CONTROL_FAILED",
    "EVIDENCE_MISSING",
    "UNRESOLVED_CRITICAL_CONFLICT"
  ]
}
```

A repository may later override only explicitly allowed operational fields.

The policy must not be treated as authority to mutate infrastructure, production, secrets, finance or other sensitive systems.

## 8. Execution envelope

The resolver returns one execution envelope per claimed task.

Minimum conceptual contract:

```text
execution_id
session_id
claim_id
work_item_id
program_id
phase_id
work_package_id
task_id

observed_head_sha
claimed_head_sha

objective
action
method

inputs
artifact_dependencies
evidence_dependencies

allowed_mutation_scope
collision_domains

files_or_surfaces_to_read
expected_outputs
required_controls
required_tests
required_evidence

stop_conditions
next_result_contract
```

The envelope is the exact unit the coding agent executes.

It must not contain invented paths or inferred permissions.

## 9. Task result contract

The agent returns a structured result.

Minimum conceptual contract:

```text
execution_id
session_id
claim_id
work_item_id

head_before
head_after

result_status
summary

files_read[]
files_changed[]

tests[]
controls[]

artifacts[]
evidence[]

discovered_work[]

blockers[]
rulings[]
```

Allowed result states should include at minimum:

- `PASS`;
- `FAILED`;
- `HOLD`;
- `BLOCKED_EXTERNAL`;
- `APPROVAL_REQUIRED`;
- `HEAD_MOVED`.

A task must not become DONE simply because the agent says PASS.

The completion service independently validates the contract.

## 10. Eligibility algorithm

A task is executable only if all required conditions pass.

Conceptually:

```text
eligible(task, session, head) =
    task.status in executable states
    AND task_dependencies_satisfied(task)
    AND artifact_dependencies_satisfied(task)
    AND evidence_dependencies_satisfied(task)
    AND upstream_exit_controls_pass(task)
    AND session_intent_allows_mutation(session)
    AND entry_action_allows_dispatch(session)
    AND authority_allows_task(session, task)
    AND no_collision(task)
    AND exact_head_valid(head)
```

Selection order:

1. resume the current session's valid active claim;
2. recovery/blocker work explicitly inserted before the normal sequence;
3. next executable task in the current work package;
4. next executable task in the next unlocked work package;
5. no executable work → stop cleanly.

Within the same eligibility class, preserve the current deterministic ordering principle:

```text
priority DESC
sequence ASC
work_item_id ASC
```

## 11. Continuous loop

Conceptual algorithm:

```text
while true:
    head = observe_head()

    session = load_active_session()

    reconcile_session_and_claims(head)

    resolution = resolve_next_executable_task(session, head)

    if resolution.stop:
        checkpoint(resolution.reason)
        return resolution

    claim = ensure_claim(resolution.task, session, head)

    envelope = build_execution_envelope(claim)

    return envelope_to_agent

    result = receive_task_result()

    validation = validate_task_result(result)

    persist(validation)

    if validation.requires_stop:
        checkpoint(validation.reason)
        return validation

    release_claim_if_complete()

    checkpoint(task_complete)

    recompute_queue()

    continue
```

The practical implementation may expose one CLI call per loop iteration rather than attempting to keep one operating-system process alive forever.

That is intentional: repository state provides continuity across agent/runtime interruptions.

## 12. Stop conditions

The controller stops on the following conditions.

### 12.1 `APPROVAL_REQUIRED`

A required human approval or explicit owner decision is missing.

### 12.2 `NO_EXECUTABLE_WORK`

Nothing is currently executable.

This is a clean stop, not an error.

### 12.3 `AUTHORITY_BLOCKED`

Intent is compatible but authority is insufficient or unknown.

### 12.4 `UNRESOLVED_HEAD_MOVED`

HEAD changed and the change cannot be safely reconciled.

### 12.5 `COLLISION_BLOCKED`

All otherwise eligible work collides with active claims.

### 12.6 `EXTERNAL_DEPENDENCY`

An external repository, system or approval blocks progress.

### 12.7 `CONTROL_FAILED`

A required control or regression check fails.

### 12.8 `EVIDENCE_MISSING`

The task cannot prove a required result.

### 12.9 `UNRESOLVED_CRITICAL_CONFLICT`

Two authorities or observations conflict and no precedence rule resolves them.

No stop condition may be automatically downgraded merely to keep the loop running.

## 13. HEAD movement and reconciliation

`HEAD_MOVED` is not automatically fatal to the overall session.

Required behavior:

```text
claimed HEAD != current HEAD
→ freeze mutation
→ inspect intervening change
→ recompute dependencies/collisions
→ determine whether current claim remains valid
```

Possible outcomes:

- `RESUME_SAFE` — claim may continue with refreshed HEAD;
- `RECOMPUTE_TASK` — release/supersede claim and dispatch again;
- `HOLD_CONFLICT` — stop;
- `TASK_ALREADY_SATISFIED` — validate evidence and close without duplicating work.

No automatic force push, rollback or history rewrite is permitted.

## 14. Claim lifecycle and stale claims

Current claim semantics are extended, not replaced.

Target claim lifecycle:

```text
ACTIVE
→ COMPLETED
→ RELEASED
```

or:

```text
ACTIVE
→ STALE_RECONCILIATION_REQUIRED
→ RELEASED / SUPERSEDED / RESUMED
```

Planned fields may include:

```text
claim_id
session_id
work_item_id
claimed_head_sha
claimed_at
last_heartbeat_at
collision_domains
status
release_reason
supersedes_claim_id
```

A claim must never disappear silently.

A stale claim can be released only when the reconciliation policy proves that no live writer still owns the collision domain.

## 15. Session continuity and agent replacement

Continuous execution must survive agent replacement.

Example:

```text
Agent A
→ executes T31
→ executes T32
→ checkpoint
→ session/runtime ends

Agent B
→ connects
→ observes canonical state
→ resumes or creates governed session
→ reconciles prior claim
→ resolver returns T33
→ continues
```

Continuity is therefore project-level, not conversation-level.

## 16. Discovered work

A task may discover a defect or prerequisite that was not in the original queue.

The new work must not be executed directly from conversational memory.

Required flow:

```text
discovery
→ create candidate work item
→ classify scope/severity
→ persist provenance
→ insert dependencies
→ validate queue consistency
→ recompute
→ resolver decides whether it is now executable
```

For a blocker:

```text
T08
→ discovers DEFECT-001
→ DEFECT-001 blocks T09
→ DEFECT-001 becomes READY
→ resolver selects DEFECT-001
→ after PASS, T09 can unlock
```

This preserves the existing rule that newly discovered work enters canonical memory before execution.

## 17. Role, intent and authority

The continuous loop is intended primarily for coding agents, but role alone never grants authority.

Required dimensions remain independent:

```text
PRINCIPAL
AGENT
CONNECTION
SESSION
ROLE
AUTHORITY
ENTRY_ACTION
CONNECTION_INTENT
```

At minimum:

- `CODE_CHANGE` or compatible governed work intent is required for mutable code dispatch;
- `CONTINUE_GOVERNED_WORK` permits normal dispatch in an already governed repository;
- CREATE / ADOPT / MAP / LAB retain their specific gate semantics;
- MAP remains read-only unless another explicit workflow authorizes writing mapping artifacts;
- LAB cannot mutate the canonical branch;
- infrastructure/production/secrets require separate authority.

## 18. Multi-agent concurrency

The current collision-domain principle remains:

```text
SINGLE_WRITER_PER_COLLISION_DOMAIN
```

The continuous controller must not monopolize the whole repository if independent work is safely parallelizable.

Two agents may work concurrently only when:

- both sessions are valid;
- tasks are independently executable;
- collision domains do not overlap;
- task dependencies permit concurrency;
- each task owns a distinct active claim.

The resolver for each session must account for other active claims before selecting work.

## 19. Checkpointing and handoff

A checkpoint is persisted after each significant boundary:

- task claim created;
- task completed;
- task failed;
- task held;
- HEAD reconciliation;
- group exit;
- session stop;
- discovered blocker insertion.

Minimum checkpoint information:

```text
session_id
work_item_id
claim_id
observed_head_sha
result_status
artifacts
evidence
blockers
next_action
checkpoint_at
```

Handoff is used when a session closes or another agent must resume.

The existing handoff model remains authoritative.

## 20. Work-package exit

For hierarchical programmes such as the Governance Model Catalogue, completing the last child task does not automatically complete the group.

The controller must evaluate work-package exit controls.

For GMC-style groups:

```text
all required child tasks validated
+ required persistent artifacts VALIDATED
+ required evidence present
+ exit controls PASS
+ no critical HOLD
→ group VALIDATED_EXIT
```

Only then may downstream artifact/evidence dependencies resolve.

## 21. Governance Model Catalogue integration

The GMC programme already defines:

- 19 work packages;
- 174 atomic tasks;
- task dependencies;
- artifact dependencies;
- evidence dependencies;
- exit controls;
- persistent planned knowledge artifacts.

The continuous execution subsystem should eventually consume those contracts directly rather than maintain a separate GMC-specific scheduler.

Example:

```text
GMC-G03-T12 PASS
→ G03 child task set complete
→ validate DOMAIN_REGISTRY
→ validate provenance evidence
→ run G03 exit controls
→ G03 VALIDATED_EXIT
→ resolver reevaluates G04
→ G04-T01 becomes executable
```

The GMC programme remains dependency-bound behind CASE 1 until the existing programme explicitly unlocks it.

## 22. Compatibility with the four structuring cases

### CREATE

The controller may continuously execute the applicable creation sequence, but repository creation and setup approvals remain explicit gates.

### ADOPT

Continuous execution may progress through observation and approved additive integration. Conflicts stop for review.

### MAP

The controller may continuously execute read-only observation/mapping tasks. It must not convert MAP into an implementation flow.

### LAB

The controller may continuously execute lab tasks on the explicitly authorized branch/PR while preserving canonical branch protection.

### CONTINUE_GOVERNED_WORK

This is the primary normal-work path for automatic multi-task continuation in an already governed repository.

## 23. Backward compatibility

Existing commands must continue working:

- `observe`;
- `entry-actions`;
- `session-start`;
- `dispatch`;
- `checkpoint`;
- `handoff`;
- intake flows.

Initial activation should be additive.

A safe rollout sequence is:

```text
existing manual governed flow
        +
new continuous controller available but not default
        ↓
regression matrix PASS
        ↓
opt-in AUTO_CONTINUE for governed CODE_AGENT sessions
        ↓
case validation
        ↓
consider default activation later
```

The first implementation must not silently switch every repository/session to auto-continue.

## 24. Source/client boundary

The control plane source repository contains source-only programme memory.

The new continuous execution runtime that must exist in instantiated governed clients must be clearly separated from source-only control-plane history.

The implementation plan must explicitly classify every added file as either:

- distributed governance runtime;
- source-only control-plane state;
- schema/policy distributed to clients;
- source-only tests/fixtures.

No source programme history may leak into generated clients.

## 25. Proposed file surface

This is a design target, not authorization to create the files yet.

Potential new distributed/runtime files:

```text
scripts/
├── continuous_governed_execution.py
├── governed_task_resolver.py
├── governed_task_completion.py
└── governed_reconciliation.py

schemas/
├── continuous-execution.schema.json
├── execution-envelope.schema.json
└── task-result.schema.json

.governance/
└── continuous-execution-policy.json
```

Potential updates:

```text
scripts/governance_agent.py
.governance/work/work-items.json schema/contract
.governance/work/claims.json schema/contract
.governance/sessions/sessions.json schema/contract
Governance CI
client upgrader static surface
template manifest
relevant tests
```

The implementation plan must first verify the exact existing schema filenames and distribution manifest before selecting final paths.

## 26. TDD and regression matrix

Implementation must use RED → GREEN for new behavior.

Required scenario coverage:

1. auto-continue across three sequential tasks;
2. task dependency blocks downstream task;
3. artifact dependency blocks downstream task;
4. evidence dependency blocks downstream task;
5. work-package exit control blocks downstream group;
6. valid active claim resumes before selecting new work;
7. collision with another session blocks selection;
8. two independent sessions receive non-colliding tasks;
9. HEAD_MOVED → safe reconciliation → resume;
10. HEAD_MOVED → conflict → HOLD;
11. task test failure prevents completion;
12. missing evidence prevents completion;
13. missing approval stops;
14. missing authority stops;
15. no executable work stops cleanly;
16. discovered blocker inserted before downstream task;
17. stale claim requires reconciliation and is never silently deleted;
18. interrupted session can be resumed by a later agent;
19. existing manual `dispatch` behavior remains compatible;
20. CREATE / ADOPT / MAP / LAB routing regressions remain green;
21. source-only memory does not leak into clients;
22. GMC task → artifact/evidence → group exit → next group unlock works.

Governance CI must run the new regression suite together with all existing governance self-tests.

## 27. Observability

The subsystem should emit/persist structured events for at least:

- `CONTINUOUS_LOOP_STARTED`;
- `TASK_RESOLVED`;
- `TASK_CLAIMED`;
- `TASK_EXECUTION_RESULT_RECEIVED`;
- `TASK_VALIDATED`;
- `TASK_HELD`;
- `CLAIM_RELEASED`;
- `HEAD_RECONCILIATION_STARTED`;
- `HEAD_RECONCILIATION_RESULT`;
- `WORK_DISCOVERED`;
- `QUEUE_RECOMPUTED`;
- `NO_EXECUTABLE_WORK`;
- `CONTINUOUS_LOOP_STOPPED`.

Events are operational evidence. They do not replace canonical authorities.

## 28. Safety and non-regression invariants

The implementation must preserve:

```text
NO_FORCE_PUSH
NO_HISTORY_REWRITE
EXACT_HEAD_BEFORE_MUTATION
SINGLE_WRITER_PER_COLLISION_DOMAIN
UNKNOWN_FAILS_CLOSED
INTENT_NE_AUTHORITY
ENTRY_ACTION_NE_AUTHORITY
INTAKE_NE_WORK_ITEM
CONTRADICTION_HOLD_FOR_REVIEW
SOURCE_CONTROL_PLANE_MEMORY_NE_CLIENT_MEMORY
NO_PARALLEL_CANONICAL_DATABASE
PLANNED_NE_IMPLEMENTED
```

Additional invariant:

```text
CONTINUOUS_EXECUTION_NE_UNLIMITED_AUTHORITY
```

and:

```text
AUTO_CONTINUE_MUST_PRESERVE_ALL_EXISTING_GATES
```

## 29. Rollout strategy

### Stage A — Internal subsystem

Implement resolver, result validation and loop contracts behind an inactive/opt-in policy.

### Stage B — Existing governed normal work

Validate on `CONTINUE_GOVERNED_WORK` using synthetic/local fixtures.

### Stage C — Multi-agent concurrency

Validate collision domains, stale claims and agent replacement.

### Stage D — Case compatibility

Validate CREATE / ADOPT / MAP / LAB without changing each case's authority semantics.

### Stage E — GMC consumption

After CASE 1 and the relevant GMC prerequisites unlock, use the same engine against the GMC task/artifact/evidence graph.

### Stage F — Activation decision

Only after the regression matrix and case evidence pass should `AUTO_CONTINUE` become a normal default for eligible coding sessions.

## 30. Alternatives considered

### Alternative A — one large extension inside `governance_agent.py`

Rejected as the primary design because it would further concentrate resolver, mutation, completion and reconciliation logic in one file, making testing and future evolution harder.

Existing CLI behavior remains, but new responsibilities should have clear module boundaries.

### Alternative B — separate orchestration database/service

Rejected.

It would create a second state authority and conflict with the existing Git-versioned canonical memory and deterministic relational projection strategy.

### Alternative C — external always-on daemon

Not required for the first implementation.

The durable loop is logical, not dependent on one immortal process. A new agent/runtime can resume the next iteration from persisted state.

An external daemon can be considered later as an execution host, but never as the canonical state authority.

## 31. Integration with current live programme

At the time of this design:

```text
unique executable task = C1-12-K
```

The design work does not complete, supersede or bypass that task.

Implementation of this subsystem must be inserted into the canonical programme at an explicitly authorized integration slot.

The future implementation plan must therefore begin with a preflight that re-reads:

- current `main` HEAD;
- `CURRENT_STATE.md`;
- `TASKS.md`;
- `NEXT_ACTION.md`;
- checkpoint;
- handoff;
- active claims/sessions;
- canonical decisions.

If the active programme has advanced, the implementation plan follows the newer authority.

## 32. Acceptance criteria for implementation

Implementation is complete only when:

1. an eligible code-agent session can receive multiple sequential tasks without human re-prompting;
2. all existing gates remain active;
3. task selection is deterministic and dependency-safe;
4. artifact/evidence dependencies are enforced;
5. collision safety works across concurrent sessions;
6. HEAD movement reconciles or stops safely;
7. task completion is independently validated;
8. claims are never silently lost;
9. checkpoints permit agent replacement;
10. newly discovered blocking work is inserted canonically;
11. group exit controls are enforced;
12. existing manual dispatch remains compatible;
13. source/client boundaries remain intact;
14. full Governance CI and the new regression matrix pass;
15. no current programme gate was bypassed.

## 33. Non-goals

This design does not:

- create a background service outside repository governance;
- grant agents new authority;
- remove human approval gates;
- make MAP mutable;
- allow LAB to write the canonical branch;
- replace the canonical task store;
- replace sessions/claims/checkpoints/handoffs;
- create a parallel database;
- implement the Governance Model Catalogue itself;
- bypass the current CASE 1 programme.

## 34. Design decision

The selected design is:

> Add a thin Continuous Governed Execution subsystem above the existing session/dispatch/claim/checkpoint primitives. The subsystem continuously resolves the next governed executable task, emits a structured execution envelope, validates structured task results, persists artifacts/evidence/checkpoints, reconciles HEAD/claims, recomputes the queue and continues until an explicit fail-closed stop condition occurs.

This preserves the existing governance architecture while enabling project-level continuous work across tasks and across agent/session replacement.
