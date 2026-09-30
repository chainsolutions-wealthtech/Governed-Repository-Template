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


## 2026-09-27 — P12-S5 Ekyc MCP endpoint recovery defect

- Central request #49 created the second fresh public repository `Patricked-code/Ekyc` from Template 2.8.6.
- Zero-touch bootstrap and initial Governance CI passed.
- First-agent local entry `Ekyc#1` captured the approved eKYC mission, scope, technical profile and setup choices.
- MCP linkage was enabled with transport `BOTH`, full governed mapping, domain strategy `DISCOVER_EXISTING_THEN_PROPOSE`, and runtime policy `EXPLICIT_APPROVAL_FOR_SCOPED_WRITE`.
- MCP discovery target run `36294979599` failed with `HTTP 404: Not Found`.
- The accepted endpoint answer was the MCP host root; prior governed evidence on the same service proves the direct MCP route is under `/mcp`.
- Generic framework diagnosis: after retryable discovery failure, the state machine exposed retry only and provided no governed path to correct `mcp_endpoint`.
- `Ekyc` was frozen; no target-specific repair was made.
- Created Template branch `governance/fix-mcp-discovery-endpoint-recovery` and PR #50.
- TDD RED commit `1e3aef857b57290de1b98eb4682d2339f1211343`; CI `36295172971` failed only with `HTTP 404 must reopen MCP endpoint correction`.
- Minimal fix commit `ec52fb0e0786eaf18fa8886950546c21c96a176c`: HTTP 404 now reopens endpoint correction; a corrected endpoint archives the failed evidence, clears the hold and returns to MCP discovery.
- GREEN Governance CI `36295231828`: PASS across the complete suite, including MCP fallback, relational materialization, Governance Model integrity and textual integrity.
- Canonical corrective task: `C1-13-A` IN_PROGRESS until PR #50 is merged, propagated to `Ekyc`, and the affected discovery checkpoint is resumed.


## 2026-09-27 — C1-13-B client local-entry test portability

- PR #50 merged to Template main at `dbe0014784362393c8cfbb02ce7810d483cf2bb7`.
- Source post-merge Governance CI `36295619581`: PASS.
- The official `/governed-upgrade-local-entry` path upgraded `Patricked-code/Ekyc` from `b6be4b96306a765efd6bbd20727f02d5ef17553d` to `2ece8cff98258f7c40cf7b7383ceb5c026db9639`.
- Open local-entry `Ekyc#1` was migrated automatically from revision 23 to 24; accepted business/setup answers and the 404 discovery evidence were preserved.
- Ekyc Governance CI run `36295714554` failed only in `Test repository-local governed agent entry`.
- Exact root cause: the newly distributed self-test attempted to read `.github/workflows/governed-control-plane.yml`, a source-only workflow intentionally absent from client repositories.
- No target patch was applied; Ekyc was frozen again.
- Created Template PR #51 / `C1-13-B`.
- RED commit `c2d70bbd07cd77d0b44a0e8c17b5366b2e2e76fb`; CI `36295815960` failed exactly with the new portability assertion.
- Minimal fix commit `0e000473c8a58d62918f28fefa482679bce47fe0`: source-only permission assertions execute only when `.template-source` exists.
- Functional GREEN Governance CI `36295850914`: PASS across the full suite.
- Unique next action: merge PR #51 after final reconciled CI, governed-reupgrade Ekyc, require target CI green, then resume the preserved MCP discovery checkpoint.


## 2026-09-27 — C1-13-C Governance Model client portability

- PR #51 merged to Template main at `0a4a9961565d53a872d6eb62ad3f4afadbb11d6e`.
- Source post-merge Governance CI `36296114629`: PASS.
- Official governed re-upgrade advanced `Patricked-code/Ekyc` to `dd5a2664c4422ab14fc7131a77e5c2df0e0356a0`; `Ekyc#1` migrated to revision 25 without losing approved answers or the MCP 404 evidence.
- Ekyc Governance CI `36296169271` passed all portable client/local-entry tests through governed-upgrade continuity.
- The sole failure was `Test Governance Model projection integrity`, which attempted to read source-only Governance Model files absent by design from a client repository.
- Ekyc was frozen; no target-specific patch was applied.
- Created Template PR #52 / corrective task `C1-13-C`.
- RED commit `dfd786caf325fbe1b971d7545d3b0f895f561911`; CI `36296258279` failed exactly on the new missing-client-skip regression assertion.
- Minimal fix commit `d0d4c3faabe561f60e80f9e2fd23c7956580e553`: `test_governance_model_integrity.py` exits successfully when `.template-source` is absent; full source validation is unchanged.
- Functional GREEN Governance CI `36296295586`: PASS.
- Next: finish source reconciliation, require final PR #52 CI green, merge exact-head, governed-reupgrade Ekyc, require client CI fully green, then resume the preserved MCP discovery checkpoint.


## 2026-09-29 — C1-13-D upgrader Governance Model test distribution

- PR #52 merged to Template main at `ca8ce60e31a1d5f07fc1293cac54ca29906b7501`; source post-merge Governance CI `36620454972`: PASS.
- Official governed client upgrade advanced `Patricked-code/Ekyc` to `bbe20f4406eb794df4d2452161462f945e2d3fc6`.
- Ekyc Governance CI `36620623398` failed in governed-upgrade continuity with `UPGRADE_SELFTEST_FAILED: client governance-model integrity test must skip source-only model state`.
- Diagnosis: the Template source already contained the portable Governance Model integrity test from C1-13-C, but `control_plane_upgrade_local_entry.py` did not distribute that script, leaving a stale client copy.
- Ekyc stayed frozen; no target-specific change was made.
- Created Template PR #53 / corrective task `C1-13-D`.
- RED commit `58cdbc1e0565a0937ea4c4bcdd0dea545277d82e`; CI `36620804501` failed exactly on the missing-distribution regression assertion.
- Minimal fix commit `5aa1601ee5c91a8523454197e76b47bed59459ba`: add `scripts/test_governance_model_integrity.py` to upgrader `static_paths`.
- Functional GREEN Governance CI `36620877757`: PASS.
- Next: final reconciled PR #53 CI, exact-head merge, governed Ekyc re-upgrade, fully green client CI, then resume MCP endpoint recovery/discovery.


## 2026-09-29 — C1-13-E MCP TLS external blocker

- PR #53 merged at `7b8cf2193514efd8f3fe8ce635b0d21abfe53639`; source post-merge Governance CI `36621351173`: PASS.
- Official governed upgrade advanced `Patricked-code/Ekyc` to `87c28f4fd4e36aa3d65cfc384309a054c1640e4c`.
- Ekyc Governance CI `36621490571`: SUCCESS across the full client suite; the four Template/client portability defects C1-13-A/B/C/D are therefore closed.
- The preserved MCP read-only discovery checkpoint was retried via governed command; target run `36621624763` failed with `SSL: CERTIFICATE_VERIFY_FAILED ... certificate has expired`.
- Live code review confirms transport `BOTH` cannot use SSH as a workaround because the repository-SSH certificate broker is also HTTPS on `mcp.wealthtechinnovations.com`.
- No TLS bypass, HTTP downgrade, direct target patch or MCP runtime/code mutation was attempted.
- External intake-only issue opened: `Patricked-code/MCP#201`.
- P12-S5 remains active but externally blocked. Resume only after MCP-side TLS remediation is attested, then retry the preserved discovery flow.

## 2026-09-29 — Ekyc owner-feedback authority reconciliation

The Ekyc CASE 1 replay revealed a generic semantic defect: the state machine treated completed MCP configuration answers as sufficient to advance into executable discovery.

Owner intent is now canonical: configuration prepares; it does not execute. The immediate task is `C1-13-E-A`, implemented in the Template first. Ekyc remains frozen and its existing answers are preserved.

The correction is intentionally complementary: the existing governance files, work-items, dependencies, sessions, claims, checkpoints, handoffs and Loop Engineering remain authoritative. The adaptive questionnaire must feed those existing structures with richer project/resource facts and prepared tasks.

## 2026-09-29 — V2.8.7 propagated to Ekyc

Template PR #55 merged at `8b3a1ac4abf250820558ba873110581f8607a2b3`; post-merge Governance CI `36637371154` passed.

The governed upgrade path advanced Ekyc to `a6b0c99cc8d90a1d5cbaf4d6288d52b995e596c6`; Ekyc Governance CI `36637639375` passed. Ekyc#1 preserved every prior answer and moved to `WAITING_FOR_DISCOVERY_APPROVAL` revision 29. The premature TLS failure is retained only in history.

CASE 1 is now correctly stopped at an owner authority gate: approve or change the concrete read-only discovery plan. No MCP execution is implied by earlier configuration choices.

## 2026-09-30 — Explicit discovery executed; TLS blocker confirmed

The owner approved the exact read-only MCP discovery plan. The central control plane accepted the answer, provisioned the governed credential path, and dispatched the machine command under Ekyc HEAD `a6b0c99cc8d90a1d5cbaf4d6288d52b995e596c6`.

Ekyc run `36638780542` attempted discovery and failed only on the expired public TLS certificate. The baseline write was skipped. Ekyc#1 advanced from revision 29 approval-waiting to revision 31 retryable discovery failure while preserving `mcp_discovery_approved=true`.

MCP#201 remains open. Its latest recorded programme evidence confirms remediation is not complete and that its own Governed Deploy #87 failed with the same certificate-expired condition.

The Template workstream is therefore correctly blocked on the external MCP TLS dependency. The same approved read-only plan may be retried after remediation, provided the plan has not materially changed.

## 2026-09-30 — TLS cleared; endpoint recovery reached approval gate

The prior MCP TLS blocker is no longer active. MCP Governed Deploy `36625479517` completed successfully and subsequent GitHub OIDC read-only evidence reached the MCP HTTPS endpoint successfully.

The already-approved Ekyc retry `36642689845` then failed with HTTP 404, which is a different and more advanced failure: HTTPS/TLS succeeded, but the stored endpoint targeted the host root. The canonical MCP architecture already identifies `/mcp` as the MCP endpoint.

The control plane corrected the factual endpoint through its existing machine command path. No direct Ekyc patch and no new MCP intake were used. Ekyc#1 is revision 33 and correctly requires explicit reapproval because the plan endpoint materially changed.

## 2026-09-30 — /mcp direct discovery passed; signed SSH profile recovery required

The corrected `/mcp` plan was explicitly reapproved. Ekyc run `36644247227` reached MCP successfully and all five direct read-only probes passed. The run then stopped at `SSH_PROFILE_MISMATCH`: the broker signs repository SSH access for S1 `212.227.212.33:22/root`, not for the MCP public hostname previously stored in the Ekyc answer.

Baseline application was skipped. Ekyc#1 persisted revision 35.

The new generic task `C1-13-G` adds a recovery path from signed broker evidence. The owner additionally required a persistent MCP capability image in the central Template; that additive work is queued as `C1-13-H` and will feed the existing Loop Engineering rather than replace it.

## 2026-09-30 — Persistent MCP capability image implementation

The owner requested that the central Template keep a durable MCP discovery image and refresh it whenever necessary, including a case-aware map of candidate MCP tools and prepared operations.

C1-13-H implements this as source-only Control Plane memory, not as a second engine. The snapshot consumes the MCP's own dynamic current-state/tool catalogue when refreshed and maps every observed tool to its declared surface and required authority. CREATE, ADOPT, MAP, LAB and CONTINUE receive planning candidates that flow into the existing Loop Engineering.

Refresh is read-only and event/need based. It uses the existing central MCP credential, validates the resulting snapshot, and persists changes only through a dedicated branch/PR.

During implementation, a security boundary was tightened: persistent public capability memory excludes server connection coordinates. Logical server IDs and capability metadata remain persisted; actual connection coordinates are refreshed live when an operation needs them.

Ekyc is separately waiting at revision 38 for explicit approval of the materially changed BOTH plan. No approval is inferred from this capability-memory work.

## 2026-09-30 — First central MCP capability refresh

The first source-only refresh was triggered through the governed `/refresh-mcp-capabilities` command.

Run `36646869819` proved the core design:

- direct read-only MCP refresh: PASS;
- generated snapshot validation: PASS;
- 135 tools observed;
- 2 resources observed;
- catalogue digest: `8447f9dcc5078fdc9287068c9a791ab5366cc8f10ead5770f6830ed4aca34f1b`;
- no MCP/server mutation;
- no secret values persisted.

The run failed only during Git persistence. Root cause: `actions/checkout` persisted the workflow `GITHUB_TOKEN` extraheader, which took precedence over the separately minted GitHub App token and produced a 403 push refusal.

The corrective branch disables checkout credential persistence so the explicit GitHub App token owns branch/PR persistence. The snapshot representation is also compacted: global tool metadata is stored once, case maps reference tool names, and only safe input-field metadata is retained.

## 2026-09-30 — C1-13-H semantic QA before snapshot merge

The automated MCP refresh successfully produced PR #63 from live runtime evidence. Security and transport controls passed, but semantic QA correctly stopped the merge.

Two defects were found:

1. the write-context parser treated indented metadata labels (`path:`, `note:`) as project IDs;
2. tag-intersection mapping made nearly every MCP tool a candidate for nearly every governance case.

The live catalogue remains valid evidence; only its planning projection is rejected.

The refinement branch `governance/refine-mcp-capability-map` now implements a capability-first model and observation-first questionnaire resolution. The purpose is not to know every tool exhaustively. It is to let an agent know, before asking the owner, which facts can already be observed and which MCP capability/authority would be needed for a concrete next operation.

Ekyc remains independently frozen at its corrected discovery approval gate, revision 38.

## 2026-09-30 — Capability-first MCP memory canonical; return to Ekyc

The raw-tool snapshot approach was refined through two semantic QA cycles before canonical merge. PRs #63 and #66 were deliberately closed unmerged. PR #65 established capability-first/adaptive-question semantics; PR #67 separated project scope and governed operational authority; the final refresh generated PR #68.

PR #68 merged at `6c293a809df15b85fe40685b3a0f6a3508e1ee4d`, and post-merge Governance CI `36652771078` passed.

C1-13-H is therefore DONE. The Template now knows both (a) stable project capabilities/question-resolution rules and (b) the refreshable current MCP implementation image.

Ekyc remains intentionally untouched at revision 38. CASE 1 resumes at C1-13-I: explicit approval of the corrected read-only BOTH discovery plan.

## 2026-09-30 — BOTH transport semantic correction

Owner clarified that `BOTH` means “configure both so the system can intelligently use one or the other”, not “couple both executions”.

Live source review confirmed the defect: the discovery runner currently executes DIRECT and then SSH for `BOTH`, and its historical summarizer expects combined evidence.

C1-13-I-A corrects the Template first. Ekyc remains untouched. Its prior DIRECT PASS is authorized evidence and will be migrated as the selected current route after the generic release; corrected SSH becomes an alternate configured route with independent readiness.

## 2026-09-30 — Ekyc resumes after BOTH smart-routing migration

PR #70 and its post-merge CI proved the generic correction. The governed v2.8.14 upgrade migrated Ekyc from revision 38 to revision 39 and reused the explicitly authorized DIRECT PASS from run 36644247227.

Ekyc now records DIRECT as the selected successful route and SSH as `CONFIGURED_NOT_ATTESTED`; no coupled rediscovery occurred.

All target workflows on the new Ekyc HEAD passed. The next unresolved step is `Q_DOMAIN_BINDING`. Discovery found no Ekyc registration/domain, so the factual part is resolved and only the owner's domain-binding intent remains.
