# CONTROL PLANE PROGRAM

## Purpose

This file is the durable source-only program authority for development of `Governed-Repository-Template`.

It does not replace the generic entry-action policy distributed to clients.

## Active program

`CREATE_NEW_REPOSITORY_COMPLETION`

Operational issue: `#12`.

Current checkpoint: `STEP_4_SECOND_FRESH_REPOSITORY_E2E`.

The second fresh-repository test is temporarily gated by work package `SG-20260926-001` so that the control plane first becomes self-governed.

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
- `docs/control-plane/TASKS.md`: durable work queue.
- `docs/control-plane/NEXT_ACTION.md`: unique resumable action.
- `docs/control-plane/DECISIONS_LOG.md`: durable decisions.
- `docs/control-plane/SUIVI.md`: chronological history.
- `.governance/control-plane-state/*.json`: deterministic machine projections.
- Git commits/CI: execution evidence.
- GitHub issues: orchestration and external interaction evidence.
