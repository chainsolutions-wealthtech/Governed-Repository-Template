# GACR Presence-First / Acceptance Test Architecture

> Authority family: `CP-AGENT-RELAY-001`
>
> Role of this artifact: implementation-ready design for GACR Origin Realignment steps 4 through 12.
>
> Baseline observed before authoring: `main = 6a32debcc96d7c33b421dc901c514f79a4d05104`.
>
> Status: **PREPARED / NOT_EXECUTED**.
>
> This document is not evidence that steps 4-12 are DONE. It changes no runtime, workflow, production script, schema, session state, claim state, takeover state, Beacon state, Correlator state, Forensics state or Dispatcher state.
>
> Preconditions for implementation: preserve the attested R1-R6 baseline and consume the final `ORIGINAL_INTENT ↔ CURRENT_IMPLEMENTATION ↔ GAP` matrix after it is merged/reobserved.

## 0. Scope and invariants

This artifact prepares exactly the corrective Presence-First architecture and acceptance contract required by `docs/control-plane/GACR_ORIGIN_REALIGNMENT.md` steps 4-12.

It does not replace Beacon, Watch, Correlator, Interruption Forensics or Dispatcher. It places a Presence Fabric in front of those canonical capabilities.

Hard invariants:

1. A governed agent must not need to remember to invoke GACR before GACR can know that the agent exists on an instrumentable access surface.
2. Internal transport is never an agent identity.
3. Missing provider-private metadata remains `UNAVAILABLE`; it is never invented.
4. A connection fingerprint is a continuity/correlation key, never a provider conversation ID.
5. Heartbeat/liveness evidence is not progress evidence.
6. Ambiguous repository activity remains unbound; it is never assigned arbitrarily.
7. Silence may drive governed stall state transitions, but silence alone never establishes an external cause.
8. Existing claim, collision-domain, exact-HEAD and takeover authority gates remain authoritative.
9. No cookies, tokens, passwords, authorization headers, secret material, raw transcript content or private reasoning may enter Presence evidence.
10. Proprietary silent reads cannot be made observable by repository code alone; they require a provider/client/gateway adapter if automatic observation is desired.

---

# STEP 4 — R4-R6 drift analysis

**Status: PREPARED / NOT_EXECUTED**

## 4.1 Original center of gravity

The intended center is:

```text
REPOSITORY ACCESS
→ PRESENCE OBSERVATION
→ CREATE / RESUME SESSION
→ PRESENCE / ACTIVITY EVIDENCE
→ existing BEACON / WATCH / CORRELATOR / FORENSICS / DISPATCHER
```

The repository interaction is the trigger where an access path is instrumentable. Explicit telemetry remains useful enrichment, but it must not be the only way the system discovers a governed agent.

## 4.2 What R4 genuinely achieved

R4 introduced a real automatic-attachment primitive in `scripts/gacr_auto_attach.py`.

It can create/resume a session from these anchors, in priority order:

1. explicit client/provider metadata;
2. a fresh active Conversation Chronicle;
3. a GitHub Actions execution identity that is not the internal GACR workflow.

This is genuine Presence-First behavior in two bounded cases:

- a fresh Chronicle already exists and provides a stable `chronicle_id + current_session` anchor;
- an external GitHub Actions worker executes with observable repository/actor/run metadata.

R4 also correctly keeps provider conversation metadata unavailable when it is not supplied and later enriches the same connection-bound session instead of duplicating it.

## 4.3 Where R4 is not yet a general Presence Fabric

The current auto-attach primitive is invoked by an event transport; it is not itself an observer of every repository access path.

Current `push` handling routes the internal `Governed Agent Continuity Relay` workflow to `auto-attach`, while `gacr_auto_attach.py` deliberately excludes that workflow from becoming a GitHub Actions agent identity. This correction prevents the transport from fabricating a session, but it also means that the original repository actor represented by the triggering event is not yet modeled as a separate Presence Observation source.

Therefore:

```text
push event arrives
→ internal GACR workflow executes
→ internal workflow correctly cannot identify itself as agent
→ fresh Chronicle may still provide an anchor
→ otherwise auto-attach may SKIP
```

That is safe, but it is not the final Presence-First objective.

A future Presence Observer must distinguish:

```text
EVENT SUBJECT / REPOSITORY ACTOR
!=
GACR TRANSPORT EXECUTOR
```

and may use the former as evidence without ever treating the latter as the agent.

## 4.4 R5 drift toward explicit event transport

R5 adds `scripts/gacr_client_emitter.py`.

The emitter is valuable and must remain canonical. It emits:

- `gacr_auto-attach`;
- `gacr_heartbeat`;
- `gacr_beacon`;

through GitHub `repository_dispatch`.

However, liveness/action observation exists only when a host/client process explicitly runs the emitter or an equivalent adapter.

Current dependency chain:

```text
CLIENT / HOST
→ emitter runs
→ explicit repository_dispatch
→ workflow bridge
→ auto-attach / heartbeat / Beacon
→ existing GACR core
```

This proves an instrumented protocol, not universal automatic repository-presence observation.

## 4.5 R6 drift toward explicit provider-host ingress

R6 adds `scripts/gacr_host_issue_ingress.py` and a controlled issue-comment adapter.

Current dependency chain:

```text
provider host
→ creates configured issue comment
→ comment begins with /gacr-host
→ safe JSON payload
→ issue_comment workflow
→ host ingress validator
→ auto-attach / heartbeat / Beacon
```

The adapter is safe and useful, but its entry is still an explicit GACR event emitted by the provider host.

For a previously unknown session, host ingress currently requires at least one stable supplied anchor among:

- `provider_ref`;
- `provider_url`;
- `connection_ref`;
- `client_instance_id`.

This is stronger than inventing identity and must be preserved, but it is not equivalent to observing first repository touch automatically.

## 4.6 Current explicit dependencies

| Dependency | Current role | Why it remains explicit-event-centric | Preserve? |
|---|---|---|---|
| `/gacr-host` | R6 provider-host adapter | provider host must deliberately create a specially formatted comment | YES, as adapter |
| `repository_dispatch` | R2/R5 transport for attach/heartbeat/Beacon/etc. | caller must deliberately emit a GACR event | YES, as transport |
| client emitter | R5 liveness/action nerve | a client/orchestrator must actually run it | YES, as high-quality evidence source |
| explicit heartbeat | renews lease / liveness | heartbeat exists only if a client/host emits it | YES, but do not equate with progress |
| explicit Beacon | telemetry/correlation input | event must be emitted or generated downstream of another explicit ingress | YES, as canonical evidence sink |
| explicit provider metadata | enriches identity/correlation | provider-private values are only known if provider/client supplies them | YES, optional enrichment only |

## 4.7 Existing true Presence-First detection

Current true/partial Presence-First mechanisms are:

| Mechanism | Presence-First quality | Boundary |
|---|---|---|
| Fresh Conversation Chronicle → auto-attach | REAL / PARTIAL | Chronicle must already exist and be fresh |
| External GitHub Actions execution identity → auto-attach | REAL / PARTIAL | only activity executing as an observable external workflow |
| Source `main` push → GACR workflow invocation | EVENT-VISIBLE ONLY | current internal transport cannot itself become the agent; event subject is not yet separately projected as Presence |
| Correlator from anonymous Beacon | RECONCILIATION PRIMITIVE | requires a Beacon to already exist; does not discover raw repository access |
| GitHub issue-comment host ingress | CONTROLLED but EXPLICIT | requires `/gacr-host` envelope |
| R5 emitter | CONTROLLED but EXPLICIT | requires emitter/adapter execution |

## 4.8 Critical current blind spots

1. A repository read through a proprietary connector/API can be completely silent to GitHub.
2. A direct GitHub API read normally produces no repository event usable by this workflow.
3. The current GACR workflow listens to `push` only on `main`; first writes on a feature branch are not a GACR workflow trigger.
4. PR creation/update is not currently a direct GACR workflow trigger.
5. A `push` that does trigger GACR is executed inside the internal GACR workflow, which correctly suppresses itself as an agent identity; the event subject is not yet represented by a dedicated Presence Observation contract.
6. Current telemetry has Beacon/Correlation/Forensics records but no canonical `connection_fingerprint`, no `UNBOUND_ACTIVITY` object, and no independent `PROGRESS` state.

---

# STEP 5 — Acceptance tests before corrective implementation

**Status: PREPARED / NOT_EXECUTED**

The tests below are the contract. Runtime implementation must be written to satisfy them, not the reverse.

Until the final gap matrix is merged and the test implementation is rebased against it, tests A-F are designated `PLANNED_EXPECTED_FAIL`. This label is a planning expectation, not an executed result.

Tests G-H exercise substantial existing R1-R6 capability and are designated `PLANNED_REVALIDATION`; no new PASS is asserted by this document.

## TEST A — FIRST TOUCH

**Status: `PLANNED_EXPECTED_FAIL`**

Fixture:

- create a fresh governed agent instance with no pre-existing GACR session;
- route it through a controlled/instrumentable repository access surface;
- instruct it only to inspect/work on the governed repository;
- do not mention GACR, registration, Beacon, heartbeat, `/gacr-host` or telemetry.

Required assertions:

1. first observable repository touch creates a `PRESENCE_OBSERVATION`;
2. a canonical GACR session is automatically created or an exact existing session is resumed;
3. no manual `gacr_register`, `gacr_auto-attach`, Beacon, heartbeat or host command is required from the agent prompt;
4. transport executor identity is not used as agent identity;
5. if the surface cannot expose a stable agent anchor, the observation exists but remains unbound rather than fabricating a session;
6. provider conversation ID may be `UNAVAILABLE` and absence does not block a session when another deterministic anchor exists.

Negative fixture:

- perform only a proprietary silent read with no adapter and no GitHub-visible side effect.

Required assertion: GACR must not claim that the read was observed.

## TEST B — CONNECTION ENVELOPE

**Status: `PLANNED_EXPECTED_FAIL`**

The first Presence Observation must produce a safe Connection Envelope.

Required assertions:

- every field carries provenance;
- unavailable fields are explicitly represented as `UNAVAILABLE`;
- provider-private data is never guessed;
- safe GitHub/event/client data may be preserved;
- secret/transcript/private-reasoning fields are rejected;
- an envelope can exist before a session is bound.

Minimum canonical shape:

```text
GACR_CONNECTION_ENVELOPE_V1
  observation_id
  observed_at
  repository
  repository_id
  organization
  git_provider
  surface_class
  transport_or_integration
  entry_action
  event_type

  actor
  github_app_or_installation
  provider
  agent_identity
  agent_type_or_model

  client_instance_id
  connection_ref
  provider_conversation_ref
  provider_conversation_url

  task_id
  claim_id
  branch
  base_branch
  observed_head
  written_head
  pull_request

  workflow_run_id
  job_id
  run_attempt
  delivery_or_correlation_id

  session_id
  connection_fingerprint

  provenance_by_field
```

Each field should use an evidence-bearing value record:

```json
{
  "value": "UNAVAILABLE",
  "availability": "UNAVAILABLE",
  "provenance": "NOT_OBSERVABLE_ON_THIS_SURFACE",
  "confidence": "NONE"
}
```

or, for observed values:

```json
{
  "value": "chainsolutions-wealthtech/Governed-Repository-Template",
  "availability": "OBSERVED",
  "provenance": "GITHUB_EVENT.repository.full_name",
  "confidence": "DIRECT"
}
```

Allowed availability/provenance classes:

- `OBSERVED` — directly visible to repository/gateway/platform event;
- `EXPLICITLY_SUPPLIED` — supplied by client/provider adapter;
- `DERIVED_SAFE` — deterministic normalization/derivation from observed/supplied facts;
- `CORRELATED` — selected by Correlator with explicit correlation level;
- `UNAVAILABLE` — not observable/supplied.

## TEST C — CONNECTION FINGERPRINT

**Status: `PLANNED_EXPECTED_FAIL`**

Goal: correlate two activities from the same operational instance without manufacturing a provider conversation ID.

Required assertions:

1. same stable instance + same connection anchor produces the same fingerprint;
2. provider conversation reference may remain `UNAVAILABLE`;
3. the fingerprint is explicitly typed as a GACR correlation key, not provider identity;
4. collision/ambiguity cannot cause arbitrary session selection;
5. changing a stable client/connection identity changes the fingerprint;
6. event-specific fields such as current HEAD movement do not accidentally create a new instance fingerprint after the session has been established.

Proposed canonical formula:

```text
fingerprint_payload_v1 =
  canonical_json({
    version: "gacr-connection-fingerprint/v1",
    repository_key: repository_id || repository_full_name,
    surface_class,
    actor_or_app_key,
    client_instance_id_if_supplied,
    connection_ref_if_supplied,
    task_id_if_known,
    claim_id_if_known,
    branch_if_known,
    pull_request_if_known,
    first_observed_head,
    first_touch_time_bucket
  })

connection_fingerprint =
  "GACR-FP1-" + sha256(fingerprint_payload_v1)
```

Rules:

- `first_observed_head` and `first_touch_time_bucket` are frozen session-anchor inputs after creation; later HEAD/timestamp changes do not recalculate identity from new values.
- If there is insufficient entropy to distinguish concurrent instances, correlation is `AMBIGUOUS`/`UNBOUND`.
- The fingerprint never appears in `provider_conversation_ref`.

## TEST D — LIVENESS != PROGRESS

**Status: `PLANNED_EXPECTED_FAIL`**

Fixture:

1. create/resume a session;
2. emit only heartbeats for a period;
3. emit no commits, PR changes, completed action trace, checkpoint, written-HEAD movement or other progress evidence.

Required assertions:

```text
LIVENESS = ACTIVE
PROGRESS = NO_RECENT_PROGRESS_EVIDENCE
```

Forbidden assertion:

```text
heartbeat received
⇒ PROGRESS = ADVANCING
```

Then emit a qualifying progress event and assert independently:

```text
LIVENESS = ACTIVE
PROGRESS = ADVANCING
```

Suggested progress evidence classes:

- action `COMPLETED` with outcome;
- written HEAD movement;
- commit/PR mutation bound to the session;
- checkpoint advancement;
- explicit governed work-item advancement;
- other allowlisted operational evidence defined by the final gap matrix.

## TEST E — UNBOUND ACTIVITY

**Status: `PLANNED_EXPECTED_FAIL`**

Fixture:

- observe a GitHub repository activity event;
- construct two equally plausible candidate sessions, or no deterministic candidate;
- do not supply session/provider conversation identity.

Required assertions:

1. create a canonical `UNBOUND_ACTIVITY` observation;
2. preserve repository event evidence and candidates;
3. Correlator may report `AMBIGUOUS` or `UNKNOWN`;
4. `selected_session_id = UNAVAILABLE` / no selection;
5. no session receives fabricated liveness/progress attribution;
6. later deterministic evidence may reconcile the same observation idempotently;
7. unresolved activity remains `UNBOUND`.

## TEST F — SESSION CONTEXT

**Status: `PLANNED_EXPECTED_FAIL`**

A single canonical context query must answer from evidence:

- who is present?
- repository?
- task?
- claim?
- branch?
- PR?
- observed HEAD?
- written HEAD?
- last activity?
- last progress?
- action in flight?
- checkpoint?
- takeover eligible?
- successor reobservation requirements?

Unknown values must be explicit `UNAVAILABLE`.

Existing `agent_context()` and Interruption Forensics are the reuse base. The corrective layer should aggregate them rather than create a second context store.

Required semantic distinctions:

```text
last_activity != last_progress
observed_HEAD != written_HEAD
takeover_ready != takeover_accepted
known predecessor state != inferred external failure cause
```

## TEST G — STALL

**Status: `PLANNED_REVALIDATION`**

Fixture:

- session starts with fresh liveness evidence;
- stop all fresh liveness evidence in a controlled test;
- run Watch/scan at deterministic times crossing the configured thresholds.

Required transition:

```text
ACTIVE or QUIET
→ SUSPECTED_STALL
→ STALLED / TAKEOVER_READY
```

Required assertions:

- timestamps derive from evidence/lease thresholds;
- active claim remains preserved until governed takeover;
- no provider/browser/network cause is invented;
- Forensics uses `UNOBSERVED_EXTERNAL_CAUSE` unless an explicit interruption code was observed.

## TEST H — TAKEOVER

**Status: `PLANNED_REVALIDATION`**

Fixture:

Agent A has stalled with a known task/claim/branch/checkpoint and forensic resume point.

Agent B arrives through the Presence Fabric.

Required assertions:

1. B discovers A as predecessor from GACR context;
2. B receives A's stopping point including in-flight/completed action evidence where available;
3. B reobserves the exact work branch HEAD;
4. mismatched HEAD rejects takeover;
5. matching HEAD allows existing governed `takeover-accept`;
6. active claim transfers only after acceptance;
7. A becomes terminal/closed and cannot resurrect by late heartbeat;
8. B preserves predecessor lineage;
9. B continues the same work without blindly replaying an unresolved in-flight action.

---

# STEP 6 — Additive Presence Fabric

**Status: PREPARED / NOT_EXECUTED**

## 6.1 Architecture

```text
REPOSITORY ACCESS
        |
        v
PRESENCE OBSERVER
        |
        +-- classify access surface
        +-- capture safe observed facts
        +-- keep missing facts UNAVAILABLE
        |
        v
CONNECTION ENVELOPE
        |
        +-- connection_fingerprint
        +-- field provenance
        +-- evidence/idempotency key
        |
        v
SESSION BINDER
        |
        +-- exact deterministic resume
        +-- deterministic create
        +-- ambiguous → UNBOUND_ACTIVITY
        |
        v
PRESENCE / ACTIVITY EVIDENCE
        |
        +--> BEACON
        +--> WATCH
        +--> CORRELATOR
        +--> FORENSICS
        +--> DISPATCHER
```

## 6.2 New responsibilities versus reused responsibilities

Presence Fabric owns only:

- observing first touch on supported surfaces;
- normalizing a safe Connection Envelope;
- creating the connection fingerprint;
- binding or refusing to bind activity;
- emitting Presence/Activity evidence;
- maintaining independent liveness/progress projections;
- exposing session interrogation/challenge semantics.

Existing components continue to own:

- Beacon persistence/telemetry;
- Watch lease/stall transitions;
- Correlator confidence and fail-closed attribution;
- Forensics stopping-point reconstruction;
- Dispatcher standby/takeover delivery;
- claim/collision authority;
- exact-HEAD takeover acceptance.

No second session database, claim model, takeover queue or continuity store is introduced.

---

# STEP 7 — Instrument controlled repository access paths

**Status: PREPARED / NOT_EXECUTED**

Instrumentation priority:

1. controlled gateway/connector/MCP/bridge entrypoints;
2. existing provider/client adapters;
3. GitHub event-visible reconciliation;
4. proprietary silent access remains explicitly limited.

The instrumentation hook must occur because the access surface is used, not because the agent was prompted to call GACR.

For a controlled connector/gateway, the ideal hook sequence is:

```text
connector receives repository operation
→ emit safe first-touch Presence Observation
→ continue repository operation
→ emit safe activity/result observation when appropriate
```

A read-only first touch is sufficient to establish presence when the gateway itself can observe it.

---

# STEP 8 — Canonical Presence / Activity evidence

**Status: PREPARED / NOT_EXECUTED**

Proposed evidence types:

- `PRESENCE_FIRST_TOUCH`;
- `PRESENCE_RESUME`;
- `REPOSITORY_READ_ACTIVITY` when genuinely observable by controlled gateway;
- `REPOSITORY_WRITE_ACTIVITY`;
- `GITHUB_EVENT_ACTIVITY`;
- `CLIENT_HEARTBEAT`;
- `ACTION_STARTED`;
- `ACTION_COMPLETED`;
- `CHECKPOINT_ADVANCED`;
- `LIVENESS_CHALLENGE_SENT`;
- `LIVENESS_CHALLENGE_ACK`;
- `LIVENESS_CHALLENGE_TIMEOUT`;
- `UNBOUND_ACTIVITY`.

Every item requires:

- immutable observation id;
- timestamp;
- surface class;
- safe Connection Envelope reference/digest;
- evidence source/provenance;
- optional session binding;
- optional correlation level;
- idempotency key.

Presence evidence may be converted into/referenced by existing Beacon records. The Presence layer must not fork a parallel telemetry history.

---

# STEP 9 — Independent LIVENESS and PROGRESS projections

**Status: PREPARED / NOT_EXECUTED**

## 9.1 Liveness

Suggested projection states:

- `ACTIVE`;
- `QUIET`;
- `SUSPECTED_STALL`;
- `STALLED`;
- `UNKNOWN`;
- `TERMINAL`.

Inputs may include:

- heartbeat;
- observed repository interaction;
- challenge acknowledgement;
- recent safe client/action event;
- Watch lease timing.

## 9.2 Progress

Suggested projection states:

- `ADVANCING`;
- `NO_RECENT_PROGRESS_EVIDENCE`;
- `BLOCKED_IF_EXPLICITLY_OBSERVED`;
- `UNKNOWN`.

Progress timestamps must be separate from liveness timestamps:

```text
last_activity_at
last_liveness_evidence_at
last_progress_at
```

A heartbeat updates liveness/activity timestamps but not `last_progress_at` unless the same event independently contains qualifying progress evidence.

---

# STEP 10 — Session interrogation and active liveness challenge

**Status: PREPARED / NOT_EXECUTED**

## 10.1 Canonical session context

The target aggregate should compose existing session, claims, Beacon, correlations, Forensics, takeover and dispatch evidence.

Suggested response contract:

```text
session_identity
presence
repository
task
claims
branch
pull_request
observed_head
written_head

liveness:
  state
  last_evidence_at
  lease_expires_at

progress:
  state
  last_progress_at
  last_progress_evidence

activity:
  last_activity_at
  last_action_started
  last_action_completed
  action_in_flight

checkpoint
forensics
takeover:
  eligible
  reason
  predecessor
  successor
  exact_head_reobservation_required
```

## 10.2 Challenge boundary

Where a controlled client/gateway exposes a bidirectional endpoint, GACR may issue a challenge.

Allowed response semantics:

- `ACK`;
- `BUSY`;
- `IDLE`;
- `CHECKPOINTING`;
- `TERMINATING`.

No response records `LIVENESS_CHALLENGE_TIMEOUT`.

It must not be translated into “browser crashed”, “network failed” or any other unobserved cause.

A challenge is optional enrichment. Lack of a challenge channel never prevents repository-based continuity/takeover.

---

# STEP 11 — UNBOUND_ACTIVITY reconciliation

**Status: PREPARED / NOT_EXECUTED**

Required object:

```text
UNBOUND_ACTIVITY
  observation_id
  repository
  observed_at
  event/activity class
  safe envelope/digest
  candidate_session_ids
  correlation_level
  reasons
  status = UNBOUND | RECONCILED | SUPERSEDED
  reconciled_session_id
  reconciled_at
```

Rules:

1. raw activity may exist before session attribution;
2. `AMBIGUOUS` and `UNKNOWN` never auto-select;
3. later deterministic evidence may reconcile the existing activity;
4. reconciliation is idempotent and auditable;
5. an unbound activity must not renew an arbitrary session lease or progress state;
6. actor/app alone is not always sufficient when one identity can operate multiple concurrent sessions.

The existing Correlator already supplies `EXACT / STRONG / PROBABLE / AMBIGUOUS / UNKNOWN`; Step 11 should reuse that confidence vocabulary.

---

# STEP 12 — Reuse existing canonical components

**Status: PREPARED / NOT_EXECUTED**

Correct target:

```text
Presence Fabric
→ existing Beacon
→ existing Watch
→ existing Correlator
→ existing Interruption Forensics
→ existing Dispatcher
→ existing exact-HEAD takeover
```

Forbidden target:

```text
Presence Fabric
→ second Beacon store
→ second session engine
→ second correlator
→ second stall engine
→ second dispatcher
```

Integration contract:

- Presence creates safe evidence;
- Beacon remains the telemetry sink/projection;
- Watch remains authoritative for lease/stall transitions;
- Correlator remains authoritative for evidence-based session attribution;
- Forensics remains authoritative for stopping-point reconstruction;
- Dispatcher remains authoritative for takeover delivery preparation;
- existing takeover acceptance remains authoritative for claim transfer and exact-HEAD gating.

---

# Access-surface map

## Class 1 — Controlled / instrumentable

Examples:

- a framework-owned gateway;
- a repository connector wrapper;
- MCP/bridge path controlled by the framework;
- R5 client emitter host;
- R6 provider-host adapter.

Observable when instrumented:

- timestamp;
- target repository;
- operation class/read/write;
- authenticated integration/application identity when safely exposed;
- client instance/connection reference when supplied by the adapter;
- request correlation/idempotency reference;
- branch/ref/PR/HEAD when known to the operation;
- task/claim when the governed client context has it.

Timing: before/at first repository operation, plus activity/result boundaries.

Confidence:

- direct for gateway-observed facts;
- explicitly supplied for provider/client metadata;
- derived/correlated only when labeled as such.

GACR binding:

```text
first gateway touch
→ Connection Envelope
→ fingerprint
→ exact resume/create if deterministic
→ otherwise UNBOUND_ACTIVITY
```

Impossible without provider/client support:

- provider-private conversation identity;
- browser tab state;
- provider internal execution state;
- private reasoning/transcript.

## Class 2 — GitHub event-visible

Examples:

- push/commit events;
- PR open/update/merge events;
- issue comments;
- workflow/run/job events;
- checks/statuses where subscribed/available.

Observable:

- repository;
- event type/time;
- actor/application identity exposed by GitHub;
- ref/branch;
- commit SHA;
- PR number where event supplies it;
- workflow/run/job metadata where applicable.

Timing: after GitHub emits the platform event; this is not proof of earlier silent reads.

Confidence: direct for the GitHub event itself; correlation to an agent session may be exact/strong/probable/ambiguous/unknown.

GACR binding:

- first attempt deterministic binding using stored connection/session anchors;
- then Correlator;
- if not deterministic, create `UNBOUND_ACTIVITY`.

Current implementation note:

- the GACR workflow currently subscribes to `push` on `main`, not all branch pushes;
- PR activity is not currently a direct workflow trigger;
- issue comments enter the host path only when they use the `/gacr-host` prefix.

Impossible from GitHub events alone:

- prove which provider conversation caused the action unless supplied elsewhere;
- detect a provider-side read that produces no GitHub event;
- know private model state.

## Class 3 — Proprietary silent access

Examples:

- provider-side repository reads through a proprietary integration that emits no hook to GACR and no GitHub event.

Observable by repository/GitHub: nothing reliable about the access itself.

Timing: none; a later write/event may become visible, but must not retroactively be represented as proof that an earlier read was observed.

Confidence: `NONE` for the silent access.

GACR binding: impossible until an adapter/gateway event or later independent repository evidence appears.

Required representation:

```text
provider_conversation_ref = UNAVAILABLE
silent_read_presence = UNAVAILABLE / NOT_OBSERVED
```

Never claim automatic coverage for this class without a provider/client adapter.

---

# Ultimate live scenario design

**Status: DESIGNED / NOT_RUN**

The live scenario belongs to later realignment steps 13-24. This document prepares it but does not run it.

## Phase A — Agent A first touch

1. Create a genuinely fresh Agent A.
2. Give A normal repository work instructions only.
3. Do not mention GACR registration, Beacon, heartbeat, host ingress or telemetry.
4. Route A through a Class-1 instrumentable repository path.
5. Assert Test A and B.
6. Verify a canonical session was created/resumed from first touch.
7. Verify provider conversation reference remains `UNAVAILABLE` unless genuinely supplied.
8. Record the connection fingerprint.
9. Make A perform real governed work.
10. Observe independent liveness and progress.

Expected evidence sequence:

```text
PRESENCE_FIRST_TOUCH
→ CREATE/RESUME
→ repository activity
→ progress evidence
→ checkpoint/action evidence as applicable
```

## Phase B — controlled loss of fresh evidence

1. Stop Agent A's instrumented activity without emitting a fabricated cause.
2. Preserve last observed activity/progress/checkpoint/action evidence.
3. Let Watch cross deterministic freshness thresholds.
4. Observe:

```text
ACTIVE/QUIET
→ SUSPECTED_STALL
→ STALLED
→ TAKEOVER_READY
```

5. Verify Forensics reports `UNOBSERVED_EXTERNAL_CAUSE` unless an explicit interruption signal was truly observed.

## Phase C — Agent B arrival

1. Create a fresh Agent B through the same governed Presence path.
2. B discovers the stalled predecessor from session context.
3. B obtains:
   - task;
   - claim;
   - branch;
   - PR;
   - observed HEAD;
   - written HEAD;
   - last activity;
   - last progress;
   - action in flight;
   - checkpoint;
   - exact-head reobservation requirement.
4. B fetches/reobserves the actual current work branch HEAD.
5. A mismatch must fail takeover.
6. An exact match allows existing governed takeover acceptance.
7. Existing claim transfers only after acceptance.
8. B continues the same work.
9. A late heartbeat from A must not resurrect predecessor ownership.

Ultimate PASS requires the entire chain live, not just unit tests.

---

# Implementation-agent handoff

Before implementing any runtime correction, the next agent must:

1. reobserve current `main` exactly;
2. read the merged R6 baseline attestation;
3. read the final merged Original-Intent gap matrix;
4. re-read this document and `GACR_ORIGIN_REALIGNMENT.md`;
5. verify no newer decision supersedes this design;
6. add acceptance tests first;
7. keep Presence Fabric additive;
8. preserve all R1-R6 regression tests;
9. avoid any secret/transcript/private-reasoning instrumentation;
10. leave steps 4-12 not-DONE until their actual exit evidence exists.

## Suggested future test files — names only, not created by this artifact

```text
scripts/test_gacr_presence_first.py
scripts/test_gacr_connection_envelope.py
scripts/test_gacr_connection_fingerprint.py
scripts/test_gacr_liveness_progress.py
scripts/test_gacr_unbound_activity.py
scripts/test_gacr_session_context.py
scripts/test_gacr_presence_live_acceptance.py
```

The implementation agent may consolidate these if the final gap matrix shows a better fit with the existing test layout. The behavioral contract in Tests A-H is authoritative over file naming.

---

# Prepared-state ledger

| Realignment step | This artifact | Runtime executed? |
|---:|---|---|
| 4 drift analysis | PREPARED | NO |
| 5 acceptance tests | SPECIFIED BEFORE CODE | NO |
| 6 Presence Fabric | DESIGNED | NO |
| 7 controlled path instrumentation | DESIGNED | NO |
| 8 Presence/Activity evidence | DESIGNED | NO |
| 9 liveness vs progress | DESIGNED | NO |
| 10 context/challenge | DESIGNED | NO |
| 11 UNBOUND_ACTIVITY | DESIGNED | NO |
| 12 reuse existing components | DESIGNED | NO |

No entry in this ledger is a completion attestation.
