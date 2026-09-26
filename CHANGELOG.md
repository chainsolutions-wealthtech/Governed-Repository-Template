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

