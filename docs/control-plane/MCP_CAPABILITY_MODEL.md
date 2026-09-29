# MCP Capability Model — CP-MCP-CAP-001

> Source-only authority for `chainsolutions-wealthtech/Governed-Repository-Template`.
> This authority is removed from instantiated client repositories.

## Purpose

The central Control Plane keeps a **persistent last-known image of MCP capabilities** so CREATE, ADOPT, MAP, LAB and CONTINUE do not start from zero each time.

The snapshot is knowledge and planning authority only:

```text
LIVE READ-ONLY MCP DISCOVERY
→ VERSIONED CAPABILITY SNAPSHOT
→ CASE / CAPABILITY MATCH
→ CANDIDATE TOOLS
→ PREPARED OPERATIONS
→ EXISTING LOOP_ENGINEERING
→ LIVE AUTHORITY + FRESHNESS PREFLIGHT
→ EXECUTE ONLY IF AUTHORIZED
```

It never turns tool availability into write authority.

## Canonical machine projection

`.governance/control-plane-state/mcp-capability-snapshot.json`

Authority ID: `CP-MCP-CAP-001`.

The snapshot stores only non-secret information needed for planning:

- MCP server identity and protocol;
- observed source/runtime/catalogue digests;
- S1/S2 non-secret target coordinates;
- current MCP tool catalogue and declared surfaces;
- current MCP resources;
- safe summary of the scoped-write context;
- case → capability/tool candidate mapping;
- provenance, refresh sequence and contradictions;
- explicit authority requirements for every tool surface.

It never persists bearer tokens, private keys, passwords or secret values.

## Refresh policy

Refresh is **event- and need-based**, not blind periodic polling.

A read-only refresh is appropriate when:

- no snapshot exists;
- a required capability is absent from the stored image;
- catalogue/runtime/source evidence contradicts the stored image;
- an agent or owner explicitly requests refresh;
- a mutation is being prepared and live capability attestation is required.

Every mutation-capable operation requires a live preflight even when the snapshot is current.

The user has authorized the central Template to perform these MCP refresh discoveries when necessary. That standing authority is strictly read-only and does not extend to MCP/server mutation.

## Persistence workflow

`.github/workflows/mcp-capability-refresh.yml` performs a source-only direct MCP refresh using the Control Plane's existing MCP credential, validates the result, and persists changes through a dedicated branch/PR.

It does not push directly to `main`, use force-push, mutate MCP, or create MCP intakes.

## Loop Engineering integration

The snapshot does not create another dispatcher.

It feeds the existing project model/work-item/Loop Engineering chain:

```text
CASE / WORK ITEM
→ required capability
→ snapshot candidate
→ refresh if evidence is insufficient
→ candidate tool + required authority
→ prepared operation
→ existing dependency/claim/session/approval gates
→ execute
→ evidence
```

Tool mappings are **planning candidates**, not automatic permissions.

Read tools are marked `READ_ONLY_DISCOVERY_AUTHORITY`.
Operational/scoped write tools are marked `EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED`.
Unknown surfaces fail closed to `AUTHORITY_CLASSIFICATION_REQUIRED`.

## Relationship to Governance Model

Decision: `CPD-033`.

The snapshot is implemented now because CASE 1 needs it operationally. Its relational projection remains explicitly:

`PENDING_PROJECTION_GMC_INTEGRATION`

until the already scheduled Governance Model relational extension. No second database is introduced.
