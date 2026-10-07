# CONTROL PLANE CANONICAL MEMORY DATABASE

## Master architecture integration

Whole-system relationship: `docs/control-plane/MASTER_SYSTEM_MAP.md`.

Requirements/status/roadmap traceability: `docs/control-plane/REQUIREMENTS_ROADMAP.md`.

This document owns the data/interaction model. It does not own programme order or capsule routing semantics.

## Purpose

The control plane needs a durable memory that is both:
- auditable and reviewable in Git;
- queryable by a future web application.

The canonical model therefore uses **versioned SQL + JSON seeds** as Git authority and materializes a relational database for validation/runtime use.

The mutable SQLite binary is **not** committed as canonical state.

## Current implementation

Source-only directory:

`.governance/control-plane-db/`

Files:
- `001_schema.sql` — relational schema;
- `catalog.json` — reusable cases, modes, questions, options and activities;
- `runtime-seed.json` — current known repositories/runs/decisions/checkpoints/intakes;
- `materialize.py` — builds and validates a SQLite projection.
- `004_server_inventory_facts.sql` — normalized S1/S2 observation slots, freshness and provenance.
- `.governance/control-plane-state/server-inventory-facts.json` — versioned KBI-04D source facts, initially `NOT_COLLECTED`.

The same logical schema is intentionally suitable for later migration to PostgreSQL for the admin web application.

## Data domains

### 1. Catalogue / reusable design
- `framework_cases`
- `modes`
- `case_phases`
- `phase_dependencies`
- `questions`
- `question_options`
- `activities`

These tables answer: **What can the framework do and what does it ask?**

### 2. Execution / observed history
- `repositories`
- `runs`
- `run_answers`
- `decisions`
- `run_events`
- `evidence`
- `agent_sessions`
- `agent_activity_events`

These tables answer: **What happened for a concrete repository/run?**

### 3. Continuity / owner steering
- `checkpoints`
- `handoffs`
- `owner_feedback`
- `intakes`
- `artifacts`

These tables answer: **Where do we resume, what did the owner change, what evidence exists, and what external dependency remains?**

### 4. Server knowledge projection

`server_inventory_facts` carries the ten bounded S1/S2 observation slots from
KBI-04C. Each row contains a fact status and freshness class, an allowlisted
value if known, last successful provenance if any, last attempt provenance and
the source-memory revision. The materializer validates the source state first.
An initial source at revision 0 produces zero rows, not invented infrastructure
facts. A failed refresh preserves an older value as `KNOWN_STALE`, which does
not satisfy an execution preflight. The relational binary remains derived.

## First-touch probe observability projection

Additive migration `006_first_touch_probe_observability.sql` projects durable first-touch discovery records from
`docs/control-plane/probes/*.md` into the existing canonical relational materialization.

The projection deliberately uses three layers:

- `first_touch_probe_records` stores probe identity, correlation metadata, source path, document hash, counts, and the **complete raw Markdown document**;
- `first_touch_probe_lines` stores **every source line** with line number and section context, so no observation is lost when the normalization parser does not yet understand it;
- `first_touch_probe_observations` stores queryable key/value observations extracted from header metadata, bullet key/value fields, labelled values, and the `Raw anchor inventory`.

This design makes the relational projection exhaustive without pretending that every future provider-specific field is already modeled. The raw record and line projection are lossless; normalized observations are additive and can evolve.

The probe tables are evidence projections only. They do not grant session, claim, routing, function invocation, or mutation authority.

```text
first-touch discovery Markdown
        ↓
raw document + every line
        ↓
generic key/value observations
        ↓
SQLite materialization / validation
        ↓
future PostgreSQL projection
```

## Reuse across all cases

The same model is used for:
1. `CREATE_NEW_REPOSITORY`;
2. `ADOPT_EXISTING_REPOSITORY`;
3. `MAP_EXISTING_PROJECT`;
4. `LAB_EVOLUTION`.

`CONTINUE_GOVERNED_WORK` is represented as a post-case mode.

CASE 1 is currently the first fully populated replay dataset. Cases 2–4 are already registered in the catalogue and will progressively populate their phases/questions/activities as their tests are executed.

## Owner feedback as first-class data

Owner feedback is not free-floating chat history. It becomes a record with:
- run;
- phase;
- feedback class;
- content;
- execution effect;
- earliest affected phase;
- dependent revalidation list;
- source reference.

This supports controlled return to an earlier checkpoint without erasing history.

## Decision history

Decisions are append/supersede records rather than destructive updates.

A later decision may reference the previous decision via `supersedes_decision_id`. Historical choices remain queryable.

## Future admin web application

The future front-end can expose:
- case catalogue;
- current runs;
- questionnaire rendering from `questions/question_options`;
- activity/gate status;
- decisions and superseded decisions;
- checkpoints/handoffs;
- owner feedback and required revalidation;
- MCP/external intakes;
- artifacts and CI evidence;
- resume/continue actions.

No front-end is implemented yet. First we validate all workflows and populate the canonical model from real test evidence.

## Canonicality rule

```text
Git-versioned authorities + SQL migrations + JSON seeds
        ↓
deterministic relational materialization
        ↓
future PostgreSQL runtime
        ↓
admin web application
```

The application database must never become an untracked source of truth that contradicts Git governance. Runtime writes must be projected back into governed/versioned authorities or explicitly reconciled.

## Evolution rule

Database changes are additive migrations:
- `001_schema.sql`
- later `002_*.sql`, `003_*.sql`, etc.

Never silently rewrite historical schema semantics.


## Agent activity continuity

Every meaningful agent work session can now be represented independently from Git commits.

`agent_sessions` records:
- agent identity/provider/actor when known;
- workstream;
- source/pilot repository;
- observed HEADs;
- objective;
- status;
- unique next action;
- source reference.

`agent_activity_events` records:
- task/phase;
- event type;
- action/result;
- evidence;
- remarks/proposals through structured payloads;
- chronology.

This supports future admin views such as “who did what”, “what was discovered”, “what remains”, and “where to resume”.


## Canonical authority revisioning

Migration `003_canonical_authorities.sql` adds:

- `canonical_authorities`
- `canonical_authority_revisions`
- `canonical_memory_events`

`canonical_authorities` stores the stable identity and current revision pointer of durable authorities such as `CP-ARCH-001`.

`canonical_authority_revisions` preserves monotone revisions with subject HEAD, content hash, predecessor, reason and source decision.

`canonical_memory_events` provides append-oriented history for authority creation/revision and future memory events.

The initial authority is:

```text
CP-ARCH-001
→ CANONICAL_TARGET_ARCHITECTURE
→ docs/control-plane/CANONICAL_ARCHITECTURE.md
→ revision 1
```

## Complete runtime projection loaders

The deterministic materializer now supports the history tables already defined by the schema:

- `run_answers`
- `run_events`
- `evidence`
- `handoffs`
- `owner_feedback`
- `artifacts`
- canonical authority/revision/event records

This closes the gap where tables existed in SQL but could not be populated from the versioned seed.

## Target/current/history separation

```text
TARGET      → canonical architecture / accepted invariants
CURRENT     → current state / checkpoint projection
EXECUTION   → program / tasks / next action
CONTINUITY  → handoff / replay / agent activity
HISTORY     → decisions / events / evidence / owner feedback
```

A current projection may be regenerated; history must remain explainable and revisioned.


## Continuous projection rule

The relational database is built **while** the governance workflows are built; it is not a later reconstruction project.

For every durable structured change:

```text
OWNER / AGENT / WORKFLOW INFORMATION
        ↓
canonical Git authority / history
        ↓
relational seed/event projection
        ↓
deterministic materialization
        ↓
validation
```

Categories covered include:
- owner feedback;
- decisions and supersessions;
- agent sessions/activity;
- program/task/subtask changes;
- evidence;
- checkpoints;
- handoffs;
- intakes;
- artifacts;
- canonical authority revisions.

If a structured record cannot yet be represented by the current schema, it must be explicitly recorded as `PENDING_PROJECTION` and become a schema/migration task. Silent omission is forbidden.

This preserves the future Admin UI objective without allowing the UI/database to outrank Git authorities.


## Current LIVE identity/session chain and planned normalized registry

The original `agent_sessions` table is not the whole arrival/session model anymore.

The currently LIVE-proven pre-entry chain uses additive GSCC/GSE/GACR structures, including:
- GSCC conversation identities and First Touch snapshots;
- per-arrival `gscc_arrival_ref` / `connection_ref`;
- per-arrival durable state scope;
- GSE SessionTwin;
- explicit GSCC/GSE/GACR binding;
- canonical GACR durable session;
- persisted runtime/gate evidence through Q12/F1/release.

Current runtime relationship:

```text
CONTROLLED ARRIVAL
→ GSCC ARRIVAL / CONNECTION
→ GSCC LOGICAL IDENTITY
→ GSE SESSION TWIN
→ CANONICAL GACR SESSION
→ Q12 / F1 / RELEASE EVIDENCE
```

This chain is LIVE proven through `IDN-006`.

A **broader normalized relational registry** is still planned for common GMC/ARCH/API use. It separates:

```text
PRINCIPAL  = authenticated external identity/account
AGENT      = acting agent/provider identity
CONNECTION = one observed arrival/event
SESSION    = governed continuity/resume unit
ROLE       = responsibility model
AUTHORITY  = separately observed permission/mutation envelope
```

Target normalized relational entities still include:
- `principals`;
- `agents`;
- `connections`;
- `governed_sessions`;
- `session_identity_bindings`;
- `session_authority_snapshots`;
- `session_events`.

These future entities must **reuse/migrate compatibly from the LIVE GSCC/GSE/GACR chain**. They must not create a second session truth or replay First Touch. GACR remains the durable continuity authority until an explicitly governed migration changes that contract.

## Planned two-stage purpose routing data

The automated source-entry router adds three durable questionnaire fields:

- `entry_purpose`
  - `WORK_ON_CONTROL_PLANE`
  - `APPLY_GOVERNANCE_CASE`
- `control_plane_work_kind`
  - `CODE_IMPLEMENTATION`
  - `EXECUTE_EXISTING_TASK`
  - `ADD_OR_ENRICH_INFORMATION`
- `selected_structuring_case`
  - `CREATE_NEW_REPOSITORY`
  - `ADOPT_EXISTING_REPOSITORY`
  - `MAP_EXISTING_PROJECT`
  - `LAB_EVOLUTION`

These choices are stored as governed answers/events and must be resumable. A reconnecting session resumes at the first unresolved applicable question/action instead of replaying completed questions.

The existing active `entry_action` router is preserved until the two-stage router is implemented and regression-tested. The new fields are currently target/planned semantics, not a silent runtime behavior change.

Human users provide decisions/approvals only; the system performs authorized technical actions.

## Governance Model Catalogue extension

Decision authorities: `CPD-025`, `CPD-026`, `CPD-027`.

Canonical model authority: `CP-GOVMODEL-001`.

The existing relational memory will be extended additively after the current CASE 1 dependency chain permits execution. The target extension covers one shared governance-model catalogue for domains, capabilities, components, objects, fields, relationships, states, transitions, workflows, controls, gates, evidence types, failures/recoveries, implementation mappings, tests and dependencies.

Planned implementation rule:

```text
versioned governance-model authority/catalogue
+ next additive SQL migration
        ↓
existing materialize.py
        ↓
SQLite validation projection
        ↓
future PostgreSQL projection
```

A second canonical database or second materializer is forbidden. Until the schema extension exists, the detailed catalogue is explicitly `PENDING_PROJECTION` and its accepted target is stored in `CP-GOVMODEL-001`.


## First-touch field / block / gate evidence model

First-touch observability is stored in the existing canonical control-plane database. It does not create a second database authority.

Migration `007_first_touch_field_block_gate.sql` adds:

- `first_touch_capture_records` — complete raw capture plus capture identity/digests/counts;
- `first_touch_capture_nodes` — one row for every JSON path/node;
- `first_touch_capture_api_attempts` — every complementary API attempt, including denied/unavailable results;
- `first_touch_evidence_blocks` — B00–B30 evidence-block catalogue;
- `first_touch_process_gates` — capture, Q1–Q12, post-authorization and continuity gates;
- `first_touch_gate_requirements` — block requirements per gate;
- `first_touch_field_assignment_rules` — additive path-to-block rules;
- `first_touch_field_block_membership` — many-to-many field usages;
- `first_touch_capture_block_status` — per-capture evidence completeness;
- `first_touch_gate_evaluations` — evidence readiness only.

The mandatory no-loss invariant is:

```text
every captured JSON node
→ stored in first_touch_capture_nodes
→ has B00 RAW_CAPTURE_PROVENANCE membership
→ may have zero or more additional functional memberships
```

No field is dropped because it lacks an immediate GSCC/GSE/GACR use.

A gate evaluation of `EVIDENCE_READY_FOR_CANONICAL_VALIDATION` grants no authority. Canonical GSCC admission, Access Grant, function-exposure, exact-HEAD, claim and takeover validators remain authoritative.

See `docs/control-plane/FIRST_TOUCH_FIELD_BLOCK_GATE_MODEL.md`.
