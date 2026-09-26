# CONTROL PLANE PROGRAM

## Purpose

This file is the durable source-only program authority for development of `Governed-Repository-Template`.

It does not replace the generic entry-action policy distributed to clients.

## Active macro case

`CREATE_NEW_REPOSITORY`

Operational issue: `#12`.

## Canonical six-step completion program

### STEP 1 — MCP connectivity-choice contract completion
State: `DONE`

Exit proof:
- optional MCP linking contract tested;
- when MCP linking is enabled, transport choice remains owner-driven: `DIRECT_MCP_TOKEN`, `SSH`, or `BOTH`;
- direct MCP credential contract tested;
- SSH OIDC read-only path tested;
- `BOTH` tested as one valid combined mode, not as a mandatory mode;
- target upgrade path tested;
- external MCP gaps routed as intake rather than implemented here.

### STEP 2 — Resume Gouvern through MCP discovery
State: `DONE`

Exit proof:
- existing `LOCAL-000002` resumed without losing answers/history;
- DIRECT MCP evidence and SSH OIDC evidence preserved separately;
- final discovery PASS/non-degraded;
- no runtime/MCP write authority inferred.

### STEP 3 — Complete technical setup and APPLY_BASELINE
State: `DONE`

Exit proof:
- setup owner-approved;
- domain binding preserved as `UNRESOLVED` rather than invented;
- `STANDARD_GOVERNED_FLOW` selected;
- baseline commit `23975e0435e63fb45d7436d1f23ce8ce0a450a5f`;
- `LOCAL_HANDOFF_READY` persisted for first-agent bootstrap.

### STEP 4 — Prove subsequent NORMAL_GOVERNED_ENTRY on Gouvern
State: `IN_PROGRESS`

Goal:
- connect a subsequent agent after first-agent completion;
- prove the repository routes to `NORMAL_GOVERNED_ENTRY`, not back to `FIRST_AGENT_BOOTSTRAP`;
- preserve existing baseline/session/work authorities;
- prove no duplicate first-agent baseline is created.

Exit gate:
- live subsequent local-entry evidence;
- normal-entry handoff produced;
- no baseline reset;
- CI remains green.

### STEP 5 — Fresh repository E2E proof from zero
State: `PENDING_STEP_4`

Goal:
- create a second clean disposable repository from the current template;
- run the entire path from creation to handoff without relying on `Gouvern` migration history.

Required lifecycle adapts to the owner's choices:

`CREATE → BOOTSTRAP → FIRST_AGENT → PROJECT BASELINE → OPTIONAL MCP LINK → [DIRECT_MCP_TOKEN | SSH | BOTH when linked] → DISCOVERY when applicable → DOMAIN when applicable → SETUP → APPLY_BASELINE → HANDOFF → NORMAL ENTRY`.

If MCP linking is declined, the lifecycle must continue without inventing an MCP dependency.

Exit gate:
- uninterrupted governed lifecycle;
- no target-specific repair;
- all CI/attestations green.

### STEP 6 — Close CREATE_NEW_REPOSITORY and release next macro case
State: `PENDING_STEP_5`

Goal:
- reconcile documentation, manifest/version, tests and durable evidence;
- ensure all external MCP needs are represented only as intakes;
- close CASE 1 only after STEP 5 passes;
- release the next macro case according to the framework roadmap.

## Anti-deviation rules

1. Execute STEP 1 → 2 → 3 → 4 → 5 → 6 only.
2. Never compress two chronological gates into one state.
3. A later step cannot become IN_PROGRESS before the current step satisfies its exit gate.
4. Generic defects found in a pilot are fixed in the template first, then propagated.
5. Never patch only the pilot to hide a framework defect.
6. MCP linkage and transport are choices, not framework mandates; the state machine must follow the selected path without forcing `BOTH`.
7. `Patricked-code/MCP` is READ / OBSERVE / INTAKE only from this workstream.
8. Every mutable action requires exact-HEAD reconciliation and verifiable CI.
9. Historical answers/sessions/checkpoints are migrated or reconciled, never silently discarded.
10. Keep one unique next action.

## Continuity contract

```text
Conversation / Agent N
  -> observations
  -> decisions
  -> implementation
  -> evidence
  -> checkpoint
  -> versioned source-only authorities
  -> Conversation / Agent N+1
  -> reobserve HEAD
  -> read source-only authorities
  -> reconcile
  -> resume unique next action
```

Conversation memory is supplemental context only.

## Source-of-truth relationship

- `docs/control-plane/CURRENT_STATE.md`: human current state.
- `docs/control-plane/TASKS.md`: durable active work queue.
- `docs/control-plane/NEXT_ACTION.md`: unique resumable action.
- `docs/control-plane/DECISIONS_LOG.md`: durable decisions.
- `docs/control-plane/SUIVI.md`: chronological history.
- `docs/control-plane/CASE1_REPLAY_LEDGER.md`: detailed phase-by-phase replay authority for CASE 1, including owner feedback/return points.
- `.governance/control-plane-state/*.json`: deterministic machine projections.
- Git commits/CI: execution evidence.
- GitHub issues: orchestration and external interaction evidence.


## Canonical architecture authority

The program evolves against:

`docs/control-plane/CANONICAL_ARCHITECTURE.md` — authority `CP-ARCH-001`.

This target authority defines the durable platform shape and roadmap. It does not replace chronological case gates or the current unique next action. New defects/intakes/owner changes must be inserted into the existing program with dependency analysis rather than starting a parallel program.
