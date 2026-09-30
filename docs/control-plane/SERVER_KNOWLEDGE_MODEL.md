# SERVER KNOWLEDGE AND OPERATION RECIPES

Authority: `CP-SERVER-KNOWLEDGE-001`

The Control Plane must understand a server as a **managed platform**, not merely as a hostname.

It needs two complementary kinds of knowledge:

1. **Inventory** — what exists and how the server is organized.
2. **Operation recipes** — how to safely create, configure, verify and rollback the things a project may need.

This is still source-only planning knowledge. It does not execute server mutations.

## Complete server inventory target

For each logical server (currently S1 / S2), the knowledge model covers:

- identity, role, OS and control panel;
- web servers and reverse-proxy stack;
- firewall/network and port allocation model;
- DNS zones and DNS management model;
- TLS issuance, renewal and certificate inventory;
- domains, subdomains, aliases and vhosts;
- project/document-root/log/backup layout conventions;
- Docker / Compose / PM2 / systemd and language/runtime versions;
- listening services and allocated application ports;
- database engines, logical databases, roles and backup model;
- Git checkout, repository binding, build, deployment and rollback model;
- environment/secrets injection model;
- services, workers, cron/scheduled jobs and queues;
- healthchecks, logs, metrics, alerts and audit logs;
- backup, restore and recovery procedures;
- security/access/ownership/permission model;
- disk, memory, CPU and capacity headroom;
- project-to-server/domain/path/runtime/database/port/MCP mappings;
- current MCP read/write capability surfaces.

The objective is that an agent arriving later can understand **what exists, where a governed project belongs, and how the server expects applications to be organized**.

## Paths

The system may persist governed path templates and named project paths that are needed for deployment.

It does not persist an unbounded recursive filesystem dump.

Example distinction:

```text
OK:
project Ekyc → deployment path selected under governed S2 project layout

NOT OK:
store every path and file existing on S2
```

## Operation recipes

The initial catalogue includes recipes for:

- create a project directory;
- create a subdomain;
- create a new domain binding;
- allocate an application port;
- configure reverse proxy;
- provision TLS;
- create/bind a database;
- bind a repository to a server project;
- deploy an application;
- configure environment/secrets references;
- configure process/service;
- configure scheduled job;
- configure observability;
- configure backup/rollback;
- attest production.

Every recipe contains:

```text
required inventory
→ required capability
→ required authority
→ preflight
→ prepare
→ execute
→ verify
→ rollback
→ evidence
→ freshness refresh before execution
```

A recipe describes the operation but does not authorize it.

## Example — Ekyc on S2 with a subdomain

If the owner later chooses:

```text
production_server = S2
domain_posture = CREATE_NEW
domain_type = SUBDOMAIN
```

the Control Plane should already know which facts it needs from S2 and which operations follow:

```text
S2 inventory
→ available parent domains
→ choose parent
→ choose subdomain label
→ derive FQDN
→ determine project path convention
→ determine runtime
→ allocate port if needed
→ create vhost/subdomain
→ configure DNS
→ configure reverse proxy
→ provision TLS
→ bind repository
→ provision environment/secrets references
→ build/deploy
→ configure service
→ healthcheck
→ backup/rollback
→ production attestation
```

Before execution, current volatile facts are refreshed. Stable conventions are reused rather than rediscovered.

## Incremental continuation

This slice intentionally stops at knowledge and recipes.

Next small slices:

- `KBI-04C` — read-only S1/S2 inventory collector;
- `KBI-04D` — normalized persisted inventory with provenance/freshness;
- `KBI-04E` — map recipe requirements to actual MCP tools and identify only truly missing capabilities;
- `KBI-04F` — E2E dry-run: S2 + subdomain → complete deployment blueprint, no mutation;
- `KBI-04G` — later Loop Engineering binding under AuthorityEnvelope.

This preserves the current CASE 1 execution order.

## Identity and credential plane

Server operation recipes consume `CP-IDENTITY-SECRET-001`.

The server model knows what must be configured; the identity/secret model knows how the required credentials are obtained, created, injected, verified, rotated and revoked.

Examples include ephemeral SSH certificates, scoped service identities, application environment secrets, database credentials, DNS-provider credentials and TLS key material under the certificate manager.

No recipe may infer authority merely because a credential exists.
