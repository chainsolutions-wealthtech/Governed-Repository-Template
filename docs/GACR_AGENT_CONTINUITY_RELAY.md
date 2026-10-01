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
