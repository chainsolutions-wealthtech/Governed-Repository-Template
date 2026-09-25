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
