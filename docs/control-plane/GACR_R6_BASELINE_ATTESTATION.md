# GACR R6 Baseline Attestation

> Operation: `GACR-OR-01_REOBSERVE_AND_ATTEST_R6_BASELINE`
> Authority family: `CP-AGENT-RELAY-001`
> Status: **PASS**
> Scope: GACR programme only.
> Global Control Plane programme: **OUT OF SCOPE / UNCHANGED**.
> `P12-S6`: **NOT A DEPENDENCY / NOT EXECUTED / NOT ADVANCED**.

## Attested source baseline

The exact `main` HEAD reobserved immediately before creation of the dedicated attestation branch was:

```text
afda467be7cb9194696b91963af3a4cf5cf0e7d5
```

Commit:

```text
Merge pull request #122 from chainsolutions-wealthtech/governance/gacr-original-intent-checkpoint
governance: canonize GACR original intent and autonomous program
```

The branch `governance/gacr-or-01-r6-baseline-attestation` was created from that exact SHA.

This document freezes the **observed R1-R6 implementation baseline**. It does not modify or reinterpret runtime behavior, and it does not execute Presence-First corrective work.

## Ordered authorities read before write

The following authorities were read from the exact baseline HEAD, in the required order:

1. `docs/control-plane/GACR_PROGRAM.md`
2. `docs/control-plane/GACR_ORIGINAL_INTENT.md`
3. `docs/control-plane/GACR_ORIGIN_REALIGNMENT.md`
4. `docs/GACR_AGENT_CONTINUITY_RELAY.md`
5. `docs/GACR_BRIDGE_CONTRACT.md`
6. `docs/control-plane/CURRENT_STATE.md`
7. `docs/control-plane/DECISIONS_LOG.md`
8. `docs/control-plane/TASKS.md`
9. `docs/control-plane/SUIVI.md`

The authority split is preserved:

```text
GLOBAL CONTROL PLANE PROGRAMME != GACR PROGRAMME
```

No dependency edge `P12-S6 → GACR` is introduced by this attestation.

## Current configuration reobserved

Source configuration: `.governance/agent-relay/config.json`, schema `1.5.0`.

Observed configured timing:

- heartbeat interval: 300 seconds;
- suspected-stall threshold: 900 seconds;
- stalled threshold: 1800 seconds;
- supervisor scan interval: 10 minutes.

Observed takeover policy:

- auto-detect stall: enabled;
- auto-offer to compatible standby: enabled;
- auto-execute takeover: disabled;
- exact-HEAD reconciliation: required;
- active claims transfer only after explicit takeover acceptance;
- stale predecessor cannot resume after transferred takeover.

Observed host boundary:

- client emitter: implemented;
- ChatGPT issue bridge: implemented and event-driven live-proven;
- continuous background heartbeat from the current ChatGPT host: **not proven**;
- outbound browser wake: **not implemented**;
- external bridge webhook on the latest observed run: **not configured**.

## R1-R6 capability inventory

| CAPABILITY | IMPLEMENTATION FILES | STATE FILES | TESTS | LIVE EVIDENCE | CURRENT STATUS | KNOWN LIMITATIONS |
|---|---|---|---|---|---|---|
| Governed sessions | `scripts/governed_agent_continuity_relay.py`; `scripts/gacr_auto_attach.py`; `scripts/gacr_host_issue_ingress.py` | `.governance/control-plane-state/gacr-sessions.json` | `test_governed_agent_continuity_relay.py`; `test_gacr_auto_attach.py`; `test_gacr_host_issue_ingress.py` | revision 10; canonical `session-68c97d4bb1ef71c86444de12`; historical internal-transport `session-cb22a4ed0d9e29eba5383f5d` preserved CLOSED/SUPERSEDED | IMPLEMENTED / PRESERVED | Persisted session state is evidence, not proof of present host liveness. Native provider conversation ref remains unavailable unless supplied. |
| Heartbeat | core relay; client emitter; host issue ingress | sessions relay fields + `gacr-beacons.json` | core relay; client emitter; host ingress | R6 issue-comment heartbeat/action runs; last persisted heartbeat `2026-10-02T00:59:54+00:00` | IMPLEMENTED / EVENT-DRIVEN LIVE-PROVEN | Current ChatGPT host has no proven persistent daemon heartbeat. |
| Lease | `governed_agent_continuity_relay.py`; config | `gacr-sessions.json` | core relay test | canonical persisted lease ends `2026-10-02T01:29:54+00:00` | IMPLEMENTED | The persisted status remains `ACTIVE`; this attestation does not invent a later `STALLED` state without a fresh supervisor observation. |
| `SUSPECTED_STALL` | core relay scan | sessions + takeovers | core relay test explicitly exercises late heartbeat | R1 implementation/CI and scheduled WATCH surface | IMPLEMENTED / CI-PROVEN | No current source projection is in `SUSPECTED_STALL`. |
| `STALLED` | core relay scan | sessions + takeovers | core relay test | R1 implementation/CI | IMPLEMENTED / CI-PROVEN | No current source session is persisted as `STALLED`. Silence is not a crash cause. |
| `TAKEOVER_READY` | core relay scan/takeover plan | sessions + `gacr-takeovers.json` | core relay test | R1 implementation/CI | IMPLEMENTED / CI-PROVEN | Current takeover queue is empty. |
| Standby | core relay registration + compatible-standby selection | sessions | core relay + telemetry tests | R1/R2 implementation/CI | IMPLEMENTED / CI-PROVEN | No current standby session exists in source state. |
| Claims | core relay claim preservation/transfer | `gacr-claims.json` | core relay test proves stall does not release claim and acceptance transfers claim | R1 implementation/CI | IMPLEMENTED / PRESERVED | Current source GACR claim list is empty. |
| Collision domains | existing claim/collision-domain governance reused by relay/forensics | canonical claim state; surfaced in forensics resume context | core + telemetry tests | forensics explicitly records `CLAIMS_AND_COLLISION_DOMAINS_ARE_CANONICAL` | REUSED CANONICAL SAFETY GATE | GACR has no independent lock store and must not create one. |
| Exact-HEAD takeover | `governed_agent_continuity_relay.py` | sessions/claims/takeovers | core test rejects mismatched HEAD and accepts exact reconciled HEAD | R1 CI; workflow persistence also fails closed on moved HEAD | IMPLEMENTED / CI-PROVEN / FAIL-CLOSED | No current live takeover item exists to execute. |
| Checkpoint references | telemetry/forensics action fields; existing governance checkpoint model | `gacr-beacons.json`; `gacr-forensics.json`; adjacent canonical `checkpoint.json` | telemetry tests | R6 live checkpoint refs `CHK-R6-LIVE-001`, `CHK-R6B-LIVE-001`, `CHK-R6C-LIVE-001` | IMPLEMENTED AS REFERENCES | GACR does not own a parallel checkpoint database. |
| Handoff | relay takeover lineage + existing governance handoff model | sessions/takeovers; adjacent canonical `handoff.json` | core relay test | predecessor closes as `HANDOFF_STALLED` in test model after accepted takeover | IMPLEMENTED / CI-PROVEN | Current source handoff projection belongs to broader governance history; this attestation does not rewrite it. |
| Beacon | `scripts/gacr_agent_telemetry.py` | `gacr-beacons.json` | telemetry, auto-attach, host-ingress tests | revision 13; 13 preserved Beacons including R4 AUTO_ATTACH and R6 HEARTBEAT/ACTION/HOST_HEARTBEAT_RECEIPT | IMPLEMENTED / LIVE-PROVEN | Only allowlisted safe metadata; no raw transcript/secrets/private reasoning. |
| Watch | core relay scan + scheduled workflow | sessions/takeovers/forensics | core relay + telemetry tests | latest main GACR run `36952355612` PASS; scheduled run `36948763070` failed closed on `HEAD_MOVED` during concurrent R6 state update | IMPLEMENTED / ACTIVE WORKFLOW SURFACE | A failed exact-HEAD guard is not a liveness conclusion. |
| Correlator | `scripts/gacr_agent_telemetry.py` | `gacr-correlations.json` | telemetry + auto-attach + host tests | revision 14; canonical R6 session correlations are EXACT; historical transport Beacon remains non-selected/PROBABLE | IMPLEMENTED / LIVE-PROVEN | Ambiguous evidence fails closed; terminal sessions are excluded. |
| Dispatcher | telemetry dispatcher + bridge notifier | `gacr-dispatches.json` | telemetry test covers target selection/delivery modes/no-write | R2 implementation/CI | IMPLEMENTED / CI-PROVEN | Current dispatch list empty; external bridge webhook currently unconfigured; wake never grants write. |
| Interruption Forensics | `scripts/gacr_agent_telemetry.py` | `gacr-forensics.json` | telemetry test covers lease-expired stall, explicit cause, in-flight action, exact-HEAD resume | revision 4; current canonical report `NO_INTERRUPTION_OBSERVED`, cause `UNOBSERVED_EXTERNAL_CAUSE`, exact-HEAD reobservation required | IMPLEMENTED / LIVE-PROVEN | External cause is observed-only; no browser crash/provider timeout/network loss may be inferred from silence. |
| Automatic attachment | `scripts/gacr_auto_attach.py`; workflow bridge | sessions/beacons/correlations | auto-attach test | R4 live session `session-68c97...`; Beacon `GACR-B-6e9a2275ea04`; correlation `GACR-C-caffb7cb6efd` EXACT | IMPLEMENTED / LIVE-PROVEN | Controlled source priority is explicit client → fresh Chronicle → external GitHub execution identity. Internal GACR transport may never become an agent. |
| Client emitter | `scripts/gacr_client_emitter.py` | emits into existing GACR stores via repository dispatch | client-emitter test | R5 protocol CI-proven; R6 bridge reuses same safe telemetry semantics | IMPLEMENTED / CI-PROVEN | Persistent host process is provider/deployment dependent; wake polling does not accept takeover. |
| Provider-host ingress | `scripts/gacr_host_issue_ingress.py`; workflow | existing sessions/beacons/correlations/forensics | host ingress + host workflow tests | issue #115; comments `5943461065`, `5943497457`, `5943559595`, `5943592733`; same canonical session; idempotent replay | IMPLEMENTED / CHATGPT EVENT-DRIVEN LIVE-PROVEN | Issue identity is repository-local; no native ChatGPT conversation ID was exposed, so none is stored. |
| Bridge | `scripts/gacr_bridge_notifier.py`; `docs/GACR_BRIDGE_CONTRACT.md`; schema | dispatches | telemetry notifier assertions | outbound notifier path exists; latest run reports `GACR_EXTERNAL_BRIDGE_SKIP: not configured` | OPTIONAL CAPABILITY IMPLEMENTED | Browser wake/focus is not repository-native; webhook configuration is external. |
| Agent Context | `scripts/gacr_agent_telemetry.py context` | aggregates sessions/claims/takeovers/beacons/correlations/dispatches/forensics | telemetry test verifies session + wake offer aggregation | R2 implementation/CI | IMPLEMENTED / CI-PROVEN | Resume view only; not a parallel source of truth or mutation authority. |
| Source/client isolation | source path selection in relay/telemetry/workflow/upgrader; R6 portable host inbox | source `gacr-*.json`; client repository-local stores | core, telemetry, host workflow tests | PR #100 boundary correction; R5-A terminal transport exclusion; R6-B issue-number non-distribution | IMPLEMENTED / LIVE-ATTESTED | Source runtime identities must never be copied into generated/adopted clients. |

## Canonical GACR state projections

All current source projections matching `.governance/control-plane-state/gacr-*` were reobserved:

1. `gacr-beacons.json`
2. `gacr-claims.json`
3. `gacr-correlations.json`
4. `gacr-dispatches.json`
5. `gacr-forensics.json`
6. `gacr-origin-realignment.json`
7. `gacr-original-intent.json`
8. `gacr-program.json`
9. `gacr-sessions.json`
10. `gacr-takeovers.json`

Observed runtime snapshot on the attested baseline:

- sessions: 2 historical records; exactly one persisted non-terminal/canonical session;
- canonical session: `session-68c97d4bb1ef71c86444de12`;
- canonical provider: `chatgpt`;
- provider conversation ref: `null` with provenance `UNAVAILABLE`;
- closed superseded transport session: `session-cb22a4ed0d9e29eba5383f5d`;
- claims: 0;
- takeovers: 0;
- dispatches: 0;
- Beacons: 13;
- Correlator projection revision: 14;
- Forensics projection revision: 4;
- current forensic classification: `NO_INTERRUPTION_OBSERVED`;
- current external interruption cause: `UNOBSERVED_EXTERNAL_CAUSE`;
- resume requires exact-HEAD reobservation: true.

These are **persisted repository facts**. They are not upgraded into claims about current browser/session liveness beyond what the evidence says.

## GACR scripts reobserved

Runtime / transport scripts:

- `scripts/governed_agent_continuity_relay.py`
- `scripts/gacr_agent_telemetry.py`
- `scripts/gacr_auto_attach.py`
- `scripts/gacr_bridge_notifier.py`
- `scripts/gacr_client_emitter.py`
- `scripts/gacr_host_issue_ingress.py`
- `scripts/gacr_workflow_bridge.py`

No script is changed by GACR-OR-01.

## GACR schemas reobserved

- `schemas/gacr-state.schema.json`
- `schemas/gacr-telemetry.schema.json`
- `schemas/gacr-bridge-contract.schema.json`

No schema is changed by GACR-OR-01.

## GACR workflow reobserved

- `.github/workflows/governed-agent-continuity-relay.yml`

Observed trigger surface includes push, issue_comment, schedule, workflow_dispatch and repository_dispatch GACR operations.

Repository-dispatch operations include:

- `gacr_auto-attach`
- `gacr_register`
- `gacr_heartbeat`
- `gacr_scan`
- `gacr_status`
- `gacr_takeover-plan`
- `gacr_takeover-accept`
- `gacr_beacon`
- `gacr_correlate`
- `gacr_dispatch`
- `gacr_context`
- `gacr_forensics`
- `gacr_telemetry-status`

No workflow is changed by GACR-OR-01.

## GACR tests reobserved

- `scripts/test_governed_agent_continuity_relay.py`
  - session create/resume;
  - provider enrichment without duplication;
  - provider conflict fail-closed;
  - standby;
  - suspected stall;
  - stalled / takeover-ready;
  - claim preservation;
  - idempotent takeover planning;
  - stalled predecessor heartbeat rejection;
  - exact-HEAD mismatch rejection;
  - accepted takeover and claim transfer;
  - predecessor non-resurrection;
  - source/client state isolation.

- `scripts/test_gacr_agent_telemetry.py`
  - safe Beacon;
  - EXACT and STRONG correlation;
  - Dispatcher target/delivery modes;
  - wake does not grant write;
  - Agent Context;
  - action trace;
  - interruption forensics;
  - explicit observed interruption cause;
  - secret-like telemetry rejection;
  - terminal-session exclusion;
  - ambiguous correlation fail-closed.

- `scripts/test_gacr_auto_attach.py`
  - Chronicle attachment;
  - late provider binding reuses session;
  - repeated resume/single-session invariant;
  - internal GACR workflow skip;
  - genuine external GitHub worker attach;
  - provider conflict fail-closed.

- `scripts/test_gacr_client_emitter.py`
  - attach;
  - heartbeat;
  - action trace;
  - interruption signal;
  - secret-like key rejection;
  - bounded heartbeat daemon behavior;
  - session resolution;
  - wake polling.

- `scripts/test_gacr_host_issue_ingress.py`
  - issue/title/author/schema/field validation;
  - safe evidence ID from comment;
  - source/client issue identity behavior;
  - provider enrichment through existing auto-attach path;
  - heartbeat renewal;
  - ACTION_TRACE;
  - Correlator/Forensics refresh;
  - duplicate comment idempotence.

- `scripts/test_gacr_host_issue_workflow.py`
  - issue_comment trigger;
  - no source issue-number hard-code in generic workflow;
  - prefix gate;
  - default-branch reconciliation ordering;
  - host adapter inclusion;
  - client upgrader clears source issue number;
  - title fallback strategy.

No test is changed by GACR-OR-01.

## R1-R6 evidence chain

### R1 — core continuity relay

- PR #98: `governance: add GACR agent continuity relay`
- merge: `0d0c595be7f6833bb36778a0cdac46c82abbd2ab`
- post-merge Governance CI: `36915276875` PASS.

Source/client runtime-memory correction:

- PR #100
- merge: `d894d29eca6fcc2a1784c459e9e3ddac672b3515`
- post-merge Governance CI: `36916456136` PASS.

### R2 — Beacon / Correlator / Dispatcher / Agent Context / Bridge notifier

- PR #102
- merge: `abefcfccbf822fa2fcf590e592ad51c767e32937`
- post-merge Governance CI: `36921331490` PASS.
- attestation PR #103.

### R3 — Interruption Forensics

- PR #104 candidate Governance CI: `36927496576` PASS.
- PR #104 merge: `ada6866efdfe9d2aed2e77171c01ca774a76a885`.
- post-merge Governance CI: `36927683547` PASS.
- workflow-registration run `36927681943`: FAILURE/no jobs, explicitly detected rather than ignored.
- corrective PR #105 merge: `05f49a634e1da46f3da5a016e32499236223ff1d`.
- corrective candidate CI: `36927942003` PASS.
- corrected post-merge Governance CI: `36928024260` PASS.
- final R3 attestation PR #106.

### R4 — Automatic Continuity Attachment

- PR #109 candidate Governance CI: `36939255201` PASS.
- merge: `4c7db9f0e2e782de147ef316c41086ed0863b49e`.
- post-merge Governance CI: `36939325620` PASS.
- post-merge GACR run: `36939325451` PASS.
- live AUTO_ATTACH session: `session-68c97d4bb1ef71c86444de12`.
- Beacon: `GACR-B-6e9a2275ea04`.
- Correlation: `GACR-C-caffb7cb6efd` EXACT.
- runtime persistence: `7467bbbca0f554df9d43831588ca03a0d1862c9f`.
- attestation PR #110.

### R5 / R5-A — Client emitter and internal-transport correction

R5:

- PR #111 candidate Governance CI: `36941120405` PASS.
- merge: `9b371b45711a9274a0976fe5015d8b19b0315e6c`.
- post-merge Governance CI: `36941216248` PASS.
- post-merge GACR run: `36941216312` PASS.

Detected regression evidence preserved:

- internal-transport run: `36941625864`;
- invalid transport session: `session-cb22a4ed0d9e29eba5383f5d`.

R5-A correction:

- PR #113 candidate Governance CI: `36942282684` PASS.
- merge: `bfb7b6fb81244f18f1b2c8c1ea82526af0dc2d62`.
- post-merge Governance CI: `36942347934` PASS.
- post-merge GACR run: `36942347872` PASS.
- no new internal-transport session/Beacon after correction.
- final attestation PR #114.

### R6 / R6-A / R6-B / R6-C — Provider-host issue bridge

R6 implementation:

- PR #116 candidate CI: `36947562102` PASS.
- merge: `a99a08e24626ed1d93c06b2e2fb9426e0e985b1a`.
- live START comment: `5943461065`.
- state commit: `69ccfc90c14f2fa02a264c765e31c49c64951635`.
- ACTION_TRACE + EXACT correlation + forensics observed.

R6-A rerun idempotence:

- PR #117 candidate CI: `36947919754` PASS.
- merge: `22c0f6f1a17a6478221436de3e638b3efc643b56`.
- live COMPLETED comment: `5943497457`.
- state commit: `3d258e3c9fdfacd1232fb0a19448594ab452b47f`.
- rerun result: `GACR_HOST_EVENT_ALREADY_PROCESSED / GACR_NO_STATE_CHANGE`.

R6-B portability:

- PR #118 candidate CI: `36948433046` PASS.
- merge: `21e499e5f556df53c3b1105aaa4b4712361287ec`.
- portability heartbeat comment: `5943559595`.
- state commit: `371509ac60d1a63c0be7cee8ec8620346210d824`.

R6-C provider enrichment:

- PR #119 candidate CI: `36948711458` PASS.
- merge: `914b251e9d01063fe38d8684271267b43f81d7e0`.
- provider-enrichment comment: `5943592733`.
- state commit: `46a4a3068f0eb28ec3dc1d141cbcf349542a3348`.
- provider enriched to `chatgpt` on the same canonical session.
- native provider conversation ref remains unavailable and was not invented.

Final R6 attestation:

- PR #120 merge: `bd6c0c869f66ab3cb138db82945320bc1753fc05`.
- post-merge Governance CI: `36949110223` PASS.
- post-merge GACR run: `36949110243` PASS.

Origin-realignment registration after R6:

- PR #121 merge: `c3f52511cb48fc94b786b5700e9398360871d38d`.
- Governance CI: `36951353590` PASS.
- GACR run: `36951353573` PASS.

Original-intent/autonomous-program registration:

- PR #122 merge / attested baseline HEAD: `afda467be7cb9194696b91963af3a4cf5cf0e7d5`.
- Governance CI: `36952356766` PASS.
- GACR run: `36952355612` PASS.
- latest observed push behavior: no external agent anchor, no state change, external bridge not configured.

### Exact-HEAD fail-closed evidence

Scheduled GACR run `36948763070` started from `914b251e9d01063fe38d8684271267b43f81d7e0` while the R6-C live event advanced remote `main` to `46a4a3068f0eb28ec3dc1d141cbcf349542a3348`.

The run produced a local scan commit but refused persistence with:

```text
HEAD_MOVED: expected=914b251e9d01063fe38d8684271267b43f81d7e0
remote=46a4a3068f0eb28ec3dc1d141cbcf349542a3348
```

Exit code 3 was therefore a deliberate exact-HEAD guard. No stale state was pushed.

## Known baseline limitations — authoritative for the next agents

The following limitations are **not corrected by GACR-OR-01**:

1. Presence-First realignment is not implemented merely because R4 auto-attach/R5 emitter/R6 host ingress exist.
2. The full safe Connection Envelope remains a historical target; this attestation does not claim every target field has one canonical exhaustive runtime representation.
3. A canonical `connection_fingerprint` formula remains to be evaluated in the intent/current/gap work; no provider identity may be synthesized from it.
4. Liveness and progress are not yet the fully separated Presence-First model required by realignment step 9.
5. Session interrogation/liveness challenge from realignment step 10 is not declared complete.
6. `UNBOUND_ACTIVITY` from realignment step 11 is not declared complete.
7. The current ChatGPT host does not prove an always-running background heartbeat.
8. Provider-private conversation identifiers/URLs remain unavailable unless actually supplied.
9. Browser crash, timeout, network-loss or provider-failure causes remain unknown unless explicitly observed.
10. External bridge/browser wake is optional and not configured/proven on the latest observed run.
11. The source currently has no live GACR claim, takeover, standby or dispatch item; their behavior is implementation/CI-proven, not inferred from empty projections.
12. The ultimate fresh-agent → observable presence → work → loss of fresh evidence → stall → second agent → exact-HEAD takeover → continuation scenario has **not** been run by this operation.
13. Realignment steps 3+ remain **NOT EXECUTED** by this operation.

## Non-regression assertion

Diff intent for this operation is governance-only.

Forbidden surfaces remain untouched:

- GACR runtime scripts;
- GACR workflow;
- GACR schemas;
- GACR tests;
- existing R1-R6 state/evidence;
- claims/collision-domain machinery;
- global Control Plane programme;
- `P12-S6`.

No R1-R6 history is deleted, rewritten or rolled back.

## GACR-OR-01 exit gate

| Gate | Result |
|---|---|
| Exact current `main` reobserved before branch/write | PASS |
| R1-R6 inventory completed | PASS |
| Current runtime/state identified | PASS |
| Tests linked | PASS |
| Live evidence linked | PASS |
| No runtime/workflow/schema/script corrective change | PASS |
| No Presence-First correction started | PASS |
| No step 3+ marked DONE | PASS |
| Canonical baseline attestation created | PASS |
| Machine projection created | PASS |
| Candidate CI | PASS — run `36954021583` |
| PR merge | PASS — PR #123 → `3ebf1e962b7c176a7b9e2eaf44d0842feda8345d` |
| Post-merge revalidation | PASS — Governance CI `36954073273`; GACR run `36954073285` |

The remaining repository gates were observed green on merged `main@3ebf1e962b7c176a7b9e2eaf44d0842feda8345d`. Therefore **`GACR-OR-01 = PASS`**. The post-merge runtime projections remained unchanged: sessions rev. 10, Beacons rev. 13, Correlator rev. 14, Forensics rev. 4.

## OR-01 closure evidence

- candidate Governance CI: `36954021583` — PASS;
- attestation PR: #123 — merged;
- merge SHA: `3ebf1e962b7c176a7b9e2eaf44d0842feda8345d`;
- post-merge Governance CI: `36954073273` — PASS;
- post-merge GACR run: `36954073285` — PASS;
- PR #123 changed files: exactly the human attestation and its machine projection;
- post-merge operational GACR projections: unchanged from the reobserved baseline;
- global programme / `P12-S6`: untouched.

## Authoritative stopping point for the two successor agents

Once this attestation is merged and post-merge revalidated, the following baseline facts are authoritative:

- R1-R6/R5-A/R6-A/R6-B/R6-C are preserved implemented history.
- The canonical source runtime stores are the existing `gacr-*.json` projections; no new parallel store is authorized.
- The canonical current session identity in persisted source evidence is `session-68c97d4bb1ef71c86444de12`.
- The historical internal-transport session is terminal/superseded and must never be revived or used as correlation identity.
- Internal GACR transport is never an agent identity.
- Claims and collision domains remain canonical ownership safety.
- Exact-HEAD reconciliation remains mandatory before mutable takeover.
- Provider conversation identity remains observed/supplied-only.
- Interruption cause remains observed-only.
- R6 proves event-driven provider-host ingress, not continuous provider-host liveness.
- Source/client runtime isolation remains mandatory.
- Presence-First remains the required direction; existing R1-R6 components are inputs to realignment, not proof that realignment is complete.

What remains to analyze after OR-01:

1. **Realignment step 2 formal gate only**: revalidate the already-canonical `GACR_ORIGINAL_INTENT.md` now that step 1 is closed. Do not rewrite its historical intent.
2. After step 2 is explicitly closed, build the step 3 `ORIGINAL_INTENT ↔ CURRENT_IMPLEMENTATION ↔ GAP` matrix.
3. Then, and only in frozen order, analyze the step 4 center-of-gravity drift.
4. Do not start Presence Fabric implementation, tests-before-code tranche, liveness/progress redesign, `UNBOUND_ACTIVITY`, or fresh-agent ultimate acceptance as part of this attestation.
5. Do not touch the global programme or treat `P12-S6` as a GACR dependency.

This is the precise handoff boundary of GACR-OR-01.
