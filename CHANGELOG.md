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
