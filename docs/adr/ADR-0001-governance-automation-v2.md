# ADR-0001 — Additive Governance Automation V2

- Status: `ACCEPTED`
- Scope: generic repository template
- Compatibility: additive / backward-compatible

## Context

V1 provides deterministic governance, persistent state, validation and manual bootstrap. The MCP PRECODE laboratory demonstrates reusable patterns for GitHub-first continuity, exact-head guards, canonical-memory pointers, multi-agent collision control, checkpoints, handoffs and bounded information intake.

## Decision

Add those patterns as generic repository-local building blocks without importing MCP runtime authorities.

The V2 layer:

- keeps V1 files and commands;
- automates initialization when a supported GitHub event is available;
- persists a bootstrap receipt;
- maintains a machine-readable canonical-memory pointer;
- requires HEAD reconciliation before stale writes;
- supports temporary session/work claims by collision domain;
- registers new information separately from canonical memory and work;
- fails closed on contradiction and ambiguity.

## Explicit exclusions

V2 does not import MCP Operational Memory runtime, Governed Task Queue runtime, runtime lock service, Live State, OAuth/session runtime, server/domain/runtime resolvers, deployment authority or project-specific history.

## Consequences

A repository can be initialized and resumed more automatically while preserving human-readable governance, Git provenance and non-regression rules.
