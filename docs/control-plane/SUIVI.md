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

## 2026-10-01 — KBI-04O first live refresh exposed a test-fixture defect

- Workflow run `36844233362` reached the live MCP read-only collector successfully.
- KBI-04N persistence succeeded transiently at revision 1 with 17 validated facts.
- Validation then failed only because `test_control_plane_server_identity_secret_facts.py` loaded the already-mutated source file as its supposed revision-0 fixture.
- The runner did not reach the governed PR persistence step, so no live fact state was committed.
- Generic correction `KBI-04O-A` makes the unit fixture independent of the live canonical revision while still validating the current source state.

## 2026-10-01 — KBI-04O live refresh canonical

The corrected KBI-04O pipeline completed end-to-end. Run `36844701817` performed bounded read-only S1/S2 observation, revision-guarded safe-fact persistence, validation and governed PR creation.

PR #86 contained only `.governance/control-plane-state/server-identity-secret-facts.json`, revision 1 / 17 facts. CI `36844736669` passed and the PR merged at `b665fba88d276b9efb636a894e53d890344b2faa`; post-merge CI `36844997332` also passed.

KBI-04O and KBI-04O-A are complete. The unique CASE 1 next action remains the Ekyc domain-binding owner decision.

## 2026-10-01 — Ekyc server-before-domain correction proven

PR #88 corrected the generic fresh-project question order. Full source CI passed before and after merge.

The governed v2.8.25 upgrade advanced Ekyc from `9ace9f...` revision 39 / `Q_DOMAIN_BINDING` to `b67a4ec58d837a66f3c3dedb02caadaf044912d5` revision 40 / `Q_PRODUCTION_SERVER_SELECTION`.

All prior answers and authorized MCP discovery evidence were preserved. No discovery replay, server mutation or domain mutation occurred.

The next unique owner decision is the Ekyc production-server selection among observed `S1` / `S2` or explicit deferral/new-server planning.

## 2026-10-01 — Ekyc selects S1; progressive domain-choice correction

Owner selected S1 through the exact current Ekyc local-entry gate. The governed command advanced Ekyc#1 to revision 41 without moving the Git HEAD or mutating S1.

The resulting legacy `Q_DOMAIN_BINDING` is too coarse for the required adaptive flow. Generic corrective task C1-13-I-B-C splits domain planning into domain intent, observed S1 parent/existing-domain selection, label/name choice, automatic binding derivation and prepared capability requirements.

No target-specific Ekyc patch is permitted.

## 2026-10-01 — Ekyc domain-intent gate ready

The v2.8.26 governed upgrade migrated Ekyc#1 from the legacy coarse domain object gate to the progressive domain-intent gate while preserving the owner's S1 production-server choice.

All source and target validation runs passed. Ekyc is now revision 42 at `Q_DOMAIN_INTENT`. The next owner input is only the domain intent; later questions are derived from that choice and the already-known S1 inventory.

## 2026-10-01 — Existing-host path capability and Ekyc workflow-model gate

The owner selected `CREATE_NEW_ROOT_DOMAIN`, then `DISCOVER_AVAILABLE_NAMES` for Ekyc. These answers advanced the local entry to `Q_WORKFLOW_MODEL` without registering a domain or mutating S1/DNS/Plesk/TLS.

During the domain discussion the owner required the generic platform to also support an application mounted under an HTTP path of an already existing domain or subdomain. Template PR #92 implemented this additively: DNS host binding and HTTP deployment path are now separate facts, with `HOST_ROOT`, `CREATE_PATH`, `REUSE_EXISTING_PATH` and `DECIDE_LATER` mount modes. Path creation prepares reverse-proxy capability/authority requirements but never grants execution authority from the questionnaire answer.

PR #92 merged at `8143db05b8ed412bdbc3d710f4a1fdf49f652161`; post-merge Governance CI `36880059834` passed. The governed v2.8.27 upgrade run `36880153919` advanced Ekyc to `4bf80309313f3d34f74ffca183bd540583d2e87f` and migrated Ekyc#1 revision 44 → 45 while preserving all business/setup answers. Target Governance CI `36880223661`, Auto Bootstrap `36880223820`, and Governed Local Entry `36880228405` all passed.

The unique next owner decision is now `C1_13_I_B_E_SELECT_EKYC_WORKFLOW_MODEL`. P12-S6 and GMC remain downstream.

## 2026-10-01 — Ekyc STANDARD_GOVERNED_FLOW selected

Owner selected `STANDARD_GOVERNED_FLOW` through the governed central command path. Control Plane run `36894608509` and Ekyc Governed Local Entry run `36894651525` passed. Ekyc HEAD remains `4bf80309313f3d34f74ffca183bd540583d2e87f`; Ekyc#1 advanced to revision 46 / `SETUP_APPROVAL`.

The next unique gate is explicit `setup_approved` approval of the prepared repository setup and governed rights matrix. Domain/server operations remain prepared-only and no S1/DNS/Plesk/TLS execution authority is implied.

## 2026-10-01 — P12-S5 second fresh E2E PASS

Owner setup approval was dispatched through central comment `5936330817`. Control Plane run `36895996929` and Ekyc target run `36896033996` passed. The approved first-agent baseline materialized as Ekyc commit `3e889a2bdac78312ebcc7e31d1388ead65c9fceb`, with `LOCAL-000001-S1` as the first-agent session and `WORK-PROJECT-001` still `READY`.

The required subsequent-agent proof then ran through Ekyc#2 / `LOCAL-000002` in `NORMAL_GOVERNED_ENTRY` mode. Start run `36896607275` and final command run `36896992524` passed. Final state is `LOCAL_HANDOFF_READY`, revision 6. Ekyc HEAD did not change during the normal-entry proof, the first-agent session remained unique, and the project work item was neither modified nor executed.

P12-S5 therefore satisfies its exit gate without target-specific repair. No S1/domain/DNS/Plesk/TLS mutation occurred. P12-S6 is now the unique chronological next task; GMC-A remains blocked behind CASE 1 closure.

## 2026-10-01 — GACR agent continuity relay

- Added reusable **Governed Agent Continuity Relay**.
- Heartbeat/lease, stall detection, standby takeover, exact-HEAD reconciliation and claim transfer implemented.
- Provider conversation references can be correlated when explicitly supplied; no identifier is invented.
- Client upgrades preserve mutable GACR takeover/session/claim state.
- PR #98 merged at `0d0c595be7f6833bb36778a0cdac46c82abbd2ab`.
- Post-merge Governance CI `36915276875`: PASS.
- No change to programme priority; `P12-S6` remains active.

## 2026-10-01 — GACR source/client boundary v2.8.30

- Corrective PR #100 merged at `d894d29eca6fcc2a1784c459e9e3ddac672b3515`.
- Post-merge Governance CI `36916456136`: PASS.
- Template-source GACR sessions/claims/takeovers now live only under source-only `.governance/control-plane-state/gacr-*.json`.
- Client projects keep repository-local GACR runtime stores.
- Source conversation/session state cannot leak through template initialization or governed client upgrade.
- No change to CASE 1 / `P12-S6` priority.

## 2026-10-01 — GACR R2 Beacon / Correlator / Dispatcher

- Added Beacon safe connection/action telemetry.
- Added Correlator with EXACT/STRONG/PROBABLE/AMBIGUOUS/UNKNOWN outcomes.
- Auto-binding is limited to exact or unique strong evidence.
- Added Dispatcher with repository polling, repository-dispatch and optional external-bridge delivery modes.
- Added safe agent-context aggregation for deterministic resume.
- Added optional outbound bridge notifier using GitHub variable + secret configuration.
- Added source/client telemetry state isolation and client-upgrade preservation.
- Added runtime namespaces `GACR-B-*`, `GACR-C-*`, `GACR-D-*`.
- Template target version: `2.8.31`.
- Full Governance CI pending.
- No change to `P12-S6` priority.

## 2026-10-01 — GACR R2 CI-proven

- PR #102 merged at `abefcfccbf822fa2fcf590e592ad51c767e32937`.
- Post-merge Governance CI `36921331490`: PASS.
- Safe connection telemetry, correlation, dispatch, agent-context and optional bridge notifier are now part of Template v2.8.31.
- No provider conversation identifier is fabricated when unavailable.
- No wake event bypasses claim/authority/exact-HEAD gates.
- `P12-S6` remains the active programme priority.

## 2026-10-01 — GACR R3 Interruption Forensics

- Started from exact canonical main `0d4ca9ff007b88f8fee040ff845ea9a0387d1815` after R2 attestation.
- R2 was not replayed: Beacon, Watch, Correlator, Dispatcher, Agent Context and Bridge contract remain intact.
- Added `CP-AGENT-RELAY-001-R3` / `CPD-052`.
- Added safe action/tool trace fields to Beacon without payload/secret capture.
- Added deterministic Interruption Forensics current projection with observed-only external cause classification.
- Resume reports expose last heartbeat, task/branch/PR, claims/collision domains, last observed/written HEAD, last started/completed action, last tool call, in-flight action, checkpoint/evidence references, takeover/dispatch state and exact-head resume requirements.
- Added source/client forensics-state separation and governed-client upgrade preservation.
- No independent lock store, task engine or authority surface introduced.
- Programme priority remains `P12-S6`; this cross-cutting branch does not execute CASE 1 closure.
- Candidate CI pending.

## 2026-10-01 — GACR R3 workflow registration correction

- PR #104 merged R3 at `ada6866efdfe9d2aed2e77171c01ca774a76a885`; Governance CI `36927683547` passed.
- GitHub nevertheless emitted failed workflow-registration run `36927681943` with no jobs for the changed GACR workflow.
- The R3 runtime/tests were therefore not considered fully attested.
- Corrective action is minimal: restore the previously accepted manual `workflow_dispatch` input surface and keep rich action/interruption trace fields on repository-dispatch/client-bridge/CLI telemetry.
- No R3 forensic capability is removed.
- Template candidate version: `2.8.33`.
- Programme priority remains `P12-S6`; no CASE 1 closure work is executed.

## 2026-10-01 — GACR R3 corrected main CI-proven and final attestation

- Corrective PR #105 merged to `main` at `05f49a634e1da46f3da5a016e32499236223ff1d`.
- PR #105 candidate Governance CI `36927942003`: PASS.
- Post-merge Governance CI `36928024260`: PASS.
- The prior workflow-registration failures are tied only to superseded HEAD `ada6866efdfe9d2aed2e77171c01ca774a76a885`; no equivalent failure is present on corrected main.
- R3 runtime, telemetry, source/client separation, upgrader preservation, namespaces and regression tests are intact.
- Agent activity is now durably recorded as `AAL-20261001-GACR-001` in human and machine projections.
- The global programme remains parked at `P12-S6_CLOSE_CREATE_NEW_REPOSITORY_CASE`.
- Per owner instruction, do not resume `P12-S6` until explicit owner OK after GACR is attested.

## 2026-10-02 — GACR R4 Automatic Continuity Attachment candidate

- Reobserved canonical main: `75996ee63ae283fd0d6d94549c9746f1bd2ac2bc`.
- Historical GACR method preserved: dedicated `governance/gacr-*` branch, additive implementation, CI, PR, merge, post-merge CI, attestation.
- R4 candidate branch: `governance/gacr-r4-auto-attach`.
- New runtime: `scripts/gacr_auto_attach.py`.
- A fresh active Conversation Chronicle can provide a stable provider-independent connection anchor.
- GitHub execution identity is the fallback when no explicit client or fresh Chronicle anchor is available.
- Missing provider conversation reference no longer blocks GACR attachment.
- Late provider metadata reuses and enriches the existing connection-bound session.
- New E2E test checks create → late ChatGPT binding → resume → single-session invariant → fail-closed provider conflict.
- Source-main push activation is protected against repository-automation state-persistence loops.
- Template candidate version: `2.8.34`.
- `P12-S6` remains preserved and unexecuted pending owner OK after GACR completion.

## 2026-10-02 — GACR R4 live auto-attach proof

- PR #109 candidate Governance CI `36939255201`: PASS.
- PR #109 merged at `4c7db9f0e2e782de147ef316c41086ed0863b49e`.
- Post-merge Governance CI `36939325620`: PASS.
- Post-merge GACR workflow `36939325451`: PASS.
- Active Chronicle `CHAT-MEM-20261002-001 / SESSION-000002` automatically produced GACR session `session-68c97d4bb1ef71c86444de12`.
- Beacon `GACR-B-6e9a2275ea04` records `source=CONVERSATION_CHRONICLE`, `event_type=AUTO_ATTACH`.
- Correlation `GACR-C-caffb7cb6efd` is `EXACT`.
- Runtime state persisted at `7467bbbca0f554df9d43831588ca03a0d1862c9f`.
- R4 attestation is the remaining GACR step; global `P12-S6` remains waiting for owner OK.

## 2026-10-02 — GACR R5 Client Liveness and Trace Emitter candidate

- Reobserved main: `6d6ba0e23d052d563e014e290ba4b32fc88b87db`.
- R4 remains `LIVE_AUTO_ATTACH_PROVEN / CI_PROVEN`.
- Candidate branch: `governance/gacr-r5-client-liveness-trace`.
- New generic emitter: `scripts/gacr_client_emitter.py`.
- Added runtime provenance `CLIENT_EMITTER`.
- Added attach, heartbeat, action trace, explicit interruption, session resolution and wake polling operations.
- Runtime transport credentials are never serialized into client payloads.
- Wake polling is read-only with respect to takeover authority.
- Added `scripts/test_gacr_client_emitter.py` and Governance CI coverage.
- Candidate Template version: `2.8.35`.
- This tranche does not claim that the current ChatGPT browser UI runs a persistent emitter unless such a host surface is actually observed.
- `P12-S6` remains preserved and unexecuted.

## 2026-10-02 — GACR R5 post-merge proof and generic-core completion

- PR #111 candidate Governance CI `36941120405`: PASS.
- PR #111 merged at `9b371b45711a9274a0976fe5015d8b19b0315e6c`.
- Post-merge Governance CI `36941216248`: PASS.
- Post-merge GACR workflow `36941216312`: PASS.
- Existing current-conversation session stayed singular and ACTIVE.
- AUTO_ATTACH Beacon `GACR-B-ff8bedbc4bf2` correlated EXACT through `GACR-C-976bbba3924d`.
- GACR runtime persistence advanced main to `34ceb14a140202ad7b57c9db2700241d50e7460c`.
- Generic R5 client emitter supports attach, heartbeat, action/tool trace, explicit interruption, session resolution and wake polling.
- The current ChatGPT host does not expose a persistent client process or direct repository-dispatch action to this assistant; therefore autonomous browser-side heartbeat remains an external host-instrumentation boundary, not a repository-core defect.
- Generic GACR R1-R5 is now complete as a reusable repository/client protocol.
- Do not resume `P12-S6` until explicit owner OK.

## 2026-10-02 — GACR R5 post-attestation internal-transport regression

- Final control after PR #112 detected `session_count=2`; GACR was therefore not declared final.
- The added session `session-cb22a4ed0d9e29eba5383f5d` came from GACR workflow run `36941625864`, not from a second conversation/agent.
- Its Beacon is `GACR-B-127716e672d9` with `source=GITHUB_ACTIONS` and workflow `Governed Agent Continuity Relay`.
- Root cause: stale Chronicle → internal GitHub Actions fallback.
- Corrective decision `CPD-055`: internal GACR transport is never an agent identity.
- The correction does not increase Chronicle freshness and does not invent client liveness.
- Historical defective records are preserved; the invalid session is closed/superseded and terminal sessions are removed from future correlation candidates.
- Candidate Template version: `2.8.36`.
- Final acceptance requires post-merge proof of no new internal-transport session.
- `P12-S6` remains preserved and unexecuted.

## 2026-10-02 — GACR R5-A correction live-proven; generic core complete

- PR #113 candidate Governance CI `36942282684`: PASS.
- PR #113 merged at `bfb7b6fb81244f18f1b2c8c1ea82526af0dc2d62`.
- Post-merge Governance CI `36942347934`: PASS.
- Post-merge GACR run `36942347872`: PASS.
- No new session or Beacon was created by the internal GACR workflow after the fix.
- Runtime contains two preserved session records but only one active session: `session-68c97d4bb1ef71c86444de12`.
- Historical transport session `session-cb22a4ed0d9e29eba5383f5d` is `CLOSED`, superseded by the canonical conversation session, with reconciliation decision `CPD-055`.
- Correlator live projection excludes the terminal session from candidates.
- Derived projection persistence advanced main to `173297fee3c6ac55a03ca3787558b063cb85b668`.
- The historical defective Beacon remains preserved as evidence; no history was deleted or rewritten.
- Generic GACR R1-R5 is complete and ready for provider-host adapters wherever the host can invoke the emitter.
- Current ChatGPT host still does not expose a persistent client-emitter process to this assistant; this is an external integration boundary, not silently promoted to PASS.
- Stop before `P12-S6` and await explicit owner OK.

## 2026-10-02 — GACR R6 provider-host issue bridge candidate

- Owner requested automatic, real, proved provider-host integration from the current ChatGPT conversation.
- Existing R5 limitation was revalidated: this host can write GitHub issues/comments but does not expose a persistent local client process or direct repository-dispatch action.
- Dedicated source ingress issue `#115` created.
- R6 uses GitHub `issue_comment` as a governed host transport into the existing GACR runtime.
- New adapter: `scripts/gacr_host_issue_ingress.py`.
- Supported events: attach, heartbeat, action trace, explicit interruption.
- The adapter auto-resolves/attaches sessions, renews liveness, records safe telemetry, refreshes correlation/forensics and uses comment ID as idempotency evidence.
- No transcript body, cookie, token, authorization header, password, private key or secret value is accepted.
- No execution authority is granted.
- Candidate branch: `governance/gacr-r6-host-issue-bridge`.
- Required acceptance sequence: candidate CI → merge → real ChatGPT comment event → persisted state proof → no-duplication proof → final attestation.
- `P12-S6` remains parked and unexecuted.

## 2026-10-02 — GACR R6 first live proof and R6-A rerun hardening

First live ChatGPT-host event:
- issue #115 comment `5943461065`;
- source event: `issue_comment`;
- state commit: `69ccfc90c14f2fa02a264c765e31c49c64951635`;
- existing session resolved automatically: `session-68c97d4bb1ef71c86444de12`;
- lease renewed to `2026-10-02T01:16:41+00:00`;
- ACTION_TRACE Beacon: `GACR-B-ddc264dcf74e`;
- correlation: `EXACT`;
- forensics: current session active, action in-flight, exact-head reobservation still required before replay;
- total historical sessions remained 2 with exactly 1 active session.

Before final attestation, rerun semantics were hardened: issue-comment reruns now reconcile to latest default-branch state before idempotency evaluation. Candidate R6-A branch: `governance/gacr-r6a-rerun-idempotence`.

## 2026-10-02 — GACR R6-B portability correction

Before final R6 attestation, a portability review found that Template source issue `#115` must not be copied into generated/adopted clients.

R6-B therefore:
- removes `#115` from generic workflow conditions;
- keeps `#115` only in Template source config;
- clears `issue_number` during governed client upgrade;
- uses the canonical inbox title as the client fallback discriminator;
- preserves source/client runtime-memory isolation;
- adds regression tests for number mode, title fallback mode and upgrader non-distribution.

Candidate version: `2.8.39`. No target client repository was mutated to prove this source-only correction.

## 2026-10-02 — GACR R6-C provider attribution correction

Post-R6-B live heartbeat `5943559595` succeeded and persisted through commit `371509ac60d1a63c0be7cee8ec8620346210d824`, but semantic review found the canonical session still carried historical `provider = other`.

R6-C adds safe late provider enrichment:
- stable connection remains the identity anchor;
- explicit host provider may upgrade generic `other` to `chatgpt`;
- native ChatGPT conversation ID remains unavailable/not invented;
- same session ID must be reused;
- conflicting specific provider fails closed.

Candidate version: `2.8.40`. Final acceptance requires a live event from this conversation after merge.

## 2026-10-02 — GACR R6 provider-host integration complete

Final result:

- dedicated source ingress: issue #115;
- schema: `gacr-host-event/v1`;
- transport: GitHub `issue_comment`;
- source/client issue identity separation: PASS;
- host event safety validation: PASS;
- action START/COMPLETED traces: PASS live;
- heartbeat renewal: PASS live;
- exact session resolution without supplied session ID: PASS live;
- provider attribution `other → chatgpt` on the same session: PASS live;
- native provider conversation ID: remains unavailable and not invented;
- Correlator: EXACT;
- Forensics: PASS;
- duplicate active session: NONE;
- exact workflow rerun: PASS with `GACR_HOST_EVENT_ALREADY_PROCESSED` and `GACR_NO_STATE_CHANGE`;
- continuous background daemon heartbeat: not claimed because the ChatGPT host does not expose a persistent process.

Canonical active session: `session-68c97d4bb1ef71c86444de12`.

R6 is therefore integrated for event-driven host activity. The broader programme remains stopped before `P12-S6` until explicit owner approval.

## 2026-10-02 — GACR origin realignment plan accepted and durably registered

- Owner clarified that GACR evolved usefully but not fully in the original intended direction.
- Existing R1-R6 capabilities and evidence are preserved; no destructive rollback is authorized.
- New canonical planning authority: `docs/control-plane/GACR_ORIGIN_REALIGNMENT.md`.
- New machine-readable projection: `.governance/control-plane-state/gacr-origin-realignment.json`.
- Decision: `CPD-057`.
- Primary invariant restored: instrumentable repository use itself should make an agent/conversation observable to GACR; explicit self-registration/event emission must not remain the conceptual prerequisite.
- Mandatory sequence of 24 operations is recorded in exact order, including original-intent reconstruction, intent/current/gap matrix, tests-before-code, Presence Fabric, controlled-access instrumentation, liveness/progress separation, unbound-activity reconciliation, real fresh-agent proof, controlled stall, second-agent exact-HEAD takeover and continuation.
- Ultimate completion test is explicit: a fresh agent is asked to work on the repo without being told to register with GACR; GACR must observe it through an instrumented path, track safe activity, detect loss of fresh evidence, and enable another governed agent to continue the same work after exact-HEAD reconciliation.
- Silent provider capabilities that are not exposed remain `UNAVAILABLE`; no provider ID, crash cause or continuous liveness is invented.
- Global Control Plane unique task remains `P12-S6_CLOSE_CREATE_NEW_REPOSITORY_CASE`; this change records future GACR work and does not execute it.


## 2026-10-02 — GACR original intent and historical stop point canonized

- Added `docs/control-plane/GACR_ORIGINAL_INTENT.md` as authority `CP-AGENT-RELAY-001-ORIGIN`.
- Added `docs/control-plane/GACR_PROGRAM.md` as the autonomous GACR programme authority.
- Added machine projections `gacr-original-intent.json` and `gacr-program.json`.
- Preserved the historical baseline, the two external limits, BEACON/WATCH/CORRELATOR/DISPATCHER target, full Connection Envelope, connection fingerprint, correlation-confidence model, Dispatcher compatibility/activation flow, optional Bridge boundary and Agent Context philosophy.
- Historical version `2.8.30` is retained only as remembered context for that stop point; later R1-R6 implementation is the current preserved baseline.
- Clarified that GACR and the global Control Plane programme are separate workstreams. There is no `P12-S6 → GACR` dependency.
- GACR own next action is `GACR-OR-01_REOBSERVE_AND_ATTEST_R6_BASELINE`.
- Owner sequencing remains: finish GACR first; return to the global programme only after explicit owner OK.


## 2026-10-02 — GACR multi-agent implementation supervision observations

Scope: GACR only. The global Control Plane programme remains parked; `P12-S6`, CASE 1 and GMC are not advanced by this observation record.

Live supervision baseline reobserved before this entry:

- canonical `main`: `652d7e3385c7efa05ee7b085adf22e4574485db5`;
- Worker A branch: `governance/gacr-presence-envelope-runtime`;
- Worker B branch: `governance/gacr-liveness-progress-context`;
- Worker C branch: `governance/gacr-correlator-dispatcher-integration`.

Observed worker state:

- Worker A / PR #128 — Presence / ConnectionEnvelope / fingerprint. Latest observed head during this supervision slice: `0cac225524d1cdd0f405cf9371fb3d1a8d2a74f6`.
- Worker B / PR #127 — Liveness / Progress / Session Context. Latest observed head: `84ee4998f4ec8d38db89a3c1c974505523d404cd`.
- Worker C / PR #129 — Correlator / Dispatcher / Takeover integration. Latest observed head: `ead8953c3b1d5706b79675a983905e166d855d73`.

Supervisor findings preserved under existing CPD-012 / CPD-019 rules:

1. Three independently launched conversations became distinguishable at repository level through three dedicated branches, but the current GACR state did not automatically materialize three distinct governed GACR sessions at first repository touch.
2. Repository-level observability is therefore currently stronger than session-level GACR observability for these live workers; this is direct evidence for the Presence-First corrective tranche rather than a theoretical gap.
3. Branch creation is evidence of presence/entry but is not evidence of useful progress. During live observation, one worker initially had a branch identical to `main` while others already had commits; later it began advancing. This validates the required separation `PRESENCE != LIVENESS != PROGRESS`.
4. A shared GitHub actor/account can represent multiple concurrent agent conversations. `github_actor` alone is therefore insufficient as a unique session key; correlation must combine independent safe signals and fail closed on ambiguity.
5. All three workers modified `.github/workflows/governance-ci.yml`. This is a real shared integration surface and must be reconciled deliberately before merge; no worker may silently overwrite another worker's CI registration.
6. The worker-specific acceptance-test files are separate:
   - A: `scripts/test_gacr_presence_first.py`;
   - B: `scripts/test_gacr_liveness_progress_context.py`;
   - C: `scripts/test_gacr_correlator_dispatcher_takeover_integration.py`.
7. The first CI failures were acceptance-contract failures, while the previously existing GACR regression tests observed in those runs remained green up to the new gates. These RED results are implementation evidence, not by themselves regressions:
   - A exposed missing Presence/ConnectionEnvelope CLI/runtime inputs;
   - B exposed missing `session_signal_projection`;
   - C exposed a missing/unsatisfied Correlator integration API contract.
8. Git commits and PRs provide durable result evidence but are insufficient to answer whether an agent is currently thinking, testing, blocked, idle or gone between repository events. GACR therefore still requires automatic activity/liveness/progress/checkpoint evidence on supported instrumentable surfaces.
9. The current live three-worker run must not be used as the ultimate Presence-First acceptance proof because the workers were explicitly launched with GACR-aware implementation prompts and predefined branches. The final Steps 13–24 proof still requires fresh agents not instructed to register with GACR.

Integration supervision rule for this tranche:

- do not merge workers merely in completion order;
- stabilize/reconcile Worker A contracts first where B/C depend on Presence/Envelope primitives;
- reobserve current `main` and each PR head before every merge;
- reconcile `governance-ci.yml` changes explicitly;
- preserve all R1–R6 tests and exact-HEAD/claim/collision-domain safety;
- do not declare GACR complete until the fresh-agent → stall → second-agent exact-HEAD takeover → continuation live scenario passes.

These observations are durable supervision evidence, not new mutation authority and not a replacement for GACR sessions, claims, checkpoints, handoffs or canonical programme authorities.


## 2026-10-02 — GACR Presence/Liveness/Dispatcher integration complete through Step 12

- Parallel implementation workers A/B/C completed their local tranches with GREEN CI.
- Worker A PR #128 was integrated first; post-merge Governance CI and Relay PASS.
- Worker B could not be merged directly after A because shared files conflicted; a controlled A+B integration branch preserved both Presence and Liveness/Progress contracts. PR #132 merged GREEN.
- Worker C was then reconciled over canonical A+B. The merged runtime preserves B session-signal/Agent Context/UNBOUND semantics while adding C categorical correlation, standby compatibility, takeover package and Dispatcher behavior. PR #133 merged GREEN.
- Final post-merge Governance CI `36961935777`: PASS.
- Final post-merge GACR Relay `36961935794`: PASS.
- Runtime-state commit `a27893681c8e90e5d225dae23d15df5cc4b93d29` proves live Presence-First enrichment of the canonical current session.
- Session now includes `GACR_PRESENCE_FIRST`, `connection_fingerprint`, `presence_anchor`, `surface_class`, `connection_method`, `github_actor` and full provenance-bearing `ConnectionEnvelope`.
- Existing provider conversation reference remains `UNAVAILABLE`; it was not invented.
- Old parallel PRs #127 and #129 plus intermediate PR #131 were closed as superseded after canonical integration.
- The earlier PR-comment soft-wake experiment proved that a durable GitHub signal does not itself wake a browser/provider conversation; addressable wake still requires a session-bound client/provider/bridge channel.
- GACR origin realignment is not complete. Steps 4–12 are closed; Step 13 fresh-agent live proof is next.
- `P12-S6`, CASE 1 and GMC remain unchanged.
- Relational projection for the detailed GACR step ledger remains `PENDING_PROJECTION_NO_DEDICATED_GACR_REALIGNMENT_STEP_TABLE`.


## 2026-10-02 — GACR Step 13 external-worker live probe

- Added bounded workflow `.github/workflows/repository-presence-probe.yml` via PR #135; Governance CI `36963534713 = PASS`.
- Opened neutral issue #136. The issue text contained no GACR registration, Beacon, heartbeat, host-ingress or telemetry instruction.
- Workflow run `36963595777` executed as a distinct external repository worker and returned:
  - `status = CREATE`;
  - `presence_event = PRESENCE_FIRST_TOUCH`;
  - `binding.state = BOUND`;
  - `binding.reason = NEW_STABLE_ANCHOR`;
  - session `session-c7c1466e55afb2e4da868944`;
  - fingerprint `GACR-FP1-30eed83027210717042c4ffad8ea222e977ec71d075c5ec2f439eff3907d6d9a`;
  - `surface_class = CONTROLLED_INSTRUMENTABLE`;
  - provider conversation reference remained `UNAVAILABLE`.
- Canonical Correlator bound the new Beacon to the new session at `EXACT` using session/client/connection anchors.
- Older ambiguous activity remained `AMBIGUOUS / UNBOUND_ACTIVITY`; it was not arbitrarily reassigned.
- At 06:14:34 Europe/Paris the fresh worker had recent liveness evidence but no qualifying progress evidence. By the canonical signal rules this is `LIVENESS=ACTIVE / PROGRESS=NO_RECENT_PROGRESS_EVIDENCE`.
- A separate negative live observation also succeeded: repeated direct GitHub connector reads from the current ChatGPT conversation did not change `last_seen_at`. These reads remain provider/connector-side silent to repository code unless the connector/client/gateway emits Presence metadata.
- Therefore Step 13 is PARTIAL, not closed:
  - external instrumented worker first-touch = PASS;
  - direct connector-read automatic observation = NOT AVAILABLE on the current surface;
  - genuinely fresh provider conversation/agent = NOT YET EXECUTED.
- Ultimate live acceptance remains NOT_PASSED.
- No P12-S6 / CASE 1 / GMC progression occurred.


## 2026-10-02 — GSCC / GSE / GSCC↔GACR integration complete

- Three parallel implementation tranches completed from the same GACR Step 13 partial baseline:
  - GSCC Core: branch `governance/gscc-core-v1`, final head `b4cfec2e5dabfd28ab557e4ef740f0c44fa44457`, PR #140, Governance CI `36966935952 = PASS`, local GSCC suite 24/24 PASS.
  - GSE Session State Engine: branch `governance/gse-session-state-engine-v1`, final head `c1913ddbcc9563f9ba532bf2a550a510524b9587`, PR #138, Governance CI `36966912324 = PASS`, local GSE suite 24/24 PASS.
  - GSCC↔GACR Control: branch `governance/gscc-gacr-bidirectional-control-v1`, final head `185f00795811093432eccfa7e1b1cec0312377f1`, PR #139, Governance CI `36966930385 = PASS`.
- Frozen cross-layer contract was verified before integration: 16 EVENTS, 13 COMMANDS and 13 DELIVERY_STATES are identical across GSCC Core, GSE and GSCC↔GACR control.
- Integration order executed:
  - PR #140 merged first at `a07e8211ff182b17948b6001bd8622a7252069ca`; post-merge Governance CI `36967370835 = PASS`; Relay `36967370863 = PASS`.
  - GSE was then integrated over canonical GSCC Core via PR #141, merge `1d8215f527b38ac4aead40d699387b23b2021499`; post-merge Governance CI `36967581229 = PASS`; Relay `36967581241 = PASS`.
  - Final GSCC↔GACR control integration was performed via PR #142.
- Two cross-layer defects were found before final merge and corrected on the integration branch:
  1. control harness expected `send(command)` while the real GSCC `SessionEndpoint` receives commands through `receive_commands()`; added a minimal `GSCCSessionControlEndpoint` adaptation seam without transferring GACR authority.
  2. GSE refreshed liveness on every `CHALLENGE_RESPONSE`; corrected so `replay=true` / `fresh_liveness=false` never refreshes `last_liveness_evidence_at`.
- Governance CI now gates all four layers together:
  - GSCC Core;
  - GSE SessionTwin;
  - GSCC↔GACR control harness;
  - controlled GSCC→GSE→GACR E2E.
- First combined E2E run `36968072978` failed because the test command used a stale fixed timestamp and was correctly expired by the live GSCC endpoint. The fixture was corrected to runtime-relative time; no runtime semantics were weakened.
- Corrected candidate run `36968154806 = PASS`, including the controlled E2E.
- PR #142 merged at `feea5dfc9055c96c9a589889d96708b3fba353e2`.
- Final post-merge Governance CI `36968203836 = PASS`; final Relay `36968203882 = PASS`.
- Worker PR #138 is now integrated/superseded; worker PR #139 is closed as superseded. PR #140 was merged canonically.
- `COMMAND DELIVERY != MUTATION AUTHORITY` remains preserved. No control message transfers claims or bypasses exact-HEAD reconciliation.
- Step 13B has not been executed. It is now the next authorized gate: real fresh provider agent/conversation on the integrated GSCC/GSE/GACR path.
- Ultimate live acceptance remains `NOT_PASSED`.
- `P12-S6`, CASE 1 and GMC remain unchanged.


## 2026-10-02 — GACR G4 / AUDIT-01 closed

- Baseline before G4: `a35d0aa85f7ddbf3181e5c1a198efc585ed05ab9`.
- PR #147 canonicalized the shared GSCC protocol authority.
- `scripts/gscc_gacr/contract.py` no longer redeclares shared EVENTS / COMMANDS / DELIVERY_STATES / terminal states / secretless restrictions.
- Shared control aliases now reference canonical objects from `scripts/gscc/protocol.py`.
- Historical control restrictions were preserved by strengthening the canonical GSCC secretless policy.
- First candidate CI exposed missing canonical rejection of `browser_session`; the fix was made in canonical GSCC policy, not through a local control exception.
- Corrected candidate Governance CI `36970569867 = PASS`.
- PR #147 merge: `cbc87ef5f31c6c8190be3add44f446fdc316b6f2`.
- Post-merge Governance CI `36970611124 = PASS`.
- Post-merge GACR Relay `36970611145 = PASS`.
- Post-auto-attach main observed at `b7d0e3540747af21db9705fc333baeca1d74adef`.
- `GACR-INT-AUDIT-01 = CLOSED_PASS`.
- `GACR-INT-AUDIT-02` remains `OPEN_BLOCKING_PRE_13B`; Step 13B remains blocked.
- Next remediation: G5 control-response → canonical GSE projection proof.


## 2026-10-02 — GACR G5 / AUDIT-02 closed; G6 reconciliation

- G5 branch baseline: `0d3b259105f57e523e257134c7d939ecc63de34b`.
- PR #149 added `scripts/gscc_gacr/gse_projection.py` as the single additive control-response → canonical GSE mapper.
- The real `GSCCSessionControlEndpoint` now executes STATUS / PROGRESS / CONTEXT / CHECKPOINT through `SessionEndpoint.receive_commands()`.
- Mapping semantics:
  - STATUS → CONTEXT_UPDATE;
  - CONTEXT → CONTEXT_UPDATE;
  - CHECKPOINT → CHECKPOINT without `checkpoint_advanced`;
  - PROGRESS → PROGRESS with `qualifying_progress=false`.
- Unit and extended E2E prove no false liveness or progress is manufactured.
- Candidate Governance CI `36971442096 = PASS`.
- PR #149 merge: `d831c29ea0943bd5015a757e303187fa505b5f1c`.
- Post-merge Governance CI `36971501671 = PASS`.
- Post-merge GACR Relay `36971501664 = PASS`.
- Post-auto-attach main observed at `114c5397966a5c6ad7d8770298abd698929ecf8f`.
- `GACR-INT-AUDIT-02 = CLOSED_PASS`.
- Both blocking audit findings are now closed.
- Step 13B remains `BLOCKED_PENDING_G6_REAUTHORIZATION` until G6 reconciliation itself passes.


## 2026-10-02 — GACR G6 reconciliation PASS / Step 13B reauthorized

- G4 / AUDIT-01 = CLOSED_PASS.
- G5 / AUDIT-02 = CLOSED_PASS.
- Current main reobserved before G6: `114c5397966a5c6ad7d8770298abd698929ecf8f`.
- G6 reconciliation PR #150 first full Governance CI `36971795607 = PASS`.
- All GSCC/GSE/control/projection/E2E/historical GACR/governance gates pass together.
- GACR authority boundaries remain unchanged.
- Step 13B transitions from `BLOCKED_PENDING_G6_REAUTHORIZATION` to `NEXT_AUTHORIZED`.
- Fresh provider agent remains NOT_EXECUTED; ultimate live acceptance remains NOT_PASSED.


## 2026-10-02 — GACR G6 final closure

- G6 first reconciliation CI with Step 13B still blocked: `36971795607 = PASS`.
- G6 final reauthorized candidate CI: `36972111008 = PASS`.
- PR #150 merge: `d0f66130f135f4aa7363c3e88c1e3f44ced9a828`.
- Post-merge Governance CI: `36972158291 = PASS`.
- Post-merge GACR Relay: `36972158234 = PASS`.
- Exact post-auto-attach main: `ab3fd3848878e93f929cbd3d89c9d15be43537a7`.
- G4 / AUDIT-01 = CLOSED_PASS.
- G5 / AUDIT-02 = CLOSED_PASS.
- G6 = PASS_CLOSED.
- Step 13B = NEXT_AUTHORIZED / NOT_EXECUTED.
- Fresh-provider acceptance has not yet occurred; ultimate live acceptance remains NOT_PASSED.

## 2026-10-02 — GSCC admission/access gate inserted before live function exposure

- Owner clarified the repository-entry invariant: GitHub identity/authentication alone is insufficient for governed agent access.
- A governed agent must first submit a safe admission dossier, have it validated and stored with provenance, receive only `PREAUTHORIZED`, complete a mandatory qualification path, and receive an Access Grant before becoming eligible for governed function exposure.
- Canonical specification added at `docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md`.
- The design explicitly separates identity, admission, preauthorization, access authorization, function exposure and mutation authority.
- Existing GSCC, GSE, GACR and the PR #153/#156 Function Exposure Gate remain authoritative and are extended rather than duplicated.
- The Access Grant is not mutation authority; each function still requires the existing exact-HEAD, function-contract, authority, live-preflight and pre-call revalidation controls.
- Safe admission metadata only: provider-private values remain supplied-only/UNAVAILABLE; secrets, cookies, tokens, prompts, transcripts, raw tool payloads and private reasoning remain prohibited.
- Decision recorded as `CPD-061`.
- Current main was reobserved immediately before this documentation change at `016442b00dab345ffa79fc2bf8026a9f96b73339`.
- Work branch: `governance/gscc-admission-access-gate`.
- No runtime, workflow, repository-access enforcement or function gate implementation has been changed in this documentation tranche.
- Step 13B / the real live function-exposure request is now chronologically blocked behind tests-first implementation and attestation of this stronger admission/access invariant.
- The global programme remains unchanged: `P12-S6` is neither executed nor advanced.

## 2026-10-02 — Existing GSCC arrival gateway explicitly preserved under the admission layer

- Reobserved canonical `main = 6a25ba59688c92c89a21872e312b195e9cc36b8b`.
- Confirmed the repository already has `.github/workflows/gscc-observable-arrival.yml` and `scripts/gscc_observable_arrival.py`.
- Existing route is preserved: observable/controlled arrival → GSCC SessionEndpoint → SESSION_ATTACH → GACR client-emitter compatibility → `gacr_auto-attach` → Presence/canonical session.
- Owner clarification: do not delete, replace or bypass this existing arrival layer.
- New admission/access logic is an additive higher-order prerequisite for governed access/function exposure.
- On controlled client/provider surfaces, admission precedes use of the existing controlled-arrival path.
- On GitHub-event-visible surfaces, the existing arrival observer may fire first because the event already exists; that observation remains presence evidence only and grants no preauthorization, access, invocation or mutation authority.
- The existing GSCC Function Exposure Gate is also preserved downstream.
- No runtime implementation was changed by this clarification; PR #158 remains documentation/governance only.

## 2026-10-02 — GSCC Admission / Access Gate implemented tests-first on PR #159

- Owner authorized live implementation after CPD-061 / `GSCC_ADMISSION_ACCESS_GATE.md` became canonical.
- Work branch created from observed `main = 89fb28e498fde0b4df597da75499990f4deb5269`: `governance/gscc-admission-runtime`.
- Existing Observable Arrival Gateway, SessionEndpoint, GSE, GACR and canonical Function Exposure Gate were preserved.
- Admission core RED: Governance CI `37000902994 = FAILURE` on missing `gscc.admission`.
- Admission core GREEN: `37001048628 = SUCCESS`.
- Access Grant RED: `37001183473 = FAILURE` on missing qualification API.
- Access Grant GREEN: `37001289277 = SUCCESS`.
- Function gate RED: `37001452126 = FAILURE` because the existing evaluator did not accept an Access Grant.
- Function gate corrected GREEN: `37001737386 = SUCCESS`.
- Admission workflow RED: `37001911592 = FAILURE` because the admission workflow did not yet exist.
- Final candidate Governance CI `37002023347 = SUCCESS`.
- Final candidate GSCC Observable Arrival Gateway `37002023374 = SUCCESS`.
- Final candidate GSCC Function Exposure Gate `37002023423 = SUCCESS`.
- New read-only workflow: `.github/workflows/gscc-admission-gate.yml` with `contents: read`.
- Admission may return only `PREAUTHORIZED`; qualification may issue a bounded `gscc-access-grant/v1`.
- The existing Function Exposure Gate now rejects absent/expired/mismatched grants before function/authority evaluation.
- Access Grant still grants neither invocation authority nor mutation authority.
- Status remains candidate until merge + post-merge attestation. No real provider admission request has yet passed on canonical `main`.
- Step 13B remains NOT_EXECUTED. Global `P12-S6` remains untouched.

## 2026-10-02 — GSCC Admission / Access Gate post-merge integration attested

- PR #159 merged at `56c48aafbe00a50b47ad2189f4ab3645b937c82f`.
- Post-merge Governance CI `37002783058 = SUCCESS`.
- Post-merge GSCC Observable Arrival Gateway `37002783052 = SUCCESS`.
- Post-merge GSCC Function Exposure Gate `37002783152 = SUCCESS`.
- Post-merge GSCC Function Route Selftest `37002783428 = SUCCESS`.
- Post-merge GACR Relay push `37002783111 = SUCCESS`.
- Post-merge GACR Relay repository-dispatch `37002796444 = SUCCESS`.
- Admission/access gate is now integrated and regression-green on canonical main.
- Existing Observable Arrival Gateway and existing Function Exposure Gate remain preserved.
- No real provider admission request has yet been executed through the new gate.
- Unique GACR next action becomes `GSCC_ADMISSION_GATE_RUN_LIVE_REQUEST`.
- Step 13B remains NOT_EXECUTED and ultimate live acceptance remains NOT_PASSED.
- Global `P12-S6` remains untouched.


### 2026-10-02 — PR #163 GSCC canonical admission harvester

- Owner-authorized branch: `governance/gscc-admission-harvester`.
- Initial exact main at branch creation: `3b0f72c7c6425d6e634e14f96cc927a5a5b670c4`.
- Tests-first RED: commit `c7ade40b7af024bb3a31d1b563e631ffceda40ab`; Governance CI `37003462162 = FAILURE` only on the intentionally missing harvester.
- Runtime adds GitHub repository/branch GET observation, exact HEAD, GACR canonical session resolution, ConnectionEnvelope reuse, governance digests, task/claim reconciliation, structured unavailable evidence, provenance matrix and `gscc_entry_request`.
- Concurrent main work added provider issue ingress on issue #161 and canonical admission→GACR session binding. #163 was reconciled additively rather than overwriting it.
- Exact-main reconciliation merge: `9fd0f8435da7da517659034b3fa05207e9470ae9`.
- Caller-provided qualification evidence is deprecated and ignored by the canonical workflow; `evaluate_access_grant` requires a canonical harvester bundle and matching integrity digest.
- Reconciled PR validation: Governance CI `37005672855 = SUCCESS`; Function Exposure `37005672883 = SUCCESS`; Observable Arrival `37005673101 = SUCCESS`.
- Candidate final functional head before this documentation-only attestation: `eb92101a2f6fa5d855380d4f2ac9820552f19b53`.
- No merge performed by this agent. Step 13B remains NOT_EXECUTED. P12-S6 / CASE 1 / GMC untouched.


### 2026-10-02 — PR #163 Q8→Q12 controlled qualification closure

- Candidate branch: `governance/gscc-admission-harvester`.
- Added existing-bridge control challenge transport over issue #115; canonical evidence remains in `gacr-dispatches.json`.
- Added correlated host `command_ack` / `challenge_response` handling with expiry, nonce, correlation and replay checks.
- Added on-demand GSE admission projection via the existing Session State Engine; no parallel GSE store.
- Added default-DENY source-only admission Access Policy, bounded to `READ_ONLY_DISCOVERY_AUTHORITY`; no operational or mutation authority is granted.
- Added full controlled Q12 proof from AdmissionEnvelope to validated bounded Access Grant.
- Q12 Governance CI `37015716729 = SUCCESS`.
- Latest exact-main state alignment merge `72a9b8d0872a59eed0a45e8d8e78223a072d055b`.
- Final aligned candidate: Governance CI `37016097906 = SUCCESS`; Function Exposure `37016097994 = SUCCESS`; Observable Arrival `37016098117 = SUCCESS`.
- PR remains unmerged. Real provider issue-control challenge/ACK/response on canonical main remains NOT_EXECUTED.
- No P12-S6 / CASE 1 / GMC advancement. No production/server mutation.

## 2026-10-05 — PR #157 entry-context prototype superseded by canonical Admission/Q1→Q12 path

- Open draft PR #157 (`governance/gscc-entry-context-gate`) was re-audited against current canonical main rather than merged from its stale 2026-10-02 head.
- The branch is hundreds of commits behind current main and predates CPD-061 / CPD-062, PR #159 Admission Runtime, PR #163 canonical Harvester/Q1→Q12, and PRs #164→#175 live hardening.
- The useful invariant from #157 is preserved, but its separate `gscc-entry-context/v1` receipt/gate is no longer a valid authority surface because CPD-061 requires one additive admission/access path and one canonical Function Exposure authority.
- Field reconciliation:
  - `provider` → required `AdmissionEnvelope.agent.provider`;
  - `agent_identity` → optional/supplied-only under Admission; provider-private identity must remain unavailable when not exposed;
  - `client_instance_id` → required `AdmissionEnvelope.client.client_instance_id`;
  - `connection_ref`, `connection_method`, `surface_class` → required canonical connection facts;
  - old `capabilities` declaration → split into `requested_capabilities` + `control_capabilities`, then independently tested at Q8/Q9;
  - old `function_surface` declaration → intentionally NOT an authority; canonical MCP capability snapshot + Access Grant + per-function GSCC exposure validation decide the actual governed surface;
  - repository / owner / name / default branch / requested ref / exact HEAD → independently harvested/reobserved from GitHub by the canonical Harvester instead of trusting host input;
  - old `ENTRY_CONTEXT_OPEN` → superseded by `PREAUTHORIZED → Q1…Q12 → bounded Access Grant → existing Function Exposure Gate`.
- Therefore #157 must be closed as **SUPERSEDED**, not rebased or merged.
- No runtime code is removed by this attestation because #157 never reached canonical main.
- Global P12-S6 remains untouched.
- GACR ultimate live acceptance remains NOT_PASSED; this cleanup only removes a stale parallel-entry prototype from the active work surface.

