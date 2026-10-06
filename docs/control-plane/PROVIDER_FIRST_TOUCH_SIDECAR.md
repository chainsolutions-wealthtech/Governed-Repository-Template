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


## Exhaustive evidence contract

Provider First Touch is not an identity-only envelope. The canonical expected-field registry now enumerates the complete observable surface across agent/provider/model, conversation/session, transport, authenticated GitHub identity, repository, permissions, branch/ref, commits/trees, issues, pull requests, Actions/CI, tool calls, chronological sequence, first-touch fingerprint, repository state, correlated events, GSCC, GSE, GACR, process gates, provenance, confidence/quality, timestamps, component versions, runtime environment, technical results and explicit negative/security facts.

Every canonical field produces one `first-touch-field-evidence/v1` row:

- `field_id`
- `value`
- `status`
- `source`
- `confidence`
- `reason`
- `observed_at`
- `evidence_ref`

If the provider supplies a field, its actual non-sensitive value is retained. If it explicitly reports the field unavailable, the row is `UNAVAILABLE` with `source=not_exposed`. If it does not supply an expected field, that is also materialized as `UNAVAILABLE` with reason `provider_envelope_did_not_supply_field`. Silent absence is therefore forbidden.

The provider may send canonical nested structures directly (for example `tool.name`, `workflow.run_id`, `gscc.identity_id`) or use supported top-level aliases such as `provider`, `model`, `repository`, `branch`, and `observed_head`.

Observed values may themselves be evidence wrappers with `value`, `source`, `confidence`, `reason` and `evidence_ref`; those provenance attributes are preserved.

Negative facts are first-class evidence, including `codex_used=false`, `repository_mutated=false`, `token_exposed=false`, and equivalent non-secret status flags.

Raw credential-bearing fields remain forbidden at provider ingress. A provider must report only safe status metadata about secrets; it must never put an OAuth token, GitHub token, password, cookie, authorization header, private key, client secret or equivalent credential value into the envelope.

The full raw non-sensitive provider envelope and the normalized field-evidence rows are both retained in the existing B00-B30 first-touch projection. This is evidence collection only and grants no mutation authority.
