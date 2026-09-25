# PROJECT PROFILES — Technical intent without false facts

## Principle

The governance core remains generic. A project profile describes a planned or discovered technical direction; it does not assert implementation, deployment or production state.

```text
PLANNED != IMPLEMENTED != TESTED != CONFIGURED != ACTIVATED != DEPLOYED != PRODUCTION_VERIFIED
```

## Profiles

- `generic`: no technical assumption.
- `application`: application project, stack defined by discovery/decision.
- `chainsolutions-fullstack-web`: Chainsolutions default candidate for web applications.
- `data-platform`: data-oriented project, architecture defined by discovery/decision.

### Chainsolutions full-stack web candidate

The default candidate plans:

- backend runtime: Node.js;
- backend framework: project-defined;
- frontend: Next.js + TypeScript;
- database: PostgreSQL.

These values remain `PLANNED` until project discovery or an explicit decision activates the profile.

## Activation

A newly instantiated repository starts with `selection_status = DISCOVERY_REQUIRED`. An agent must inspect the repository and durable decisions before selecting a profile. Existing evidence always outranks the candidate default.
