# ARCHITECTURE

## Current architecture

TO_INITIALIZE

## Required sections

- system context;
- components/modules;
- data stores;
- external integrations;
- trust boundaries;
- deployment topology;
- observability;
- rollback / recovery;
- architectural constraints.

Architecture changes that invalidate a previous decision require an ADR.


## Technical intent versus observed architecture

Before architecture is discovered, `.governance/project-profile.json` may contain a planned candidate such as `chainsolutions-fullstack-web` (Node.js, Next.js + TypeScript, PostgreSQL).

A candidate is not the current architecture. Discovery must decide whether to select, adapt or reject it.

## Deployment topology discovery

Use `.governance/infrastructure-intent.json` to represent the deployment lifecycle, including an unknown server, missing directory or unprovisioned database.

No server, domain, directory or deployment state becomes factual without observation or an explicit provisioning result.
