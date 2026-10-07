# CONTROL PLANE PROGRAM

## Purpose

This file is the durable source-only program authority for development of `Governed-Repository-Template`.

It does not replace the generic entry-action policy distributed to clients.

## Active programme

`GOVERNANCE_MODEL_CATALOGUE / GMC-A / GMC-G01`

Previous macro case `CREATE_NEW_REPOSITORY` is closed under `CPD-073`.

Historical operational issue: `#12`.

## Canonical six-step completion program

### STEP 1 — MCP connectivity-choice contract completion
State: `DONE`

Exit proof:
- optional MCP linking contract tested;
- when MCP linking is enabled, transport choice remains owner-driven: `DIRECT_MCP_TOKEN`, `SSH`, or `BOTH`;
- direct MCP credential contract tested;
- SSH OIDC read-only path tested;
- `BOTH` tested as one valid combined mode, not as a mandatory mode;
- target upgrade path tested;
- external MCP gaps routed as intake rather than implemented here.

### STEP 2 — Resume Gouvern through MCP discovery
State: `DONE`

Exit proof:
- existing `LOCAL-000002` resumed without losing answers/history;
- DIRECT MCP evidence and SSH OIDC evidence preserved separately;
- final discovery PASS/non-degraded;
- no runtime/MCP write authority inferred.

### STEP 3 — Complete technical setup and APPLY_BASELINE
State: `DONE`

Exit proof:
- setup owner-approved;
- domain binding preserved as `UNRESOLVED` rather than invented;
- `STANDARD_GOVERNED_FLOW` selected;
- baseline commit `23975e0435e63fb45d7436d1f23ce8ce0a450a5f`;
- `LOCAL_HANDOFF_READY` persisted for first-agent bootstrap.

### STEP 4 — Prove subsequent NORMAL_GOVERNED_ENTRY on Gouvern
State: `DONE`

Goal:
- connect a subsequent agent after first-agent completion;
- prove the repository routes to `NORMAL_GOVERNED_ENTRY`, not back to `FIRST_AGENT_BOOTSTRAP`;
- preserve existing baseline/session/work authorities;
- prove no duplicate first-agent baseline is created.

Exit gate:
- live subsequent local-entry evidence;
- normal-entry handoff produced;
- no baseline reset;
- CI remains green.



### STEP 4 completion evidence

- exact pilot HEAD: `671774dfc8e8be8eac2b50d5fb8f0928591694b3`;
- machine-created local entry: `Patricked-code/Gouvern#4`;
- request: `LOCAL-000004`;
- mode: `NORMAL_GOVERNED_ENTRY`;
- final status: `LOCAL_HANDOFF_READY`;
- no baseline/session/work duplication;
- no pilot Git mutation during proof.

### STEP 5 — Fresh repository E2E proof from zero
State: `DONE`

Goal:
- create a second clean disposable repository from the current template;
- run the entire path from creation to handoff without relying on `Gouvern` migration history.

Required lifecycle adapts to the owner's choices:

`CREATE → BOOTSTRAP → FIRST_AGENT → PROJECT BASELINE → OPTIONAL MCP LINK → [DIRECT_MCP_TOKEN | SSH | BOTH when linked] → DISCOVERY when applicable → DOMAIN when applicable → SETUP → APPLY_BASELINE → HANDOFF → NORMAL ENTRY`.

If MCP linking is declined, the lifecycle must continue without inventing an MCP dependency.

Exit gate:
- uninterrupted governed lifecycle;
- no target-specific repair;
- all CI/attestations green.

#### Inserted corrective gate — C1-13-A

During the live second-fresh E2E on `Patricked-code/Ekyc`, read-only MCP discovery returned HTTP 404 after the owner supplied the MCP root URL. The generic state machine then offered only retry and could no longer correct the captured endpoint.

By anti-deviation rules 4 and 5:
- the fresh target is frozen;
- the defect is fixed in the Template first;
- PR #50 carries a RED→GREEN regression proof;
- after merge, the fix must be distributed through the governed client-update path;
- the E2E resumes from the affected MCP endpoint/discovery checkpoint with all previous answers preserved.

`P12-S5` remains IN_PROGRESS. STEP 6 remains blocked.

#### Inserted corrective gate — C1-13-B

After PR #50 merged and its governed client upgrade was applied to `Patricked-code/Ekyc`, client Governance CI exposed a second generic defect: the distributed local-entry self-test referenced source-only `.github/workflows/governed-control-plane.yml`.

By the same pilot-defect rule:
- the client stays frozen;
- the source-only workflow remains source-only and must not be added to clients;
- PR #51 adds a RED→GREEN portability regression test;
- the self-test now guards source-only assertions behind the `.template-source` marker;
- after merge the current Template surface must be redistributed through the official governed upgrader before C1-13 resumes.

`C1-13-A` and `C1-13-B` are DONE. `P12-S5` remains the active parent and STEP 6 remains blocked.

#### Inserted corrective gate — C1-13-C

After PR #51 merged and the current governance surface was redistributed to `Patricked-code/Ekyc`, target CI passed every portable client/local-entry test and then failed on Governance Model projection integrity because that test attempted to load source-only control-plane state.

The correct generic behavior is:
- Governance Model planning authority remains source-only;
- client repositories do not receive the source control-plane state;
- the integrity self-test explicitly skips when `.template-source` is absent;
- Template source continues to run the full integrity validation;
- the fresh E2E remains frozen until PR #52 is merged and redistributed through the governed upgrader.

`C1-13-A`, `C1-13-B` and `C1-13-C` are DONE. `P12-S5` remains the active parent and STEP 6 remains blocked.

#### Inserted corrective gate — C1-13-D

After PR #52 merged and was redistributed to `Patricked-code/Ekyc`, the target retained the stale Governance Model integrity test because the client upgrader did not include that script in its portable static surface.

The generic correction is:
- keep Governance Model source state source-only;
- distribute the portable integrity test itself;
- add the corrected test to upgrader `static_paths`;
- require a fresh governed client upgrade and fully green target CI before MCP discovery resumes.

`C1-13-A` through `C1-13-D` are DONE. `P12-S5` remains the active parent and STEP 6 remains blocked.

#### External dependency gate — C1-13-E

After the full client portability chain was corrected and `Patricked-code/Ekyc` reached an all-green Governance CI, the preserved MCP discovery retry failed because the public TLS certificate for `mcp.wealthtechinnovations.com` is expired.

This is not a Template defect:
- direct MCP is blocked at TLS verification;
- SSH fallback cannot bootstrap because the GitHub-OIDC SSH certificate broker is HTTPS on the same host;
- TLS verification must not be bypassed;
- MCP is observation/intake-only from this workstream.

External intake `Patricked-code/MCP#201` records the blocker. C1-13 resumes only after MCP-side governed remediation and fresh TLS evidence.

### STEP 5 completion evidence — Ekyc second fresh E2E

- Fresh repository: `Patricked-code/Ekyc`.
- Approved baseline materialization: `3e889a2bdac78312ebcc7e31d1388ead65c9fceb`.
- First-agent session: `LOCAL-000001-S1`.
- First project work item: `WORK-PROJECT-001` remains `READY`.
- Subsequent normal-entry issue: `Ekyc#2`, request `LOCAL-000002`.
- Normal-entry mode: `NORMAL_GOVERNED_ENTRY`.
- Final state: `LOCAL_HANDOFF_READY`, revision 6.
- Normal-entry proof preserved Ekyc HEAD and created no target Git mutation.
- Generic defects discovered during replay were corrected in the Template first; no target-specific repair was used.
- No product work and no S1/domain/DNS/Plesk/TLS mutation was executed.
- Exit gate: `PASS`.

### STEP 6 — Close CREATE_NEW_REPOSITORY and release next macro case
State: `DONE`

Goal:
- reconcile documentation, manifest/version, tests and durable evidence;
- ensure all external MCP needs are represented only as intakes;
- close CASE 1 only after STEP 5 passes;
- release the next macro case according to the framework roadmap.

### STEP 6 completion evidence

- CASE 1 checkpoint: `CREATE_NEW_REPOSITORY_CASE_COMPLETE`.
- `P12-S6 = DONE`.
- `C1-14 = DONE`.
- historical parent `C1-13-I-B` reconciled through children `A..G`.
- relational run `CASE1-PILOT-GOUVERN = DONE` with no active phase.
- `CREATE_NEW_REPOSITORY` catalogue status = `DONE`.
- external MCP items remain intake/history only.
- no executable CASE 1 task remains orphaned.
- `GMC-01 / GMC-G01` released as the next work package.
- GMC remains planning/knowledge extraction only until a later governed step authorizes implementation.

## Anti-deviation rules

1. Execute STEP 1 → 2 → 3 → 4 → 5 → 6 only.
2. Never compress two chronological gates into one state.
3. A later step cannot become IN_PROGRESS before the current step satisfies its exit gate.
4. Generic defects found in a pilot are fixed in the template first, then propagated.
5. Never patch only the pilot to hide a framework defect.
6. MCP linkage and transport are choices, not framework mandates; the state machine must follow the selected path without forcing `BOTH`.
7. `Patricked-code/MCP` is READ / OBSERVE / INTAKE only from this workstream.
8. Every mutable action requires exact-HEAD reconciliation and verifiable CI.
9. Historical answers/sessions/checkpoints are migrated or reconciled, never silently discarded.
10. Keep one unique next action.

## Continuity contract

```text
Conversation / Agent N
  -> observations
  -> decisions
  -> implementation
  -> evidence
  -> checkpoint
  -> versioned source-only authorities
  -> Conversation / Agent N+1
  -> reobserve HEAD
  -> read source-only authorities
  -> reconcile
  -> resume unique next action
```

Conversation memory is supplemental context only.

## Source-of-truth relationship

- `docs/control-plane/CURRENT_STATE.md`: human current state.
- `docs/control-plane/TASKS.md`: durable active work queue.
- `docs/control-plane/NEXT_ACTION.md`: unique resumable action.
- `docs/control-plane/DECISIONS_LOG.md`: durable decisions.
- `docs/control-plane/SUIVI.md`: chronological history.
- `docs/control-plane/CASE1_REPLAY_LEDGER.md`: detailed phase-by-phase replay authority for CASE 1, including owner feedback/return points.
- `.governance/control-plane-state/*.json`: deterministic machine projections.
- Git commits/CI: execution evidence.
- GitHub issues: orchestration and external interaction evidence.


## Canonical architecture authority

The program evolves against:

`docs/control-plane/CANONICAL_ARCHITECTURE.md` — authority `CP-ARCH-001`.

This target authority defines the durable platform shape and roadmap. It does not replace chronological case gates or the current unique next action. New defects/intakes/owner changes must be inserted into the existing program with dependency analysis rather than starting a parallel program.

## Queued programme — Governance Model Catalogue and Cross-Case Industrialization

Authority: `CP-GOVMODEL-001` — `docs/control-plane/GOVERNANCE_MODEL_CATALOGUE.md`.

State: `ACTIVE_GMC_G01_PLANNING_ONLY`.

Dependency `P12-S6 CLOSE_CREATE_NEW_REPOSITORY_CASE`: `VALIDATED_EXIT`.

This programme formalizes the central governance model before the remaining cases are industrialized. It does not change the current unique executable task.

Chronology:

```text
P12-S4 NORMAL ENTRY
→ P12-S5 SECOND FRESH E2E
→ P12-S6 CLOSE CASE 1
→ GMC-A MODEL BOUNDARY
→ GMC-B INVENTORY/NORMALIZATION
→ GMC-C STATES/CONTROLS/EVIDENCE
→ GMC-D IMPLEMENTATION/DEPENDENCY/RELATIONAL CATALOGUE
→ GMC-E APPLICABILITY + SEMANTIC COMPARISON
→ GMC-F CONTROL-PLANE + FOUR-CASE REBIND
→ GMC-G CROSS-CASE VALIDATION / GOVERNANCE MODEL 1.0.0
→ POSTGRES / API / ADMIN UI
```

The existing `ARCH-*`, `IDN-*` and `RTE-*` workstreams are absorbed as dependencies/sub-workstreams where applicable, not duplicated.

### P12-S5 owner-feedback corrective gate — C1-13-E-A

The second fresh E2E remains inside STEP 5. Owner feedback established that MCP configuration answers prepare the project model but do not authorize network execution.

Before resuming the previously observed TLS-dependent discovery, the Template must add and validate an explicit read-only discovery-plan approval gate, then distribute that generic correction to Ekyc through the governed upgrader.

This is an additive correction to the existing programme. STEP 6 and the dependency-bound GMC programme remain unchanged and blocked behind completion of STEP 5.

### P12-S5 MCP capability-memory enrichment

CASE 1 live discovery has now produced enough evidence to refine the reusable control plane without changing the macro chronology.

- `C1-13-G` — generic signed SSH profile recovery; blocking before Ekyc can continue.
- `C1-13-H` — persistent source-only MCP capability snapshot and case/tool/operation planning map; additive to the existing Loop Engineering.

The capability snapshot is not a second execution engine and does not authorize writes. It lets the Template reuse a dated last-known MCP image, refresh it through read-only discovery when freshness/need requires it, and prepare existing work-items with the correct tools, dependencies and authority gates.

Historical note: at that point, P12-S6 and GMC remained downstream of P12-S5. This dependency is now satisfied by CPD-073.
