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
| CPD-012 | 2026-09-26 | Every meaningful agent work session must persist observed HEADs, claimed task, actions, evidence/results, defects discovered, remarks/proposals and next action; Git commits alone are insufficient as the agent-work ledger. | ACCEPTED |
| CPD-013 | 2026-09-26 | Newly discovered tasks/subtasks must enter the canonical task queue before later workflow progression, preserving dependencies and a single executable next action. | ACCEPTED |
| CPD-014 | 2026-09-26 | `docs/control-plane/CANONICAL_ARCHITECTURE.md` (`CP-ARCH-001`) is the source-only durable target-architecture authority for the Governed Repository Platform. It defines four structuring cases plus `CONTINUE_GOVERNED_WORK` as a post-case mode and must never be confused with live current state. | ACCEPTED |
| CPD-015 | 2026-09-26 | Canonical memory evolves by append/supersede/revalidate: durable event/history records coexist with current projections, and canonical authorities use monotone revision history rather than silent replacement. | ACCEPTED |
| CPD-016 | 2026-09-26 | Git-versioned governed authorities remain foundational; SQL/JSON materialization, future PostgreSQL, API and Admin UI are projections/control surfaces and may not silently become independent sources of truth. | ACCEPTED |
| CPD-017 | 2026-09-26 | Agent/task lineage follows Architecture → Program → Case/Workstream → Phase → Integration Slot → Task → Subtask; new intake, defects and owner changes enrich the existing program instead of replacing it with parallel work. | ACCEPTED |
| CPD-018 | 2026-09-26 | Workflow semantics and the four case paths must be validated before Governance API/PostgreSQL/Admin UI implementation; frontend remains intentionally downstream of case stabilization. | ACCEPTED |
| CPD-019 | 2026-09-26 | Canonical memory and relational projection evolve together: every durable structured change (owner feedback, decision, agent activity, task/program change, evidence, checkpoint, handoff, intake, artifact or authority revision) must be persisted in Git authorities and, when representable by the relational model, projected into the versioned database seed/event model in the same governed change or explicitly marked pending projection. | ACCEPTED |
| CPD-020 | 2026-09-26 | Agent entry identity must separate PRINCIPAL, AGENT, CONNECTION and SESSION. Authenticated account data and permission snapshots should be captured automatically when available, then used to create/resume a stable governed session before role/authority/routing. Ambiguity fails closed; identity or role never creates authority. | ACCEPTED |
