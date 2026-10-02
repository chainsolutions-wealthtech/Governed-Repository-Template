# GSCC Admission & Repository Access Gate

> Status: `INTEGRATED / POSTMERGE_GREEN / PENDING_LIVE_ADMISSION_REQUEST`  
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



## Existing arrival layer preservation and placement

The repository already has a canonical arrival layer and it must not be deleted, bypassed or replaced.

Existing implementation:

```text
.github/workflows/gscc-observable-arrival.yml
        ↓
scripts/gscc_observable_arrival.py
        ↓
GSCC SessionEndpoint
        ↓
SESSION_ATTACH
        ↓
GACRClientEmitterAdapter
        ↓
gacr_auto-attach
        ↓
GACR Presence / canonical session
```

It currently observes GitHub-visible arrivals such as push, create, pull request, issue/comment and review events, and it also exposes the controlled-host arrival function for instrumentable provider/client adapters.

The new admission/access layer is therefore a **higher-order prerequisite**, not a replacement for this existing arrival mechanism.

For a controlled provider/client surface, the intended order is:

```text
AGENT / CONVERSATION
        ↓
NEW ADMISSION GATE
        ↓
AdmissionEnvelope validation
        ↓
PREAUTHORIZED + qualification
        ↓
ACCESS GRANT
        ↓
EXISTING controlled GSCC arrival path
        ↓
SessionEndpoint / SESSION_ATTACH
        ↓
GACR canonical session
        ↓
existing entry-action / intent / authority gates
        ↓
EXISTING Function Exposure Gate
        ↓
governed repository function
```

For a GitHub-event-visible arrival that has already occurred, the existing Observable Arrival Gateway may necessarily observe the event before admission because the GitHub event itself is the observation source. In that case its output is **presence evidence only**:

```text
GITHUB EVENT
        ↓
EXISTING OBSERVABLE ARRIVAL GATEWAY
        ↓
presence / session evidence
        ↓
NO ACCESS AUTHORITY
        ↓
NEW ADMISSION GATE REQUIRED
        ↓
qualification
        ↓
ACCESS GRANT
        ↓
EXISTING Function Exposure Gate
```

Therefore:

```text
OBSERVABLE ARRIVAL
!= PREAUTHORIZED
!= AUTHORIZED
```

and:

```text
EXISTING ARRIVAL GATEWAY = PRESERVED
NEW ADMISSION GATE = ADDED ABOVE GOVERNED ACCESS
EXISTING FUNCTION EXPOSURE GATE = PRESERVED
```

No implementation may delete, rename away, silently supersede or duplicate the existing Observable Arrival Gateway solely to introduce admission.

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



## Candidate implementation evidence — PR #159

The owner-authorized live implementation is carried by PR #159 on branch `governance/gscc-admission-runtime`.

Implemented candidate surfaces:

- `scripts/gscc/admission.py` — fail-closed admission validation, in-process idempotence, qualification and bounded Access Grant validation;
- `schemas/gscc-admission-envelope.schema.json`;
- `schemas/gscc-admission-receipt.schema.json`;
- `schemas/gscc-access-grant.schema.json`;
- `.github/workflows/gscc-admission-gate.yml` — read-only admission/qualification workflow;
- the existing `scripts/gscc_function_exposure_gate.py` now requires a valid Access Grant before function-contract/authority/preflight evaluation;
- the existing `.github/workflows/gscc-function-exposure-gate.yml` carries the serialized safe Access Grant into the canonical evaluator.

Tests-first evidence:

- RED admission core: Governance CI `37000902994 = FAILURE` on missing `gscc.admission`;
- GREEN admission core: `37001048628 = SUCCESS`;
- RED Access Grant qualification: `37001183473 = FAILURE` on missing `evaluate_access_grant`;
- GREEN qualification: `37001289277 = SUCCESS`;
- RED function-gate binding: `37001452126 = FAILURE` because the existing gate did not accept `access_grant`;
- corrected full gate GREEN: `37001737386 = SUCCESS`;
- RED admission workflow: `37001911592 = FAILURE` because `.github/workflows/gscc-admission-gate.yml` did not exist;
- final candidate Governance CI: `37002023347 = SUCCESS`;
- final candidate Observable Arrival Gateway: `37002023374 = SUCCESS`;
- final candidate Function Exposure Gate: `37002023423 = SUCCESS`.

This evidence proves implementation and regression safety on the PR candidate only. It does **not** prove post-merge activation, a real provider admission request, Step 13B, or ultimate GACR live acceptance.


## Post-merge integration attestation — PR #159

PR #159 merged into canonical main at `56c48aafbe00a50b47ad2189f4ab3645b937c82f`.

Post-merge evidence on that exact merge commit:

- Governance CI `37002783058 = SUCCESS`;
- GSCC Observable Arrival Gateway `37002783052 = SUCCESS`;
- GSCC Function Exposure Gate `37002783152 = SUCCESS`;
- GSCC Function Route Selftest `37002783428 = SUCCESS`;
- GACR Relay push run `37002783111 = SUCCESS`;
- GACR Relay repository-dispatch run `37002796444 = SUCCESS`.

Therefore the admission/access implementation is integrated and regression-green on canonical main.

This does **not** yet prove a real provider admission request. The next required live proof is `GSCC_ADMISSION_GATE_RUN_LIVE_REQUEST`. Step 13B and ultimate live acceptance remain open.

## Programme boundary

This is a cross-cutting GSCC/GSE/GACR hardening requirement.

Recording it:

- does not execute Step 13B;
- does not pass ultimate GACR live acceptance;
- does not advance `P12-S6`;
- does not start GMC;
- does not grant repository, mutation or production authority.

The currently authorized executable next actions remain governed by their existing programme authorities until explicitly changed.

## 2026-10-02 — Canonical qualification evidence harvester candidate

PR #163 implements the missing canonical-evidence layer after the post-merge audit of PR #159.

The reconciled path is:

```text
AdmissionEnvelope
→ PREAUTHORIZED
→ existing admission→GACR session binding
→ GSCC Admission Harvester
   → GitHub GET repository metadata
   → GitHub GET requested/default branch exact HEAD
   → canonical GACR session + existing ConnectionEnvelope
   → controlled governance document digests
   → canonical task/claim reconciliation
   → capability/control/GSE/access-policy evidence only when canonically proven
→ qualification validator
→ Access Grant only when every required evidence class is complete
→ existing Function Exposure Gate
```

The harvester does not implement a second correlator. It consumes the canonical session binding introduced concurrently on main and enriches the selected GACR session with the existing ConnectionEnvelope.

Canonical qualification no longer trusts caller-provided `qualification_evidence_json`. That workflow input remains only as a deprecated compatibility surface and is not injected into the canonical qualification evaluator.

Fail-closed rules:

- a GACR/session HEAD differing from the current GitHub GET HEAD yields stale-session evidence and blocks qualification;
- declared capabilities are not promoted to `VERIFIED` without challenge evidence;
- control reachability is not promoted to `VERIFIED` without canonical control evidence;
- GSE state is not invented when no canonical GSE admission projection exists;
- access policy remains pending unless canonical policy evidence is supplied;
- provider-private facts that are not exposed remain explicitly unavailable;
- no Admission Receipt, Access Grant or harvested bundle grants invocation or mutation authority.

Tests-first / reconciliation evidence:

- RED contract commit: `c7ade40b7af024bb3a31d1b563e631ffceda40ab`;
- RED Governance CI: `37003462162 = FAILURE` exactly at the missing harvester test;
- first runtime candidate: `5934bd56d41d0ae63f33174fc79deab1e257fabb`;
- exact-main reconciliation merge: `9fd0f8435da7da517659034b3fa05207e9470ae9`, preserving the concurrent provider issue ingress and canonical admission→GACR session binding;
- reconciled green head before restoring the temporary CI trigger: `d6315b890fdd28c4d162abd02678aa3c4ee43154`;
- PR Governance CI: `37005600659 = SUCCESS`;
- PR Function Exposure Gate: `37005600581 = SUCCESS`;
- PR Observable Arrival Gateway: `37005600560 = SUCCESS`;
- final no-temporary-trigger head: `eb92101a2f6fa5d855380d4f2ac9820552f19b53`;
- final PR Governance CI: `37005672855 = SUCCESS`;
- final PR Function Exposure Gate: `37005672883 = SUCCESS`;
- final PR Observable Arrival Gateway: `37005673101 = SUCCESS`.

This candidate does not execute Step 13B, does not grant production/server authority and does not advance P12-S6, CASE 1 or GMC.


## 2026-10-02 — Q8→Q12 candidate closure: real control transport seam, GSE projection and bounded access policy

PR #163 now closes the previously identified controlled-candidate qualification gaps without creating parallel authorities.

Candidate qualification path:

```text
PREAUTHORIZED
→ canonical admission→GACR session binding
→ exact live lease check
→ GitHub GET repository / branch / exact HEAD
→ canonical GACR ConnectionEnvelope
→ GSCC LIVENESS_CHALLENGE over existing GACR Host Issue Bridge (#115)
→ correlated COMMAND_ACK
→ correlated CHALLENGE_RESPONSE
→ canonical control proof in existing gacr-dispatches.json
→ existing GSE Session State Engine admission projection
→ canonical baseline Access Policy evaluation
→ complete gscc-qualification-evidence/v1
→ bounded gscc-access-grant/v1
→ existing Function Exposure Gate
```

### Q8/Q9 — capability and control proof

The candidate extends the already-live GACR Host Issue Bridge rather than creating a second transport authority.

Controller request:

```text
/gscc-control {"schema":"gscc-control-request/v1","event":"challenge_request","session_id":"..."}
```

GSCC/GACR command delivery:

```text
/gscc-control-command {... LIVENESS_CHALLENGE ...}
```

The host/provider response continues through the canonical `/gacr-host` ingress as two distinct events:

```text
command_ack
challenge_response
```

The evidence is accepted only when session, dispatch, command, correlation, challenge and nonce all match and the challenge is still fresh. A response before ACK, an expired challenge, a mismatched nonce or a replay never becomes fresh liveness.

A successful proof verifies only the bounded minimum:

- `COMMAND_RECEIVE`;
- `COMMAND_ACK`;
- `CHALLENGE_RESPONSE`;
- `control_channel = REACHABLE`.

It grants neither invocation nor mutation authority.

Tests-first proof:

- RED contract commit `81914925ee4a2531f04cee62d5004ca22d930c64`;
- Governance CI `37013852868 = FAILURE` exactly at **Test GSCC issue control challenge bridge**.

### Q10 — GSE admission projection

No second GSE store is introduced. The candidate projects `gscc-gse-admission-state/v1` on demand through the existing deterministic GSE engine from the canonical GACR session plus canonical challenge evidence.

Independent dimensions remain preserved:

- liveness may become `QUIET` while a still-fresh control channel remains `REACHABLE`;
- absent challenge proof leaves control `UNKNOWN`, never falsely `REACHABLE`;
- challenge traffic does not manufacture progress.

Tests-first proof:

- RED contract commit `7399233766803369845d89b0ff4ca3fc6b59f077`;
- Governance CI `37014621966 = FAILURE` exactly at **Test GSCC admission GSE projection**;
- corrected GSE-semantics candidate `84c2e29b83a1418387711e1c1aa328c6dcb8d473`;
- Governance CI `37015025085 = SUCCESS`.

### Q11 — baseline Access Policy

Canonical source-only policy:

`.governance/agent-relay/gscc-admission-access-policy.json`

Authority:

`GSCC-ADMISSION-ACCESS-POLICY-001`

The policy defaults to `DENY` and may allow only `READ_ONLY_DISCOVERY_AUTHORITY` for the bounded read-only request family. Unknown, operational or mutation requests are denied by this baseline policy.

The policy never grants invocation or mutation authority. Function-specific authority evidence remains mandatory at the existing Function Exposure Gate.

Tests-first proof:

- RED contract commit `0aa92f27ccef48f15972f47165829340e5b89195`;
- Governance CI `37015269742 = FAILURE` exactly at **Test GSCC admission access policy**;
- policy candidate `4cbb1cde354f0dada0cd776e1200812a5331f474`;
- Governance CI `37015477695 = SUCCESS`.

### Q12 — complete controlled qualification

The complete candidate flow was exercised as one controlled test:

- read-only admission → `PREAUTHORIZED`;
- exact session + valid lease;
- current repository/HEAD observation;
- correlated control challenge proof;
- verified GSE admission projection;
- baseline Access Policy `ALLOW`;
- `QUALIFICATION_EVIDENCE_COMPLETE`;
- bounded Access Grant `AUTHORIZED / GOVERNED_FUNCTION_EXPOSURE_ELIGIBLE`;
- allowed authority class exactly `READ_ONLY_DISCOVERY_AUTHORITY`;
- invocation authority remains `false`;
- mutation authority remains `false`;
- Access Grant binding/HEAD/session/expiry validation passes.

The mutation-request variant remains not authorized.

Q12 commit:

`0f9b4432a973e507c4a519501f002b3d0b7669a7`

Governance CI:

`37015716729 = SUCCESS`

Final exact-main state alignment merge:

`72a9b8d0872a59eed0a45e8d8e78223a072d055b`

Final aligned candidate proof:

- Governance CI `37016097906 = SUCCESS`;
- GSCC Function Exposure Gate `37016097994 = SUCCESS`;
- GSCC Observable Arrival Gateway `37016098117 = SUCCESS`.

### Acceptance boundary

This proves the complete controlled candidate path through a bounded read-only Access Grant. It does **not** prove a real provider/host challenge/ACK/response after integration on canonical main.

Therefore:

```text
PR #163 = CANDIDATE_GREEN / NOT_MERGED
REAL_PROVIDER_CONTROL_PROOF = NOT_EXECUTED
POSTMERGE_LIVE_ACCESS_GRANT = NOT_EXECUTED
STEP_13B = NOT_EXECUTED
ULTIMATE_LIVE_ACCEPTANCE = NOT_PASSED
```
