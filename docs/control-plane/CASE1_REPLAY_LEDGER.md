# CASE 1 REPLAY LEDGER — CREATE_NEW_REPOSITORY

> Source-only replay authority for the `CREATE_NEW_REPOSITORY` macro case.
> This ledger exists so a later conversation or agent can replay CASE 1 chronologically, stop at any gate, incorporate owner feedback, and resume from the correct checkpoint without reconstructing history from chat.

## Replay principles

1. Reobserve exact `main` HEAD before any mutable action.
2. Read this ledger with `PROGRAM.md`, `CURRENT_STATE.md`, `TASKS.md`, `NEXT_ACTION.md`, `DECISIONS_LOG.md` and machine checkpoint/handoff state.
3. Owner choices are inputs, not hard-coded framework assumptions.
4. MCP linking is optional. If enabled, transport may be `DIRECT_MCP_TOKEN`, `SSH`, or `BOTH`.
5. A later phase never starts until the current gate is satisfied.
6. Generic defects found in a pilot are fixed in the template first, tested, merged, then propagated.
7. `Patricked-code/MCP` is READ / OBSERVE / INTAKE only from this framework workstream.
8. Every owner comment that changes scope, sequence, choice, or acceptance criteria must be persisted in `DECISIONS_LOG.md` and, when it affects execution, in the machine replay state before continuing.
9. Returning to an earlier phase does not erase later evidence. Mark later phases `NEEDS_REVALIDATION` and resume from the selected checkpoint.
10. Never silently restart a first-agent bootstrap or discard historical answers.

## CASE 1 purpose

Create a new governed repository, initialize governance automatically, conduct the first-agent baseline/setup, produce a governed handoff, then prove subsequent normal entry and finally repeat the entire scenario on a second clean repository.

The framework must adapt to the owner's answers rather than force one architecture.

---

## PHASE C1-00 — Entry action and repository creation request

### Objective
Identify that the owner wants `CREATE_NEW_REPOSITORY` and collect only the creation facts needed before generating the repository.

### Canonical choice sequence
1. entry action = `CREATE_NEW_REPOSITORY`;
2. creation target owner/account;
3. repository name;
4. visibility;
5. authority/preflight;
6. create from template.

### Historical correction
V2.3.2 corrected the earlier order so irrelevant connection-intent questions are not asked before repository creation.

### Replay gate
Do not create the target until owner/name/visibility/authority are all explicit and target absence is verified.

### Owner feedback hook
The owner may change account/organization, name, or visibility before creation. If changed after creation, treat it as a new governed mutation/migration request, not a silent rewrite.

### Evidence
- CHANGELOG V2.3.2.
- `scripts/control_plane_create_repository.py`.
- governed request/control-plane issue state.

### Checkpoint
`REPOSITORY_CREATED_FROM_TEMPLATE`.

---

## PHASE C1-01 — Automatic bootstrap of the generated repository

### Objective
Convert the generated template copy into an instantiated governed target client.

### Required behavior
- remove `.template-source`;
- initialize repository identity and canonical branch;
- remove source-only control-plane surfaces;
- create bootstrap receipt/state;
- validate governance;
- preserve generic client templates only.

### Historical hardening
V2.7.0 added source-only control-plane memory and proved it does not leak into initialized clients.

### Replay gate
Bootstrap CI/attestation must PASS before first-agent setup.

### Owner feedback hook
No business decision should be required here unless repository identity/ownership facts contradict observed GitHub state.

### Evidence
- Governance Auto Bootstrap.
- `scripts/auto_bootstrap.py`.
- `scripts/finalize_bootstrap.py`.
- `scripts/test_bootstrap_consistency.py`.
- V2.7.0 client non-leak proof.

### Checkpoint
`GOVERNANCE_INITIALIZED_BASELINE_REQUIRED`.

---

## PHASE C1-02 — First-agent identity and business baseline

### Objective
The first agent identifies itself and learns the project before any final baseline write.

### Questions
- agent identity;
- provider;
- connection intent;
- project mission;
- in-scope / out-of-scope;
- project profile;
- architecture status;
- architecture notes;
- infrastructure status;
- known external systems;
- constraints;
- first work objective.

### Pilot answers — Gouvern
The pilot became a web application project for African OPCVM static data/documents with progressive official-source cataloguing. Daily NAV/performance/trading functions were outside the initial baseline.

### Replay gate
Owner explicitly approves the proposed business baseline.

### Owner feedback hook
This is a major intervention point. Any owner correction must update the proposed baseline before approval. Do not write project authorities until approval.

### Checkpoint
`BASELINE_APPROVED`.

---

## PHASE C1-03 — Decide whether to perform technical setup now

### Choice
`setup_repository_now = true | false`.

### If false
Materialize only the approved business baseline and hand off with technical setup deferred.

### If true
Continue technical questionnaire.

### Owner feedback hook
The owner may defer setup without losing the approved business baseline.

### Checkpoint
`TECHNICAL_SETUP_SELECTED` or `BASELINE_ONLY_PATH`.

---

## PHASE C1-04 — Optional MCP linkage

### Choice
`link_mcp_server = true | false`.

### If false
No MCP credential, discovery, SSH, domain or MCP registration requirement may be invented. Continue to workflow/setup questions that remain applicable.

### If true
Proceed to transport selection.

### Historical clarification
The historical `Gouvern` pilot chose MCP linkage, but MCP is not mandatory for CASE 1.

### Owner feedback hook
This is an explicit owner choice. Persist it. Do not infer it from presence of credentials or infrastructure.

### Checkpoint
`MCP_LINK_CHOICE_RECORDED`.

---

## PHASE C1-05 — MCP transport choice when linkage is enabled

### Allowed choices
- `DIRECT_MCP_TOKEN`;
- `SSH`;
- `BOTH`.

### Adaptive behavior

#### DIRECT_MCP_TOKEN
- `GOVERNED_MCP_AUTH_TOKEN` mandatory;
- direct discovery only;
- fail closed if credential unavailable.

#### SSH
- no persistent repository SSH private key;
- GitHub OIDC ephemeral certificate;
- read-only force-command gateway;
- SSH discovery only.

#### BOTH
- direct MCP preferred when central token exists;
- SSH OIDC provides independent/fallback read-only evidence;
- if direct token is unavailable, SSH-only discovery may continue as `PARTIAL/degraded`;
- if direct token later becomes available, stale degraded evidence must refresh before setup approval.

### Historical evolution
- V2.6.3 automatic direct MCP secret provisioning.
- V2.6.4 stable safe provisioning failure evidence.
- V2.6.5 earlier preflight failure classification.
- V2.6.6 preservation/migration of active local-entry HEAD state across governed upgrades.
- V2.6.7 `BOTH` SSH fallback when direct credential absent.
- V2.6.8 persisted retryable MCP discovery failure evidence.
- V2.6.9 opportunistic direct credential provisioning for `BOTH`.
- V2.6.10 refresh stale degraded `BOTH` evidence before approval.

### Pilot path — Gouvern
Transport selected: `BOTH`.

### Owner feedback hook
Changing transport after evidence was collected requires discovery revalidation. Preserve prior evidence in history; do not overwrite silently.

### Checkpoint
`MCP_TRANSPORT_SELECTED`.

---

## PHASE C1-06 — MCP endpoint / SSH profile / discovery scope / domain strategy / runtime policy

### When applicable
Only if MCP linkage is enabled.

### Inputs
- public MCP endpoint;
- non-secret SSH profile for SSH/BOTH;
- discovery scope;
- domain strategy;
- initial runtime mutation policy.

### Required safety
- no token in issue/state;
- no persistent SSH private key;
- no arbitrary shell;
- initial discovery read-only;
- write tools remain disabled until project registration and explicit authority.

### Pilot path — Gouvern
- discovery scope: full governed mapping;
- domain strategy: discover existing then propose;
- runtime mutation policy: explicit approval for scoped write.

### Owner feedback hook
The owner may narrow discovery or choose no domain yet. A broader runtime-write policy may not bypass MCP registration/authorization invariants.

### Checkpoint
`MCP_DISCOVERY_CONFIGURATION_READY`.

---

## PHASE C1-07 — Credential provisioning and discovery execution

### Direct credential control-plane model
Central source secret:
`GOVERNED_MCP_AUTH_TOKEN`.

The control plane writes the encrypted Actions secret into the target through the GitHub App when the chosen path uses direct MCP. The secret value is never committed, commented, logged, or read back.

### Pilot incidents and fixes
1. Central token originally missing → precise failure `CONTROL_PLANE_MCP_AUTH_TOKEN_MISSING`.
2. Historical issue expected HEAD became stale after upgrades → V2.6.6 introduced governed local-entry HEAD migration.
3. SSH broker initially returned HTTP 403 → external intake `Patricked-code/MCP#192`; no MCP code changed by this workstream.
4. Discovery failures originally existed only in Actions logs → V2.6.8 persisted stable retryable evidence.
5. After token was configured, V2.6.9 provisioned it opportunistically.
6. V2.6.10 refreshed stale `BOTH` evidence.

### Pilot final evidence
- DIRECT MCP: PASS;
- SSH OIDC: PASS;
- overall discovery: PASS / non-degraded;
- mutation authority: not granted.

### Replay gate
Required discovery path(s) must produce usable current evidence appropriate to the selected transport.

### Owner feedback hook
If the owner changes transport/scope/domain strategy, invalidate only the affected evidence and replay from the corresponding checkpoint.

### Checkpoint
`MCP_DISCOVERY_VALID`.

---

## PHASE C1-08 — Domain binding choice when applicable

### Choices
- bind observed existing domain;
- request a new domain after approval;
- leave unresolved.

### Pilot choice
`{"mode":"UNRESOLVED"}`.

### Rule
Never invent a domain.

### Owner feedback hook
The owner can return here later. A new domain request is a separate explicit mutation gate.

### Checkpoint
`DOMAIN_BINDING_RECORDED`.

---

## PHASE C1-09 — Workflow model selection

### Current choices
- `STANDARD_GOVERNED_FLOW`;
- project-specific governed model where supported.

### Pilot choice
`STANDARD_GOVERNED_FLOW`.

### Owner feedback hook
Changing the workflow model before setup approval is allowed. After baseline materialization it requires a governed update, not silent mutation.

### Checkpoint
`WORKFLOW_MODEL_SELECTED`.

---

## PHASE C1-10 — Setup approval

### Objective
Present the complete technical plan and rights matrix before materialization.

### Owner approval covers
- selected setup path;
- MCP choice/transport when applicable;
- current discovery evidence;
- domain choice when applicable;
- workflow model;
- Git rights;
- forbidden operations;
- runtime-write limitations.

### Pilot
Owner explicitly approved the setup.

### Replay gate
No `APPLY_BASELINE` before explicit approval.

### Owner feedback hook
This is the second major intervention point. Any correction returns to the relevant prior choice while preserving already-valid answers/evidence.

### Checkpoint
`SETUP_APPROVED`.

---

## PHASE C1-11 — APPLY_BASELINE transaction

### Objective
Materialize approved business/setup state into versioned project authorities.

### Expected outputs
- `PROJECT_CONTEXT.md`;
- `STATUS.md`;
- `SUIVI.md`;
- `TODO.md`;
- `NEXT_ACTION.md`;
- `HANDOFF.md`;
- architecture/acceptance documents;
- machine memory/session/work projections;
- MCP/access/infrastructure bindings when applicable.

### Safety
- exact-HEAD guard;
- governance validation before/after write;
- no hidden reset of historical state;
- first-agent session/work item created once.

### Pilot evidence
Baseline commit:
`23975e0435e63fb45d7436d1f23ce8ce0a450a5f`.

First governed session:
`LOCAL-000002-S1`.

Local-entry state:
`LOCAL_HANDOFF_READY`.

### Checkpoint
`FIRST_AGENT_BASELINE_MATERIALIZED`.

---

## PHASE C1-12 — Subsequent normal governed entry proof

### Current status
`IN_PROGRESS`.

### Objective
Prove a later agent does not repeat the first-agent bootstrap.

### Required live proof
- fresh local governed entry;
- mode = `NORMAL_GOVERNED_ENTRY`;
- existing baseline/session/work authorities preserved;
- no duplicate first-agent baseline;
- normal-entry handoff emitted;
- CI remains green.

### Owner feedback hook
The owner may choose local action:
- `CONTINUE_GOVERNED_WORK`;
- `MAP_EXISTING_PROJECT`;
- `LAB_EVOLUTION`.

For this CASE 1 proof, choose an action that demonstrates normal entry without beginning a different macro-case completion program prematurely.

### Live discoveries during C1-12

1. `Gouvern#3` created for the subsequent-agent proof.
2. Human issue-start path failed closed on actor authorization and advanced no governed state.
3. V2.8.1 introduced exact-HEAD machine local-entry start.
4. Upgraded historical clients required current control-plane-policy synchronization → V2.8.2.
5. Portable bootstrap tests had to isolate synthetic fixtures from real instantiated project choices → V2.8.3.
6. Remaining discovered defect: connection-intent self-test still assumes a work-item shape incompatible with the instantiated/normal-entry client state.
7. Current blocker is `INTENT_SELFTEST_FAILED: unexpected work item` on Gouvern CI run `36262734626`.
8. Required next pattern remains: fix generic template first → CI → governed upgrade → client CI → resume `Gouvern#3`.

### Agent-work requirement

Every agent intervention during this phase must record:
- agent/session identity when known;
- observed HEAD;
- task/sub-task claimed;
- actions taken;
- files/PRs/issues touched;
- evidence/result;
- defects discovered;
- remarks/proposals;
- next action;
- whether later evidence needs revalidation.

### Checkpoint
`NORMAL_GOVERNED_ENTRY_PROVEN`.

---

## PHASE C1-13 — Second fresh repository E2E

### Status
`PENDING_C1_12`.

### Objective
Create a new disposable repository from the current template and replay CASE 1 from zero without relying on migration history from `Gouvern`.

### Adaptive path
`CREATE → BOOTSTRAP → FIRST_AGENT → BUSINESS BASELINE → SETUP NOW? → MCP LINK? → [DIRECT | SSH | BOTH if linked] → DISCOVERY/DOMAIN when applicable → WORKFLOW → SETUP APPROVAL → APPLY_BASELINE → FIRST HANDOFF → NORMAL ENTRY`.

### Important
The owner may choose different answers from the historical pilot. The framework must adapt and still complete coherently.

### Exit gate
- uninterrupted lifecycle;
- no target-specific repair;
- all generic defects, if found, fixed in template first;
- all checks green;
- normal entry proven.

### Checkpoint
`SECOND_FRESH_E2E_PASS`.

---

## PHASE C1-14 — CASE 1 closure

### Objective
Close `CREATE_NEW_REPOSITORY` only after the fresh E2E passes.

### Required closure
- reconcile PROGRAM/CURRENT_STATE/TASKS/NEXT_ACTION/SUIVI/DECISIONS;
- record final template version and HEAD;
- record pilot and clean-E2E evidence;
- list external MCP intakes without implementing them;
- mark no orphan CASE 1 task;
- release next macro case according to roadmap.

### Checkpoint
`CREATE_NEW_REPOSITORY_CASE_COMPLETE`.

---

## Owner-comment / return protocol

At any phase, an owner comment is classified before execution:

### A — Clarification
No state rollback. Persist note if it changes interpretation.

### B — Choice change before its exit gate
Update the answer and resume within the same phase.

### C — Choice change after its exit gate but before baseline materialization
Return to the earliest affected phase, preserve evidence history, mark dependent later evidence `NEEDS_REVALIDATION`.

### D — Choice change after baseline materialization
Create a governed change/update path. Never rewrite historical baseline evidence as if it never existed.

### E — Generic framework defect
Pause pilot, fix template, CI, merge, governed-upgrade pilot, migrate active checkpoint, then resume.

### F — MCP-side dependency defect
Do not modify `Patricked-code/MCP`. Create/update an intake for its independently governed program and continue only along valid available paths.

## Replay completion rule

CASE 1 is replayable only when a new agent can determine, without this chat:
- what phase is active;
- what was already decided;
- what evidence exists;
- what owner choice led to the current branch;
- which later phases depend on it;
- what to invalidate if the owner changes that choice;
- the one unique next action.


#### Framework product boundary during pilot validation

CASE 1 pilots are evidence surfaces, not framework implementation targets.

```text
PILOT REVEALS DEFECT
→ DIAGNOSE GENERIC CAUSE
→ FIX Governed-Repository-Template
→ TEMPLATE CI / RELEASE
→ UPGRADE OR REPLAY PILOT
→ CAPTURE VALIDATION EVIDENCE
```

Current example: the `unexpected work item` failure was traced to `scripts/test_connection_intent.py` in the Template. V2.8.4 fixes the synthetic test fixture in the Template; no pilot business work-item is rewritten to satisfy the test.
