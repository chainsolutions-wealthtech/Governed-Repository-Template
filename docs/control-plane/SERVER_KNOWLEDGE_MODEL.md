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

Incremental slices:

- `KBI-04C` — read-only S1/S2 inventory collector implemented; live collection pending;
- `KBI-04D` — normalization, versioned persistence and relational projection implemented; live ingestion pending;
- `KBI-04E` — source-derived recipe/capability mapping implemented; live tool attestation remains operation-specific;
- `KBI-04F` — E2E dry-run: S2 + subdomain → complete deployment blueprint, no mutation;
- `KBI-04G` — later Loop Engineering binding under AuthorityEnvelope.

This preserves the current CASE 1 execution order.

### KBI-04C — collector implemented; live inventory pending

`scripts/control_plane_server_inventory_collector.py` intersects the existing
`CP-MCP-CAP-001` capability map and catalogue with a live MCP `tools/list`. It
calls only the fixed S1/S2 domain, Docker, PM2, disk and backup read tools that
remain generic and read-only. A missing or contradictory classification blocks
that tool. The transient JSON result reports only validated domain names,
aggregate process states/counts, maximum disk usage and backup counts. It marks
all other inventory domains unobserved and copies no raw tool response, host
coordinate, project path or secret value.

Run from the control-plane source with `GOVERNED_MCP_AUTH_TOKEN` available in
the process environment:

```bash
python3 scripts/control_plane_server_inventory_collector.py
```

The collector writes JSON to stdout only. No live observation was performed
while implementing the collector because that credential was unavailable in the
execution environment.

### KBI-04D — persistence adapter implemented; live facts pending

`scripts/control_plane_server_inventory_facts.py` validates a saved `KBI-04C`
observation against the versioned MCP capability snapshot and the server
knowledge model. It reduces only the ten bounded S1/S2 slots supported by the
collector: domains, Docker, PM2, maximum disk usage, and backup counts.
Other inventory domains remain unobserved. Success from a tool whose source
classification is no longer read-only is refused.

For a reviewed live observation, use the current source checkout and its exact
state revision:

```bash
python3 scripts/control_plane_server_inventory_collector.py > /tmp/kbi-04c-observation.json
python3 scripts/control_plane_server_inventory_facts.py \
  --input /tmp/kbi-04c-observation.json --expected-revision 0
python3 .governance/control-plane-db/materialize.py
```

The command requires the collector's current process credential and a real
read-only response. The importer performs no network call and never fetches
credentials. `--expected-revision` protects the exact versioned state; use the
actual current revision rather than the example `0` after the first ingestion.
Commit the reviewed JSON state through the governed GitHub PR/CI path. The
SQLite database is deterministically rebuilt from that state and is not
committed. A same-time replay is idempotent; conflicting or older observations
fail. Unknown or partial responses do not become known facts. A later failed
refresh marks a formerly known value `KNOWN_STALE` for planning and preserves
its last successful provenance. No raw MCP output, secret, connection
coordinate, container name, filesystem path or unbounded inventory is stored.

`KNOWN_CURRENT` means observed successfully **at the recorded time**. Domain,
runtime, disk and backup facts still require their model-specific live refresh
before an operation that depends on them. The local source state starts at
`NOT_COLLECTED`, revision `0`, with zero facts; it does not assert current S1/S2
conditions. A JSON observation asserts its collector origin and matching
snapshot, but is not cryptographically signed. Review its origin before
ingestion. Neither collection nor persistence grants production authority.

### KBI-04E — derived recipe capability mapping

Run `python3 scripts/control_plane_server_recipe_capabilities.py` to derive a
deterministic JSON matrix from the versioned recipes, the current
`CP-MCP-CAP-001` snapshot and the persisted KBI-04D inventory. It covers every
`required_capabilities` and `required_inventory` item of every recipe without
creating a second mapping authority. The result includes the snapshot digest,
observation time and inventory revision. Re-running against a refreshed
snapshot recomputes the mapping; no permanent copy of volatile project registry
IDs is stored.

For each capability, the matrix distinguishes:

| Status | Meaning |
|---|---|
| `CAPABILITY_UNDEFINED` | Required by a recipe, absent from the capability map. |
| `NO_MUTATION_CANDIDATE` / `NO_OBSERVATION_CANDIDATE` | Modelled capability without a matching tool of the required surface. |
| `PROJECT_SCOPED_ONLY` / `PROJECT_SPECIFIC_ONLY` | Candidate exists, but is bound to registered/specific projects. |
| `GENERIC_SNAPSHOT_CANDIDATE` | Generic candidate exists in the versioned snapshot, pending live check and authority. |
| `CATALOGUE_CONTRADICTION` | Candidate and catalogue disagree; candidate selection fails closed. |

The current snapshot exposes generic read candidates for domain/runtime
observation. It does not expose generic create-subdomain, DNS-change or TLS
mutation candidates. A Git pull and deployment candidate on S2 are scoped to
registered projects, so they do not provide an Ekyc binding or deployment path
merely because their names appear in the catalogue. The output also reports
the precise gap IDs and scope constraints. Inventory requirement status remains
`NO_PERSISTED_OBSERVATION` while KBI-04D has zero live facts.

This matrix states *snapshot candidates*, never live callable tools, free
capacity, project eligibility, execution authority or production readiness.
Only a concrete governed operation may trigger a missing-capability intake or
live capability refresh. `KBI-04F` may consume the derived matrix for a
non-executing blueprint.

## Identity and credential plane

Server operation recipes consume `CP-IDENTITY-SECRET-001`.

The server model knows what must be configured; the identity/secret model knows how the required credentials are obtained, created, injected, verified, rotated and revoked.

Examples include ephemeral SSH certificates, scoped service identities, application environment secrets, database credentials, DNS-provider credentials and TLS key material under the certificate manager.

No recipe may infer authority merely because a credential exists.
