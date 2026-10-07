# GACR — Governed Agent Continuity Relay

Authority: `CP-AGENT-RELAY-001`

GACR is the reusable governed process for keeping long-running multi-agent work resumable when one agent or conversation becomes unavailable, times out, stalls, or loses its client connection.

It extends the existing session / claim / checkpoint / handoff model. It is **not** a second task engine.

## Core model

```text
REGISTER / RESUME AGENT
→ SESSION
→ OPTIONAL EXTERNAL CONVERSATION REF
→ HEARTBEAT + LEASE
→ CLAIMED WORK
→ CHECKPOINTS / EVIDENCE
→ SUPERVISOR SCAN
   ├─ healthy            → continue
   ├─ suspected stall    → SUSPECTED_STALL
   └─ lease expired      → STALLED
                           ↓
                    TAKEOVER_READY
                           ↓
                 standby agent offered
                           ↓
              exact branch/HEAD reconciliation
                           ↓
                    ACCEPT TAKEOVER
                           ↓
                  transfer active claim
                           ↓
                     continue work
```

A stall never automatically releases an active claim. The old claim continues to block concurrent writers until a successor has re-observed the work branch / PR, reconciled the exact current HEAD, and explicitly accepts the takeover.

## External conversation references

GACR may associate a session with an external conversation reference, for example a ChatGPT conversation ID.

Rules:

- use only an identifier/URL actually supplied by the client, orchestrator or user;
- never invent an unavailable provider conversation ID;
- by default, persist the provider reference but not the full conversation URL;
- for known providers, the URL may be reconstructed on request from the stored reference;
- the canonical identity remains the governed session ID, not the external chat URL.

For ChatGPT, a supplied URL such as:

```text
https://chatgpt.com/c/<conversation-id>
```

is normalized to the provider conversation reference `<conversation-id>`.

## States

`ACTIVE` — working session with a live lease.

`STANDBY` — connected/prepared session that has no current mutable claim and can be offered a takeover.

`SUSPECTED_STALL` — heartbeat late but lease not yet expired.

`STALLED` — lease expired; no further mutable dispatch is allowed from the predecessor session.

`TAKEOVER_READY` — stalled session has a takeover queue item.

`HANDOFF_STALLED` — ownership was transferred after exact-state reconciliation.

`CLOSED` — normal terminal handoff.

## Multi-agent collision safety

GACR complements, rather than replaces:

- `CP-NAMESPACE-001` for semantic ID uniqueness;
- work claims for ownership;
- collision domains for single-writer guarantees;
- dependency-safe dispatch;
- exact-HEAD guards;
- checkpoints and handoffs.

A standby agent is never allowed to write simply because another agent is stale.

## Automatic supervision

The distributed workflow `.github/workflows/governed-agent-continuity-relay.yml` scans leases on a schedule.

The workflow can automatically:

- identify suspected/stalled agents;
- create/maintain a takeover queue;
- offer stalled work to a compatible standby session;
- persist the resulting coordination state with an exact-HEAD guarded commit.

It does **not** have a universal way to wake an arbitrary browser tab or ChatGPT conversation. A provider/orchestrator may consume GACR state or send `repository_dispatch` events, and any standby agent that reconnects can deterministically discover its offered takeover.

## Commands

```bash
python3 scripts/governed_agent_continuity_relay.py register ...
python3 scripts/governed_agent_continuity_relay.py heartbeat --session-id ...
python3 scripts/governed_agent_continuity_relay.py scan
python3 scripts/governed_agent_continuity_relay.py status
python3 scripts/governed_agent_continuity_relay.py identify --provider chatgpt --provider-ref ...
python3 scripts/governed_agent_continuity_relay.py takeover-plan --stalled-session-id ...
python3 scripts/governed_agent_continuity_relay.py takeover-accept ...
```

## Reuse in another project

GACR is part of the generic Template surface. A governed project receives the same config, workflow, script and state contract. The project retains its own sessions, claims, checkpoints and takeover queue.

No project-specific hard-coding is required.

## Source Control Plane versus client runtime state

GACR preserves the same source/client memory boundary as the rest of the framework:

```text
SOURCE CONTROL PLANE GACR MEMORY
!=
DISTRIBUTED CLIENT GACR STATE
```

On the Template source, runtime continuity is stored only in:

- `.governance/control-plane-state/gacr-sessions.json`
- `.governance/control-plane-state/gacr-claims.json`
- `.governance/control-plane-state/gacr-takeovers.json`

On an instantiated/adopted client repository, GACR uses that project's local session/claim/takeover stores.

Only the generic GACR code, schemas, configuration and workflow are distributed. A source conversation or source agent claim must never become client project state.

## Beacon, Correlator, Dispatcher and Agent Context

GACR v2 adds:

- **Beacon** — safe connection/action telemetry;
- **Correlator** — deterministic or evidence-based session attribution;
- **Dispatcher** — target-specific takeover wake records;
- **Agent Context** — one safe aggregate view for resume.

Commands:

```bash
python3 scripts/gacr_agent_telemetry.py beacon ...
python3 scripts/gacr_agent_telemetry.py correlate
python3 scripts/gacr_agent_telemetry.py dispatch
python3 scripts/gacr_agent_telemetry.py context --session-id <session>
python3 scripts/gacr_agent_telemetry.py status
```

The GitHub workflow exposes the same operations through `workflow_dispatch` and `repository_dispatch`.

Only allowlisted GitHub metadata is captured. Provider conversation references are used only when actually supplied. The Correlator fails closed on ambiguous evidence.

## Interruption Forensics

Revision authority: `CP-AGENT-RELAY-001-R3`.

GACR R3 adds **Interruption Forensics** as a deterministic projection over the existing GACR evidence. It is not a new event store, task engine, claim system or source of truth.

```text
BEACON
→ WATCH
→ CORRELATOR
→ INTERRUPTION FORENSICS
→ DISPATCHER
→ exact-HEAD takeover reconciliation
→ continue
```

Forensics reconstructs, when evidence exists: last heartbeat/lease/stall state; task/branch/PR; active claims and collision domains; last observed and explicitly reported written HEAD; last action started/completed; last observed tool call; in-flight action; checkpoint/evidence references; takeover/dispatch state; and a deterministic resume point.

External failure cause is **observed-only**. GACR never claims browser crash, provider timeout, network loss or tool failure unless a client/orchestrator explicitly emitted that interruption code. Otherwise the cause remains `UNOBSERVED_EXTERNAL_CAUSE`.

A forensic report never grants mutation authority. Resume/takeover still requires fresh exact-HEAD observation and the existing claim/authority gates.

```bash
python3 scripts/gacr_agent_telemetry.py forensics --session-id <session>
```

The scheduled WATCH scan refreshes forensic projections before Dispatcher evaluates takeover delivery.

Rich action/interruption trace metadata is intended for the CLI, `repository_dispatch`, or a client/orchestrator Bridge. The manual `workflow_dispatch` form remains bounded and is not expanded with every telemetry field.

## Automatic Continuity Attachment

Revision authority: `CP-AGENT-RELAY-001-R4`.

R4 makes GACR attachment the default governed-arrival behavior instead of requiring a human or agent to remember to register manually.

```text
GOVERNED AGENT / CONVERSATION ARRIVAL
→ strongest observable attachment anchor
   1. explicit client/provider metadata
   2. fresh active Conversation Chronicle
   3. GitHub Actions execution identity
→ CREATE or RESUME GACR session
→ AUTO_ATTACH Beacon
→ Correlator
→ WATCH / FORENSICS / DISPATCHER
```

A provider conversation ID or URL is not required to attach. If unavailable, the session is created from the strongest safe connection anchor and keeps provider conversation metadata unavailable. When an explicit provider reference later becomes observable, R4 enriches the same connection-bound session instead of creating a duplicate.

For the Template source, an active source-only Conversation Chronicle may provide the stable pair `chronicle_id + current_session`, projected as `connection_ref = chronicle:<chronicle_id>:<session>`.

The Chronicle remains conversation continuity memory, not business authority. GACR remains the liveness/relay engine. Neither replaces the other.

On source `main`, normal repository activity invokes auto-attachment. GACR state-persistence pushes performed by the repository automation are excluded from re-entry so state commits cannot create an attachment loop.

Missing metadata is explicit `UNAVAILABLE`; it is never invented. Auto-attachment does not grant mutation authority and does not change claim, collision-domain or exact-HEAD gates.

## Client Liveness and Trace Emitter

Revision authority: `CP-AGENT-RELAY-001-R5`.

R5 completes the generic client-side nerve needed after R4 attachment.

```text
CLIENT / AGENT HOST
→ AUTO ATTACH
→ SESSION RESOLVE
→ CLIENT_EMITTER HEARTBEAT
→ ACTION / TOOL TRACE
→ explicit interruption signal when actually observed
→ optional wake poll
→ WATCH / CORRELATOR / FORENSICS / DISPATCHER
```

The emitter uses the existing GitHub `repository_dispatch` receiver:

- `gacr_auto-attach`;
- `gacr_heartbeat`;
- `gacr_beacon`.

Heartbeat and trace provenance is preserved as `CLIENT_EMITTER` even though GitHub Actions transports the event.

The client transport credential exists only in the emitter process environment. It is not placed in the GACR payload or persisted by the repository.

The emitter can poll a dispatch projection for `READY / ACTIVATED` wake records. A wake poll is informational only; it never calls `takeover-accept` and never grants write authority.

A host that cannot run the emitter continuously must not pretend that continuous client liveness is proven. Repository activity and R4 auto-attach remain valid evidence, while absence of client heartbeat remains observable as silence.

## Generic-core completion boundary

With R5, the reusable GACR core is complete through:

```text
AUTO ATTACH
→ SESSION CREATE / RESUME
→ BEACON
→ CLIENT HEARTBEAT CONTRACT
→ ACTION / TOOL TRACE CONTRACT
→ WATCH
→ CORRELATOR
→ INTERRUPTION FORENSICS
→ DISPATCHER
→ WAKE POLL / EXTERNAL WAKE
→ EXACT-HEAD TAKEOVER
→ CONTINUATION
```

Provider-specific host instrumentation remains a deployment/integration concern. An uninstrumented browser or proprietary client cannot be made continuously observable by repository code alone.

Therefore two claims stay distinct:

- `GENERIC_GACR_CORE_COMPLETE`: repository/runtime/client protocol and tests exist;
- `PROVIDER_HOST_LIVE`: only true for a host that actually invokes/runs the emitter or equivalent adapter.

This distinction is required to preserve evidence quality and fail-closed behavior.

## Internal transport is not an agent

Corrective decision: `CPD-055`.

The `Governed Agent Continuity Relay` GitHub Actions workflow transports GACR state/events. It is never itself an agent identity and must never create a fallback session when a Chronicle becomes stale.

A stale Chronicle is preserved as stale evidence. If no real external anchor is observable, auto-attachment skips session/Beacon creation and may only refresh derived correlations.

Any historical transport session created before this correction is retained as evidence but marked terminal/superseded. Terminal sessions are excluded from future correlation candidates.

## R5 final corrective attestation

The post-R5 regression in which the internal GACR workflow created a second session after Chronicle freshness expired is corrected by `CPD-055`.

Live post-merge evidence proves:

```text
internal GACR workflow
→ no external agent anchor
→ GACR_AUTO_ATTACH_SKIPPED
→ no new session
→ no new Beacon
→ terminal transport session excluded from Correlator
```

The erroneous historical transport session and Beacon remain preserved for auditability. The session is terminal/superseded and cannot participate in live correlation.

GACR R1-R5 is therefore complete at the generic repository/runtime/client-protocol layer. Provider-host instrumentation is separately attested only when an actual host invokes the R5 emitter or an equivalent adapter.

## R6 — Provider-host issue ingress

Revision authority: `CP-AGENT-RELAY-001-R6`. Decision: `CPD-056`.

R6 integrates provider hosts that cannot call `repository_dispatch` directly but can create GitHub issue comments. It does not replace the R5 client emitter; it is a transport adapter into the same GACR core.

```text
ChatGPT / Claude / provider host
→ configured GitHub issue
→ /gacr-host { safe JSON envelope }
→ issue_comment workflow
→ host ingress validator
→ existing auto-attach / heartbeat / Beacon
→ Correlator
→ Interruption Forensics
→ existing exact-HEAD / claim / takeover rules
```

The adapter is fail-closed:

- only the configured issue is accepted;
- only `OWNER / MEMBER / COLLABORATOR` comment associations are accepted;
- only schema `gacr-host-event/v1` and allowlisted fields are accepted;
- secret-like keys and transcript-like fields are rejected;
- comment ID becomes the ingress evidence/idempotency key;
- duplicate workflow delivery of the same comment is a no-op;
- host telemetry grants no mutation authority.

Supported events are `attach`, `heartbeat`, `action`, and explicitly observed `interrupt`.

For `heartbeat` and `action`, the adapter renews the existing GACR lease. For `action`, it records the R5 `ACTION_TRACE` fields. Every accepted event refreshes correlation and forensics. If no active session matches, the adapter may auto-attach only when a stable client/provider/connection anchor is supplied.

The dedicated source ingress issue is `#115`. Generated/adopted clients receive the adapter and configuration through the existing Template/upgrader path; each repository may configure its own ingress issue rather than inheriting source-project runtime history.

Candidate status on this branch: `IMPLEMENTED_PENDING_CI_AND_POST_MERGE_LIVE_PROOF`.

### R6 portability boundary

The Template source issue number is runtime-local state and is never distributed to a governed client.

- Template source currently binds its host ingress to issue `#115`.
- A distributed/upgraded client receives `host_issue_bridge.issue_number = null`.
- While no local number is bound, the ingress accepts only an issue whose title exactly matches the configured canonical host-inbox title.
- Once a repository-local issue number is explicitly bound, exact-number validation takes precedence.
- Multiple/ambiguous inbox discovery must fail closed at the host/orchestrator layer; the repository workflow does not infer an arbitrary issue.
- Source conversation/session history and source issue identity never become client runtime state.

This keeps the R6 transport reusable without leaking source-project runtime coordinates.

### R6-C — late provider identity enrichment without provider conversation ID

An existing connection-bound session may have been created before the provider identity became explicit, for example with `provider = other` and no native conversation reference.

When the same stable `connection_ref` is later accompanied by an explicit provider such as `chatgpt`, GACR may enrich **that same session** even if `provider_conversation_ref` remains unavailable.

Rules:
- only a generic provider value (`null / empty / other`) may be enriched to a specific provider;
- the session ID must remain unchanged;
- no provider conversation reference is invented;
- a conflicting specific provider fails closed;
- the provider-host adapter uses the existing auto-attach/register path rather than editing session state through a parallel mechanism.

## R6 final live attestation

R6 is live-proven with the current ChatGPT host using the governed issue-comment transport.

The integration proves automatic processing of emitted host events, not an always-running browser daemon. When the host is actively handling governed work, it can emit safe events through the GitHub connector and GACR persists liveness/action context automatically. When no host process is running, no synthetic heartbeat is generated.

The live proof preserves the core invariants: one canonical active session, no invented provider conversation ID, exact correlation, idempotent replay, exact-HEAD persistence guards, no claim/takeover bypass, and source/client runtime isolation.

## Original intent and autonomous GACR programme

Canonical historical intent: `docs/control-plane/GACR_ORIGINAL_INTENT.md`.

Canonical GACR programme: `docs/control-plane/GACR_PROGRAM.md`.

The original-intent authority preserves the two external limits, Connection Envelope, connection fingerprint, correlation confidence model, Dispatcher activation target, optional Bridge boundary, Agent Context philosophy and the historical point where the additive BEACON + WATCH + CORRELATOR + DISPATCHER evolution was ready to proceed.

GACR is distinct from the global Control Plane programme. It may progress on explicit owner direction while the global programme remains parked, and no global task such as `P12-S6` is a functional prerequisite for GACR.

## Origin realignment — Presence-First planning authority

Owner clarification after R6: R1-R6 are preserved, but future GACR evolution must return to the original presence-first objective.

The canonical plan is:

- human authority: `docs/control-plane/GACR_ORIGIN_REALIGNMENT.md`;
- machine projection: `.governance/control-plane-state/gacr-origin-realignment.json`.

Primary invariant:

> An agent/conversation using a governed repository through an instrumentable access surface must become observable to GACR from the repository interaction itself, without requiring the agent to remember to explicitly invoke GACR.

This does not invalidate R1-R6. Heartbeat/lease, Beacon, Correlator, Forensics, auto-attach, client emitter, host ingress, Dispatcher, claims and exact-HEAD takeover remain reusable canonical components.

The realignment is incomplete until the live acceptance scenario in the canonical plan proves: fresh agent arrival without explicit GACR registration instruction → automatic observable presence → safe activity/progress observation → stall detection → second-agent exact-HEAD takeover → continuation of the same work.

Registration of this plan does not change the global unique executable task or silently execute `P12-S6`.


## Independent Liveness, Progress and Session Interrogation

Presence-First realignment keeps two independent runtime questions:

```text
LIVENESS = is there fresh evidence that the governed session is present/reachable/active?
PROGRESS = is there fresh qualifying evidence that governed work actually advanced?
```

A heartbeat is liveness/activity evidence only. It never makes `PROGRESS=ADVANCING` by itself.

The canonical projection keeps three distinct timestamps:

- `last_activity_at` — latest activity bound to the session;
- `last_liveness_evidence_at` — latest evidence usable for liveness;
- `last_progress_at` — latest allowlisted progress evidence.

Liveness states are `ACTIVE / QUIET / SUSPECTED_STALL / STALLED / UNKNOWN / TERMINAL`.
Progress states are `ADVANCING / NO_RECENT_PROGRESS_EVIDENCE / BLOCKED_IF_EXPLICITLY_OBSERVED / UNKNOWN`.

Qualifying progress evidence is allowlisted: completed action evidence, explicitly reported written-HEAD movement, repository-write/commit/PR mutation evidence, checkpoint advancement, or governed work-item advancement. Missing evidence never becomes progress.

`agent_context()` remains the single Agent Context mechanism. It now aggregates the existing session, claims, Beacon, Correlator, Forensics, takeover and dispatch stores and exposes explicit `UNAVAILABLE` values for unknown facts. No second Agent Context database is created. The same aggregate exposes takeover eligibility inputs and the exact-HEAD reobservation requirement without accepting a takeover or transferring a claim.

The generic liveness-challenge hook supports only `ACK / BUSY / IDLE / CHECKPOINTING / TERMINATING`. A missing response yields `LIVENESS_CHALLENGE_TIMEOUT`; it never becomes a claim that a browser crashed, a provider timed out, or a network was lost. Actual challenge delivery remains optional and requires a bidirectional provider/client/gateway integration.

### UNBOUND_ACTIVITY

Repository activity that cannot be deterministically attributed is retained as an `UNBOUND_ACTIVITY` projection attached to the existing Correlator record. This deliberately avoids a second telemetry or continuity store.

```text
observation_id
repository
observed_at
activity_class
safe_envelope_digest
candidate_session_ids
correlation_level
reasons
status = UNBOUND | RECONCILED | SUPERSEDED
reconciled_session_id
reconciled_at
```

`AMBIGUOUS` and `UNKNOWN` never select a session. Unbound activity does not renew a candidate lease and does not create candidate progress. Later deterministic correlation may reconcile the same observation idempotently.

### Parallel-worker integration boundary

This tranche does not own Presence Fabric / ConnectionEnvelope creation and does not expand Dispatcher routing. Until the parallel Presence/ConnectionEnvelope API is merged, the integration state is `SHARED_INTEGRATION_REQUIRED`.

For downstream Correlator/Dispatcher work, `worker_c_integration_projection()` exposes liveness, progress, the three timestamps, UNBOUND_ACTIVITY, Agent Context, and takeover-eligibility inputs while leaving Dispatcher authority unchanged.

## Correlator / Dispatcher / Takeover integration hardening

The additive Correlator / Dispatcher / Takeover contract is defined in
`docs/control-plane/GACR_CORRELATOR_DISPATCHER_TAKEOVER_INTEGRATION.md`.

The hardened Correlator uses named categorical evidence rules; only `EXACT`
and unique `STRONG` may select a session. Dispatcher compatibility reuses
the existing sessions, claims, collision domains, work-item dependencies and
exact-HEAD gate. Compatibility and wake preparation grant no mutation
authority.

The prepared Agent A -> stall -> Agent B harness remains
`SHARED_INTEGRATION_REQUIRED` until separately-owned Presence/Envelope and
Liveness/Progress worker surfaces are available. It is not the ultimate live
Steps 13-24 proof.


## GSCC Observable Arrival Gateway

Canonical entry rule:

```text
OBSERVABLE GOVERNED REPOSITORY ARRIVAL
→ GSCC
→ SESSION_ATTACH / SESSION_RESUME semantics
→ existing GACR auto-attach / Presence Fabric
→ GSE / Correlator / WATCH / Forensics / Dispatcher
```

The additive gateway is implemented by:

- `scripts/gscc_observable_arrival.py`;
- `.github/workflows/gscc-observable-arrival.yml`;
- canonical `scripts/gscc/session_endpoint.py`;
- existing `GACRClientEmitterAdapter`;
- existing `gacr_auto-attach` repository-dispatch path.

The agent does not need to call GACR or know a GACR session ID. On a controlled host, the host supplies a stable `connection_ref` / `client_instance_id` at first touch. On GitHub-event-visible surfaces, the gateway derives only safe observable surface identity and emits a GSCC `SESSION_ATTACH`.

GitHub `repository_dispatch` limits `client_payload` to ten top-level properties. The gateway therefore preserves extended safe arrival metadata inside one `arrival_context` object. `gacr_workflow_bridge.py` expands only an explicit allowlist before invoking the existing Presence Fabric. Secrets, raw prompts, transcripts, private reasoning and provider-private identifiers remain excluded.

Loop guards prevent GACR state-persistence pushes, GACR/GSCC repository-dispatch traffic and `/gacr-host` transport comments from becoming new agent arrivals.

A GitHub-visible event identifies an observable repository surface, not necessarily a provider conversation. Provider identity/reference remains unavailable unless a controlled provider host actually supplies it.

`PROPRIETARY_SILENT` remains an explicit external boundary: repository code cannot trigger on a read for which neither GitHub nor a controlled gateway receives an event. Such silence must never be converted into synthetic presence.

This gateway enables the missing Step 13B instrumented path, but its implementation or self-test is **not** fresh-provider acceptance evidence. Step 13B still requires a genuinely fresh agent after canonical integration.

## GSCC mandatory function exposure gate

After observable arrival attachment, function publication/use is separately gated.

```text
ARRIVAL
→ GSCC Observable Arrival Gateway
→ GACR Presence
→ GSCC Function Exposure Gate
→ route artifact
→ explicit function request
→ active GSCC session + exact HEAD + contract + authority
→ live preflight when required
→ VALIDATED exposure receipt
→ function may be published
→ pre-call GSCC revalidation
→ tool lifecycle
```

The workflow `.github/workflows/gscc-function-exposure-gate.yml` runs an arrival-plan job for the same observable GitHub arrival classes and an evaluate job for `gscc_function_exposure_request` or explicit workflow dispatch. Both fail closed. The resulting route/receipt is an Actions artifact rather than a second canonical state database.

The gate does not infer authority and does not grant mutation authority. It validates evidence that another authority source has actually supplied. A mutation tool without current live preflight remains withheld.

Provider/private surfaces that bypass this governed catalogue/wrapper cannot be made compliant by repository code alone; they must integrate the GSCC exposure API/workflow. Such an unintegrated surface is reported as outside the governed exposure boundary, never silently treated as validated.


## R7 — Capacity-aware parallel work dispatch

Revision authority: `CP-AGENT-RELAY-001-R7`. Decision: `CPD-074`.

R7 extends the existing Beacon / Correlator / Dispatcher with an explicit **agent capacity pool** for new governed work. It does not replace the canonical work-item, claim or execution engines.

```text
GACR session + liveness + explicit availability
        ↓
capacity projection
        ↓
AVAILABLE / WAITING / BUSY / BLOCKED
RATE_LIMITED / QUOTA_BLOCKED / STALLED / TERMINAL / UNKNOWN
        ↓
READY work-items
+ dependencies
+ active claims
+ collision domains
+ required capabilities
+ required authorities
+ allowed agent roles
        ↓
parallel dispatch plan
        ↓
WORK_OFFER
        ↓
agent accepts
        ↓
ACCEPTED_PENDING_CLAIM
        ↓
canonical claim + exact-HEAD reconciliation
        ↓
only then normal governed execution
```

### Availability is observed, never guessed

Silence is **not** availability.

A session is eligible for new work only when it is live enough and has either:
- explicitly declared `AVAILABLE` or `WAITING`; or
- is already in canonical `STANDBY` state.

Explicit provider/runtime limitation codes include:
- `PROVIDER_RATE_LIMIT`;
- `PROVIDER_QUOTA_EXHAUSTED`;
- `CONTEXT_LIMIT`;
- `WAITING_FOR_INPUT`;
- `DEPENDENCY_BLOCKED`.

These facts are accepted only when an agent/provider/bridge emits them. GACR never infers a rate limit, quota exhaustion or context limit from missing heartbeats.

### Parallelism safety

R7 may plan multiple tasks concurrently only when:
- every task is `READY`;
- dependencies are complete;
- no active claim owns the task;
- no active or planned task overlaps a collision domain;
- the candidate session has the required capabilities;
- required authorities are already observed;
- the candidate role is allowed;
- the repository scope matches when the work item specifies one.

A `WORK_OFFER`:
- creates no claim;
- transfers no existing claim;
- grants no mutation authority;
- requires explicit acceptance;
- still requires canonical claim creation and exact-HEAD reconciliation before mutation.

The default limit is one outstanding parallel offer per session.

Commands:

```bash
python3 scripts/gacr_capacity_dispatch.py pool
python3 scripts/gacr_capacity_dispatch.py plan-work
python3 scripts/gacr_capacity_dispatch.py dispatch-work
python3 scripts/gacr_capacity_dispatch.py accept-work --dispatch-id <id> --session-id <id>
```

Client agents can explicitly report capacity:

```bash
python3 scripts/gacr_client_emitter.py availability --session-id <id> --state WAITING --reason-code WAITING_FOR_WORK
python3 scripts/gacr_client_emitter.py availability --session-id <id> --state RATE_LIMITED --reason-code PROVIDER_RATE_LIMIT
python3 scripts/gacr_client_emitter.py availability --session-id <id> --state QUOTA_BLOCKED --reason-code PROVIDER_QUOTA_EXHAUSTED
```

The scheduled GACR relay refreshes safe work offers automatically, but only from explicit/eligible capacity evidence.


### R7 merge / live-capacity attestation

R7 is merged and CI-green.

- merge PR: `#252`;
- merge commit: `819c5f48c1cbb9b7e24a5eb1976e4d16ac1ac31a`;
- post-merge Governance CI: `37560232192 / PASS`;
- post-merge relay: `37560232214 / PASS`.

At the first post-merge read-only observation, the repository exposed non-terminal GACR sessions but no explicit `AVAILABLE`/`WAITING` capacity signal. Therefore no `WORK_OFFER` was emitted. This is expected fail-closed behavior and proves that mere session presence/silence is not treated as dispatch capacity.

The first live capacity assignment proof remains event-dependent: it occurs only when a real agent/provider emits a supported availability signal and a compatible READY work item exists.


## R8 — canonical work-role / capacity declaration junction

R8 closes the gap between a post-F1 agent declaration and capacity-aware work dispatch.

Canonical work roles:
- `CODE_AGENT`;
- `INTAKER`;
- `SUPERVISOR`;
- `REVIEWER`.

An explicit role/capability declaration may enrich the already-bound GACR session. It must not create a duplicate session and must not rewrite entry action or connection intent implicitly.

An explicit post-release outcome containing `WAITING_FOR_WORK` is normalized to:
- `availability_state = WAITING`;
- `availability_reason_code = WAITING_FOR_WORK`.

The capability remains explicit; it is not inferred from the role.

Automatic parallel work dispatch fails closed for a READY work-item that has no explicit compatibility scope. At least one of these must be present:
- `allowed_agent_roles`;
- `required_capabilities`;
- `required_authorities`;
- `target_session_id`.

This prevents an available agent from receiving an unrelated generic/stale task solely because it is idle.

Reusable role prompts: `docs/control-plane/AGENT_ENTRY_PROMPTS.md`.
