# GSCC ↔ GACR Bidirectional Control Integration

Status: **INTEGRATION HARNESS / TEST-ONLY ENDPOINT / NOT LIVE PROVIDER PROOF**

This tranche adds a reusable bidirectional control contract between GACR supervision and a future GSCC session endpoint without changing GACR programme progression, claims, takeover authority, or live runtime stores.

```text
GACR decides
    ⇅
GacrControlAdapter
    ⇅
GSCC transports
    ⇅
SessionEndpoint
    ⇅
GSE interprets
```

The current executable harness substitutes a deterministic `FakeSessionEndpoint` for the future GSCC endpoint:

```text
GACR
 ⇅
GSCC-compatible control contract
 ⇅
FakeSessionEndpoint
```

The fake is a test fixture only. It is not a provider adapter, does not prove a live ChatGPT/Claude/browser session, and does not advance GACR Step 13 or any later realignment step.

## Frozen common contract

Events:

`SESSION_ATTACH`, `SESSION_RESUME`, `HEARTBEAT`, `ACTIVITY_STARTED`, `ACTIVITY_COMPLETED`, `ACTIVITY_FAILED`, `TOOL_STARTED`, `TOOL_COMPLETED`, `TOOL_FAILED`, `PROGRESS`, `BLOCKED`, `CHECKPOINT`, `CONTEXT_UPDATE`, `INTERRUPTION`, `CHALLENGE_RESPONSE`, `COMMAND_ACK`.

Commands:

`PING`, `LIVENESS_CHALLENGE`, `STATUS_REQUEST`, `PROGRESS_REQUEST`, `CONTEXT_REQUEST`, `CHECKPOINT_REQUEST`, `REOBSERVE_HEAD`, `REPORT_BLOCKER`, `PAUSE`, `RESUME`, `SUPERVISOR_INSTRUCTION`, `HANDOFF_PREPARE`, `TAKEOVER_OFFER`.

Delivery states:

`CREATED`, `QUEUED`, `DISPATCHED`, `DELIVERED`, `ACKNOWLEDGED`, `EXECUTING`, `COMPLETED`, `FAILED`, `DECLINED`, `EXPIRED`, `CANCELLED`, `NO_RESPONSE`, `UNSUPPORTED`.

These names are defined in `scripts/gscc_gacr/contract.py` and are frozen for parallel GSCC/GSE integration.

## Authority boundary

The central invariant is:

```text
COMMAND DELIVERY != MUTATION AUTHORITY
```

Therefore:

- `RESUME` does not grant repository write authority.
- `REOBSERVE_HEAD` reports an observation only.
- `TAKEOVER_OFFER` does not mean `TAKEOVER_ACCEPT`.
- no control message transfers a claim;
- no control message bypasses collision domains, dependencies, exact-HEAD reconciliation, or existing GACR takeover acceptance.

A `TAKEOVER_OFFER` is rejected by the adapter unless its payload explicitly carries:

```text
may_write = false
requires_exact_head_reconciliation = true
requires_takeover_accept = true
```

## Command identity and targeting

Every command contains:

- `message_id`;
- `correlation_id`;
- `command_id`;
- `target_session_id`;
- `issued_at`;
- `expires_at`;
- `requires_ack`;
- `command_type`;
- safe command payload;
- `mutation_authority_granted = false`.

The adapter validates the endpoint's exact `session_id` before delivery. A command for Session A cannot be consumed by Session B.

Duplicate command dispatch is idempotent and does not execute twice.

## ACK semantics

`COMMAND_ACK` must bind to all of:

```text
command_id
correlation_id
target_session_id
```

A wrong command/correlation/target is rejected. Re-delivery of the same valid ACK is recognized idempotently and audited without creating a second execution.

## Liveness challenge

`LIVENESS_CHALLENGE` requires:

```text
challenge_id
nonce
issued_at
expires_at
```

The fake endpoint supports deterministic outcomes:

`ACK`, `BUSY`, `IDLE`, `CHECKPOINTING`, `TERMINATING`, `UNSUPPORTED`, `NO_RESPONSE`.

A previously seen nonce is returned as a replay with `fresh_liveness = false`. Replay can therefore never become new liveness evidence.

`NO_RESPONSE` is a delivery result after expiry. It is not proof of `PROCESS_CRASH`, `BROWSER_CLOSED`, `NETWORK_LOSS`, or `PROVIDER_TIMEOUT`.

## Status, progress, context and checkpoint queries

`STATUS_REQUEST` returns only configured/safe fields: current state, current action, current tool, observed HEAD, last progress timestamp, and blocker when explicitly known.

`PROGRESS_REQUEST` returns `last_progress_at`, `progress_marker`, `checkpoint_ref`, and `work_item_ref`.

`CONTEXT_REQUEST` returns a safe objective/context projection: objective reference or safe summary, phase/action, checkpoint, next action, repository, branch, and observed HEAD. It does not expose raw conversation data or private reasoning.

`CHECKPOINT_REQUEST` exercises the delivery lifecycle:

```text
DELIVERED
→ ACKNOWLEDGED
→ EXECUTING
→ COMPLETED
```

and the fixture can also simulate failure/decline/expiry.

## Reobserve, blocker and supervisor instruction

`REOBSERVE_HEAD` returns `observed_head` and explicitly grants no mutation authority.

`REPORT_BLOCKER` returns blocker data only if the endpoint fixture explicitly possesses it. Unknown values remain `UNAVAILABLE`.

`SUPERVISOR_INSTRUCTION` is transport/audit only. Tests cover success plus `FAILED`, `DECLINED`, `EXPIRED`, and `NO_RESPONSE`.

## Pause, resume and handoff

`PAUSE` and `RESUME` alter only the fake endpoint's session-control state. Their responses explicitly retain `mutation_authority_granted = false`.

`HANDOFF_PREPARE` may return checkpoint reference, current action, observed HEAD, and a safe context reference. It does not close the session by itself.

## Takeover offer

The harness proves only:

```text
GACR / Dispatcher state
→ TAKEOVER_OFFER
→ successor endpoint
→ COMMAND_ACK / receipt
```

The receipt contains:

```text
may_write = false
requires_exact_head_reconciliation = true
requires_takeover_accept = true
claim_transferred = false
```

Existing GACR takeover acceptance remains the only authority for a governed claim transfer.

## Expiration and no response

A command already expired before dispatch becomes `EXPIRED` and cannot transition to `EXECUTING`.

A command successfully delivered to an endpoint that produces no response remains `DELIVERED` until its deadline. After the deadline it becomes `NO_RESPONSE`.

No unobserved external cause is inferred.

## Audit and storage model

`GacrControlAdapter` stores only in-memory delivery state for the harness: command, current delivery state, transition history, ACK, response, and dispatch count.

It does not write a second session store, claims store, takeover store, or GACR state database.

The regression test snapshots the source GACR live stores before and after the full harness and asserts byte-for-byte equality.

## Credential boundary

Control payloads reject secret/transcript/private-reasoning fields. In particular, commands may not contain token, secret, authorization, cookie, browser session, password, private key, raw transcript, prompt, or private reasoning/chain of thought.

Any future external transport authentication must remain in runtime environment/GitHub Secrets and outside the command payload.

## Future GSCC endpoint interface

The stable replacement seam is a session endpoint with a `session_id` and:

```text
send(command) -> EndpointExchange
```

The deterministic fake additionally exposes `receive()`, `ack()`, and `respond()` helpers for harness inspection.

A real GSCC endpoint must preserve exact target verification, command identity/correlation, ACK idempotence, expiry, response correlation, replay-safe challenge nonce behavior, and the credential boundary.

The adapter should not need scenario rewrites when `FakeSessionEndpoint` is replaced with the real GSCC implementation.

## Future GSE interface

The control layer exposes data that GSE may interpret without making the control adapter a `SessionTwin`.

At minimum GSE can consume `COMMAND_ACK`, `CHALLENGE_RESPONSE`, status response payloads, progress response payloads, safe context/checkpoint responses, and the command delivery lifecycle.

GSE remains responsible for its own state interpretation. The harness does not implement GSE runtime.

## Historical external bridge compatibility

`scripts/gacr_bridge_notifier.py` remains unchanged.

The regression suite verifies its current `GACR_TAKEOVER_READY` payload still preserves dispatch ID as idempotency key, `requires_context_fetch = true`, and `may_write = false`.

A later GSCC transport may sit beside or behind that historical bridge, but this tranche does not turn the notifier into a general control API.

## GACR programme isolation

This artifact does not modify:

- `docs/control-plane/GACR_PROGRAM.md`;
- `docs/control-plane/GACR_ORIGIN_REALIGNMENT.md`;
- `.governance/control-plane-state/gacr-program.json`;
- GACR live session/Beacon/Correlation/Dispatch/Forensics/Takeover stores;
- P12-S6;
- CASE 1;
- GMC;
- the global programme.

The harness is integration preparation only. It cannot be used as evidence that a fresh provider agent has passed Step 13.


## G5 canonical control-response → GSE projection

The integration layer now provides one additive mapper:

`scripts/gscc_gacr/gse_projection.py`

It converts safe control query snapshots into the existing canonical GSE event vocabulary:

| Control response | Canonical GSE event | Semantics |
|---|---|---|
| `STATUS_RESPONSE` | `CONTEXT_UPDATE` | enrich current action/head/status snapshot only |
| `CONTEXT_RESPONSE` | `CONTEXT_UPDATE` | enrich repository/branch/head/action/next action/checkpoint |
| `CHECKPOINT_RESPONSE` | `CHECKPOINT` | update checkpoint context without `checkpoint_advanced` |
| `PROGRESS_RESPONSE` | `PROGRESS` | preserve reported progress snapshot with `qualifying_progress=false` |

Hard invariants:

```text
STATUS RESPONSE != LIVENESS EVIDENCE
CONTEXT RESPONSE != LIVENESS EVIDENCE
CHECKPOINT SNAPSHOT != PROGRESS ADVANCEMENT
PROGRESS QUERY RESPONSE != NEW PROGRESS AT QUERY TIME
CONTROL RESPONSE MAPPING != SECOND STATE ENGINE
```

`UNAVAILABLE` fields are omitted rather than overwriting known SessionTwin identity/context.
The mapper does not introduce any new GSE dimension, claim authority, takeover authority, or mutation authority.

The real `GSCCSessionControlEndpoint` also supports the four query commands through
the actual `SessionEndpoint.receive_commands()` path. The endpoint handler returns bounded
safe snapshots; these are correlated by the control adapter and then projected through the
single mapper above. No new GSCC event names are added.
