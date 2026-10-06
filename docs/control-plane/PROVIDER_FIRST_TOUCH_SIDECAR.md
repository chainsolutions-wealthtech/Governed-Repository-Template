# Provider First Touch Sidecar

## Purpose

This sidecar closes the repository-side ingestion gap for provider transports whose first observable action is a read and therefore does not produce a native GitHub webhook.

The repository cannot observe a REST/GraphQL read by itself. The provider/host that owns that transport must emit one machine ingress call automatically on first touch. No human issue, comment, branch, commit or pull request is required for ingestion.

## Contract

Dispatch type:

`gscc_provider_first_touch`

Payload schema:

`gscc-provider-first-touch-envelope/v1`

Required fields:

- `schema`
- `provider`
- `transport`
- `repository`

Recommended evidence:

- `actor`
- `model`
- `branch`
- `observed_head`
- `identity.conversation_ref`, `identity.session_ref` or `identity.connection_ref` when genuinely exposed
- capabilities and non-sensitive transport metadata
- explicit `UNAVAILABLE` markers for identifiers the provider does not expose

Secrets, tokens, passwords, cookies, authorization headers, private keys and client secrets are rejected.

## Fail-closed identity rule

The complete provider envelope is always preserved as first-touch evidence and projected into the existing B00-B30 SQLite model.

GSCC controlled arrival is emitted only when the provider supplies a stable conversation/session/connection reference. If none is exposed, the result is `CAPTURE_ONLY_IDENTITY_UNRESOLVED`; evidence remains preserved but Q1/continuity progression is not fabricated.

## Concurrency boundary

This sidecar is additive. It does not modify `gscc-observable-arrival.yml`, the existing first-touch store/GSE projection, GACR stores, or the realignment files introduced by PR #200.
