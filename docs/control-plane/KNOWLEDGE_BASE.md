# CONTROL PLANE KNOWLEDGE BASE

Authority: `CP-KNOWLEDGE-001`

This source-only knowledge model exists so agents do **not rediscover the same stable facts and patterns on every run**.

It complements the canonical Governance Model, adaptive question catalogue, MCP capability model and existing relational memory. It is not another runtime engine.

## Core rule

```text
KNOW ONCE
→ persist provenance + freshness
→ reuse while current
→ refresh only when volatile / contradictory / action-sensitive
→ ask owner only for decisions or genuinely non-discoverable facts
```

Knowledge never grants execution authority.

## Layers

The knowledge base distinguishes:

- target governance model;
- adaptive question/decision model;
- MCP capability semantics and refreshable implementation image;
- Git provider knowledge;
- server-organization knowledge;
- project-specific facts;
- owner decisions;
- observed reusable conventions;
- volatile operational evidence.

This distinction matters because they do not age at the same speed.

A governance decision can remain current until a governed revision changes it. A server health check may need live refresh immediately before deployment.

## Example — Ekyc

If Ekyc has already been observed as:

- GitHub repository;
- new/fresh project;
- no existing MCP project registration;
- no existing Ekyc domain;
- MCP DIRECT route working;
- SSH route configured as alternate;

then a later agent must reuse those facts while they remain current. It should not rediscover them merely because the conversation changed.

If the owner later chooses S2 as production target, that becomes an OWNER_DECISION and should not be re-asked unless the owner supersedes it or the project scope materially changes.

The system may still refresh volatile facts immediately before mutation: current S2 capacity, current domains/vhosts, free ports, runtime health, DNS/TLS state, exact repository HEAD, etc.

## Example — AfricaFunds

AfricaFunds is an ADOPT_EXISTING reference.

Known facts such as its repositories, S2 role and existing public surfaces should be reused as project knowledge. They are inputs to the adaptive questionnaire and gap analysis.

The system should ask questions about **what to do with what exists**, not repeatedly ask whether those resources exist.

Observed conventions from AfricaFunds or another project may become candidate patterns, but they do not automatically become universal standards. Promotion to a mandatory standard remains a governed decision.

## Server knowledge

The Control Plane should gradually learn S1/S2 organization:

```text
logical server
→ hosting model
→ domain/vhost conventions
→ runtime/process-manager patterns
→ deployment conventions
→ database conventions
→ observability/backup conventions
→ MCP capabilities
```

Persistent public knowledge intentionally does not store SSH host/user coordinates, private keys, secret values or exhaustive server filesystem paths.

When an operation needs current sensitive/volatile details, the Control Plane performs a bounded authorized refresh.

## Freshness

Every persisted fact must have provenance and a freshness class.

Typical behavior:

- stable governance rule → reuse until governed revision changes;
- owner decision → reuse until superseded;
- project repository topology → reuse until contradiction/scope change;
- server convention → reuse for planning, refresh before mutation;
- current HEAD / TLS / DNS / process health → live refresh when the operation depends on it.

## Incremental implementation

This slice only establishes the canonical model and tests.

Future KBI work will be small and resumable:

- KBI-03 normalized project-fact persistence in the existing relational model;
- KBI-04 server-organization model and operation recipes — IN PROGRESS incrementally; taxonomy/recipes seed complete;
- KBI-05 adaptive-question reuse binding;
- KBI-06 selective freshness refresh;
- KBI-07 cross-project convention learning with evidence thresholds.

No current CASE 1 task is displaced.

## Server-platform knowledge extension

`CP-SERVER-KNOWLEDGE-001` extends this knowledge base with a complete server inventory taxonomy and reusable operation recipes.

The Control Plane can therefore reason from a future owner choice such as `production = S2` and `domain = subdomain` into the inventory facts, capabilities, authorities and ordered operations required to make that project real.

Live S1/S2 population remains intentionally separate and will be performed as bounded authorized discovery.
