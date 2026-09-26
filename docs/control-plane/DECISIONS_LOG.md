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
