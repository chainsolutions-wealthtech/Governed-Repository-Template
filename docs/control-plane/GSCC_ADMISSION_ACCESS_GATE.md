# GSCC Admission & Repository Access Gate

> Status: `SPECIFIED / NOT_IMPLEMENTED`  
> Date: 2026-10-02  
> Scope: additive extension of the existing GSCC/GSE/GACR function-exposure architecture.  
> This authority does not advance `P12-S6`, CASE 1, GMC, or the global Control Plane programme.

## Purpose

An authenticated GitHub identity is not sufficient, by itself, to expose governed repository functions to an agent.

The governed target path is:

```text
AGENT / CONVERSATION
        ↓
ADMISSION ENVELOPE
        ↓
GSCC ADMISSION VALIDATION
        ↓
SAFE STORAGE + PROVENANCE
        ↓
GACR SESSION / CORRELATION
        ↓
PREAUTHORIZED
        ↓
QUALIFICATION PATH
        ↓
ACCESS GRANT
        ↓
EXISTING GSCC FUNCTION EXPOSURE GATE
        ↓
VALIDATED FUNCTIONS ONLY
        ↓
GOVERNED REPOSITORY
```

The following states are distinct and must never be collapsed:

```text
IDENTITY
!= ADMISSION
!= PREAUTHORIZATION
!= ACCESS AUTHORIZATION
!= FUNCTION EXPOSURE
!= MUTATION AUTHORITY
```

## Existing authorities preserved

This design extends, and does not replace:

- `docs/control-plane/GSCC_PROTOCOL_V1.md`;
- `scripts/gscc/session_endpoint.py`;
- `scripts/gscc/instrumentation.py`;
- `scripts/gscc_observable_arrival.py`;
- `scripts/gscc_function_exposure_gate.py`;
- `.github/workflows/gscc-observable-arrival.yml`;
- `.github/workflows/gscc-function-exposure-gate.yml`;
- GSE Session State Engine;
- GACR Presence / Correlator / Watch / Forensics / Dispatcher;
- the existing exact-HEAD, claim, authority and live-preflight gates.

No second session store, correlator, claim store, takeover engine or function-exposure authority is authorized.

## Admission envelope

Canonical target schema:

`gscc-admission-envelope/v1`.

The envelope carries safe, bounded facts from the following families:

### Request

- `request_id`;
- `correlation_id`;
- `idempotency_key`;
- `issued_at`;
- `observed_at`.

### Agent

- `agent_id` when actually available;
- `agent_identity` when actually available;
- `agent_type`;
- `provider`;
- `model_runtime` when exposed;
- `requested_role`.

### Client

- `client_instance_id`;
- `client_type`;
- `client_version` when exposed;
- `host_instance_id` when exposed.

### Session

- provider/session reference when supplied;
- conversation reference when supplied;
- session start timestamp when supplied.

Provider-private identifiers are supplied-only and are never invented.

### Connection

- `connection_ref`;
- `connection_method`;
- `surface_class`;
- `bridge_registration_ref` when present;
- declared wake channels.

### Target

- repository;
- requested branch;
- any already-observed repository facts supplied by the client.

Repository identity, organization, branch existence and exact HEAD are independently re-observed during qualification and are not trusted merely because the client declared them.

### Intent

- `entry_action`;
- `connection_intent`;
- task reference when known;
- requested role;
- requested capabilities.

### Continuity

- claim reference when known;
- checkpoint reference when known;
- last action/evidence references when known.

### Control capabilities

Declared support may include:

- heartbeat;
- command receive;
- command ACK;
- challenge response;
- checkpoint report;
- progress report;
- context report;
- exact-HEAD re-observation.

Declared capability is not proof of working capability.

## Field classes

Every field belongs to one of these classes:

```text
REQUIRED
OPTIONAL
SUPPLIED_ONLY
OBSERVED
DERIVED_SAFE
GSE_DERIVED
FORBIDDEN
```

Unknown provider-private values remain `UNAVAILABLE`.

Important provenance classes reuse the existing GACR/Presence vocabulary:

```text
OBSERVABLE_BY_PLATFORM
DECLARED_BY_AGENT_OR_CLIENT
DERIVED_SAFE
CORRELATED
PROVIDER_PRIVATE_UNAVAILABLE
```

## Forbidden material

Admission must fail closed on secret-bearing or private-content material, including:

- password / secret / token / access token / refresh token;
- private key;
- authorization header;
- browser/session cookie;
- raw prompt;
- raw transcript;
- raw assistant response;
- chain-of-thought / private reasoning;
- raw tool arguments or raw tool results.

Credentials remain in the transport/runtime boundary and are never serialized into the GSCC admission plane.

## Admission lifecycle

The admission state family is:

```text
RECEIVED
ADMISSION_INCOMPLETE
ADMISSION_INVALID
ADMISSION_DENIED
ADMISSION_AMBIGUOUS
PREAUTHORIZED
QUALIFICATION_IN_PROGRESS
AUTHORIZED
ACCESS_SUSPENDED
ACCESS_EXPIRED
ACCESS_REVOKED
CLOSED
```

A valid initial dossier yields `PREAUTHORIZED`, not repository access.

## Preauthorization

A preauthorized agent receives only a restricted qualification surface.

It may obtain:

- admission status;
- required next step;
- required governance documents through a controlled read path;
- repository-baseline observation through the controlled path;
- GSCC commands/challenges and ACK them;
- qualification evidence submission.

Preauthorization must not expose arbitrary repository read/write functions.

## Mandatory qualification path

The canonical target sequence is:

```text
Q1  ADMISSION_ENVELOPE_VALIDATED
Q2  CANONICAL_SESSION_BOUND
Q3  REQUIRED_GOVERNANCE_READ
Q4  CURRENT_REPOSITORY_BASELINE_OBSERVED
Q5  EXACT_HEAD_ESTABLISHED
Q6  TASK_RECONCILED
Q7  CLAIM_COLLISION_RECONCILED
Q8  DECLARED_CAPABILITIES_TESTED
Q9  GSCC_CONTROL_CHANNEL_CHALLENGE
Q10 GSE_INITIAL_SESSION_STATE
Q11 ACCESS_POLICY_EVALUATION
Q12 ACCESS_GRANT
```

Each gate requires evidence. A client declaration alone is not proof.

## Governance-read evidence

Required governance reading should be observable through a controlled surface and should preserve at least:

- document path;
- document/blob identity or equivalent digest;
- repository HEAD;
- session/admission identity;
- start/completion timestamps.

## Repository baseline

The qualification path independently observes:

- repository identity;
- repository ID when available;
- organization;
- default branch;
- current exact HEAD;
- requested branch and its current HEAD;
- relevant PR/task/claim evidence when applicable.

A stale prompt SHA never becomes current truth.

## Capability verification

When a client declares bidirectional-control capabilities, the qualification path may actively verify them:

```text
GACR
 ↓
GSCC
 ↓
LIVENESS_CHALLENGE
 ↓
AGENT
 ↓
COMMAND_ACK
 ↓
CHALLENGE_RESPONSE
```

A declared but unproven capability remains `DECLARED_BUT_UNVERIFIED`.

## GSE initial state

After sufficient evidence, GSE may project an initial multidimensional state, for example:

```text
presence = PRESENT
liveness = VERIFIED
activity = IDLE
progress = NOT_STARTED
blocked = NO_EVIDENCE
loop = NONE
control_reachability = REACHABLE
continuity = INITIALIZED
```

GSE interprets evidence; it does not grant repository authority.

## Access grant

Canonical target schema:

`gscc-access-grant/v1`.

An Access Grant binds, at minimum:

- grant ID;
- admission ID;
- session ID;
- connection reference;
- repository;
- bound HEAD;
- task/claim context when applicable;
- allowed authority classes/capabilities;
- constraints;
- issue/expiry timestamps.

An Access Grant does not itself grant mutation authority.

Its meaning is:

```text
AUTHORIZED SESSION
→ ELIGIBLE TO REQUEST GOVERNED FUNCTION EXPOSURE
```

## Integration with the existing Function Exposure Gate

The current canonical function route remains the sole function-exposure authority.

The target route is extended from:

```text
GSCC_SESSION_BIND
→ CONNECTION_ENVELOPE
→ EXACT_HEAD_OBSERVATION
→ ENTRY_ACTION_RESOLUTION
→ CAPABILITY_SNAPSHOT_LOAD
→ FUNCTION_CONTRACT_MATCH
→ AUTHORITY_VALIDATION
→ LIVE_PREFLIGHT_IF_REQUIRED
→ EXPOSURE_RECEIPT
→ PRE_CALL_REVALIDATION
```

to:

```text
ADMISSION_RECEIPT_VALIDATION
→ ACCESS_GRANT_VALIDATION
→ GSCC_SESSION_BIND
→ CONNECTION_ENVELOPE
→ EXACT_HEAD_OBSERVATION
→ ENTRY_ACTION_RESOLUTION
→ CAPABILITY_SNAPSHOT_LOAD
→ FUNCTION_CONTRACT_MATCH
→ AUTHORITY_VALIDATION
→ LIVE_PREFLIGHT_IF_REQUIRED
→ EXPOSURE_RECEIPT
→ PRE_CALL_REVALIDATION
```

The invariant is:

```text
NO ADMISSION
→ NO GOVERNED FUNCTION EXPOSURE

PREAUTHORIZED
→ QUALIFICATION SURFACE ONLY

AUTHORIZED
→ ELIGIBLE FOR FUNCTION EXPOSURE

VALIDATED EXPOSURE RECEIPT
→ FUNCTION MAY BE PRESENTED

VALID RECEIPT + PRE-CALL REVALIDATION
→ FUNCTION MAY BE INVOKED

MUTATION
→ STILL REQUIRES ITS OWN AUTHORITY + LIVE PREFLIGHT
```

## Catalogue boundary

The existing rule remains unchanged:

```text
RAW MCP CATALOGUE
!= GOVERNED EXPOSED FUNCTION CATALOGUE
```

Raw catalogue presence is planning/contract evidence only.

## Admission record

A bounded audit record may persist safe admission facts:

- admission/request/idempotency identities;
- canonical session and connection references;
- normalized safe envelope;
- provenance matrix;
- validation results;
- correlation result;
- preauthorization result;
- qualification status;
- access decision;
- deterministic digest.

This record is audit evidence only. It is not a parallel session, claim, correlation or takeover authority.

## Idempotence

Exact replay of the same `request_id` or `idempotency_key` must not create a second admission.

The system returns the prior result or an `ALREADY_PROCESSED` equivalent.

## Expiry and suspension

Preauthorization and Access Grant are time/state bounded.

A grant may be suspended or cease to support new function exposure when required session/lease/control/claim/exact-HEAD conditions are no longer satisfied.

Suspension does not erase durable evidence.

## Takeover

A successor never inherits the predecessor's access grant implicitly.

The target path is:

```text
Agent B admission
→ qualification
→ GACR correlation with stalled work
→ TAKEOVER_OFFER
→ ACK
→ exact-HEAD reconciliation
→ governed claim transfer
→ new Access Grant for B
→ new function-exposure receipts
```

## Required tests before implementation acceptance

At minimum:

1. valid envelope → `PREAUTHORIZED`;
2. missing required field → `ADMISSION_INCOMPLETE`;
3. secret/cookie/token material → fail closed;
4. unavailable provider conversation reference remains accepted as unavailable;
5. exact replay is idempotent;
6. ambiguous correlation fails closed;
7. PREAUTHORIZED cannot access arbitrary repository functions;
8. controlled governance read is allowed;
9. declared control capability without challenge response stays unverified;
10. complete qualification can produce an Access Grant;
11. Access Grant without exposure receipt cannot invoke a governed function;
12. Access Grant + exact HEAD + matching authority can produce a read exposure receipt;
13. mutation still requires fresh live preflight;
14. preflight HEAD mismatch fails closed;
15. expired lease/grant blocks new exposure;
16. successor cannot reuse predecessor grant;
17. governed takeover yields a new successor grant;
18. no raw prompt/transcript/tool result/secret persistence;
19. historical GSCC/GSE/GACR suites remain green.

## Planned implementation shape

No implementation is authorized merely by recording this specification.

When implementation is explicitly started, the preferred additive shape is:

```text
schemas/gscc-admission-envelope.schema.json
schemas/gscc-admission-receipt.schema.json
schemas/gscc-access-grant.schema.json
scripts/gscc/admission.py
scripts/test_gscc_admission.py
```

and targeted extension of the existing:

```text
scripts/gscc_function_exposure_gate.py
.github/workflows/gscc-function-exposure-gate.yml
docs/control-plane/GSCC_PROTOCOL_V1.md
.governance/agent-relay/config.json
```

No second function-exposure workflow/engine should be created.

## Programme boundary

This is a cross-cutting GSCC/GSE/GACR hardening requirement.

Recording it:

- does not execute Step 13B;
- does not pass ultimate GACR live acceptance;
- does not advance `P12-S6`;
- does not start GMC;
- does not grant repository, mutation or production authority.

The currently authorized executable next actions remain governed by their existing programme authorities until explicitly changed.
