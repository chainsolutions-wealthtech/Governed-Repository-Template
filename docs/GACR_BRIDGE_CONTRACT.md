# GACR Bridge Contract

GACR can operate without a provider-specific bridge. A bridge is optional and exists only to solve provider/client capabilities that GitHub cannot provide by itself, such as:

- supplying a ChatGPT/Claude conversation reference to GACR;
- supplying a stable client-instance identifier;
- receiving an external wake/takeover notification;
- opening or focusing the appropriate local conversation;
- launching an API-based standby worker.

## Client → GACR Beacon

A bridge may call the existing `gacr_beacon` / `gacr_register` repository-dispatch surface with safe correlation metadata:

```text
provider
provider_ref
provider_url (optional; not persisted by default)
client_instance_id
bridge_registration_ref
session_id (when already known)
repository/task/branch/PR context when available
wake_channels
```

The bridge must never transmit ChatGPT cookies, browser session cookies, API keys, GitHub tokens or page contents.

For a browser integration, the minimum useful information is:

```text
current conversation reference
client_instance_id
timestamp
```

GACR Correlator combines this with repository/session facts.

## GACR → External Bridge Wake

When a standby session registered `EXTERNAL_BRIDGE`, GACR Dispatcher creates a safe dispatch record.

If the repository configures:

- repository variable `GACR_BRIDGE_WEBHOOK_URL`;
- repository secret `GACR_BRIDGE_WEBHOOK_TOKEN`;

the GACR workflow can POST the wake contract to that endpoint.

The endpoint must treat `dispatch_id` as an idempotency key.

Receiving a wake event **does not grant write authority**. The worker must fetch its GACR agent context and complete exact-HEAD takeover reconciliation before mutation.

## What the bridge may automate

A provider bridge may:

- notify the user;
- focus/open an existing conversation;
- start an API/worker agent when the provider supports it;
- send a new GACR Beacon/heartbeat.

A bridge must not fabricate a conversation ID or bypass GACR claim/authority gates.

## Browser boundary

The repository cannot read a browser address bar remotely. A browser/client bridge can observe its own tab URL and explicitly submit the resulting provider reference to GACR.

This keeps the provider/client boundary explicit while allowing automatic correlation when a bridge is installed.

## R4 automatic attachment boundary

R4 separates attachment from provider enrichment.

A governed agent can attach even when a client cannot expose a provider conversation reference:

```text
repository + safe connection anchor
→ GACR session
→ Beacon / heartbeat
```

If a provider/client later supplies `provider_ref`, `provider_url` or `client_instance_id`, the existing connection-bound session is enriched. A late provider reference must not silently create a second session.

The optional external bridge remains useful for richer provider identity and wake delivery, but it is no longer a prerequisite for basic GACR attachment.

R4 attachment requires no secret material and persists only the safe metadata allowed by GACR.

## R5 client emitter transport

The generic R5 client emitter is implemented in `scripts/gacr_client_emitter.py`.

It supports:

- client-side auto-attach emission;
- recurring heartbeat;
- action/tool trace emission;
- explicit interruption signals;
- session resolution from repository state;
- wake polling.

The transport credential is runtime-only and is never part of the emitted `client_payload`.

Provider-specific adapters may call the Python API or CLI. They do not need to reimplement GACR semantics.

The emitter cannot make an uninstrumented provider UI expose events that the host does not provide. In that case, unsupported client facts remain unavailable and GACR continues to rely on the observable repository/session evidence.


## R7 availability and work-offer transport

Provider/client bridges may enrich GACR with explicit capacity facts.

Safe availability fields:

```text
session_id
availability_state
availability_reason_code
observed_head (optional)
```

Supported states include `AVAILABLE`, `WAITING`, `BUSY`, `BLOCKED`, `RATE_LIMITED`, `QUOTA_BLOCKED`, `CHECKPOINTING` and `TERMINATING`.

A bridge must never infer quota/rate-limit state from silence. When the provider does not expose the cause, keep it `UNKNOWN`.

Clients that poll the canonical dispatch store may receive `dispatch_kind = WORK_OFFER`. A work offer is accepted with `gacr_work-offer-accept`, after which the record becomes `ACCEPTED_PENDING_CLAIM`. Acceptance grants no write authority and does not create a claim.

The legacy external webhook notifier remains takeover-only until a dedicated WORK_OFFER bridge contract is explicitly configured. This prevents a work offer from being rendered as a takeover wake event.


## Provider endpoint / resumability capability matrix

This matrix is a discovery aid, not an authority source. A provider-specific endpoint is usable only when the current session or an installed adapter supplies a real, bounded reference.

| Provider/surface | Durable resume identity | Direct inbound wake endpoint | Current governed behavior |
| --- | --- | --- | --- |
| ChatGPT UI / ChatGPT GitHub connector | Provider conversation reference only when actually exposed by the client; otherwise UNAVAILABLE | No private ChatGPT callback is assumed. The live-proven GitHub issue control bridge is a repository control surface, not a ChatGPT callback. | Registered EXTERNAL_BRIDGE when present; otherwise POLL_REPOSITORY / issue-control fallback. |
| OpenAI Agents API / Codex API session | API session identifiers and reconnect metadata may be supplied by an API adapter | OpenAI session webhooks can call a webhook endpoint controlled by the integrator. Self-hosted session events may also provide reconnect metadata. This is distinct from a ChatGPT UI conversation. | Adapter may register an opaque bridge/session endpoint reference; never infer one for a ChatGPT UI session. |
| Claude Code | Claude Code can expose a session ID that can be resumed by a compatible client/adapter | No generic inbound callback to an existing Claude web conversation is assumed. | Adapter may persist the supplied session reference and launch/resume through its own bridge; otherwise POLL_REPOSITORY. |
| Claude web / generic Anthropic API | Only references actually exposed by the client are accepted | UNAVAILABLE unless an external bridge is explicitly registered | EXTERNAL_BRIDGE when registered; otherwise POLL_REPOSITORY. |
| GitHub Actions | Workflow/repository events are observable transport surfaces, not an external conversational provider session | Repository/workflow dispatch is infrastructure transport, not a user-conversation wake endpoint | Internal transport identity policy remains NEVER_CREATE_SESSION for pure GACR internal workflows. |
| human / other | Supplied stable reference only | UNAVAILABLE unless explicitly registered | EXTERNAL_BRIDGE when registered; otherwise POLL_REPOSITORY. |

Public provider capabilities are advisory inputs for adapter design. They never cause GACR to synthesize a provider conversation ID, endpoint URL, API token, webhook secret or session authority.

### Endpoint evidence classes

A session endpoint projection uses only:

- `OBSERVED`: a live session/adapter supplied a concrete safe bridge registration reference;
- `CONFIGURED`: repository configuration proves a control surface exists, but not that a specific provider conversation is reachable;
- `UNAVAILABLE`: the provider/client did not expose an inbound endpoint.

A repository-side issue comment, workflow or polling channel may be a valid control path while the provider-private endpoint remains `UNAVAILABLE`. These facts must not be conflated.
