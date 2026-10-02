# GACR Original Intent and Historical Stop Point

> Authority: `CP-AGENT-RELAY-001-ORIGIN`
> Status: `CANONICAL_HISTORICAL_INTENT`
> Purpose: preserve why GACR was created, the two external limits that drove its evolution, the intended architecture, and the exact historical point where that evolution was ready to be implemented.
> This is GACR programme authority. It is distinct from the global Control Plane programme.

## Why GACR was created

GACR was created because long-running agents could stop abruptly while working on a governed repository. A conversation could become too long, a client/provider could stop emitting activity, a browser tab could disappear, or an agent could become silent without making it clear whether it was still working, blocked, stopped, or gone.

The required invariant was:

> A conversation may disappear, an agent may crash, a tab may time out, and a client may vanish; the governed work must remain identifiable, reconstructible and resumable.

The repository/governance system must preserve enough operational evidence that continuity does not depend on survival of a particular chat tab.

## Historical baseline already implemented

At the historical stop point, the GACR baseline already covered:

- governed sessions;
- heartbeat;
- lease;
- `SUSPECTED_STALL`;
- `STALLED`;
- `TAKEOVER_READY`;
- standby sessions;
- active claim preservation while stalled;
- exact-HEAD reconciliation before takeover;
- governed claim transfer;
- checkpoint / handoff;
- periodic supervision;
- Template-source versus client-project runtime-memory separation;
- green CI for that baseline.

Historical note: the owner remembered this stop point around Template/GACR version `2.8.30`. That version reference is historical context only; later R1-R6 work superseded the implementation baseline. The original intention recorded here remains authoritative for purpose and direction.

## The two external limits that drove the next evolution

### Limit 1 — identify the actual agent/conversation more automatically

Question:

> How can GACR identify a conversation/session more automatically and recover more information when an agent connects to or acts on a repository?

Observation:

A repository interaction exposes more safe operational metadata than the original GACR baseline persisted. GitHub can expose repository, actor/application, branch/ref, SHA, pull request, workflow/run/job, timestamps, triggering event, app/installation context when available, commits, checks and related platform evidence.

The agent/client can also explicitly supply provider, model/type when available, task/goal, conversation reference when known, capabilities and active/standby mode.

Provider-private data that is never transmitted cannot be reconstructed with certainty from GitHub evidence alone.

### Limit 2 — wake or activate another standby agent

Question:

> How can GACR go beyond `TAKEOVER_READY` and actually relay/activate compatible standby capacity when an agent stalls?

The repository can detect stall, reconstruct context, rank compatible standbys and create a takeover offer. True automatic execution depends on the target worker/provider. An API/orchestrator-controlled worker may be started automatically. A normal browser ChatGPT tab may at most be identified, notified, opened/focused and supplied with a takeover package unless the provider exposes an execution surface.

GACR must not depend on provider wake capability to preserve work continuity.

## Intended four-component architecture

```text
GACR
|
+-- BEACON
|   connection + safe telemetry
|
+-- WATCH
|   heartbeat + lease + stall detection
|
+-- CORRELATOR
|   session
|      <-> GitHub activity
|      <-> branch
|      <-> PR
|      <-> commits
|      <-> workflows
|      <-> conversation when actually known
|
+-- DISPATCHER
    standby selection
    + takeover preparation
    + activation / relay
```

WATCH was already largely covered by the existing GACR baseline.

A first Dispatcher path also already existed:

```text
STALLED
→ TAKEOVER_READY
→ compatible standby search
→ takeover offer
→ exact HEAD
→ governed claim transfer
```

The historical next implementation focus was the additive enrichment of BEACON + CORRELATOR + DISPATCHER while preserving WATCH and the existing GACR core.

## GACR Connection Envelope

The target arrival/connection record was defined as a safe envelope containing only facts that are actually observable or explicitly supplied.

```text
GACR_CONNECTION_ENVELOPE

gacr_session_id
client_instance_id

provider
agent_identity
agent_type_or_model_if_supplied

repository
repository_id
organization
git_provider

github_actor
github_app_or_installation_if_observable
connection_method
permissions_or_capabilities_if_observable

entry_action
connection_intent
task_id
claim_id

branch
base_branch
observed_HEAD
pull_request

workflow_run_id
job_id
run_attempt
event_type
delivery_or_correlation_ids_if_available

connected_at
last_seen_at
heartbeat_seq
lease_expires_at

provider_conversation_ref_if_supplied
provider_conversation_url_if_supplied

checkpoint
last_action
last_evidence
```

Hard rule:

> NEVER INVENT CONVERSATION INFORMATION THAT THE CLIENT/PROVIDER DID NOT SUPPLY.

At the same time, persist and use all allowlisted operational metadata that is truly observable and useful for continuity.

The envelope must never contain secrets, tokens, cookies, passwords, authorization headers, raw transcript bodies or private reasoning.

## Connection fingerprint

A connection fingerprint was intended to strengthen session/activity correlation when a native provider conversation reference is unavailable.

Candidate inputs:

```text
provider
+ repository
+ actor / GitHub App
+ task
+ branch
+ PR
+ first observed HEAD
+ connection method
+ client_instance_id
+ bounded timestamp context
→ connection_fingerprint
```

The fingerprint is not a provider conversation ID and must never be presented as one.

Its purpose is to support a statement such as:

> This GitHub activity belongs with high confidence to the same governed agent instance first observed earlier.

A session may therefore remain operationally reconstructible even when:

```text
CHAT URL = UNKNOWN
```

while the following remain known:

```text
AGENT SESSION = KNOWN
TASK = KNOWN
BRANCH = KNOWN
PR = KNOWN
HEAD = KNOWN
CLAIM = KNOWN
LAST ACTION = KNOWN
LAST RESULT = KNOWN
LAST EVIDENCE = KNOWN
STALL STATE = KNOWN
RESUME POINT = KNOWN
```

## Correlator target

The Correlator was intended to combine:

```text
session
↓
GitHub actor/app
↓
repository
↓
task / claim
↓
branch
↓
PR
↓
commit / HEAD
↓
workflow runs
↓
timestamps
↓
external conversation ref when actually supplied
```

Correlation quality is explicit:

- `EXACT`
- `STRONG`
- `PROBABLE`
- `AMBIGUOUS`
- `UNKNOWN`

No uncertain correlation may be presented as a known provider conversation identity.

Example:

```text
correlation = STRONG
session_id = ...
task = ...
branch = ...
PR = ...
actor = ...
latest_HEAD = ...
conversation_ref = UNKNOWN
```

That may still be sufficient for safe work reconstruction.

## Dispatcher target

The Dispatcher was intended to progress beyond merely creating `TAKEOVER_READY`.

```text
STALLED
↓
CORRELATOR reconstructs context
↓
DISPATCHER finds standbys
↓
compatibility evaluation:
    repository
    authority
    capabilities
    collision domains
    dependencies
↓
standby ranking
↓
selection
↓
TAKEOVER OFFER
↓
exact-state reconciliation
↓
activation / relay where provider capability exists
```

Selection or wake does not grant mutation authority. Existing claim, collision-domain, dependency and exact-HEAD gates remain authoritative.

## Optional GACR Bridge / Provider Adapter

A provider/client bridge is optional enrichment, not a prerequisite for GACR continuity.

It may safely transmit:

- provider;
- provider conversation ID/reference;
- provider conversation URL;
- generated `client_instance_id`;
- timestamp;
- repository binding;
- GACR session ID.

It may also notify, open/focus a local conversation or invoke a programmable worker when the provider exposes an execution API.

It must never collect or transmit provider cookies, browser session cookies, secret tokens, raw conversation content or private reasoning.

## Agent-context philosophy

The intended GACR experience includes a conceptual `GET /agent-context` aggregate that can tell an arriving agent:

```text
YOU ARE SESSION X

repository = ...
task = ...
claim = ...
HEAD = ...
branch = ...
PR = ...

other agents:
A ACTIVE
B STANDBY
C STALLED

collision domains = ...
last checkpoint = ...
next safe action = ...
heartbeat / lease = ...
```

The agent should know who it is in the governed system as soon as possible.

## Historical point of interruption

The remembered historical stop point was:

> The GACR baseline was operational and the analysis of the two external limits was complete. The system was ready to implement the additive BEACON + WATCH + CORRELATOR + DISPATCHER evolution, reusing the existing GACR core without regression.

This historical stop point is not a claim that current R6 lacks all of those components. Subsequent R2-R6 work implemented significant portions of Beacon, Correlator, Dispatcher, Bridge, automatic attachment and host ingress.

The purpose of preserving the historical stop point is to prevent later work from forgetting **why** those components existed and what they were supposed to achieve.

## Relationship with the global programme

GACR is a distinct technical programme.

The global Control Plane programme and GACR may coexist in the same repository and share governance safety primitives, but they have separate chronologies and separate next actions.

The owner's sequencing instruction at this historical point was:

> Finish GACR first. Return to the global programme only after explicit owner OK.

Therefore:

- a global task such as `P12-S6` is not a functional dependency of the GACR programme;
- advancing GACR does not advance the global programme;
- advancing the global programme does not prove GACR complete;
- GACR completion is evaluated against GACR's own acceptance criteria;
- when the owner explicitly directs GACR work, the GACR programme may progress independently while the global programme remains parked.

## Foundational philosophy

```text
A CONVERSATION MAY DIE.
AN AGENT MAY CRASH.
A TAB MAY TIME OUT.
A MODEL MAY STOP.
A CLIENT MAY DISAPPEAR.

BUT:

THE GOVERNED SESSION,
THE TASK,
THE CLAIM,
THE HEAD,
THE BRANCH,
THE PR,
THE EVIDENCE,
THE CHECKPOINT,
AND THE NEXT SAFE ACTION

MUST REMAIN RECOVERABLE.
```

The repository/governance system is the durable continuity memory. Provider conversations are temporary clients of that continuity.
