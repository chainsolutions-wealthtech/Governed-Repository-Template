# GSCC Protocol v1 — Governed Session Control Channel

Status: candidate extension. This document does **not** advance, close or reinterpret any GACR realignment step.

## Mission

GSCC is a reusable, bidirectional, transport-agnostic control channel between an agent/conversation endpoint and a supervision/orchestration system. It carries events, commands, acknowledgements, capability declarations and bounded operational responses.

```text
AGENT / CONVERSATION
        ⇅
       GSCC
        ⇅
        GSE
        ⇅
       GACR
        ⇅
GOVERNED REPOSITORY
```

The separation is normative:

```text
GSCC transports.
GSE interprets.
GACR governs continuity.
```

GSCC does not decide `STALLED`, `TAKEOVER_READY`, `CLAIM_TRANSFER`, `LOOP_CONFIRMED`, inferred blocking or mutation authority. It transports evidence and control messages only.

## Message envelope

Canonical schema: `gscc-message/v1`.

Required top-level fields:

```text
schema
message_id
correlation_id
idempotency_key
kind
type
issued_at
source
target
scope
payload
delivery
```

`source`, `target`, `scope` and `payload` carry only facts actually known or explicitly supplied. Unknown provider-private identifiers are omitted or represented by an explicit application-level unavailable value; they are never manufactured.

`message_id` identifies one logical message. `correlation_id` binds request/response or command/ACK families. `idempotency_key` prevents duplicate side effects across delivery retries.

## Kinds

Frozen shared kinds:

- `EVENT`
- `COMMAND`
- `ACK`
- `CAPABILITIES`

Unknown kinds are rejected. Extensions must be additive and version-compatible.

## Events — Agent to Control

Frozen shared event types:

`SESSION_ATTACH`, `SESSION_RESUME`, `HEARTBEAT`, `ACTIVITY_STARTED`, `ACTIVITY_COMPLETED`, `ACTIVITY_FAILED`, `TOOL_STARTED`, `TOOL_COMPLETED`, `TOOL_FAILED`, `PROGRESS`, `BLOCKED`, `CHECKPOINT`, `CONTEXT_UPDATE`, `INTERRUPTION`, `CHALLENGE_RESPONSE`, `COMMAND_ACK`.

Events are evidence. Their presence does not itself authorize a GACR state transition.

## Commands — Control to Agent

Frozen shared command types:

`PING`, `LIVENESS_CHALLENGE`, `STATUS_REQUEST`, `PROGRESS_REQUEST`, `CONTEXT_REQUEST`, `CHECKPOINT_REQUEST`, `REOBSERVE_HEAD`, `REPORT_BLOCKER`, `PAUSE`, `RESUME`, `SUPERVISOR_INSTRUCTION`, `HANDOFF_PREPARE`, `TAKEOVER_OFFER`.

A GSCC command is an instruction-delivery object, not proof that the instruction executed.

## ACK and delivery lifecycle

Canonical transport lifecycle:

```text
CREATED
→ QUEUED
→ DISPATCHED
→ DELIVERED
→ ACKNOWLEDGED
→ EXECUTING
→ COMPLETED
```

Terminal or alternate states are `FAILED`, `DECLINED`, `EXPIRED`, `CANCELLED`, `NO_RESPONSE`, and `UNSUPPORTED`.

`DELIVERED` means the command reached the receiving control surface. It does **not** mean the receiving agent executed it. `ACKNOWLEDGED` means the receiver explicitly acknowledged the message. `EXECUTING` and `COMPLETED` require stronger receiver-side evidence.

An ACK uses kind `ACK`, type `COMMAND_ACK`, preserves the command `correlation_id`, and identifies the command with `payload.command_message_id`.

## Idempotence

Every message contains both `message_id` and `idempotency_key`. A receiver must suppress duplicate effects when either identity has already been processed. A repeated network delivery returns the previously recorded result or an `ALREADY_PROCESSED` equivalent.

Idempotence is transport-level safety. It does not grant business mutation authority.

## Capabilities

A client may send kind `CAPABILITIES`, type `HELLO`, containing only capabilities it actually implements.

Frozen shared capabilities:

`HEARTBEAT`, `STATUS_RESPONSE`, `PROGRESS_REPORT`, `CONTEXT_REPORT`, `CHECKPOINT_REPORT`, `CHALLENGE_RESPONSE`, `COMMAND_RECEIVE`, `COMMAND_ACK`, `BACKGROUND_EXECUTION`, `TAKEOVER_RECEIVE`.

Absence means absence. A client that receives an unsupported command returns `UNSUPPORTED`; it must not simulate a capability.

## SessionEndpoint

`scripts/gscc/session_endpoint.py` exposes the reusable endpoint contract:

```text
attach()
resume()
heartbeat()
activity_started()
activity_completed()
activity_failed()
tool_started()
tool_completed()
tool_failed()
progress()
blocked()
checkpoint()
context_update()
receive_commands()
ack_command()
respond_challenge()
disconnect()
```

The endpoint emits protocol messages through an injected transport and uses an idempotency store when consuming commands.

## Tool instrumentation

`scripts/gscc/instrumentation.py` provides the canonical wrapper interface around real tool calls. It supports a `before_tool_call` hook that executes before Function Exposure evaluation and before `TOOL_STARTED`. Provider First Touch uses this hook so the first instrumented tool of any kind may emit `gscc_provider_first_touch` without maintaining tool-specific wrappers.

Ordering is normative:

```text
before_tool_call / Provider First Touch
→ Function Exposure Gate when configured
→ TOOL_STARTED
→ real tool call
→ TOOL_COMPLETED | TOOL_FAILED
```

The instrumentation layer deliberately does not serialize tool arguments, tool results, raw exception messages, prompts or provider content.

## Transport abstraction

GSCC Core depends on a generic `Transport` contract with `send()` and `receive()`.

Current implementations:

- `InMemoryTransport` for isolated tests/harnesses;
- `GitHubDispatchTransport` for GitHub `repository_dispatch` send semantics plus an injected governed receive/poll adapter when bidirectional reception is available.

Future transports may include webhook, WebSocket, MCP or local IPC adapters. They are outside GSCC v1.

GitHub is therefore one transport, not the definition of GSCC.

## GACR backward compatibility

The historical `scripts/gacr_client_emitter.py` remains unchanged.

`scripts/gscc/gacr_compat.py` supplies an additive compatibility adapter for the event subset that has a safe historical mapping:

- `SESSION_ATTACH` / `SESSION_RESUME` → `ClientEmitter.attach()` (historical auto-attach resolves create-versus-resume);
- `HEARTBEAT` → `ClientEmitter.heartbeat()`;
- activity/tool lifecycle → `ClientEmitter.trace()`;
- `INTERRUPTION` → `ClientEmitter.interrupt()`.

Unsupported GSCC events fail explicitly rather than being silently rewritten into a different GACR meaning.

This preserves the historical API and keeps GACR as a consumer/integration target rather than making GSCC a second GACR.

## Credential boundary

Credentials are outside the GSCC message plane. The message validator rejects secret-bearing or transcript-like key families and common secret-like values.

GSCC messages must never contain passwords, secrets, private keys, authorization headers, access/refresh tokens, authentication cookies, browser session cookies, raw transcripts, raw prompts, private reasoning, chain-of-thought or raw assistant responses.

A transport/provider adapter may hold its credential in its private runtime environment. For example, `GitHubDispatchTransport` may hold a token internally to authenticate the HTTP request, but that token is never serialized into the GSCC envelope.

The safe identity surface consists of opaque facts such as `provider`, `provider_ref`, `connection_ref`, `client_instance_id` and `session_id` when those facts are actually available.

## Provider metadata rules

Provider conversation identifiers and URLs are supplied-only facts. GSCC never infers them from a repository actor, branch, SHA, fingerprint or transport connection. `UNKNOWN` and `UNAVAILABLE` are never promoted to known identity.

A repository-derived fingerprint may be carried inside `scope` or `payload` if generated by the appropriate continuity layer, but GSCC treats it as opaque evidence; it does not reinterpret it as provider identity.

## Extension mechanism

During the parallel integration tranche the shared kinds, event names, command names, delivery states and capability names are frozen. Extensions must be additive and must not force peer branches to consume them.

A protocol-breaking rename/removal requires a new schema version. An additive transport or higher-layer payload field may remain within v1 when old receivers can safely ignore it.

## Security and state isolation

GSCC Core has no dependency on live GACR state files and does not write `.governance/control-plane-state/gacr-*` stores. Tests use `InMemoryTransport`, in-memory idempotency state and deterministic fixtures only.

The channel transports control/evidence. It does not persist or mutate GACR claims, takeover state, Correlator authority or programme chronology.



## Admission and access qualification

Governed function exposure is preceded by an additive admission layer. This layer does not replace the Observable Arrival Gateway, GSE or GACR.

Canonical contracts:

- `gscc-admission-envelope/v1`;
- `gscc-admission-receipt/v1`;
- `gscc-access-grant/v1`.

Canonical candidate implementation:

- `scripts/gscc/admission.py`;
- `.github/workflows/gscc-admission-gate.yml`.

The admission workflow accepts two distinct control-plane requests:

- `gscc_admission_request` — validates the safe admission envelope and may return `PREAUTHORIZED`;
- `gscc_access_qualification_request` — validates bounded qualification evidence and may return an `AUTHORIZED` Access Grant.

`PREAUTHORIZED` never means repository access, function exposure, invocation authority or mutation authority.

A valid Access Grant is bound to admission ID, session ID, connection reference, repository, exact HEAD and expiry. It is only eligibility evidence for the existing canonical Function Exposure Gate.

The Function Exposure Gate therefore starts with:

```text
ADMISSION_RECEIPT_VALIDATION
→ ACCESS_GRANT_VALIDATION
→ GSCC_SESSION_BIND
→ ...
```

An absent, expired, mismatched or malformed Access Grant fails closed. The grant also constrains which authority classes may subsequently be proven. The grant itself still has:

```text
invocation_authority_granted = false
mutation_authority_granted = false
```

The admission workflow has repository permission `contents: read` only and persists bounded results as Actions artifacts. It does not contain repository mutation operations.

## Function exposure gate

A governed function catalogue is not a raw implementation catalogue. A function becomes publishable only after GSCC validates the complete safe route for the current connection and exact repository state.

```text
OBSERVABLE ARRIVAL
→ GSCC SESSION BIND
→ CONNECTION ENVELOPE
→ EXACT HEAD
→ ENTRY ACTION
→ CAPABILITY SNAPSHOT
→ FUNCTION CONTRACT MATCH
→ AUTHORITY VALIDATION
→ LIVE PREFLIGHT WHEN REQUIRED
→ EXPOSURE RECEIPT = VALIDATED
→ FUNCTION MAY BE EXPOSED
→ PRE-CALL REVALIDATION
→ TOOL_STARTED
→ REAL CALL
→ TOOL_COMPLETED / TOOL_FAILED
```

Canonical implementation:

- `scripts/gscc_function_exposure_gate.py`;
- `.github/workflows/gscc-function-exposure-gate.yml`;
- `schemas/gscc-function-exposure-receipt.schema.json`;
- `scripts/gscc/instrumentation.py` for pre-call revalidation.

The raw MCP capability snapshot remains planning/contract evidence and is never itself the exposed function surface. The publishable catalogue is the subset whose current exposure receipt is `VALIDATED`.

Exposure validation requires one active GSCC-bound session, exact HEAD continuity, canonical function contract match and explicit authority evidence. Mutation-capable functions also require fresh live preflight evidence bound to the same HEAD. Unknown functions, stale sessions, authority mismatch and HEAD mismatch fail closed.

The gate reuses existing GSCC event types: `ACTIVITY_STARTED / ACTIVITY_COMPLETED / ACTIVITY_FAILED` carry the safe function-exposure validation lifecycle; `TOOL_STARTED` is emitted only after validation. No new mutation authority is created by the receipt.

The phrase “all information” is bounded by the credential/privacy contract: all safe governance metadata needed to validate routing, capability, authority, exact state and preflight is carried; secrets, raw prompts, transcripts, tool arguments, tool results, provider-private identifiers and private reasoning remain excluded.