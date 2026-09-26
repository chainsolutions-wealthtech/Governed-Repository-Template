# CONTROL PLANE CANONICAL MEMORY DATABASE

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
