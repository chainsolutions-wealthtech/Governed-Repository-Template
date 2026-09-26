# CONTROL PLANE DECISIONS LOG

Append-only durable decisions for the source/control-plane repository.

| ID | Date | Decision | Status |
|---|---|---|---|
| CPD-001 | 2026-09-26 | Separate source/control-plane memory from distributed project-state templates. | ACCEPTED |
| CPD-002 | 2026-09-26 | GitHub issues are orchestration/evidence surfaces; source-only versioned authorities carry durable control-plane continuity. | ACCEPTED |
| CPD-003 | 2026-09-26 | `Patricked-code/MCP` remains an external independently governed dependency; this framework workstream may observe it and create intakes, but must not implement MCP changes. | ACCEPTED |
| CPD-004 | 2026-09-26 | A meaningful control-plane work boundary must persist current state, tasks, next action and checkpoint/handoff before a new conversation/agent resumes. | ACCEPTED |
| CPD-005 | 2026-09-26 | Source-only control-plane memory must be removed during client initialization and must be CI-tested against leakage. | ACCEPTED |
| CPD-006 | 2026-09-26 | Root `STATUS.md`, `SUIVI.md`, `NEXT_ACTION.md`, `HANDOFF.md` and generic machine projections remain distributed client templates and are not repurposed as source history. | ACCEPTED |
| CPD-007 | 2026-09-26 | Canonical chronological gates must not be compressed: STEP 4 normal-entry proof on the pilot precedes STEP 5 fresh-repository E2E. | ACCEPTED |
| CPD-008 | 2026-09-26 | `CREATE_NEW_REPOSITORY` must adapt to owner choices: MCP linking is optional; if enabled, `DIRECT_MCP_TOKEN`, `SSH`, or `BOTH` may be selected. `BOTH` is never mandatory merely because the framework supports it. | ACCEPTED |
| CPD-009 | 2026-09-26 | Canonical control-plane memory gets a reusable relational projection shared by all structuring cases; Git-versioned SQL/JSON remain auditable authority while mutable DB binaries are not canonical. | ACCEPTED |
| CPD-010 | 2026-09-26 | Future admin web UI will consume the relational model only after all structuring cases/parcours are validated; no premature front-end will define workflow semantics. | ACCEPTED |
| CPD-011 | 2026-09-26 | Owner feedback, decisions, checkpoints, handoffs, evidence and intakes are first-class relational records so workflows can return/revalidate without erasing history. | ACCEPTED |
