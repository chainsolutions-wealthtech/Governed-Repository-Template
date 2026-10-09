# 00_GSCC_ENTRY — Mandatory pre-entry before START_HERE

> Status: APPLICABLE
> Repository authority: PRE-ENTRY / FIRST TOUCH / CONTINUATION GATE
> Applies to: every agent, assistant, automation, provider integration, conversation or tool surface that intends to enter this repository's governed workflow.

## Absolute entry rule

This file MUST be processed before `00_START_HERE.md`, `AGENTS.md`, project work, mutation planning, or governed execution.

A physical repository read is NOT the same as governed admission.

No agent may treat itself as admitted to the governed workflow merely because it can read repository content or invoke GitHub functions.

The mandatory order is:

```
ARRIVAL
→ 00_GSCC_ENTRY.md
→ classify FIRST_TOUCH | CONTINUATION | UNRESOLVED
→ expose all actually available provider/agent/runtime/tool context
→ mark unavailable expected provider facts as UNAVAILABLE
→ persist/emit GSCC arrival evidence through any supported transport
→ GSCC gates
→ GSE logical qualification
→ GACR durable continuity
→ valid GACR release/handoff
→ 00_START_HERE.md
→ normal governed repository workflow
```

## Read-only cold-start reconstruction aid

After this authority has been read, an arriving provider/chat/runtime surface MAY inspect the persisted history of a known logical agent before classification by using:

`scripts/gacr_agent_reconstruction.py`

Canonical composition contract:

`.governance/agent-reconstruction-skeleton.json`

Human-readable path:

`docs/control-plane/AGENT_RECONSTRUCTION_SKELETON.md`

This reconstruction is strictly read-only and projection-only. It may recover historical aliases, logical-agent/session/provider-context relationships, continuity bus references, work/claim/dispatch links, takeover/forensic evidence and checkpoint/handoff pointers.

It MUST NOT:
- classify the current arrival as CONTINUATION by itself;
- bind or resume a current session;
- create a logical identity, session, claim, dispatch or lease;
- grant admission, invocation or mutation authority.

The current arrival MUST still continue through the normal persisted GSCC → GSE → GACR → F1 gates using its own observable evidence.

## Machine-readable sequential router

This document is the human-readable authority for the canonical pre-entry router.

Machine-readable contract:

`.governance/gscc-entry-router.json`

Deterministic router:

`scripts/gscc_entry_router.py`

The router MUST emit exactly one next step at a time and MUST NOT execute that next step automatically.

Initial routing contract:

```text
ARRIVAL
→ READ_AUTHORITY: 00_GSCC_ENTRY.md
→ RUN_PERSISTED_ENTRY_PIPELINE
   → BUILD_OBSERVABLE_PACKET
   → PERSIST_PACKET_AND_CAPTURE_TO_SQLITE
   → CLASSIFY_FIRST_TOUCH: FIRST_TOUCH | CONTINUATION | UNRESOLVED
   → EVALUATE_ENTRY_CONTRACT
   → PERSIST_CLASSIFICATION_AND_HANDOFF
→ Q1
```

Failure at any required condition routes to:

```text
BLOCK_UNRESOLVED
→ STOP_FAIL_CLOSED
```

For the entry test, once this file has been read, the expected emitted next step is:

```text
CURRENT = 00_GSCC_ENTRY.md
ACTION = RUN_PERSISTED_ENTRY_PIPELINE
NEXT_STEP = Q1 only when READY_FOR_Q1
EXECUTE_NEXT_AUTOMATICALLY = FALSE
```

## Persistent entry database

The canonical entry pipeline MUST persist its observable packet, normalized capture, classification, blocking reasons and Q1 handoff state in SQLite before progression.

Runtime orchestrator:

`scripts/gscc_persisted_entry_pipeline.py`

Schema migration:

`.governance/control-plane-db/008_gscc_observable_entry_pipeline.sql`

A blocked or unresolved entry is also persisted. Persistence never grants mutation authority.

## Observable extraction layer


Before First Touch classification, the agent MUST build one normalized observable packet from:

1. provider / agent facts exposed by the host;
2. transport / connector facts exposed by the tool surface;
3. repository facts returned by GitHub.

Canonical extractor:

`scripts/first_touch_agent_transport_extractor.py`

Its output schema is:

`gscc-first-touch-observable-packet/v1`

Every expected field MUST be accounted for. A field not exposed by the runtime is recorded as `UNAVAILABLE`; it is never silently omitted or invented.

The extractor grants no mutation authority.

## Required arrival report

Before proceeding, the arriving agent MUST report every non-sensitive fact that its own environment actually exposes about:

- provider and product surface;
- agent/client/runtime/model when exposed;
- current tool/function name and operation class;
- conversation/session/run/task/job/workspace/thread/turn/message references when exposed;
- connection/transport/plugin/connector surface when exposed;
- authenticated GitHub actor or installation facts when exposed;
- target repository and requested ref/branch/HEAD when exposed;
- chronological first-operation facts;
- capabilities and explicit negative facts.

For every expected provider-side fact not exposed by the environment, use exactly:

`UNAVAILABLE`

Never fabricate, infer, synthesize or reconstruct provider-private identifiers from GitHub actor, repository, branch, SHA, issue, PR, workflow, URL or unrelated evidence.

Never expose tokens, passwords, cookies, authorization headers, private keys, client secrets or equivalent credential material.

## Evidence state vocabulary

Expected fields MUST resolve to one of:

- `PRESENT_VALID`
- `PRESENT_INVALID`
- `UNAVAILABLE`
- `UNKNOWN`
- `STALE`
- `CONTRADICTORY`
- `NOT_APPLICABLE`
- `OPTIONAL_MISSING`

Silent omission of an expected provider field is not permitted when producing canonical First Touch evidence.

Progression is:

```
FIELD
→ BLOCK
→ PRECONDITION
→ GATE / DECISION
→ STATE TRANSITION
```

There is no fixed rule requiring every expected field to be populated with a value.

## Arrival classification

The arriving agent MUST classify the connection as exactly one of:

### FIRST_TOUCH

Use only when the canonical logical identity is new and no prior First Touch exists.

Invariant:

`FIRST_TOUCH_COUNT(canonical logical identity) <= 1`

The First Touch snapshot is immutable after creation.

### CONTINUATION

Use when the arrival correlates strongly enough with an existing canonical logical identity.

Subsequent evidence enriches the living Conversation Evidence Profile and MUST NOT create a second First Touch.

### UNRESOLVED

Use when the environment does not expose enough truthful evidence to establish FIRST_TOUCH or CONTINUATION.

UNRESOLVED MUST fail closed for governed admission.

It MUST NOT be converted into a stable identity by guessing.

## Canonical correlation strength

Identity/correlation classification uses:

```
EXACT_IDENTITY
→ STRONG_CORRELATION
→ WEAK_CORRELATION
→ AMBIGUOUS
→ NEW_IDENTITY
```

Ambiguity fails closed.

GitHub actor identity alone is not sufficient to identify a ChatGPT conversation, agent session or provider connection.

## Supported evidence transports

GSCC admission authority is independent from transport.

Supported transports may include, when actually available:

- provider-side automatic dispatch;
- GitHub `repository_dispatch`;
- controlled plugin/tool wrapper;
- governed issue/comment bridge;
- host-side adapter;
- another repository-approved transport.

No transport is itself GSCC authority.

A transport failure or unavailable provider-side hook MUST remain explicit. It MUST NOT be reported as a successful First Touch.

## Canonical post-Q1 persisted route

After the persisted entry pipeline returns `READY_FOR_Q1`, progression is controlled by:

`.governance/gscc-post-q1-router.json`

and persisted by:

`scripts/gscc_post_q1_gate_router.py`

The mandatory chronological route is:

```text
Q1
→ Q3
→ Q4
→ Q5
→ Q8
→ Q9
→ Q10 / GSE initial SessionTwin
→ Q2 / GACR durable binding
→ Q6
→ Q7
→ Q11
→ Q12
→ F1
→ 00_START_HERE.md
```

Every gate transition is persisted in SQLite. A gate advances only on its canonical success outcome. Any other observed outcome fails closed and produces no next gate.

This route does not grant invocation or mutation authority.

## Canonical GSCC → GSE → GACR order

The canonical gate order is:

```
First Touch
→ GSCC
→ Q1
→ Q3
→ Q4
→ Q5
→ Q8
→ Q9
→ Q10 / GSE initial logical SessionTwin
→ Q2 / GACR durable binding
→ Q6 / Q7
→ Q11 / Q12
→ F1
→ governed workflow
```

Role boundaries:

```
GSCC = transport + collection + First Touch identity
GSE  = logical state interpretation
GACR = durable continuity
```

GSE must not be made dependent on premature GACR binding.

GACR must not be entered before the canonical GSE qualification point.

## Admission rule for START_HERE

`00_START_HERE.md` is NOT the first authority anymore.

It becomes applicable only after a valid GSCC → GSE → GACR progression and a durable release/handoff permits normal governed repository work.

Without such evidence:

```
START_HERE_STATUS = NOT_YET_APPLICABLE
NEXT_AUTHORITY = 00_GSCC_ENTRY.md
```

If the agent can read this file but cannot emit or persist the required GSCC evidence, it MUST state that limitation and remain `UNRESOLVED` rather than silently entering the normal workflow.

## No bypass

The following are forbidden:

- starting directly from `00_START_HERE.md`;
- treating a successful `get_repo`, `fetch_file` or other GitHub read as governed admission;
- inventing provider-private identity;
- treating repository metadata as provider identity;
- creating a second First Touch for an existing canonical identity;
- entering GACR before GSE qualification;
- using transport availability as execution authority;
- using this pre-entry layer to weaken existing exact-HEAD, claim, collision, CI, approval or non-regression rules.

## Release to normal governance

Only after valid release/handoff may the agent continue with:

`00_START_HERE.md`

From that point onward, all existing repository governance remains fully applicable and unchanged.
