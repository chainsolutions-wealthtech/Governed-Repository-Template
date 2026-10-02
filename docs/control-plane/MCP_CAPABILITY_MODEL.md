# MCP Capability Model — CP-MCP-CAP-001

> Source-only authority for `chainsolutions-wealthtech/Governed-Repository-Template`.
> This authority is removed from instantiated client repositories.

## Purpose

The central Control Plane keeps a **stable capability model plus a persistent last-known image of the current MCP implementation** so CREATE, ADOPT, MAP, LAB and CONTINUE do not start from zero each time.

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
- logical server identities and non-secret capability metadata;
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

## Governed refresh command

The canonical on-demand source command is:

```text
/refresh-mcp-capabilities
```

It is accepted only on the canonical Control Plane programme issue `#12` and only when the comment author association is `OWNER`, `MEMBER` or `COLLABORATOR`.

The command authorizes only the already-standing read-only capability refresh. It does not authorize any MCP/server mutation. A changed snapshot is persisted through a unique branch and pull request, then normal Governance CI must pass before merge.

## Capability-first planning model

The live MCP catalogue is **not** the questionnaire and is **not** the governance model.

The stable planning chain is:

```text
TARGET GOVERNANCE / PROJECT PROFILE
→ CASE + CURRENT PROJECT REALITY
→ UNRESOLVED REQUIREMENT
→ CAPABILITY NEEDED
→ CURRENT MCP SURFACE
→ CANDIDATE TOOL(S)
→ REQUIRED AUTHORITY
→ PREPARED OPERATION
→ EXISTING LOOP_ENGINEERING
```

A case must therefore contain a short ordered sequence of capabilities, never an indiscriminate list of most MCP tools.

Current generic capabilities include:

- Git repository observation;
- governance-state observation;
- project/infrastructure mapping;
- domain/web observation;
- server/runtime observation;
- database read observation;
- Git repository mutation;
- governed task coordination;
- server-side repository mutation;
- server filesystem mutation;
- web-hosting mutation;
- TLS mutation;
- deployment/runtime mutation.

A capability may be:

- `AVAILABLE_GENERIC`;
- `AVAILABLE_PROJECT_REGISTRY_SCOPED`;
- `AVAILABLE_ONLY_PROJECT_SPECIFIC`;
- `NOT_EXPOSED_BY_CURRENT_MCP_CATALOGUE`.

When a required mutation capability is not exposed, the Control Plane does **not** invent a tool and does **not** immediately create an MCP intake. It prepares a bounded `SCOPED_CAPABILITY_REQUEST` only when the concrete project operation actually needs that capability.

## Adaptive question resolution

The capability model feeds the questionnaire.

```text
QUESTION TARGET FIELD
→ fresh direct Git observation?
→ fresh project memory?
→ prior owner decision?
→ authorized MCP read-only discovery?
→ only then ASK OWNER
```

A fresh resolved fact must not be re-asked.

For an existing repository, Git observation should automatically resolve repository/provider/default-branch/workflow/ruleset/check facts before owner questions are considered.

MCP observation should resolve project registration, server binding, existing domains/runtime surfaces and other factual infrastructure fields when the current standing read authority covers that observation.

Owner interaction is reserved for:

- genuine owner/business decisions;
- facts that cannot be discovered with available authority;
- contradictions requiring owner resolution;
- authority expansion when a concrete operation needs a capability that is not currently granted/exposed.

For CREATE, the same engine asks more questions because fewer facts exist. For ADOPT/MAP/CONTINUE, existing observations and prior answers collapse the questionnaire automatically.

## Snapshot versus capability model

`CP-MCP-CAP-001` has two complementary roles:

1. **Stable capability semantics** — what kind of capability a project may need, what fields it can resolve, what authority class it requires, and how it feeds the questionnaire/Loop Engineering.
2. **Refreshable implementation image** — which MCP tools/resources currently implement those capabilities.

The implementation image may change frequently. The capability semantics should remain stable and evolve through governed decisions.

A live catalogue refresh therefore answers:

> “Which current MCP surface can satisfy this already-understood capability?”

It must never redefine the project need merely because a tool exists.

## Authority classes

MCP surface classes are distinct:

- `read` → `READ_ONLY_DISCOVERY_AUTHORITY`;
- `operational-write` → `GOVERNED_OPERATIONAL_AUTHORITY_REQUIRED`;
- `scoped-write` → `EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED`.

Governed operational transitions (claiming or transitioning a governed task, reconciling intent) must not be represented as server/runtime mutation authority.

Tool scope is also explicit. A tool hard-wired to one project or project family is `PROJECT_SPECIFIC`; a tool with an allowlisted project enum is `PROJECT_REGISTRY_SCOPED`; only genuinely reusable tools are `GENERIC`.

## GSCC function exposure gate

Authority: `docs/control-plane/GSCC_FUNCTION_EXPOSURE_GATE.md`.

Every tool in the canonical catalogue is planning evidence only and carries:

- `governed_exposure_gate = GSCC_REQUIRED`;
- `governed_exposure_status = REQUIRES_RUNTIME_VALIDATION`.

A tool may be a capability candidate without being authorized for governed exposure or invocation. Before every governed MCP invocation, the Control Plane must recompute the GSCC function-gate receipt from the exact tool contract, source HEAD, package and current capability snapshot.

A contract digest change invalidates the prior receipt and requires revalidation. Exposure validation does not grant invocation or mutation authority.
