# CONTROL PLANE SUIVI

Durable chronological history for the source/control-plane repository only.

## 2026-09-26 — Self-governance gap identified

Observed that the repository already distributes persistent-memory primitives to clients but its own root project-state files remain intentionally templated with placeholders.

Confirmed existing source history was primarily recoverable through Git, issues and conversation context rather than a dedicated source-only authority set.

Decision: introduce a separate source-only memory namespace instead of converting distributed root templates into source-project state.

## 2026-09-26 — CREATE_NEW_REPOSITORY pilot checkpoint

- Template reached V2.6.10.
- `Patricked-code/Gouvern` completed first-agent baseline.
- Pilot baseline commit: `23975e0435e63fb45d7436d1f23ce8ce0a450a5f`.
- Pilot local-entry state: `LOCAL_HANDOFF_READY`.
- DIRECT MCP discovery: PASS.
- SSH OIDC discovery: PASS.
- Domain binding intentionally remains `UNRESOLVED`.
- MCP/SSH write authority remained disabled.
- Canonical framework program #12 advanced to the second fresh repository E2E proof.

## 2026-09-26 — V2.7.0 started

Purpose: make the control-plane source self-governed while guaranteeing that its own historical state never becomes client project history.

## 2026-09-26 — V2.7.0 source/client boundary proven

- Governance CI run: `36258871067` — PASS.
- Source authority coherence validation: PASS.
- Bootstrap client simulation: PASS.
- `docs/control-plane/` removed from initialized client: PASS.
- `.governance/control-plane-state/` removed from initialized client: PASS.
- Next: merge V2.7.0 and attest resulting canonical main HEAD.

## 2026-09-26 — V2.7.0 merged and source state attested

- V2.7.0 merge subject HEAD: `d11b72956e68526edf9b17aec472163a4e49a585`.
- Self-governed control-plane memory: ACTIVE.
- Source/client memory separation: ACTIVE.
- Canonical program #12 released to resume at `STEP_4_SECOND_FRESH_REPOSITORY_E2E`.

## 2026-09-26 — Program #12 chronology reconciled

- Detected mismatch: source checkpoint summarized STEP 4 as the second fresh repository test.
- Canonical issue chronology retained a distinct STEP 4 for live `NORMAL_GOVERNED_ENTRY` proof on `Gouvern`.
- Reconciliation decision: preserve both gates; STEP 4 normal-entry proof must complete before STEP 5 fresh-repository E2E.
- No test or mutable target action was started while the contradiction was unresolved.

## 2026-09-26 — Canonical relational memory started

- Introduced a source-only relational memory model for all framework cases.
- Added reusable tables for cases, modes, phases, questions/options, activities, repositories/runs, answers, decisions, events, evidence, checkpoints, handoffs, owner feedback, intakes and artifacts.
- CASE 1 is the first populated replay dataset.
- Cases 2–4 are registered and will be progressively populated from their real tests.
- CI materializes an ephemeral SQLite database and validates relational consistency.
- The committed authority remains versioned SQL/JSON; no mutable binary database is committed.
- Future target: PostgreSQL-backed admin web application after all case/parcours semantics are validated.

## 2026-09-26 — V2.8.0 canonical relational memory merged

- Release HEAD: `4c8d16b5fc71df7923942c5658c21269a0051da3`.
- Relational schema + catalog + runtime seed merged.
- Governance CI database materialization: PASS.
- Active workflow checkpoint remains CASE 1 `C1-12` / normal-entry proof.
- No frontend implemented yet; application layer remains intentionally deferred.

## 2026-09-26 — C1-12 live normal-entry proof revealed new generic work

- Created `Patricked-code/Gouvern#3` for a subsequent-agent NORMAL_GOVERNED_ENTRY proof.
- Initial start was refused by the actor authorization gate; no governed state advanced.
- V2.8.1 / PR #25 added exact-HEAD machine local-entry start.
- Gouvern upgrade to V2.8.1 exposed client control-plane policy drift.
- V2.8.2 / PR #26 synchronized current client policy while preserving target-client role.
- Gouvern upgrade to V2.8.2 exposed bootstrap self-test contamination by instantiated project choices.
- V2.8.3 / PR #27 made bootstrap consistency fixtures portable.
- Gouvern is now at `3a1b7689be5aa38b4b6fdb6456526e618f9b0dd5`.
- Current client validation passes and bootstrap self-test passes.
- Remaining blocker: Governance CI run `36262734626` fails at `scripts/test_connection_intent.py` with `INTENT_SELFTEST_FAILED: unexpected work item`.
- C1-12 remains IN_PROGRESS. C1-13 is still locked.



## 2026-09-26 — Canonical target architecture authority integrated

- User-supplied V2.8.3 architecture snapshot and integration analysis were read end-to-end.
- Snapshot live-state values were treated as historical context and reconciled against current Git state.
- Added source-only target authority `CP-ARCH-001` at `docs/control-plane/CANONICAL_ARCHITECTURE.md`.
- Added machine projection `.governance/control-plane-state/canonical-architecture.json`.
- Added imported-memory provenance/verification record; imported memory cannot grant live approval.
- Added decisions CPD-014 through CPD-018 for target architecture, revisioning/event history, Git authority hierarchy, task lineage and frontend sequencing.
- Added migration `003_canonical_authorities.sql` for authority revisions and canonical memory events.
- Completed deterministic materializer support for history tables already defined in the schema.
- Preserved current execution gate: CASE 1 / C1-12 / `C1_12_F_DIAGNOSE_UNEXPECTED_WORK_ITEM`.


## 2026-09-26 — Continuous relational projection requirement

- Owner requirement: keep recording all meaningful information and build/populate the database at the same time as framework work progresses.
- Accepted as `CPD-019`.
- Canonical rule: durable structured information is persisted in Git authorities/history and projected to the relational seed/event model in the same governed change when representable.
- If the schema cannot represent a required record yet, the gap must be explicit as `PENDING_PROJECTION` and handled by an additive migration/task.
- This enrichment does not change the active CASE 1 execution gate; C1-12-F remains the unique executable task.


## 2026-09-26 — Identity / connection / session routing backlog captured

- Owner asked whether arriving agents are automatically identified, bound to a unique session, linked to the entry account and routed chronologically.
- Live verification showed current behavior is only partial: stable session IDs and resume logic exist, but arrival/account capture and full source-control-plane auto-session are not yet automatic.
- Added decision `CPD-020`: PRINCIPAL, AGENT, CONNECTION, SESSION, ROLE and AUTHORITY are distinct dimensions.
- Added planned tasks `IDN-001` through `IDN-013`.
- Projected the requirement into relational owner-feedback and canonical-memory events.
- Active CASE 1 execution remains unchanged: `C1-12-F`.


## 2026-09-26 — Two-stage automated agent purpose routing captured

- Owner clarified the desired post-identity behavior on the control-plane source.
- Stage 1 target: choose `WORK_ON_CONTROL_PLANE` or `APPLY_GOVERNANCE_CASE`.
- Stage 2A target: if working on the repo, choose `CODE_IMPLEMENTATION`, `EXECUTE_EXISTING_TASK`, or `ADD_OR_ENRICH_INFORMATION`.
- Stage 2B target: if applying a governance case, choose exactly one of the four structuring cases.
- After case selection, the selected case's chronological question/action flow takes over.
- Human users are not expected to perform Git/GitHub/CI/file operations manually; they answer governed questions and provide explicit approvals where required.
- Added decision `CPD-021` and planned tasks `RTE-001` through `RTE-013`.
- The active runtime router is intentionally unchanged until implementation + regression tests are complete.
- Active CASE 1 execution remains `C1-12-F`.


## 2026-09-26 — V2.8.4 portable connection-intent self-test

- Framework product: `chainsolutions-wealthtech/Governed-Repository-Template`.
- Pilot repositories such as `Patricked-code/Gouvern` are validation-only fixtures.
- C1-12-F root cause confirmed: `test_connection_intent.py` copied real instantiated-client work/session state into its synthetic test.
- This allowed a real `WORK-PROJECT-001 READY` item to win dispatch while the test expected `WORK-DISCOVER-001`.
- V2.8.4 candidate rebuilds a deterministic synthetic template fixture: template marker/profile, work-items, claims, sessions and canonical-memory pointer.
- The real executing repository state is never reset; only the temporary copied self-test fixture is changed.
- C1-12-F is DONE.
- C1-12-G is IN_PROGRESS pending full Template Governance CI.
- Decision `CPD-022` codifies Template = product/framework, pilots = external validation only.


## 2026-09-26 — V2.8.4 framework release merged

- Product repository: `chainsolutions-wealthtech/Governed-Repository-Template`.
- PR #33 merged.
- Release subject HEAD: `608d29318d1b2df199e4ec304c4e2fe7bfb94263`.
- Governance CI run `36274141697`: PASS.
- Portable connection-intent self-test passed in the Template.
- C1-12-G: DONE.
- C1-12-H: DONE.
- C1-12-I: IN_PROGRESS — validate released V2.8.4 on an external CASE 1 pilot.
- Pilot validation must not introduce generic implementation changes directly into the pilot.


## 2026-09-26 — V2.8.5 dynamic client-upgrader correction

- Product repository remains `chainsolutions-wealthtech/Governed-Repository-Template`.
- Before any pilot mutation, validation found the client upgrader was still hard-coded to V2.8.3.
- The upgrader also omitted the V2.8.4 portable connection-intent test/runtime surface.
- Client CI still contained an unconditional source-only control-plane DB materialization step.
- Added C1-12-I-A as the unique executable framework task; external pilot validation remains the parent objective.
- V2.8.5 candidate now derives release version from the Template manifest, synchronizes the required generic static governance surface, preserves mutable client state, and skips source-only DB materialization cleanly on clients.
- Added CPD-023 and canonical architecture revision `CP-ARCH-001-R4`.
- No pilot repository was modified while this framework gap remained open.


## 2026-09-26 — V2.8.5 framework release merged

- Product repository: `chainsolutions-wealthtech/Governed-Repository-Template`.
- PR #35 merged.
- Release subject HEAD: `556011ea20310a483f77a9a382b66b79bed4b31c`.
- Governance CI run `36274765257`: PASS.
- Dynamic version-from-manifest client upgrader: PASS.
- Required connection-intent client surface synchronization: PASS.
- Client-safe source-only DB CI guard: PASS.
- C1-12-I-A: DONE.
- C1-12-I-B: IN_PROGRESS — apply current Template via governed exact-HEAD upgrade to external CASE 1 pilot.


## 2026-09-26 — V2.8.6 complete portable intent fixture

- Governed V2.8.5 pilot upgrade: PASS to `17f852c19ac8c5d26f40d3508338ce9c221697c8`.
- Pilot CI `36275001208`: FAIL at connection-intent synthetic bootstrap.
- Generic root cause returned to Template: copied client project-profile/infrastructure/local-entry/MCP/access/workflow state still influenced the fresh-template simulation.
- Added C1-12-J-A (diagnosis DONE), C1-12-J-B (Template fix IN_PROGRESS), C1-12-J-C (release/re-upgrade PENDING).
- V2.8.6 candidate aligns the intent test fixture with the already-proven bootstrap-consistency fixture domains.
- Subprocess diagnostics now include stdout/stderr.
- Pilot remains an external evidence surface; implementation remains in the Template.


## 2026-09-26 — V2.8.6 framework release merged

- Product repository: `chainsolutions-wealthtech/Governed-Repository-Template`.
- PR #37 merged.
- Release subject HEAD: `02173120acfa3941e84bf69c89dac0e8d74b47ce`.
- Governance CI run `36275324940`: PASS.
- C1-12-J-B: DONE.
- C1-12-J-C: IN_PROGRESS — governed exact-HEAD re-upgrade of external CASE 1 pilot.

## 2026-09-27 — Central Governance Model catalogue requirement accepted

- Owner clarified that the central Governance Model is the reference object; CREATE/ADOPT/MAP/LAB are application strategies.
- Added source-only authority `CP-GOVMODEL-001`.
- Recorded decisions `CPD-025` to `CPD-027`.
- Registered the 19-point completion programme `GMC-01..GMC-19` in seven phases.
- Preserved CASE 1 as the active chronological priority; no later task became executable.
- Reuse rule: extend the existing SQL/JSON/materializer canonical memory, never create a parallel database.
- Planned comparison becomes semantic down to capability/component/object/field/control/test, with exact/equivalent/partial/absent/conflict/obsolete/unknown/not-applicable classification.
- The detailed model registries remain `PENDING_PROJECTION` until the additive relational schema extension is implemented through the governed task chain.

## 2026-09-27 — Governance Model catalogue merged and attested

- PR #39 merged to canonical `main`.
- Merge subject HEAD: `6fb12122d5a0812f6ceca063b1d7af13511003bc`.
- Governance CI run `36284616415`: PASS.
- Canonical authority `CP-GOVMODEL-001`, architecture revision `CP-ARCH-001-R6`, decisions `CPD-025..CPD-027` and `GMC-01..GMC-19` backlog are now part of canonical source memory.
- The current execution gate remains CASE 1 / `C1-12-J-C`; no GMC task is executable before its dependencies.

## 2026-09-27 — GMC execution-blueprint preparation requirement

- Owner clarified that the 19 GMC items are not 19 tasks but 19 chronological work packages/groups.
- Each group must be prepared before coding as a mission package containing exact research locations, search methods, atomic tasks, expected results, storage destinations, evidence, exit criteria and downstream reuse.
- Results from earlier groups become validated versioned inputs to later groups.
- This is planning-only work: no Governance Model registry implementation, SQL migration, comparator, applicability engine or runtime change is authorized by this clarification.
- Recorded as decision `CPD-028`.
- Active CASE 1 execution priority remains unchanged.

## 2026-09-27 — 19 GMC work packages fully decomposed

- Added `docs/control-plane/GOVERNANCE_MODEL_EXECUTION_BLUEPRINT.md`.
- Added machine projection `.governance/control-plane-state/governance-model-execution-blueprint.json`.
- The 19 GMC items are now represented as chronological work packages `GMC-G01..GMC-G19`.
- The blueprint contains 168 atomic tasks `GMC-Gxx-Tyy`.
- Every group now records objective, sources to inspect, search patterns, atomic tasks, expected outputs, exit criteria, HOLD conditions and downstream consumers.
- Chronology corrected to the 1:1 chain `G01 → ... → G19`.
- Downstream work requires validated outputs + evidence, not a status flag alone.
- This remains planning-only; no Governance Model registry/schema/SQL/comparator/runtime implementation was started.
- Active CASE 1 execution remains unchanged.

## 2026-09-27 — GMC artifact/evidence dependency model completed

- Added decision `CPD-029`.
- Enriched the Governance Model Execution Blueprint from simple chronological dependencies to three explicit dependency dimensions:
  - `TASK_DEPENDENCY`;
  - `ARTIFACT_DEPENDENCY`;
  - `EVIDENCE_DEPENDENCY`.
- Work-package completion no longer means only a status flag; downstream unlock requires validated upstream exit, validated sufficiently-complete artifacts, required evidence and passing exit controls.
- Group results are now modeled as persistent/versioned planned knowledge artifacts with stable IDs, producer, validation state, provenance requirement, consumers and append/supersede/revalidate semantics.
- Blueprint now contains 19 work packages, 174 atomic tasks and 85 planned knowledge artifacts.
- Filled previously implicit model-registry coverage for workflows, failures, recoveries, authorities and tests, plus applicability/integration/release contracts.
- GMC-G19 now has an explicit final assembly contract covering all model registries/contracts and separate PASS demonstrations for completeness, consistency, traceability, coverage, reusability and the four structuring cases.
- Still `PLANNING_ONLY`; no registry/schema/SQL/comparator/runtime implementation was performed.
- CASE 1 unique executable task remains unchanged.


## 2026-09-27 — PR #42 post-merge GMC integrity reconciliation

- Reobserved canonical Template main at `2c70fc82aed4fa8f7eebb7f49b2573e6c57e9e59`.
- Two PR #42 review threads remain unresolved after merge.
- P1 diagnosis: 68/85 planned knowledge artifacts had GMC `consumed_by` metadata inconsistent with their dependency contracts; the contracts and 100 global artifact dependency edges were already reciprocal.
- P2 diagnosis: CPD-029 changed normative Governance Model semantics without advancing `CP-GOVMODEL-001` beyond R1.
- Inserted `C1-12-J-C-A` before external pilot mutation.
- Reconciled GMC consumer projections from a single canonical dependency source.
- Prepared append/supersede authority revision `CP-GOVMODEL-001-R2`.
- Added fail-closed CI regression test for dependency/consumer/revision integrity.
- Reconciled relational repository HEAD plus current checkpoint/handoff records.
- Parent CASE 1 action `C1-12-J-C` remains blocked until candidate CI/merge/post-merge attestation pass.


## 2026-09-27 — PR #43 GMC integrity correction merged

- PR #43 merged to `main` at `113c50aa765ae886cd7a085637b8d5dbb5c2766b`.
- Final candidate Governance CI run `36289874574`: PASS.
- New GMC integrity test: PASS with 19 work packages, 174 atomic tasks, 85 planned knowledge artifacts and 100 artifact dependency edges.
- Relational control-plane database materialization: PASS.
- `CP-GOVMODEL-001`: revision R2, append/supersede chain preserved.
- PR #42 P1/P2 review threads resolved.
- Inserted correction `C1-12-J-C-A` completed.
- Original CASE 1 chronological action restored: `C1_12_J_C_RELEASE_AND_REUPGRADE_CASE1_PILOT`.
- No direct mutation of the external pilot occurred during the framework correction.


## 2026-09-27 — V2.8.6 pilot revalidation reconciled

- Reobserved Template main at `dc2c1d5244aa11eaa9d4486edb5d3a1cc166ed6f`.
- Reobserved `Patricked-code/Gouvern` main at `671774dfc8e8be8eac2b50d5fb8f0928591694b3`.
- Verified the pilot head is the governed V2.8.6 upgrade commit, parented by the prior V2.8.5 pilot head.
- Verified `.governance/TEMPLATE_MANIFEST.json` reports `2.8.6`.
- Verified Pilot Governance CI run `36275524530` completed `SUCCESS` on the exact current pilot HEAD.
- Every pilot Governance CI step passed, including connection intent routing and governed upgrade session HEAD continuity.
- Historical source state lag was reconciled instead of replaying the already completed upgrade.
- `C1-12-J-C`: DONE.
- `C1-12-J`: DONE.
- `C1-12-K`: IN_PROGRESS.
- Unique next action: `C1_12_K_RERUN_GOUVERN_ISSUE_3`.

## 2026-09-27 — C1-12-K machine local-start transport defect

- Reobserved pilot `Patricked-code/Gouvern@671774dfc8e8be8eac2b50d5fb8f0928591694b3`.
- Existing baseline/session/work were preserved: `LOCAL-000002-S1`, `WORK-PROJECT-001`, no active claims.
- Sent the governed machine local-start through the historical source request `#4`.
- Source Control Plane acknowledged the request but no new target local-entry issue appeared.
- Framework diagnosis: repository dispatch requires `Contents: write`; the `local-start-token` requested only `Contents: read`.
- Added RED regression test in PR #47; CI `36292333079` failed only at the expected local-entry permission assertion.
- Minimal workflow correction changed only the machine local-start token to `permission-contents: write`; CI `36292388479` PASS.
- `C1-12-K-A` records the generic framework correction as DONE.
- `C1-12-K` remains IN_PROGRESS and is retried only after Template merge/reobservation.

## 2026-09-27 — C1-12 normal governed entry proof completed

- Template transport correction PR #47 merged to source main `4e7b6354f301ea1f3cb7261def738d9c1dca64b3`.
- Reobserved pilot HEAD `671774dfc8e8be8eac2b50d5fb8f0928591694b3`.
- Exact-HEAD machine local-start created `Patricked-code/Gouvern#4` / `LOCAL-000004`.
- Mode immediately proved: `NORMAL_GOVERNED_ENTRY`.
- Sequential machine answers completed through `LOCAL_HANDOFF_READY`, revision 6.
- Target start run `36292612321` PASS; answer runs `36292715800`, `36292741820`, `36292775187`, `36292816422`, `36292850873` PASS.
- Pilot HEAD remained unchanged.
- Baseline state blob, sole first-agent session `LOCAL-000002-S1`, work-items including `WORK-PROJECT-001`, and empty claims remained unchanged.
- `C1-12-K/L/M/N/O/P`: DONE.
- `P12-S4`: DONE.
- Current unique task: `P12-S5_SECOND_FRESH_REPOSITORY_E2E`.

## 2026-09-27 — C1-12-P-A dynamic relational phase validation

- Advancing CASE 1 from C1-12 to C1-13 exposed a source-only materializer validation hard-coded to `C1-12`.
- RED Governance CI: `36293227831`, all prior checks PASS, failure only at canonical DB materialization.
- Failure: `CASE1 active phase mismatch: [('C1-13',)]`.
- Fix: require exactly one active CASE 1 phase and require it to equal the pilot run's `current_phase_id`.
- GREEN Governance CI: `36293287750` PASS.
- No second database or alternate phase authority introduced.
