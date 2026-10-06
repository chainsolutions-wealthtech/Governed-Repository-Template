# GSCC → GSE → GACR Realignment Matrix

Status: `BOUNDED REALIGNMENT AUTHORITY — ISSUE #199`

## Purpose

This document makes explicit the non-destructive target dependency order already supported by the historical architecture:

```text
FIRST TOUCH / CAPTURE
        ↓
GSCC
        ↓
GSE
        ↓
GACR
        ↓
GOVERNED REPOSITORY
        ↓
existing governed workflow
```

Historical contract:

```text
GSCC transports.
GSE interprets.
GACR governs continuity.
```

The realignment preserves all useful work from the admission, harvester, binding, control, GSE, GACR, access and function-exposure tranches. It changes ownership/dependency only where a later durable-continuity concern became a hard prerequisite for an earlier interpretation concern.

## Core rule

A datum can legitimately exist at several semantic levels without transferring authority:

```text
observed evidence            → GSCC
interpreted logical state    → GSE
durable continuity state     → GACR
governed execution authority → downstream governed workflow
```

Therefore:

```text
GSCC_CONNECTION_CONTEXT
!= GSE_SESSION_TWIN
!= GACR_CONTINUITY_SESSION
!= GOVERNED_WORK_AUTHORITY
```

## Why realignment is required

The original GSCC/GSE integration established GSE as a deterministic SessionTwin engine fed by evidence/events. Later live qualification work solved a real correlation problem between an Admission connection and an independently observed GACR connection. PR #164 introduced canonical admission→GACR session binding, and PR #163 subsequently reconciled that binding into its Q1→Q12 harvester path.

The current admission harvester therefore resolves a GACR session before projecting the initial GSE admission state. The current `QUALIFICATION_REQUIREMENTS["session"]` also requires a BOUND canonical GACR session. The current field/gate catalogue then encodes Q2/Q6/Q7 as GACR-owned gates before Q10 GSE initial state.

That implementation solved correlation and liveness/control proof requirements, but it also made durable GACR continuity a hard prerequisite for initial GSE interpretation. This matrix separates those concerns without deleting any of the useful mechanisms.

## Mandatory entry contract before Q1

Every observable repository touch is now subject to a pre-Q1 entry contract:

```text
OBSERVABLE EVENT / ACTION
        ↓
IDENTIFY OR CORRELATE CONVERSATION
        ↓
FIRST TOUCH | CONTINUATION | UNRESOLVED
        ↓
AUTO-COLLECT
        ↓
NORMALIZE INTO THE COMMON B00–B30 FIELD/BLOCK SCHEMA
        ↓
STORE VALUES AS THIS CONVERSATION'S INSTANCE
        ↓
COMPLETENESS + REQUIRED-BLOCK EVALUATION
        ↓
ENTRY_READY_FOR_Q1
        ↓
Q1
```

The schema and block definitions are common to all conversations. Values and statuses are conversation-scoped.

There is no fixed numeric field-count threshold. A conversation may proceed only when every expected field is accounted for and the required entry blocks satisfy their policies. Missing, unavailable, denied, stale, conflicting or not-applicable values remain explicit rather than disappearing.

A GitHub actor plus repository is not a conversation identity. A First Touch requires an EXACT or STRONG conversation-scoped anchor. Ambiguous identity blocks progression and must not create a second First Touch.

A known identity is classified as CONTINUATION and must enrich/revalidate its existing conversation profile instead of creating a new First Touch.

The machine-readable contract is:

`.governance/control-plane-state/first-touch-entry-contract.json`

The evaluator is:

`scripts/first_touch_entry_contract.py`

The Observable Arrival workflow evaluates this contract before calling the canonical GSCC arrival gateway.

## Target process ordering

Stable gate identifiers are preserved. Their identifiers are not treated as execution ordinals.

```text
G00  CAPTURE_PRESERVED
 ↓
Q1   GSCC admission validation
 ↓
Q3   governance read
 ↓
Q4   repository baseline
 ↓
Q5   exact HEAD
 ↓
Q8   capability testing
 ↓
Q9   GSCC control challenge
 ↓
Q10  GSE initial SessionTwin
 ↓
Q2   GACR durable canonical session bind/reconcile
 ↓
Q6   durable task/work correlation
 ↓
Q7   durable claim/collision evidence reconciliation
 ↓
Q11  access policy
 ↓
Q12  bounded Access Grant
 ↓
F1   function exposure
 ↓
F2   governed pre-call revalidation
 ↓
C1/T1 ongoing continuity / handoff / takeover
```

The target execution order is stored machine-readably in:

`.governance/control-plane-state/gscc-gse-gacr-realignment.json`

## Block interpretation

The existing B00–B30 stable block identifiers are retained.

Some blocks are single-layer concerns. Others are explicitly cross-layer and must be interpreted by semantic level instead of assigning the whole subject to one subsystem.

Examples:

```text
B11 SESSION_BINDING

pre-GSE:
  GSCC connection/logical-session context

post-GSE:
  GACR durable canonical session correlation
```

```text
B13 LIVENESS

GSCC:
  heartbeat / challenge / response evidence

GSE:
  logical liveness interpretation

GACR:
  durable lease / continuity history
```

```text
B17 TASK_WORK_ITEM

GSCC:
  observed task/work hints

GSE:
  interpreted/qualified work context

GACR:
  durable correlation

Governed workflow:
  actual work/claim authority
```

The same observed → interpreted → durable → governed-authority separation applies to claim/collision, checkpoint/context and addressability data.

## Q10 target input contract

The initial GSE SessionTwin must be constructible from GSCC-owned or cross-layer evidence that exists before durable GACR continuity.

Initial target inputs:

- B04 connection identity / GSCC connection context;
- B05 repository identity;
- B06 branch/ref/exact HEAD;
- B12 control-channel evidence;
- B13 observed liveness evidence.

A GSE initial state must **not** require as hard prerequisites:

- a pre-existing canonical GACR session identifier;
- a GACR active lease;
- B26 durable continuity.

GACR may later reconcile an existing durable session against the new GSE state or establish a new durable continuity session.

## Existing-session preservation

The #164 binding/correlation logic is not discarded.

Target behavior:

```text
GSCC evidence
    ↓
GSE initial state
    ↓
GACR continuity reconciliation
    ├─ existing compatible session → correlate/reuse
    └─ no compatible session       → establish durable continuity
```

Ambiguous correlation remains fail-closed.

Exact-HEAD, lease, replay, challenge/ACK/response, takeover and claim safety rules remain preserved where their authority legitimately applies.

## ~1500-field handling

No field is removed merely because ownership changes.

Every captured node continues to belong to B00. Functional memberships remain additive.

Each field is ultimately classified by:

```text
source
collection method
observed_at
provenance
freshness
availability
block membership
GSCC use
GSE use
GACR use
governed-workflow use
gate contribution
transition effect
failure/contradiction behavior
```

The realignment therefore reuses the existing collection surface instead of building a second collector.

## Downstream boundary

GSCC/GSE/GACR do not replace the existing governed repository workflow.

The output junction remains:

```text
GSCC evidence
+
GSE SessionTwin
+
GACR durable continuity package
+
field/block/provenance/freshness evidence
        ↓
Governed Repository
        ↓
Governed Local Entry
        ↓
FIRST_AGENT_BOOTSTRAP | NORMAL_GOVERNED_ENTRY
        ↓
existing governed workflow
```

Already-known and fresh evidence may be reused downstream; stale evidence is revalidated; missing evidence is collected; contradictions fail closed or enter reconciliation.

## Execution boundary

This tranche changes no runtime behavior.

The next runtime tranche must first add tests proving that an initial GSE state can be built from GSCC connection/evidence context without a pre-existing GACR continuity session. Only after those tests are RED may the runtime adapter/harvester be changed.

P12-S6, CASE 1, GMC and Step 13B remain untouched.
