# Continuous Governed Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in continuous governed execution loop that repeatedly resolves, claims, executes, validates, checkpoints, and advances to the next safe task without bypassing existing governance gates.

**Architecture:** Keep `governance_agent.py` as the existing CLI/control-plane surface, but move new responsibilities into focused modules: a pure-ish task resolver, a task-completion validator/mutator, a HEAD/claim reconciliation module, and a thin controller that composes them. Continuous mode is logical and resumable; one CLI iteration returns an execution envelope, then a separate completion call validates the agent result and recomputes the queue.

**Tech Stack:** Python 3.12, JSON/JSON Schema files, existing Git-backed governance stores, GitHub Actions Governance CI, existing script-style self-tests.

**Spec:** `docs/superpowers/specs/2026-09-27-continuous-governed-execution-design.md`

## Global Constraints

- Current live control-plane work remains authoritative. Before implementation, re-read `main`, `CURRENT_STATE.md`, `TASKS.md`, `NEXT_ACTION.md`, checkpoint and handoff.
- At design time, the live unique executable item is `C1-12-K`; do not bypass it. If implementation is not yet the active authorized integration slot, stop after preflight.
- `CONTINUOUS_EXECUTION_NE_UNLIMITED_AUTHORITY`.
- `AUTO_CONTINUE_MUST_PRESERVE_ALL_EXISTING_GATES`.
- `NO_FORCE_PUSH`, `NO_HISTORY_REWRITE`, `EXACT_HEAD_BEFORE_MUTATION`, `SINGLE_WRITER_PER_COLLISION_DOMAIN`, `UNKNOWN_FAILS_CLOSED`.
- Existing `observe`, `entry-actions`, `session-start`, `dispatch`, `checkpoint`, `handoff`, and intake behavior must remain backward compatible.
- No parallel session store, claim store, task store, or database may be introduced.
- Continuous mode is opt-in initially. Default behavior remains single-task/manual governed dispatch.
- Source-only control-plane history must not leak into initialized/upgraded client repositories.
- New behavior is implemented RED → GREEN with the full existing Governance CI green before merge.

## Review Focus

- **Legacy claims without `claim_id`:** existing claims must still resume safely; new code must derive a compatibility identifier rather than reject or rewrite them blindly. Covered in Task 4.
- **Corrupted/cyclic work dependencies:** the resolver must fail closed rather than spin forever or select arbitrary work. Covered in Task 3.
- **Non-fast-forward or divergent HEAD movement:** reconciliation must HOLD, never treat divergence as safe. Covered in Task 5.
- **Malformed/mismatched task result identity:** a result for the wrong session/claim/work item must be rejected before any task/claim mutation. Covered in Task 6.
- **Closed/missing session with active claim:** the claim must enter explicit reconciliation, never be silently discarded or reassigned. Covered in Task 5.

---

## File Structure

### New runtime modules

- `scripts/governed_task_resolver.py` — pure eligibility, dependency indexes, deterministic next-task selection.
- `scripts/governed_task_completion.py` — validate structured task results; apply DONE/BLOCKED transitions; release claims; insert discovered work.
- `scripts/governed_reconciliation.py` — HEAD ancestry/diff reconciliation and stale-claim decisions.
- `scripts/continuous_governed_execution.py` — orchestration: next envelope, completion, checkpoint/recompute.
- `scripts/test_governed_task_resolver.py`
- `scripts/test_governed_task_completion.py`
- `scripts/test_governed_reconciliation.py`
- `scripts/test_continuous_governed_execution.py`

### New policy/schemas/docs

- `.governance/continuous-execution-policy.json`
- `schemas/continuous-execution.schema.json`
- `schemas/execution-envelope.schema.json`
- `schemas/task-result.schema.json`
- `docs/CONTINUOUS_GOVERNED_EXECUTION.md`

### Modified existing surfaces

- `schemas/work-item.schema.json`
- `schemas/work-claim.schema.json`
- `schemas/session.schema.json`
- `scripts/governance_agent.py` — CLI adapters only; preserve existing commands.
- `scripts/validate_governance.py`
- `scripts/control_plane_upgrade_local_entry.py`
- `.governance/TEMPLATE_MANIFEST.json`
- `.github/workflows/governance-ci.yml`
- `scripts/test_entry_action_router.py`
- `scripts/test_upgrade_session_head_migration.py`

---

### Task 1: Governance preflight and implementation-slot gate

**Files:**
- Read only: `docs/control-plane/CURRENT_STATE.md`
- Read only: `docs/control-plane/TASKS.md`
- Read only: `docs/control-plane/NEXT_ACTION.md`
- Read only: `.governance/control-plane-state/current.json`
- Read only: `.governance/control-plane-state/tasks.json`
- Read only: `.governance/control-plane-state/checkpoint.json`
- Read only: `.governance/control-plane-state/handoff.json`

**Interfaces:**
- Consumes: current canonical source state.
- Produces: a ledger/preflight ruling that implementation is either authorized at the current integration slot or blocked by the current unique executable task.

- [ ] **Step 1: Reobserve exact `main` HEAD and the unique executable item**

Run the repository's normal Git/GitHub observation path and record:
- exact main HEAD;
- `unique_executable_item`;
- `NEXT_ACTION`;
- blockers;
- active claims/sessions relevant to source work.

- [ ] **Step 2: Verify the implementation slot**

Expected condition before Task 2:
- the continuous-execution implementation has been explicitly inserted/authorized in the canonical task chain, **or**
- the previously active gate has completed and the new integration slot is now the unique executable item.

If not true: STOP. Do not start product code.

- [ ] **Step 3: Record the preflight result**

Expected: a checkpoint/ledger note for the implementation session that includes observed HEAD and the active authorized work item.

No code commit is made in this task.

---

### Task 2: Define opt-in continuous execution contracts

**Files:**
- Create: `.governance/continuous-execution-policy.json`
- Create: `schemas/continuous-execution.schema.json`
- Create: `schemas/execution-envelope.schema.json`
- Create: `schemas/task-result.schema.json`
- Modify: `schemas/session.schema.json`
- Modify: `schemas/work-item.schema.json`
- Modify: `schemas/work-claim.schema.json`
- Test: `scripts/test_continuous_governed_execution.py`

**Interfaces:**
- Consumes: current session/work-item/work-claim contracts.
- Produces:
  - session fields `execution_mode: "SINGLE_TASK" | "CONTINUOUS_GOVERNED"` and optional `auto_continue: boolean`;
  - work-item optional fields:
    `kind`, `work_package_id`, `objective`, `action`, `method`,
    `artifact_dependencies[]`, `evidence_dependencies[]`,
    `required_artifacts[]`, `required_evidence[]`,
    `required_controls[]`, `required_tests[]`,
    `approval_required`, `allowed_mutation_paths[]`, `completion`;
  - work-claim optional fields:
    `claim_id`, `last_heartbeat_at`, `release_reason`, `supersedes_claim_id`;
  - claim statuses extended with `COMPLETED`, `STALE_RECONCILIATION_REQUIRED`, `SUPERSEDED`.

- [ ] **Step 1: Write contract tests**

Add to `scripts/test_continuous_governed_execution.py` a schema/policy fixture test named conceptually `test_continuous_contracts_are_opt_in_and_backward_compatible` asserting:
- policy default mode is `SINGLE_TASK`;
- allowed modes are exactly `SINGLE_TASK`, `CONTINUOUS_GOVERNED`;
- all spec stop conditions exist;
- legacy session/work-item/claim fixtures without new optional fields remain valid;
- new continuous fixtures validate.

- [ ] **Step 2: Run the test to verify RED**

Run:
`python3 scripts/test_continuous_governed_execution.py`

Expected: FAIL because policy/schemas/new fields do not yet exist.

- [ ] **Step 3: Add the policy and schema changes**

Policy exact defaults:
- `default_execution_mode = "SINGLE_TASK"`;
- `auto_continue_mode = "CONTINUOUS_GOVERNED"`;
- `resume_existing_valid_claim_first = true`;
- `checkpoint_after_each_task = true`;
- `recompute_after_each_completion = true`;
- `status_only_unlock_forbidden = true`;
- `stale_claim_policy = "CLOSED_OR_MISSING_SESSION_REQUIRES_RECONCILIATION"`;
- stop conditions copied from the approved spec.

Keep all new fields optional in legacy schemas unless the new envelope/result schema specifically requires them.

- [ ] **Step 4: Run the contract test**

Run:
`python3 scripts/test_continuous_governed_execution.py`

Expected: PASS for contract section.

- [ ] **Step 5: Commit**

```bash
git add .governance/continuous-execution-policy.json schemas/continuous-execution.schema.json schemas/execution-envelope.schema.json schemas/task-result.schema.json schemas/session.schema.json schemas/work-item.schema.json schemas/work-claim.schema.json scripts/test_continuous_governed_execution.py
git commit -m "feat: define continuous governed execution contracts"
```

---

### Task 3: Implement deterministic task resolver

**Files:**
- Create: `scripts/governed_task_resolver.py`
- Create: `scripts/test_governed_task_resolver.py`

**Interfaces:**
- Consumes: work-items document, claims document, session id, current HEAD.
- Produces:
  - `build_artifact_index(items: list[dict]) -> dict[str, dict]`
  - `build_evidence_index(items: list[dict]) -> dict[str, dict]`
  - `validate_dependency_graph(items: list[dict]) -> tuple[bool, list[str]]`
  - `resolve_next_task(work_doc: dict, claims_doc: dict, session_id: str, current_head: str) -> dict`

`resolve_next_task` returns one of:
- `{"status":"CONTINUE","work_item":...,"claim":...}` for the session's valid active claim;
- `{"status":"ASSIGNABLE","work_item":...}`;
- `{"status":"WAIT","reason":"NO_DEPENDENCY_AND_COLLISION_SAFE_WORK",...}`;
- `{"status":"HOLD","reason":"INVALID_DEPENDENCY_GRAPH",...}`.

Selection ordering remains: priority DESC, sequence ASC, work_item_id ASC.

- [ ] **Step 1: Write resolver RED tests**

In `scripts/test_governed_task_resolver.py`, cover:
- three sequential tasks: only first READY/executable;
- task dependency blocks downstream;
- artifact dependency blocks until a DONE item completion exposes matching validated artifact;
- evidence dependency blocks until matching evidence exists;
- own valid claim returns CONTINUE before selecting new work;
- another session's overlapping collision domain excludes a task;
- non-overlapping tasks remain selectable;
- deterministic priority/sequence/id ordering;
- no work returns WAIT;
- cyclic dependencies return HOLD/INVALID_DEPENDENCY_GRAPH.

- [ ] **Step 2: Run RED**

Run:
`python3 scripts/test_governed_task_resolver.py`

Expected: FAIL with missing resolver module/functions.

- [ ] **Step 3: Implement indexes and dependency validation**

Implement the exact signatures above. Build artifact/evidence indexes only from `DONE` items' `completion.artifacts` and `completion.evidence`; do not infer from planned fields.

- [ ] **Step 4: Implement eligibility and deterministic selection**

Rules:
- executable statuses: `READY` only for new assignment;
- a session's existing ACTIVE claim may resume even if task status is `IN_PROGRESS`;
- task/artifact/evidence dependencies must all pass;
- `approval_required == true` makes the task ineligible and returns a reason if it is otherwise next;
- occupied collision domains come only from ACTIVE claims belonging to other sessions;
- invalid/missing dependency IDs fail closed.

- [ ] **Step 5: Run resolver tests**

Run:
`python3 scripts/test_governed_task_resolver.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/governed_task_resolver.py scripts/test_governed_task_resolver.py
git commit -m "feat: add deterministic governed task resolver"
```

---

### Task 4: Add claim compatibility and claim creation helpers

**Files:**
- Modify: `scripts/governed_task_resolver.py`
- Modify: `scripts/test_governed_task_resolver.py`
- Modify later adapter surface: `scripts/governance_agent.py` only after helper tests are green.

**Interfaces:**
- Produces:
  - `claim_identifier(claim: dict) -> str`
  - `new_claim(session_id: str, item: dict, head: str, now: str) -> dict`
  - `find_session_claim(claims_doc: dict, session_id: str) -> dict | None`

- [ ] **Step 1: Add RED tests for legacy/new claims**

Cover:
- legacy ACTIVE claim without `claim_id` gets a deterministic compatibility id derived from session/work-item/claimed-head;
- compatibility id is stable across repeated reads;
- new claim contains a real `claim_id`, `claimed_at`, `last_heartbeat_at`, collision domains, ACTIVE status, exact head;
- multiple active claims for one session returns an explicit HOLD condition, never picks one arbitrarily.

- [ ] **Step 2: Run RED**

Run:
`python3 scripts/test_governed_task_resolver.py`

Expected: FAIL for missing helpers.

- [ ] **Step 3: Implement claim helpers**

Use a deterministic hash-based compatibility id for legacy claims, but do not mutate the legacy record merely to read it.

New claim ids may use a stable hash over session/work-item/head/claimed_at.

- [ ] **Step 4: Run GREEN**

Run:
`python3 scripts/test_governed_task_resolver.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/governed_task_resolver.py scripts/test_governed_task_resolver.py
git commit -m "feat: add governed claim compatibility helpers"
```

---

### Task 5: Implement HEAD and stale-claim reconciliation

**Files:**
- Create: `scripts/governed_reconciliation.py`
- Create: `scripts/test_governed_reconciliation.py`

**Interfaces:**
- Produces:
  - `git_is_ancestor(root: Path, older: str, newer: str) -> bool`
  - `git_changed_paths(root: Path, older: str, newer: str) -> list[str]`
  - `reconcile_active_claim(root: Path, claim: dict, item: dict, session: dict | None, current_head: str) -> dict`

Return statuses:
- `RESUME_SAFE`;
- `RECOMPUTE_TASK`;
- `TASK_ALREADY_SATISFIED`;
- `STALE_RECONCILIATION_REQUIRED`;
- `HOLD_CONFLICT`.

- [ ] **Step 1: Write reconciliation RED tests**

Create temporary Git repositories and cover:
- unchanged head → RESUME_SAFE;
- fast-forward head with changed files outside `allowed_mutation_paths` → RESUME_SAFE;
- fast-forward head touching an allowed mutation path → HOLD_CONFLICT;
- divergent/non-ancestor history → HOLD_CONFLICT;
- closed session + active claim → STALE_RECONCILIATION_REQUIRED;
- missing session + active claim → STALE_RECONCILIATION_REQUIRED;
- no claim deletion/mutation occurs inside the pure reconciliation decision.

- [ ] **Step 2: Run RED**

Run:
`python3 scripts/test_governed_reconciliation.py`

Expected: FAIL with missing module/functions.

- [ ] **Step 3: Implement Git ancestry/diff helpers**

Use Git subprocess calls with explicit return-code handling. A failed ancestry/diff query fails closed.

If `allowed_mutation_paths` is absent/empty and HEAD moved, return `HOLD_CONFLICT` rather than assume safety.

- [ ] **Step 4: Implement stale-session decisions**

Only closed or missing sessions qualify for stale reconciliation in V1. Do not introduce wall-clock expiry heuristics.

- [ ] **Step 5: Run GREEN**

Run:
`python3 scripts/test_governed_reconciliation.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/governed_reconciliation.py scripts/test_governed_reconciliation.py
git commit -m "feat: add governed head and claim reconciliation"
```

---

### Task 6: Implement task-result validation and completion mutation

**Files:**
- Create: `scripts/governed_task_completion.py`
- Create: `scripts/test_governed_task_completion.py`

**Interfaces:**
- Produces:
  - `validate_task_result(item: dict, claim: dict, result: dict, current_head: str) -> list[str]`
  - `apply_task_result(work_doc: dict, claims_doc: dict, item_id: str, claim_id: str, result: dict, now: str) -> tuple[dict, dict, dict]`

The third tuple member is a summary:
`{"status": "COMPLETED" | "BLOCKED" | "HOLD", "released_claim_id": ..., "discovered_work_ids": [...]}`.

- [ ] **Step 1: Write completion RED tests**

Cover:
- mismatched session/claim/work-item id is rejected;
- `head_before` must equal claim head/compatible reconciled head;
- result `PASS` with failing required test is rejected;
- result `PASS` with failing required control is rejected;
- missing required artifact blocks completion;
- missing required evidence blocks completion;
- valid PASS marks item DONE, stores `completion`, changes claim to COMPLETED/RELEASED semantics with timestamp/reason;
- FAILED/HOLD does not mark DONE and sets item BLOCKED;
- discovered blocking work is inserted canonically before downstream work;
- duplicate discovered work ids fail closed;
- artifact/evidence duplicate ids inside one result fail validation.

- [ ] **Step 2: Run RED**

Run:
`python3 scripts/test_governed_task_completion.py`

Expected: FAIL with missing module/functions.

- [ ] **Step 3: Implement validation**

The function returns all validation errors; no mutation occurs when the list is non-empty.

Result identity fields are mandatory for completion even if the underlying legacy claim had no stored `claim_id`; compare against `claim_identifier(claim)`.

- [ ] **Step 4: Implement mutation**

On valid PASS:
- item `status = "DONE"`;
- persist full structured `completion`;
- claim moves from ACTIVE to `COMPLETED` and records `released_at`, `release_reason = "TASK_COMPLETED"`;
- append discovered work only after validating ids/dependencies.

On FAILED/HOLD:
- item `status = "BLOCKED"`;
- persist result/blocker evidence;
- release claim with explicit reason.

- [ ] **Step 5: Run GREEN**

Run:
`python3 scripts/test_governed_task_completion.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/governed_task_completion.py scripts/test_governed_task_completion.py
git commit -m "feat: validate and persist governed task completion"
```

---

### Task 7: Implement one-iteration continuous controller

**Files:**
- Create: `scripts/continuous_governed_execution.py`
- Expand: `scripts/test_continuous_governed_execution.py`

**Interfaces:**
- Consumes helpers from Tasks 3–6.
- Produces:
  - `load_policy(root: Path) -> dict`
  - `build_execution_envelope(session: dict, item: dict, claim: dict, head: str) -> dict`
  - `next_execution(root: Path, session_id: str, expected_head: str | None = None) -> dict`
  - `complete_execution(root: Path, session_id: str, result: dict, expected_head: str | None = None) -> dict`

`next_execution` returns:
- `{"status":"EXECUTE","envelope":...}`;
- `{"status":"STOP","reason":...}`;
- `{"status":"HOLD","reason":...}`.

`complete_execution` returns:
- `{"status":"CONTINUE","next_action":"RESOLVE_NEXT_TASK",...}`;
- or an explicit STOP/HOLD reason.

- [ ] **Step 1: Write controller RED tests**

Cover:
- continuous session gets first envelope;
- three sequential tasks can be completed and each completion exposes next work without human re-prompt;
- SINGLE_TASK mode returns one envelope then stops after completion;
- `approval_required` returns STOP/APPROVAL_REQUIRED;
- no work returns STOP/NO_EXECUTABLE_WORK;
- missing/blocked authority state passed from adapter returns STOP rather than executing;
- own claim resumes;
- two sessions with non-overlapping tasks get different envelopes;
- overlapping collision blocks second session;
- completion checkpoint data contains current head, item, result, artifacts/evidence and next action.

- [ ] **Step 2: Run RED**

Run:
`python3 scripts/test_continuous_governed_execution.py`

Expected: FAIL for missing controller behavior.

- [ ] **Step 3: Implement `next_execution`**

Sequence:
1. load session/work/claims/policy;
2. exact-head guard;
3. reconcile own active claim if HEAD moved;
4. resolve next task;
5. create/reuse claim;
6. set item IN_PROGRESS only when a new claim is created;
7. persist claim/work changes atomically enough for current file model;
8. return a schema-compatible execution envelope.

- [ ] **Step 4: Implement `complete_execution`**

Sequence:
1. exact-head guard;
2. locate active/compatible claim;
3. validate result;
4. apply task result;
5. persist work/claims;
6. create existing-style checkpoint;
7. if continuous mode and no stop condition, return CONTINUE; otherwise STOP/HOLD.

Do not create an immortal process loop.

- [ ] **Step 5: Run GREEN**

Run:
`python3 scripts/test_continuous_governed_execution.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/continuous_governed_execution.py scripts/test_continuous_governed_execution.py
git commit -m "feat: add continuous governed execution controller"
```

---

### Task 8: Expose continuous mode through the existing governance CLI

**Files:**
- Modify: `scripts/governance_agent.py` at `command_session_start`, parser construction, and new adapter commands.
- Modify: `scripts/test_entry_action_router.py`
- Modify: `scripts/test_continuous_governed_execution.py`

**Interfaces:**
- Existing commands unchanged.
- New CLI:
  - `session-start --execution-mode SINGLE_TASK|CONTINUOUS_GOVERNED`
  - `continuous-next --session-id <id> [--expected-head <sha>]`
  - `task-complete --session-id <id> --result-file <path> [--expected-head <sha>]`

- [ ] **Step 1: Write CLI RED tests**

Assert:
- existing `session-start` without new flag stores/behaves as SINGLE_TASK;
- continuous mode is accepted for `CONTINUE_GOVERNED_WORK` + mutable-compatible intent;
- UNKNOWN intent/action still blocks;
- MAP does not gain mutation authority merely because execution mode is continuous;
- LAB canonical-branch protection remains;
- `continuous-next` emits EXECUTE/STOP/HOLD JSON;
- malformed `--result-file` fails closed.

- [ ] **Step 2: Run RED**

Run:
`python3 scripts/test_entry_action_router.py && python3 scripts/test_continuous_governed_execution.py`

Expected: FAIL for missing CLI flags/commands.

- [ ] **Step 3: Add thin CLI adapters**

`governance_agent.py` delegates to the new controller; do not duplicate resolver/completion/reconciliation logic.

Treat sessions that predate `execution_mode` as SINGLE_TASK.

- [ ] **Step 4: Run GREEN**

Run:
`python3 scripts/test_entry_action_router.py && python3 scripts/test_continuous_governed_execution.py`

Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/governance_agent.py scripts/test_entry_action_router.py scripts/test_continuous_governed_execution.py
git commit -m "feat: expose continuous execution through governance cli"
```

---

### Task 9: Preserve session/claim continuity across governed upgrades

**Files:**
- Modify: `scripts/control_plane_upgrade_local_entry.py` static client surface near the existing list around lines 106–117.
- Modify: `scripts/test_upgrade_session_head_migration.py`
- Modify: `scripts/test_continuous_governed_execution.py`

**Interfaces:**
- Consumes: new runtime scripts/policy/schemas.
- Produces: upgraded clients receive new static files while preserving mutable `.governance/work/*.json` and `.governance/sessions/sessions.json`.

- [ ] **Step 1: Write RED migration tests**

Assert:
- existing session without `execution_mode` survives upgrade unchanged and is interpreted as SINGLE_TASK;
- existing active claim survives upgrade;
- continuous runtime/policy/schemas are synchronized;
- mutable work items/claims/sessions are not overwritten by source template defaults;
- a legacy claim without `claim_id` remains resumable through compatibility behavior.

- [ ] **Step 2: Run RED**

Run:
`python3 scripts/test_upgrade_session_head_migration.py`

Expected: FAIL because new static surface is not distributed.

- [ ] **Step 3: Extend the static client upgrade list**

Add:
- new runtime modules;
- new self-tests required on clients;
- continuous policy;
- new schemas;
- distributed continuous-execution documentation.

Do **not** add source-only spec/plan/control-plane history.

- [ ] **Step 4: Run GREEN**

Run:
`python3 scripts/test_upgrade_session_head_migration.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/control_plane_upgrade_local_entry.py scripts/test_upgrade_session_head_migration.py
git commit -m "feat: distribute continuous governed execution runtime"
```

---

### Task 10: Add distributed documentation and manifest/source-client classification

**Files:**
- Create: `docs/CONTINUOUS_GOVERNED_EXECUTION.md`
- Modify: `.governance/TEMPLATE_MANIFEST.json`
- Modify: `scripts/validate_governance.py`
- Test: `scripts/test_continuous_governed_execution.py`

**Interfaces:**
- Produces manifest categories:
  - runtime scripts/tests under `automation`;
  - policy under `machine_governance`;
  - new schemas under `schemas`;
  - doc under `coordination_docs`.
- Spec/plan remain source development documentation and are not distributed as project state.

- [ ] **Step 1: Write RED manifest/validation tests**

Assert:
- every new distributed file is present in the manifest category expected by the spec;
- no `docs/superpowers/specs/*` or `docs/superpowers/plans/*` path is treated as distributed project state;
- policy/schema files exist and parse;
- validator rejects a manifest missing any required continuous runtime file.

- [ ] **Step 2: Run RED**

Run:
`python3 scripts/test_continuous_governed_execution.py && python3 scripts/validate_governance.py`

Expected: FAIL for missing manifest/doc/validator contract.

- [ ] **Step 3: Add user-facing operational documentation**

Document:
- how a coding agent starts/resumes continuous mode;
- `continuous-next` and `task-complete`;
- stop conditions;
- checkpoint/resume behavior;
- multi-agent collision rule;
- continuous mode does not grant authority.

- [ ] **Step 4: Update manifest and validator**

Validator checks the new policy contract and distributed file presence in both template source and clients.

- [ ] **Step 5: Run GREEN**

Run:
`python3 scripts/test_continuous_governed_execution.py && python3 scripts/validate_governance.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/CONTINUOUS_GOVERNED_EXECUTION.md .governance/TEMPLATE_MANIFEST.json scripts/validate_governance.py scripts/test_continuous_governed_execution.py
git commit -m "docs: register continuous governed execution runtime"
```

---

### Task 11: Wire the new self-tests into Governance CI

**Files:**
- Modify: `.github/workflows/governance-ci.yml`

**Interfaces:**
- Consumes test scripts from Tasks 3–10.
- Produces compilation and execution gates for the new subsystem.

- [ ] **Step 1: Make CI contract test fail locally through textual assertion**

Extend the continuous self-test to assert `.github/workflows/governance-ci.yml` contains:
- all four new runtime modules in the compile step;
- all four new test scripts in the compile step;
- dedicated run steps for resolver, reconciliation, completion and controller self-tests.

- [ ] **Step 2: Run RED**

Run:
`python3 scripts/test_continuous_governed_execution.py`

Expected: FAIL because CI does not reference the new files/tests.

- [ ] **Step 3: Update Governance CI**

Add new modules/tests to `py_compile`, then dedicated test steps:
- `python3 scripts/test_governed_task_resolver.py`
- `python3 scripts/test_governed_reconciliation.py`
- `python3 scripts/test_governed_task_completion.py`
- `python3 scripts/test_continuous_governed_execution.py`

Keep every existing CI step.

- [ ] **Step 4: Run GREEN**

Run:
`python3 scripts/test_continuous_governed_execution.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/governance-ci.yml scripts/test_continuous_governed_execution.py
git commit -m "ci: validate continuous governed execution"
```

---

### Task 12: Prove work-package exit and discovered-blocker progression end-to-end

**Files:**
- Modify: `scripts/test_continuous_governed_execution.py`
- Modify only if required by failing tests: resolver/completion/controller modules.

**Interfaces:**
- Consumes all prior runtime interfaces.
- Produces end-to-end proof of hierarchical output-driven progression.

- [ ] **Step 1: Add RED end-to-end fixture**

Construct:
- Work package G1 with T01, T02 and EXIT item;
- EXIT depends on T01/T02 plus required artifact `ART-G1`, evidence `EV-G1`, and required control `CTL-G1`;
- Work package G2-T01 depends on G1 EXIT.

Assert:
- T01 → T02 sequence;
- G1 EXIT remains blocked until artifact/evidence/control are present;
- completing EXIT unlocks G2-T01;
- status-only DONE on a child does not bypass missing artifact/evidence.

- [ ] **Step 2: Add discovered blocker fixture**

T02 result discovers `DEFECT-001` which blocks EXIT.

Assert:
- DEFECT-001 is inserted;
- EXIT remains blocked;
- resolver selects DEFECT-001 before EXIT;
- once DEFECT-001 completes, EXIT can proceed.

- [ ] **Step 3: Run RED**

Run:
`python3 scripts/test_continuous_governed_execution.py`

Expected: FAIL until any missing integration logic is completed.

- [ ] **Step 4: Implement only the minimal fixes required**

Do not add GMC-specific scheduling code. The generic work-item/dependency model must satisfy the fixture.

- [ ] **Step 5: Run GREEN**

Run:
`python3 scripts/test_continuous_governed_execution.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/test_continuous_governed_execution.py scripts/governed_task_resolver.py scripts/governed_task_completion.py scripts/continuous_governed_execution.py
git commit -m "test: prove output-driven continuous progression"
```

---

### Task 13: Full regression, source/client boundary proof, and candidate versioning

**Files:**
- Potentially modify: `.governance/TEMPLATE_MANIFEST.json`
- Potentially modify: canonical release/changelog surfaces required by the live programme at execution time.
- No unrelated refactors.

**Interfaces:**
- Consumes complete feature branch.
- Produces a release-ready candidate only if all current governance gates allow it.

- [ ] **Step 1: Run every standalone self-test**

Run:
```bash
python3 scripts/validate_governance.py
python3 scripts/test_bootstrap_consistency.py
python3 scripts/test_connection_intent.py
python3 scripts/test_entry_action_router.py
python3 scripts/test_repository_adoption.py
python3 scripts/test_repository_scope.py
python3 scripts/test_control_plane_request.py
python3 scripts/test_control_plane_issue_contract.py
python3 scripts/test_repository_creation_executor.py
python3 scripts/test_local_governed_entry.py
python3 scripts/test_mcp_credential_provisioning.py
python3 scripts/test_mcp_both_ssh_fallback.py
python3 scripts/test_upgrade_session_head_migration.py
python3 scripts/test_governance_model_integrity.py
python3 scripts/test_governed_task_resolver.py
python3 scripts/test_governed_reconciliation.py
python3 scripts/test_governed_task_completion.py
python3 scripts/test_continuous_governed_execution.py
```

Expected: all PASS.

- [ ] **Step 2: Compile all governance scripts**

Run the same `python3 -m py_compile ...` surface represented in Governance CI.

Expected: exit 0.

- [ ] **Step 3: Materialize source-only relational memory**

Run:
`python3 .governance/control-plane-db/materialize.py`

Expected: PASS, no drift caused by the distributed runtime addition.

- [ ] **Step 4: Prove source-only memory non-leak**

Run the existing initialization/bootstrap non-leak path and verify:
- `docs/control-plane` absent from initialized client;
- `.governance/control-plane-state` absent;
- `.governance/control-plane-db` absent;
- new distributed continuous runtime/policy/schemas present.

- [ ] **Step 5: Run textual integrity**

Run:
`git diff --check`

Expected: no output, exit 0.

- [ ] **Step 6: Resolve template version only after fresh live preflight**

If live `main` still has `template_version = 2.8.6` and no intervening version policy says otherwise, set candidate to `2.9.0` because this is a new opt-in framework capability.

If the template version has advanced since this plan was written: STOP and reconcile the next version rather than overwriting it.

- [ ] **Step 7: Commit candidate metadata**

Commit only version/release metadata required by the current live release authority.

---

## Final Verification

Before claiming implementation complete:

1. re-read the approved spec and this plan;
2. verify each acceptance criterion maps to fresh test evidence;
3. run the full Governance CI-equivalent command set;
4. run `git diff --check`;
5. verify exact branch HEAD;
6. verify current canonical programme/next-action has not been bypassed;
7. verify source/client classification of every added file;
8. verify no active claim/session was silently dropped.

Then perform the whole-branch code review required by the selected execution skill.

## Expected rollout state after this plan

The feature should initially be:

```text
AVAILABLE = true
DEFAULT_MODE = SINGLE_TASK
CONTINUOUS_MODE = OPT_IN
AUTO_CONTINUE = only when execution_mode == CONTINUOUS_GOVERNED
AUTHORITY_GATES = unchanged
MANUAL_DISPATCH = backward compatible
```

Activation as the default for eligible coding sessions is a **separate governed decision** after case-level evidence.
