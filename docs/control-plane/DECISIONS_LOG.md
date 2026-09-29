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
| CPD-021 | 2026-09-26 | After identity/session resolution on the control-plane source, routing is two-stage: first choose `WORK_ON_CONTROL_PLANE` or `APPLY_GOVERNANCE_CASE`; then either choose the control-plane work kind (`CODE_IMPLEMENTATION`, `EXECUTE_EXISTING_TASK`, `ADD_OR_ENRICH_INFORMATION`) or choose exactly one of the four structuring cases. Human participation is limited to answers/explicit approvals required by governance; authorized technical execution is automated by the system. | ACCEPTED |
| CPD-022 | 2026-09-26 | `chainsolutions-wealthtech/Governed-Repository-Template` is the product/framework and sole target of framework evolution. Repositories such as `Patricked-code/Gouvern` are external pilot/validation fixtures for exercising governance cases; their project state may reveal generic defects but must never become the framework architecture, roadmap, canonical program, or implementation target. Generic defects are fixed in the Template first, then validated on pilots. | ACCEPTED |
| CPD-023 | 2026-09-26 | Governed client upgrades derive the release version from the Template manifest, synchronize only reusable/static governance runtime-test-policy surfaces required by the current client CI, preserve mutable client project/session/work/answer state, and make source-only CI steps skip cleanly on clients. A pilot must never be patched to compensate for an incomplete Template upgrade surface. | ACCEPTED |
| CPD-024 | 2026-09-26 | Any self-test that simulates a fresh template/bootstrap from an instantiated client must rebuild every bootstrap-influencing synthetic state (profile, project-profile, infrastructure, local-entry, MCP binding, access plan, workflow model, work-items, claims, sessions and canonical-memory pointer) inside the temporary fixture. Real client state is never rewritten, and subprocess failures must expose diagnostic stdout/stderr. | ACCEPTED |

| CPD-025 | 2026-09-27 | The central Governance Model is a first-class reusable authority distinct from CREATE/ADOPT/MAP/LAB. The four structuring cases consume the model and must not silently redefine generic governance semantics. | ACCEPTED |
| CPD-026 | 2026-09-27 | Governance Model cataloguing extends the existing Git-versioned SQL/JSON relational memory and existing materializer. No second canonical database, duplicate memory subsystem or competing source of truth may be introduced. | ACCEPTED |
| CPD-027 | 2026-09-27 | The Governance Model Catalogue completion programme is recorded now as dependency-bound canonical backlog. It preserves the current CASE 1 unique executable task; catalogue execution follows CASE 1 closure and is organized as GMC-01..GMC-19 / phases A..G, before cross-case industrialization and API/UI work. | ACCEPTED |

| CPD-028 | 2026-09-27 | The 19 GMC identifiers are chronological work packages/groups, not atomic tasks. Before any GMC implementation, each group must receive an execution blueprint defining mission, objective, questions to resolve, prerequisites, exact sources/paths/symbols/tests/decisions to inspect, search order/method, atomic tasks/subtasks, classification rules, expected findings, outputs, canonical storage destination, required evidence, validation, DONE/HOLD criteria, and downstream consumers. Results produced by one group become versioned inputs for later groups. This preparation is planning only and must not start implementation. | ACCEPTED |

| CPD-029 | 2026-09-27 | Governance Model work-package progression is output-driven, not status-driven. Every GMC group must model three dependency dimensions — TASK_DEPENDENCY, ARTIFACT_DEPENDENCY and EVIDENCE_DEPENDENCY. Group results become persistent, versioned knowledge artifacts with stable IDs, provenance, validation state, producer, downstream consumers and append/supersede/revalidate history. Each group has explicit exit controls. GMC-G19 must assemble the complete Governance Model and separately demonstrate model completeness, consistency, reference integrity, implementation traceability, test/evidence/dependency coverage, reusability and CREATE/ADOPT/MAP/LAB compatibility before Governance Model 1.0.0 may be released. This remains planning-only until separately authorized. | ACCEPTED |

### CPD-030 — Configuration intent never authorizes discovery execution

- Date: 2026-09-29.
- Decision: owner answers describing MCP linkage, transport, endpoint, discovery scope, domain strategy or runtime mutation policy enrich configuration only.
- They do not authorize credential provisioning or a network discovery call.
- A concrete read-only discovery plan must be presented and explicitly approved before execution.
- Material changes to that plan, including endpoint recovery, invalidate prior discovery approval.
- Legacy pre-approval discovery evidence is preserved in history and the state re-enters the approval gate.
- This is additive to the existing local-entry, authority, exact-HEAD and Loop Engineering model.

### CPD-031 — Adaptive questionnaire feeds the existing Loop Engineering

- Date: 2026-09-29.
- Decision: no new questionnaire engine, task engine or parallel governance source is introduced.
- CREATE/ADOPT/MAP/LAB reuse the common Governance Model and existing project memory.
- Fresh observed facts and prior owner answers are reused instead of being re-asked.
- Only unknown facts or owner decisions are requested one at a time.
- Answers/observations enrich the project/resource model, classify resources as existing/unknown/planned/to-create/to-configure/to-verify, and derive prepared work-items, dependencies and authority requirements.
- Those prepared work-items are executed later by the existing Loop Engineering when their dependencies and authority gates make them READY.

### CPD-032 — Signed MCP SSH broker profile is factual recovery evidence

- Date: 2026-09-30.
- Decision: when the authenticated MCP repository-SSH broker signs a certificate for a host/port/username that differs from the configured non-secret SSH profile, the signed profile is treated as observed factual evidence.
- The Template must reopen SSH-profile recovery instead of blindly retrying the same configuration.
- The prior discovery evidence is archived, the corrected profile becomes configuration, and prior discovery approval is invalidated because the target is a material plan element.
- This does not grant SSH write authority.

### CPD-033 — Persistent MCP capability image feeds existing Loop Engineering

- Date: 2026-09-30.
- Decision: the central Template will maintain a source-only, versioned last-known MCP capability snapshot.
- The snapshot is refreshable through authorized read-only discovery when missing, stale, contradicted or required by a pending operation.
- It captures non-secret MCP identity/protocol, servers, tools/resources and their declared read/write surfaces, observed evidence, freshness/provenance, plus derived case-to-capability and prepared-operation mappings.
- It is knowledge/planning authority only: it never grants mutation authority and never stores tokens, private keys or secret values.
- CREATE, ADOPT, MAP, LAB and CONTINUE consume this knowledge through the existing project model/work-items/Loop Engineering. No parallel governance or task engine is created.
- MCP-side changes are not requested merely to maintain this snapshot; no new MCP intake is created unless a concrete missing external capability later blocks an authorized action.
- Relational projection is explicitly pending the scheduled Governance Model integration rather than creating a parallel database.
