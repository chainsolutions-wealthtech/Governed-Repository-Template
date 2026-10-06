# First-Touch Field → Evidence Block → Process Gate Model

Status: `CANONICAL DATA MODEL EXTENSION`

## Purpose

Every safely captured first-touch datum is preserved before architectural selection and may contribute to one or more later evidence blocks.

The model is:

```text
CAPTURED JSON PATH
        ↓ 0..N functional memberships + mandatory B00 preservation
EVIDENCE BLOCK
        ↓
PROCESS GATE EVIDENCE
        ↓
CANONICAL VALIDATOR
        ↓
possible state transition
```

A capture-derived gate result never grants authority. It only states whether the captured evidence is ready to be presented to the canonical validator for that gate.

## No-loss invariant

Every JSON node is stored in `first_touch_capture_nodes`.

Every node is assigned to:

```text
B00 — RAW_CAPTURE_PROVENANCE
```

Additional rule matches are additive. No functional classification removes the B00 membership or raw value.

An unknown or not-yet-understood field therefore remains both queryable and usable later.

## Evidence blocks

The catalogue defines B00 through B30:

```text
B00 RAW_CAPTURE_PROVENANCE
B01 PLATFORM_PROVIDER_SURFACE
B02 PRINCIPAL_ACTOR_IDENTITY
B03 CLIENT_APP_INSTALLATION
B04 CONNECTION_IDENTITY
B05 REPOSITORY_IDENTITY
B06 REF_BRANCH_HEAD
B07 EVENT_FIRST_TOUCH_SUBJECT
B08 WORKFLOW_RUN_JOB
B09 PERMISSIONS_ACCESS_OBSERVABILITY
B10 CAPABILITY_TOOL_SURFACE
B11 SESSION_BINDING
B12 CONTROL_CHANNEL
B13 LIVENESS
B14 ACTIVITY
B15 PROGRESS
B16 CHECKPOINT_CONTEXT
B17 TASK_WORK_ITEM
B18 CLAIM_COLLISION_DOMAIN
B19 GOVERNANCE_READ
B20 ADMISSION_PREAUTHORIZATION
B21 QUALIFICATION
B22 ACCESS_POLICY
B23 ACCESS_GRANT
B24 FUNCTION_EXPOSURE
B25 PRECALL_MUTATION_AUTHORITY
B26 CONTINUITY
B27 FORENSICS_INTERRUPTION
B28 TAKEOVER_HANDOFF
B29 ADDRESSABILITY_WAKE
B30 UNAVAILABLE_NEGATIVE_EVIDENCE
```

A field may belong to several blocks. For example repository/ref/workflow evidence may simultaneously support first-touch provenance, repository identity, exact-HEAD reconciliation and later continuity checks.

## Process gates

The model records evidence requirements for:

```text
G00 capture preserved
Q1  admission envelope validation / preauthorization decision
Q2  canonical session binding
Q3  required governance read
Q4  current repository baseline
Q5  exact HEAD
Q6  task reconciliation
Q7  claim/collision reconciliation
Q8  capability testing
Q9  GSCC control challenge
Q10 GSE initial session state
Q11 access policy
Q12 Access Grant
F1  function exposure
F2  pre-call revalidation
C1  continuity evaluation
T1  takeover/handoff
```

The requirement matrix is versioned in:

`.governance/control-plane-state/first-touch-field-block-gate-catalog.json`

## Preauthorization invariant

`PREAUTHORIZED` is not inferred from field presence.

First-touch evidence can make Q1:

`EVIDENCE_READY_FOR_CANONICAL_VALIDATION`

but only the existing canonical GSCC admission validator may issue a PREAUTHORIZED admission receipt.

Therefore:

```text
captured evidence
!= PREAUTHORIZED

PREAUTHORIZED
!= repository access

PREAUTHORIZED
!= function exposure

PREAUTHORIZED
!= invocation authority

PREAUTHORIZED
!= mutation authority
```

The same separation applies to Q12, function exposure, pre-call revalidation and takeover.

## Database tables

Migration:

`.governance/control-plane-db/007_first_touch_field_block_gate.sql`

Tables:

```text
first_touch_capture_records
first_touch_capture_nodes
first_touch_capture_api_attempts
first_touch_evidence_blocks
first_touch_process_gates
first_touch_gate_requirements
first_touch_field_assignment_rules
first_touch_field_block_membership
first_touch_capture_block_status
first_touch_gate_evaluations
```

The raw JSON remains in `first_touch_capture_records.raw_json`; normalized paths are additive projections and never replace it.

## Runtime artifact

For each observable first touch, the workflow produces:

```text
first-touch-capture-<run-id>-<attempt>/
├── first-touch-capture.json
└── first-touch-capture.sqlite
```

The SQLite contains the capture, field memberships, block status and gate evidence readiness for that exact capture.

## Status semantics

Block statuses:

```text
EMPTY
PARTIAL
PRESENT
SUFFICIENT
VERIFIED
CONFLICTING
STALE
UNAVAILABLE
```

Capture classification can establish evidence presence/sufficiency. Runtime/canonical validators are still responsible for semantic verification when required.

Gate evidence statuses:

```text
BLOCKED
EVIDENCE_PARTIAL
EVIDENCE_READY_FOR_CANONICAL_VALIDATION
```

There is intentionally no `AUTHORIZED` state in this projection.

## Layer relationship

```text
CAPTURE
  ↓
GSCC transports / admission / control evidence
  ↓
GSE interprets session-state evidence
  ↓
GACR governs continuity / claims / exact-HEAD takeover
  ↓
Governed repository execution
```

The field/block/gate database is an evidence model. It does not replace GSCC, GSE, GACR, admission, claims, exact-HEAD authority or function exposure.
