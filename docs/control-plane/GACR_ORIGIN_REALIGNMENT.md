# GACR Origin Realignment — Presence-First Plan

> Canonical planning authority under `CP-AGENT-RELAY-001`.
> Status: `ACCEPTED_PLAN / NOT_YET_EXECUTED`.
> Baseline preserved: GACR R1 through R6 inclusive.
> This document is source-control-plane memory and must not be interpreted as proof that the planned realignment has already been implemented.

## Why this plan exists

GACR R1-R6 produced valuable continuity primitives: governed sessions, heartbeat/lease, takeover, Beacon, Correlator, Interruption Forensics, automatic attachment, client emitter, provider-host ingress, fail-closed correlation, exact-HEAD takeover and source/client isolation.

The owner has clarified that the accumulated implementation drifted away from the original center of gravity.

The original center of gravity is **presence-first continuity**:

> When a governed agent or conversation uses a governed repository through an instrumentable access surface, the repository interaction itself must be sufficient to make that agent/session observable to GACR. The agent must not need to remember to invoke GACR in order for GACR to know that the agent exists.

R1-R6 are therefore preserved as reusable capabilities. The next GACR evolution must realign how those capabilities are entered and interpreted; it must not delete or replace them.

## Non-destructive invariants

1. Do not delete, rewrite or roll back R1-R6 history, tests, schemas, state or live evidence.
2. Do not introduce a second task engine, second claim model, second lock store or parallel continuity database.
3. Preserve claims, collision domains, exact-HEAD reconciliation and existing authority gates.
4. Missing provider-private metadata remains `UNAVAILABLE`; it is never invented.
5. Internal transport is not an agent identity.
6. Safe operational observability does not include cookies, tokens, secrets, raw transcript bodies or private chain-of-thought.
7. Liveness and progress are different dimensions and must not be conflated.
8. Silence alone does not prove crash, timeout or a particular external cause.
9. A provider-specific wake capability is optional; continuity must still permit safe takeover by another governed agent.
10. GACR must not be declared fully realigned until the end-to-end acceptance scenario in this document passes live.

## Target model

```text
AGENT / CONVERSATION
        |
        | first observable repository interaction
        v
GACR PRESENCE FABRIC
        |
        +--> observe safe connection/access metadata
        +--> CREATE / RESUME canonical GACR session
        +--> emit PRESENCE / ACTIVITY evidence
        |
        v
LIVENESS EVIDENCE + PROGRESS EVIDENCE
        |
        v
WATCH / CORRELATOR / FORENSICS
        |
        +--> WORKING
        +--> QUIET
        +--> SUSPECTED_STALL
        +--> STALLED
        |
        v
DISPATCH / WAKE WHEN AVAILABLE
        |
        v
EXACT-HEAD TAKEOVER
        |
        v
CONTINUE
```

The architectural correction is therefore not “more telemetry events”. It is to make **observable repository presence** the primary entry into the already-built GACR capabilities wherever the access path can be instrumented.

## Mandatory execution sequence

The following order is frozen. A later step may not be treated as executable proof for an earlier unfinished step.

| # | Operation | Initial status | Exit evidence |
|---:|---|---|---|
| 1 | Freeze and attest the current R6 baseline so nothing already built is lost. | BASELINE_AVAILABLE / REOBSERVE_BEFORE_EXECUTION | Exact current `main`, R1-R6 assets and live evidence reobserved and recorded. |
| 2 | Reconstruct the original GACR intention from R1 history, owner requirements and existing authorities. | SOURCE_CAPTURED / FORMAL_GATE_PENDING_STEP_1 | `docs/control-plane/GACR_ORIGINAL_INTENT.md` now preserves the original intention and historical stop point; ordered execution is not marked DONE before step 1. |
| 3 | Build `ORIGINAL_INTENT ↔ CURRENT_IMPLEMENTATION ↔ GAP` matrix. | PLANNED | Every original objective mapped to current capability, partial coverage or gap. |
| 4 | Identify precisely where R4-R6 shifted the center of gravity toward explicit event transport rather than automatic presence observation. | PLANNED | Documented drift analysis; no existing capability deleted. |
| 5 | Write acceptance tests before corrective implementation. | PLANNED | RED/expected-fail tests for automatic presence, liveness/progress, stall and takeover behavior. |
| 6 | Introduce the GACR Presence Fabric in front of the existing GACR core. | PLANNED | Additive architecture integrated without replacing R1-R6. |
| 7 | Instrument repository access paths that the framework controls. | PLANNED | First-touch/activity hooks on controlled gateway/connector/bridge surfaces. |
| 8 | Convert each safe observable access/activity into Presence/Activity evidence. | PLANNED | Canonical safe observation envelope persisted/correlated. |
| 9 | Separate `LIVENESS` from `PROGRESS`. | PLANNED | Independent states/evidence and no heartbeat-as-progress inference. |
| 10 | Add session interrogation and active liveness challenge where a target endpoint supports it. | PLANNED | Queryable session context plus challenge outcome semantics. |
| 11 | Add `UNBOUND_ACTIVITY` reconciliation for repository activity not yet explained by a GACR session. | PLANNED | Fail-closed correlation or explicit UNBOUND classification. |
| 12 | Reuse Beacon, Correlator, Forensics and Dispatcher behind the new presence layer. | PLANNED | Existing components remain canonical and receive presence-derived evidence. |
| 13 | Run a real test using a fresh conversation/agent. | PLANNED | Fresh external agent/conversation selected as live fixture. |
| 14 | Verify the agent appears in GACR without being explicitly instructed to register with GACR. | PLANNED | Presence/session created or resumed from instrumented repository use alone. |
| 15 | Make the agent perform real governed repository work. | PLANNED | Observable governed work activity with no bypass. |
| 16 | Observe the agent's evolution while it works. | PLANNED | Time-ordered liveness and progress evidence. |
| 17 | Interrupt or allow the live activity to stop in a controlled test. | PLANNED | No fabricated cause; last safe evidence preserved. |
| 18 | Observe `SUSPECTED_STALL → STALLED` according to governed lease/evidence rules. | PLANNED | Deterministic state transition evidence. |
| 19 | Connect a second governed agent. | PLANNED | Distinct successor session/presence observed. |
| 20 | Reconstruct the predecessor's exact operational stopping point. | PLANNED | Forensic/context package identifies branch/task/action/checkpoint/evidence. |
| 21 | Reobserve exact branch/HEAD before ownership transfer. | PLANNED | Exact-HEAD reconciliation PASS. |
| 22 | Accept governed takeover through the existing claim/authority gates. | PLANNED | Ownership transfer is explicit, collision-safe and auditable. |
| 23 | Continue the actual work from the reconstructed state. | PLANNED | Successor advances the same governed work without replaying completed work. |
| 24 | Only then declare GACR origin realignment complete. | PLANNED | Ultimate acceptance scenario PASS plus CI/live attestation. |

## Presence observation contract to design

The realignment must define a safe observation envelope capable of representing, when actually observable:

- observation timestamp;
- repository;
- transport/integration class;
- stable connection/client instance reference when provided;
- provider when provided;
- provider conversation reference only when truly supplied;
- repository operation class;
- branch and observed HEAD when available;
- canonical GACR session binding;
- source/provenance of the observation.

The contract must explicitly reject secret material and transcript/private-reasoning capture.

## Liveness versus progress

Realignment must make these independently queryable.

Examples:

```text
LIVENESS = ACTIVE
PROGRESS = ADVANCING
```

```text
LIVENESS = ACTIVE
PROGRESS = NO_RECENT_PROGRESS_EVIDENCE
```

```text
LIVENESS = UNKNOWN
PROGRESS = NO_RECENT_EVIDENCE
```

Progress evidence may include safe observable facts such as repository/tool activity, action STARTED/COMPLETED traces, commits, PR changes, checkpoints, written-HEAD movement or other allowlisted operational evidence. A heartbeat alone is not proof of progress.

## Session interrogation target

A canonical session-context view should ultimately answer, from evidence:

- Who/what session is present?
- What repository/task/branch/PR is it associated with?
- Is there evidence that it is alive?
- Is there evidence that it is progressing?
- When was the last progress evidence?
- What action is currently in flight, if any?
- What is the last safe checkpoint?
- What are the observed and written HEADs?
- What claim/collision-domain state applies?
- Is takeover eligible?
- What must a successor reobserve before continuation?

Unknown facts remain unknown.

## Active liveness challenge boundary

Where a provider/client/gateway exposes a challenge channel, GACR may request a liveness acknowledgement such as `ACK`, `BUSY`, `IDLE`, `CHECKPOINTING` or `TERMINATING`.

No response is evidence of `LIVENESS_CHALLENGE_TIMEOUT`; it is **not** independent proof of a crash.

## Unbound repository activity

If a commit, PR change or other governed repository activity is observed without a deterministically bound session, GACR must create an `UNBOUND_ACTIVITY` observation and attempt fail-closed reconciliation using safe evidence.

If the evidence is insufficient, it remains `UNBOUND`; attribution is never invented.

## Access-surface classes

The realignment must distinguish:

1. **Controlled/instrumentable access** — gateway, connector, bridge or MCP path where first-touch/activity can be observed directly.
2. **GitHub event-visible activity** — commits, PRs, issue comments, workflow events and other platform events observable after the fact.
3. **Proprietary silent access** — provider-side repository reads that expose no usable event or instrumentation hook.

Class 3 must not be falsely represented as automatically observable. The architecture should move as much governed access as practical through class 1 while retaining class 2 reconciliation and explicit class 3 limitations.

## Ultimate acceptance scenario

GACR origin realignment is not complete unless this scenario is live-proven:

```text
START A NEW CONVERSATION / AGENT.

ASK IT TO WORK ON THE GOVERNED REPOSITORY.

DO NOT TELL IT TO REGISTER WITH GACR.

GACR MUST OBSERVE IT THROUGH AN INSTRUMENTED ACCESS PATH.

GACR MUST CREATE OR RESUME ITS CANONICAL SESSION.

GACR MUST OBSERVE ITS SAFE ACTIVITY.

GACR MUST DISTINGUISH LIVENESS FROM PROGRESS.

WHEN THE AGENT STOPS, GACR MUST DETECT THE LOSS OF FRESH EVIDENCE
AND FOLLOW THE GOVERNED STALL TRANSITION.

A SECOND AGENT MUST BE ABLE TO RECONSTRUCT THE STOPPING POINT,
REOBSERVE EXACT HEAD, ACCEPT TAKEOVER THROUGH EXISTING AUTHORITY GATES,
AND CONTINUE THE SAME WORK.

THE WORK MUST NOT DEPEND ON THE SURVIVAL OF THE ORIGINAL CHAT.
```

If this scenario does not pass, the status must remain partial even if unit/CI tests are green.

## Relationship to the global programme

GACR is a distinct technical programme with its own chronology and next action. The global Control Plane programme is governed separately by `docs/control-plane/PROGRAM.md`.

Canonical GACR programme authority: `docs/control-plane/GACR_PROGRAM.md`.

Rules:

- there is no dependency edge `P12-S6 → GACR`;
- advancing GACR does not advance the global programme;
- advancing the global programme does not prove GACR complete;
- when the owner directs GACR work, GACR may progress while the global programme remains parked;
- the historical sequencing instruction is: finish GACR first, then return to the global programme only after explicit owner OK;
- all GACR mutation still follows repository governance, exact-HEAD and CI requirements;
- the presence-first invariants in this document must be read before any further GACR revision is designed.

