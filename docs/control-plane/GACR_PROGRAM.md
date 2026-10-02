# GACR PROGRAM

> Programme authority for Governed Agent Continuity Relay.
> This programme is distinct from `docs/control-plane/PROGRAM.md`, which governs the global Control Plane roadmap.

## Programme identity

- Programme: `GACR — Governed Agent Continuity Relay`
- Authority family: `CP-AGENT-RELAY-001`
- Original-intent authority: `docs/control-plane/GACR_ORIGINAL_INTENT.md`
- Current realignment authority: `docs/control-plane/GACR_ORIGIN_REALIGNMENT.md`
- Machine intent projection: `.governance/control-plane-state/gacr-original-intent.json`
- Machine realignment projection: `.governance/control-plane-state/gacr-origin-realignment.json`

## Separation from the global programme

```text
GLOBAL CONTROL PLANE PROGRAMME
!=
GACR PROGRAMME
```

They share repository governance and safety mechanisms, but neither programme's next action is the other's next action.

There is no dependency edge `P12-S6 → GACR`.

The owner may explicitly park the global programme while GACR advances.

## Preserved implemented baseline

Current GACR implementation includes R1-R6 family capabilities and evidence. Nothing in the origin realignment rolls those capabilities back.

## Historical evolution target

The original next evolution after the baseline was:

```text
BEACON
→ WATCH
→ CORRELATOR
→ DISPATCHER
```

with the Connection Envelope, connection fingerprint, explicit correlation confidence, optional Bridge and deterministic Agent Context described in `GACR_ORIGINAL_INTENT.md`.

Later R2-R6 work implemented many parts of that target. The realignment programme exists to compare the original intent against what is now implemented and close remaining gaps without regression.

## GACR realignment sequence

The mandatory 24-step sequence lives in `GACR_ORIGIN_REALIGNMENT.md`.

Current GACR programme state:

- `ORIGINAL_INTENT`: CANONICAL / RECORDED.
- `R1-R6_BASELINE`: PRESERVED / REOBSERVED / ATTESTED (`GACR-OR-01 = PASS`).
- `ORIGIN_REALIGNMENT_PLAN`: ACCEPTED.
- `REALIGNMENT_EXECUTION`: STEPS 1-12 CLOSED; STEP 13 IN PROGRESS; PRE-13B INTEGRATION REMEDIATION REQUIRED.
- `ULTIMATE_LIVE_ACCEPTANCE`: NOT YET PASSED.

## GACR next action

`GSCC_ADMISSION_GATE_RUN_LIVE_REQUEST`

Step 13B remains the next live acceptance gate, but its execution is temporarily blocked until the two bounded post-integration findings in `docs/control-plane/GACR_GSCC_GSE_INTEGRATION_AUDIT.md` are closed and re-attested from the then-current `main`.

The GSCC Core, GSE Session State Engine and GSCC↔GACR bidirectional-control integration are functionally integrated and green. PR #142 post-merge Governance CI `36968203836` passed the GSCC, GSE, control-harness, combined E2E and historical GACR regression suites; Relay run `36968203882` also passed. PR #143 durably attested these prerequisites without claiming fresh-provider acceptance.

A later canonical audit found two residual integration risks before Step 13B. Both are now CLOSED/PASS; G6 reconciliation is the remaining gate:

1. **CLOSED/PASS** — PR #147 removed the second shared protocol authority: `scripts/gscc_gacr/contract.py` now consumes canonical `scripts/gscc/protocol.py`; candidate and post-merge CI plus Relay are green.
2. **CLOSED/PASS** — PR #149 extends the real SessionEndpoint E2E so the combined path proves `COMMAND_ACK` and `CHALLENGE_RESPONSE` projection into GSE, but the STATUS / PROGRESS / CONTEXT / CHECKPOINT control-response paths are not yet proven end-to-end through the canonical GSE input model.

A procedural deviation is also recorded: Worker A and Worker B were merged before all three worker PRs remained open for one final integration audit, contrary to the worker prompts. This is non-blocking because the subsequent dependency-ordered integration, full green CI and controlled PR #142 contained the runtime risk, but it remains part of the durable audit record.

No GACR step is rolled back. Step 13B remains `NOT_EXECUTED`. After G6, the owner introduced a stronger pre-exposure invariant: no governed function may be published or invoked before a GSCC exposure route is validated. PR #153 implements that additive gate. PR #153 is now merged and its post-merge CI, arrival-route workflow, observable-arrival gateway and GACR relay are green. Step 13B remains blocked only until one real governed function exposure request traverses the new evaluator and yields the expected fail-closed/VALIDATED behavior. This programme remains independent of `P12-S6`, CASE 1, GMC and the global Control Plane programme.



### Existing arrival gateway preservation

The owner clarified that the already-integrated GSCC Observable Arrival Gateway is part of the preserved baseline and must remain in place.

The admission/access gate is layered around it as follows:

```text
controlled client/provider
→ admission
→ qualification / Access Grant
→ existing controlled GSCC arrival
→ SessionEndpoint / GACR auto-attach
→ existing function exposure gate

GitHub-event-visible arrival
→ existing observable-arrival gateway
→ presence/session evidence only
→ admission still required
→ qualification / Access Grant
→ existing function exposure gate
```

Observable arrival never equals access authority. No admission implementation may remove or duplicate the existing arrival gateway.

## Completion condition

GACR may be declared origin-realigned only after the live acceptance scenario proves:

fresh agent not explicitly told to register with GACR
→ observable first-touch through an instrumented path
→ canonical session create/resume
→ safe liveness and progress evidence
→ controlled loss of fresh evidence
→ governed stall transition
→ second agent
→ deterministic stopping-point reconstruction
→ exact-HEAD reconciliation
→ governed takeover
→ continuation of the same work.

Until then, the programme status remains partial regardless of green unit tests.

### G6 reconciliation

- Current main reobserved before G6: `114c5397966a5c6ad7d8770298abd698929ecf8f`.
- GACR-INT-AUDIT-01: `CLOSED_PASS`.
- GACR-INT-AUDIT-02: `CLOSED_PASS`.
- G6 reconciliation PR #150 first full Governance CI: `36971795607 = PASS`.
- Shared protocol, GSE projection, combined E2E, historical GACR, governance integrity and authority boundaries all pass together.
- Step 13B is reauthorized as `NEXT_AUTHORIZED`.
- Fresh provider agent remains `NOT_EXECUTED`.
- Ultimate live acceptance remains `NOT_PASSED`.

## 2026-10-02 — GSCC observable-arrival remediation

Status: **IMPLEMENTED ON PR #152 / FINAL INTEGRATION PENDING / STEP 13B NOT EXECUTED**.

The first fresh-provider attempt exposed a real external seam rather than a GACR/GSE semantic failure: direct provider-side GitHub reads can remain `PROPRIETARY_SILENT`, so the repository had no event with which to create the fresh Agent A session.

PR #152 adds one additive entry gateway:

```text
observable repository arrival
→ canonical GSCC SessionEndpoint
→ SESSION_ATTACH
→ GACRClientEmitterAdapter
→ gacr_auto-attach
→ Presence Fabric / canonical GACR session
```

The gateway covers GitHub-event-visible arrivals and exposes a controlled-host entry for provider adapters. It does not create a second session store, second correlator, second state engine or mutation-authority path.

Tests were introduced before implementation. Initial Governance CI run `36974868172` failed at the missing gateway. A live transport defect then exposed GitHub's ten-property repository-dispatch limit; the gateway now uses bounded top-level metadata plus one allowlisted `arrival_context` projection. Subsequent live gateway runs reached the canonical GACR relay and produced `connection_method = gscc-github-event-gateway` sessions.

This evidence proves the repository-side GSCC entry seam for observable events. It does **not** prove that an arbitrary proprietary provider read is observable, and it does not satisfy the fresh Agent A acceptance by itself.

Canonical acceptance remains:

`Step 13B = NEXT_AUTHORIZED / NOT_EXECUTED`

`ULTIMATE_LIVE_ACCEPTANCE = NOT_PASSED`.

## 2026-10-02 — GSCC mandatory function exposure hardening

Owner rule:

```text
observable repository arrival or governed function request
→ GSCC
→ mandatory Actions workflow
→ safe context / exact HEAD / entry route / capability contract
→ explicit authority validation
→ live preflight when mutation-capable
→ VALIDATED exposure receipt
→ function may be exposed
→ pre-call revalidation
→ tool lifecycle
```

PR #153 implements this rule additively over the already-merged observable-arrival gateway. It does not replace GACR, GSE, the MCP capability snapshot or the governed execution engine.

The raw MCP catalogue remains planning evidence and is explicitly **not** the governed exposed function catalogue.

Step 13B remains `NOT_EXECUTED`. It must not resume until PR #153 is integrated and a post-merge `gscc_function_exposure_request` proves the workflow fails closed for invalid requests and produces a `VALIDATED` receipt only for a properly authorized request.

### PR #153 post-merge attestation

- merge: `14641e4abcf8abf37f7a4975a8311c6253ea9263`
- post-merge Governance CI: `36977148809 = PASS`
- GSCC Function Exposure Gate arrival-route workflow: `36977148865 = PASS`
- GSCC Observable Arrival Gateway: `36977148970 = PASS`
- GACR Relay: `36977148872 = PASS`
- downstream auto-attach relay: `36977162025 = PASS`

The remaining proof is deliberately narrow: execute one real governed function exposure request through `gscc_function_exposure_request`. This connector cannot emit repository-dispatch writes, so that specific live request is not fabricated here.

### PR #156 consolidation — one authority, every governed invocation routed

PR #156 consolidates the owner rule into the already-canonical PR #153 function-exposure authority. It deliberately does **not** introduce a second function-gate engine or workflow.

Additive guarantees:

- all 135 functions in the current MCP capability snapshot are marked `GSCC_REQUIRED / REQUIRES_RUNTIME_VALIDATION`;
- raw catalogue presence remains planning evidence, never exposure or invocation authority;
- the existing `.github/workflows/gscc-function-exposure-gate.yml` is also the reusable mandatory gate for Governed Execution;
- every MCP invocation occurrence in an execution package is represented in one exact-HEAD package-route receipt, including contract digest, capability, phase, authority class, argument field names and an opaque argument-value digest;
- the execution engine independently recomputes the package-route digest before any real MCP call;
- route validation grants neither invocation authority nor mutation authority;
- the observable-arrival GSCC gateway is distributed by the governed-client upgrader;
- the source-only function gate remains source-only so client CI portability is preserved.

Tests-first evidence:

- RED: Governance CI `36977945009` failed because the package-route primitive did not yet exist;
- candidate Governance CI `36978496025 = PASS`;
- candidate PR Function Exposure Gate arrival-route workflow `36978495981 = PASS`;
- candidate PR Observable Arrival Gateway `36978496029 = PASS`.

A source-only post-merge workflow, `.github/workflows/gscc-function-route-selftest.yml`, will exercise the reusable `workflow_call` against canonical `main`. Until that post-merge proof and the already-required real `gscc_function_exposure_request` are observed, Step 13B remains `NOT_EXECUTED`.

## 2026-10-02 — Owner admission/access invariant supersedes the pending live exposure request

Status: **SPECIFIED / NOT IMPLEMENTED / STEP 13B BLOCKED**.

After integration of the existing GSCC Function Exposure Gate, the owner introduced a stronger prerequisite for governed agent repository access.

Canonical authority:

`docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md`

The required order is now:

```text
IDENTITY
→ ADMISSION ENVELOPE
→ SAFE VALIDATION + PROVENANCE
→ CANONICAL SESSION / CORRELATION
→ PREAUTHORIZED
→ QUALIFICATION PATH
→ ACCESS GRANT
→ EXISTING GSCC FUNCTION EXPOSURE GATE
→ VALIDATED FUNCTION SURFACE
→ GOVERNED REPOSITORY
```

The following remain distinct:

```text
IDENTITY
!= ADMISSION
!= PREAUTHORIZATION
!= ACCESS AUTHORIZATION
!= FUNCTION EXPOSURE
!= MUTATION AUTHORITY
```

The admission/access layer must extend the existing GSCC/GSE/GACR/function-gate authority. A second gate engine, second session store, second correlator, second claim store or second takeover authority is forbidden.

A valid admission yields only `PREAUTHORIZED`. The agent must then complete governance-read, current repository baseline, exact-HEAD, task/claim/collision, capability/challenge and GSE-initial-state qualification before an Access Grant may be issued. An Access Grant only makes the session eligible to request function exposure; it grants neither invocation nor mutation authority.

Therefore the previously pending real `gscc_function_exposure_request` is no longer the immediate executable GACR action. It must not be used to bypass this newly specified admission prerequisite.

Current GACR next action:

`GSCC_ADMISSION_ACCESS_GATE_IMPLEMENT_TESTS_FIRST`

Step 13B remains `NOT_EXECUTED` and blocked until the admission/access gate is implemented, regression-tested and attested from then-current `main`. After that, the real function-exposure request remains a required downstream live proof.

This is GACR/GSCC cross-cutting hardening only. It does not execute or replace `P12-S6`, CASE 1, GMC or the global Control Plane programme.

## 2026-10-02 — GSCC admission/access candidate implemented tests-first

PR #159 implements the admission/access prerequisite without removing the existing Observable Arrival Gateway or creating a second function-exposure authority.

Candidate flow:

```text
AdmissionEnvelope
→ PREAUTHORIZED
→ qualification evidence
→ bounded Access Grant
→ existing GSCC Function Exposure Gate
→ existing exact-HEAD / function-contract / authority / preflight controls
```

The candidate adds one read-only admission workflow, `.github/workflows/gscc-admission-gate.yml`, and extends the existing canonical function gate so no governed function can become exposable without an Access Grant that matches connection, session, repository, exact HEAD and expiry.

RED→GREEN evidence:

- `37000902994 FAIL → 37001048628 PASS` — admission core;
- `37001183473 FAIL → 37001289277 PASS` — qualification / Access Grant;
- `37001452126 FAIL → 37001737386 PASS` — Access Grant required by existing function gate;
- `37001911592 FAIL → 37002023347 PASS` — live admission workflow contract;
- final candidate Observable Arrival Gateway `37002023374 = PASS`;
- final candidate Function Exposure Gate `37002023423 = PASS`.

Status: `CANDIDATE_IMPLEMENTED_TESTED_PENDING_MERGE`.

Next GACR action: `GSCC_ADMISSION_ACCESS_GATE_MERGE_AND_POSTMERGE_ATTEST`.

No real provider admission request has yet been executed through canonical `main`; Step 13B and ultimate live acceptance remain NOT_PASSED. The global `P12-S6` programme remains untouched.

## 2026-10-02 — GSCC admission/access post-merge attestation PASS

PR #159 merged at `56c48aafbe00a50b47ad2189f4ab3645b937c82f`.

Exact-merge post-merge evidence:

- Governance CI `37002783058 = PASS`;
- Observable Arrival Gateway `37002783052 = PASS`;
- Function Exposure Gate `37002783152 = PASS`;
- Function Route Selftest `37002783428 = PASS`;
- GACR Relay push `37002783111 = PASS`;
- GACR Relay dispatch `37002796444 = PASS`.

The admission/access prerequisite is now integrated on canonical main. Existing arrival and function-exposure authorities remain preserved.

Next GACR action: `GSCC_ADMISSION_GATE_RUN_LIVE_REQUEST`.

A real provider admission has not yet been executed. Step 13B remains NOT_EXECUTED; ultimate live acceptance remains NOT_PASSED. Global `P12-S6` remains untouched.
