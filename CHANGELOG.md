# CHANGELOG

## Unreleased

### Added

- Governed Repository baseline.
- Loop Engineering.
- Persistent project memory.
- Machine-readable governance profile.
- Governance validation CI.

## Governance Automation V2

### Added

- automatic repository bootstrap with fail-closed template guard;
- bootstrap receipt and attestation state;
- canonical-memory current pointer with canonical/work revisions;
- exact-HEAD reconciliation guard;
- repository-local multi-agent sessions;
- dependency-safe and collision-safe deterministic work dispatch;
- structured checkpoints and handoffs;
- information intake with monotone cursor;
- contradiction `HOLD_FOR_REVIEW`;
- source-CI simulation of automatic initialization and agent dispatch.

### Compatibility

All V1 governance files and manual initialization remain supported. No runtime MCP, server lock, production authority or project-specific Regulatory state is introduced.


## Governance Automation V2.1.0

### Added

- machine-readable project profiles with a non-binding `chainsolutions-fullstack-web` candidate;
- planned Node.js, Next.js + TypeScript and PostgreSQL intent without claiming implementation;
- infrastructure lifecycle that represents unknown or missing server/domain/directory/database resources;
- preferred `DIRECT_MCP` server access with governed `SSH` fallback;
- explicit prohibition on repository-stored infrastructure credentials;
- connection intent classification and deterministic routing;
- fail-closed mutable dispatch for `UNKNOWN`, context intake and information intake;
- regression tests for bootstrap capability intent and session intent routing.

### Compatibility

The V2.0.2 zero-touch governance baseline remains structurally compatible. The generic core still does not force a framework or provision infrastructure. Existing projects can keep project-specific architecture and infrastructure decisions; V2.1 records planned/discovered intent separately.


## Governance Automation V2.2.0

### Added

- mandatory macro entry-action questionnaire on agent connection;
- repository creation routing with owner-scope and authority gates;
- additive existing-repository adoption plan/apply helper;
- current/target architecture mapping route;
- isolated lab branch/PR evolution route;
- normal governed-work continuation route;
- organization, personal-account and explicitly authorized owner scopes;
- CI tests for entry routing, adoption preservation and personal-account scope.

### Compatibility

Entry action is separate from connection intent and authority. Adoption starts read-only and preserves existing project files. Mapping is read-only by default. Lab evolution cannot dispatch mutable work from the canonical branch. V2.1 zero-touch bootstrap remains the base behavior.


## Governance Automation V2.3.0

### Added

- central Governed Repository control plane hosted by `chainsolutions-wealthtech/Governed-Repository-Template`;
- GitHub Issue persisted request state, outside template content;
- direct machine entry through `repository_dispatch: governed_request_start`;
- one-question-or-action-at-a-time governed request state machine;
- chronological preparation plans for create/adopt/map/lab/continue workflows;
- plan approval gate before preparatory execution;
- structured evidence validation for every preparatory action;
- explicit `HANDOFF_READY` package before normal target work;
- source-control-plane versus generated/adopted target-client role separation;
- automatic removal of source-only control-plane workflow/issue form from generated clients.

### Compatibility

V2.3 is additive over V2.2. Repository-local governance, zero-touch bootstrap, connection intent, entry actions, adoption, mapping, lab evolution and personal/organization scopes remain intact. The control-plane issue workflow has no cross-repository write permission and cannot bypass target authority.


## Governance Automation V2.3.2

### Fixed

- corrected `CREATE_NEW_REPOSITORY` sequence to owner → repository name → visibility → creation;
- removed the irrelevant connection-intent question before repository creation;
- added explicit `private` / `public` visibility selection;
- mapped human choice `Patricked` to canonical GitHub owner `Patricked-code`.

### Added

- fail-closed GitHub REST `generate from template` executor;
- per-creator GitHub App user-access credential mapping;
- automatic PREP-001 execution from the control-plane workflow;
- `/governed-execute` retry path after credential/authority remediation;
- executor preflight for authenticated principal, private-template visibility, target absence and organization membership;
- CI self-test covering organization, Wealthtechinnovations and Patricked-code creation paths.

### Security

Creator tokens remain outside Git. The standard workflow `GITHUB_TOKEN` cannot create target repositories. Missing or insufficient creator authority leaves PREP-001 pending and never fabricates PASS evidence.

## Governance Automation V2.6.3

### Added

- central control-plane provisioning of the direct MCP Actions credential into a governed target repository when its local first-agent state is exactly at the MCP credential gate;
- target-owner GitHub App token narrowed to repository Contents, Issues and Secrets permissions required by the machine command path;
- exact repository, issue and HEAD verification before provisioning;
- target secret metadata attestation after provisioning without reading or exposing the secret value;
- regression test for unsupported credential requirements, command-line secret leakage and provisioning workflow wiring.

### Security

The MCP credential remains stored only as a GitHub Actions secret. Its value is never written to Git, issue state, comments, handoff evidence or logs. Provisioning fails closed if the central secret is absent, the GitHub App lacks repository Secrets write permission, the target HEAD moved, the local state moved, or the credential gate requests an unsupported secret.

### Compatibility

V2.6.3 preserves the V2.6.2 direct-MCP token contract and the V2.6 OIDC ephemeral SSH fallback. It automates distribution of the existing direct MCP credential; it does not grant MCP write authority, bypass project registration, or widen the SSH read-only boundary.

## Governance Automation V2.6.4

### Fixed

- credential provisioning failures now emit stable non-secret failure codes;
- the central control plane persists the failure code and exact target/HEAD context into the Governed Request issue;
- machine local commands are not dispatched after a failed credential provisioning attempt.

### Safety

Failure evidence never includes credential values. A failed provisioning attempt leaves the target local-entry state unchanged and provides a deterministic remediation reason before retry.

## Governance Automation V2.6.5

### Fixed

- classifies failures that occur before the MCP source-secret check: target repository/ref lookup, local-entry issue lookup, state decoding and credential-gate contract validation;
- preserves stable non-secret failure evidence so the central request identifies the exact remediation class instead of a generic Actions failure.

### Compatibility

No authentication contract changes. V2.6.5 is diagnostic and fail-closed over V2.6.4.

## Governance Automation V2.6.6

### Fixed

- governed target upgrades now preserve the existing `.governance/local-entry/state.json` projection instead of resetting first-agent completion fields;
- open `[Governed Local Entry]` issues can migrate their `expected_head_sha` to the newly created upgrade commit when the prior expected HEAD reaches the pre-upgrade HEAD through a verified chain containing only governed local-setup upgrade commits;
- issue state revision advances monotonically and an audit comment records the HEAD migration without modifying business answers or baseline content;
- upgrade GitHub App tokens request target Issues write permission only because migration writes the governed issue state and audit comment.

### Safety

An open local-entry issue is not migrated across unrelated project commits. If the comparison chain contains any non-governance mutation, its expected HEAD remains unchanged and later mutable commands continue to fail closed.

## Governance Automation V2.6.7

### Changed

- `BOTH` now means direct MCP preferred plus governed GitHub OIDC SSH fallback for initial read-only discovery;
- absence of the central direct MCP credential no longer blocks `BOTH` discovery when the SSH fallback is available;
- the direct path is preserved as `UNAVAILABLE_CREDENTIAL` evidence and the combined discovery is recorded as `PARTIAL` / degraded rather than a false `PASS`;
- `DIRECT_MCP_TOKEN` continues to require `GOVERNED_MCP_AUTH_TOKEN`.

### Safety

The SSH fallback remains read-only and cannot grant MCP scoped-write authority. Project registration, explicit mutation approval and MCP write-tool gates are unchanged. No change is made to `Patricked-code/MCP` by this release.

## Governance Automation V2.6.8

### Fixed

- MCP discovery failures are persisted into the governed local-entry state with a stable non-secret failure code and retryable evidence;
- HTTP 403 from the repository-SSH certificate broker is classified as `SSH_CERTIFICATE_BROKER_FORBIDDEN`;
- `/local-execute` can retry read-only discovery while the exact local state remains at `MCP_DISCOVERY`;
- human and machine execute paths now use the same current credential-requirement logic.

### Safety

`HEAD_MOVED` still stops before any discovery-state mutation. Discovery retry does not widen project or runtime authority, and failed external discovery never advances to domain binding.

## Governance Automation V2.6.9

### Fixed

- `BOTH` now opportunistically provisions the central `GOVERNED_MCP_AUTH_TOKEN` into the target repository whenever a governed local command is dispatched and the central secret is available;
- sessions that already advanced beyond the historical credential gate can still gain the preferred direct MCP path without restart;
- missing central direct credential remains non-blocking for `BOTH` and preserves SSH OIDC read-only fallback.

### Safety

The token value is never read back or exposed. Exact-HEAD and target issue guards still apply before secret provisioning. Direct MCP provisioning does not grant scoped-write authority.

## Governance Automation V2.6.10

### Fixed

- degraded `BOTH` discovery is automatically refreshed before setup approval when the preferred direct MCP credential becomes available later;
- answers already supplied after the initial discovery are preserved across the refresh;
- prior discovery evidence is retained in a bounded history instead of being silently overwritten;
- the rebuilt setup package uses the refreshed evidence.

### Safety

The refresh is read-only, exact-HEAD governed, and does not widen MCP write authority. Fresh non-degraded evidence does not trigger repeated refresh loops.

## Governance Automation V2.7.0 — Self-Governed Control Plane

### Added

- source-only human continuity authorities under `docs/control-plane/`:
  `CURRENT_STATE.md`, `SUIVI.md`, `NEXT_ACTION.md`, `DECISIONS_LOG.md`, `TASKS.md`, and `PROGRAM.md`;
- source-only machine projections under `.governance/control-plane-state/`:
  `current.json`, `checkpoint.json`, `handoff.json`, and `tasks.json`;
- explicit source-entry reading order for agents working on the template/control plane itself;
- validation that source current state, checkpoint, handoff, and unique executable task remain coherent.

### Changed

- source-only paths may now be directories as well as files;
- client initialization removes source-only directories recursively;
- source/control-plane history is explicitly separated from the generic root project-state templates distributed to new repositories;
- GitHub issues remain orchestration/evidence surfaces rather than the durable source-project authority.

### Safety / non-regression

- root template files with placeholders remain unchanged as distributed client templates;
- bootstrap self-test proves `docs/control-plane/` and `.governance/control-plane-state/` do not survive client initialization;
- `Patricked-code/MCP` remains outside this workstream's implementation scope.

## Control-plane continuity — CASE 1 replay ledger

### Added

- a source-only phase-by-phase replay authority for `CREATE_NEW_REPOSITORY`;
- a machine-readable replay projection with current phase, dependencies, historical pilot choices, and return semantics;
- explicit owner-comment handling for clarification, choice changes, post-baseline changes, generic framework defects, and MCP-side dependencies;
- governance validation requiring exactly one active CASE 1 replay phase and next-action consistency.

### Purpose

A later agent can replay CASE 1 in detail without depending on chat history, and owner comments can safely return execution to the earliest affected checkpoint without erasing historical evidence.

## Governance Automation V2.8.0 — Canonical Relational Memory

### Added

- source-only relational schema for reusable framework cases, phases, dependencies, modes, questions/options and activities;
- execution/history tables for repositories, runs, answers, decisions, events and evidence;
- continuity tables for checkpoints, handoffs, owner feedback, external intakes and artifacts;
- CASE 1 seed data and current pilot checkpoint;
- registration of the four structuring cases plus `CONTINUE_GOVERNED_WORK` as a post-case mode;
- deterministic SQLite materialization/validation in Governance CI.

### Architecture

Git-versioned SQL migrations, JSON catalogues and governed source authorities remain canonical. A mutable SQLite database binary is materialized for validation/queryability but is not committed as the source of truth.

The logical model is designed for later PostgreSQL-backed use by an admin web application after all cases and parcours have been validated.

### Safety / non-regression

- the database directory is source-only and is removed from newly initialized or adopted client repositories;
- owner feedback and decision changes preserve history instead of destructive overwrite;
- database work does not change the active CASE 1 checkpoint;
- `Patricked-code/MCP` remains outside implementation scope.

## Governance Automation V2.8.1 — Machine Local Entry Start

### Fixed

- the documented `governed_local_start` machine path is now exposed through the central control plane;
- the central GitHub App dispatches a new local entry under an exact-HEAD guard;
- the target creates and initializes the local-entry issue/state in the same dispatch rather than depending on a second GitHub issue event;
- subsequent entries after `first_agent_completed=true` can now be proven through the machine path as `NORMAL_GOVERNED_ENTRY`.

### Safety

Human issue/comment authorization remains unchanged. Machine start requires a GitHub App bot sender, the canonical central source repository, and an exact target HEAD.

## Governance Automation V2.8.2 — Client Policy Upgrade Synchronization

### Fixed

- governed local-entry upgrades now project the current control-plane policy into target clients;
- the projected policy is forced to `GOVERNED_TARGET_CLIENT` and bound to the target repository;
- current source-only path contracts stay aligned with `validate_governance.py` without copying source-only memory into clients.

### Why

V2.8.1 exposed that an upgraded historical client could receive the new manifest/validator while retaining an older control-plane policy. This created a validation contradiction even though the source-only directories were correctly absent.

## Governance Automation V2.8.3 — Portable Bootstrap Self-Test

### Fixed

- bootstrap consistency self-tests now reset `.governance/project-profile.json` to generic discovery state before simulation;
- bootstrap consistency self-tests now reset `.governance/infrastructure-intent.json` to generic discovery state before simulation;
- an already-baselined client can therefore execute the same bootstrap self-test without its real project choices contaminating the synthetic template fixture.

### Safety

This changes only the test fixture. It does not reset or mutate the real instantiated repository project profile or infrastructure intent.

## Control-plane continuity — C1-12 live-state reconciliation and agent ledger

### Added
- durable human and machine agent-activity ledgers;
- relational `agent_sessions` and `agent_activity_events` tables via migration `002_agent_activity.sql`;
- explicit C1-12 discovered sub-task chain from live pilot evidence;
- exact blocker tracking for the remaining Gouvern connection-intent self-test failure.

### Reconciled
- template live version/head through V2.8.3;
- Gouvern live pilot head and CI blocker;
- V2.8.1–V2.8.3 generic fixes and their reasons;
- unique next action narrowed to `C1_12_F_DIAGNOSE_UNEXPECTED_WORK_ITEM`.

No CASE 1 phase was skipped and C1-13 remains locked.



## Control-plane memory — Canonical target architecture authority — CP-ARCH-001

### Added
- source-only `CANONICAL_ARCHITECTURE.md` target authority;
- machine projection with source provenance and imported-memory approval prohibition;
- canonical authority revision registry and append-oriented canonical memory events;
- complete runtime-seed materialization support for answers/events/evidence/handoffs/owner-feedback/artifacts;
- architecture hardening backlog and durable roadmap toward API/PostgreSQL/Admin UI.

### Preserved
- four structuring cases + `CONTINUE_GOVERNED_WORK` as post-case mode;
- source/client memory boundary;
- Git-versioned authorities as foundational source of truth;
- active CASE 1 phase and exact unique next action;
- MCP external governance boundary.

No CASE 1 execution gate is advanced by this memory enrichment.


## Control-plane routing — Two-stage automated agent purpose routing

### Added
- Stage 1 target choice: `WORK_ON_CONTROL_PLANE` vs `APPLY_GOVERNANCE_CASE`.
- Stage 2A work kinds: `CODE_IMPLEMENTATION`, `EXECUTE_EXISTING_TASK`, `ADD_OR_ENRICH_INFORMATION`.
- Stage 2B case choices limited to the four canonical structuring cases.
- RTE-001..RTE-013 backlog, machine queue projection and relational questionnaire fields.
- CPD-021 and owner-feedback/event projections.
- Canonical architecture revision `CP-ARCH-001-R2`.

### Automation boundary
Humans answer governed questions and give explicit approvals where required. Authorized Git/GitHub/CI/file operations are performed by the governed system; automation never bypasses authority or fail-closed gates.

The current runtime router is intentionally unchanged until implementation and regression tests complete. CASE 1 C1-12-F remains the unique executable task.


## Governance Automation V2.8.4 — Portable Connection-Intent Self-Test

### Fixed

- `scripts/test_connection_intent.py` no longer inherits real work-items, claims, sessions or canonical-memory state from an already-instantiated client executing the self-test;
- the test builds an explicit temporary template-source fixture before auto bootstrap;
- the fixture asserts exactly `WORK-INIT-001 DONE` and `WORK-DISCOVER-001 READY` before validating intent dispatch;
- a real project `WORK-PROJECT-001` can no longer contaminate the synthetic routing test.

### Product boundary

- `chainsolutions-wealthtech/Governed-Repository-Template` is the framework product and generic implementation target;
- repositories such as `Patricked-code/Gouvern` are external validation pilots only;
- generic defects discovered by pilots are fixed in the Template first and then revalidated on pilots.

### Safety

The correction changes only the copied temporary self-test fixture. It never rewrites or resets the real project work-items, sessions, claims or business state of an instantiated client.
