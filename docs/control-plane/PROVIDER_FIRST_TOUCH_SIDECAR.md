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

When the provider supplies a stable conversation/session/connection reference, the sidecar projects it into the canonical First Touch identity surface and enters the existing GSCC First Touch store / entry contract. If none is exposed, the result remains capture-only and Q1 progression is not fabricated. The provider sidecar must not dispatch directly to GACR.

## Canonical routing boundary

The provider sidecar reuses the same canonical state and gate machinery as repository-observable First Touch:

```text
provider first tool call
→ gscc_provider_first_touch
→ provider_first_touch_ingress
→ exhaustive capture + field evidence
→ canonical First Touch state restore
→ B00–B30
→ completeness
→ GSCC First Touch identity / uniqueness
→ GSCC First Touch handoff
→ Q1
→ remaining GSCC gates
→ Q10 GSE
→ GACR durable continuity
```

It must not call the historical `emit_controlled_arrival() → target=gacr` path during First Touch.


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


## Provider first-tool hook

The repository includes `scripts/provider_first_tool_hook.py` as the host-side adapter contract for the first GitHub tool call.

Expected host behavior:

```text
FIRST_GITHUB_TOOL_CALL
→ build gscc-provider-first-touch-envelope/v1
→ repository_dispatch: gscc_provider_first_touch
→ mark host-local emitted marker
→ continue normal tool execution
```

The host-local marker is only an emission optimization. Canonical First Touch uniqueness remains owned by the GSCC First Touch store. Repeated provider dispatches for the same strong/exact identity must classify as continuation rather than create a second First Touch.

If no stable conversation/session/connection reference is available, the hook fails closed and must not fabricate one from GitHub actor + repository alone.


## Minimal provider signal / repository-owned enrichment

The provider is not required to reproduce GitHub repository state that the governed repository can observe itself.

Minimum provider signal:

```text
schema
provider
transport
repository
identity.{conversation_ref|session_ref|connection_ref} when genuinely exposed
first tool metadata when exposed
observed_at when exposed
explicit UNAVAILABLE markers for provider-only identifiers not exposed
```

After `gscc_provider_first_touch`, the repository enriches the signal using read-only GitHub APIs before exhaustive capture. The enrichment currently observes repository/owner metadata, effective repository permissions visible to the workflow credential, default branch, current branch HEAD, commit/tree facts and Actions workflow/run state. These observations are projected into the existing canonical First Touch field registry with repository-side provenance.

The repository must not treat workflow-token permissions as proof of the original provider connector's private scopes. Provider-only facts remain provider-sourced or `UNAVAILABLE`.

A missing stable provider conversation/session/connection reference no longer prevents evidence capture. It produces a fully enriched capture with `UNRESOLVED` identity and blocks Q1 until a strong/exact identity can be established. No identity may be fabricated from GitHub actor + repository alone.

Canonical boundary:

```text
MINIMAL PROVIDER SIGNAL
→ REPOSITORY READ-ONLY ENRICHMENT
→ FULL OBSERVABILITY EVIDENCE
→ B00–B30 / SQLite
→ identity gate
→ Q1 only when identity is sufficient
```


## Governed GitHub read wrapper

The repository now includes `scripts/governed_github_read_connector.py` as the executable adapter that binds common GitHub reads to Provider First Touch.

Supported governed reads:

- `get_repo()`
- `fetch_file(path, ref=...)`

Behavior:

```text
first governed get_repo OR fetch_file
→ provider_first_tool_hook
→ repository_dispatch: gscc_provider_first_touch
→ GitHub read

subsequent governed reads in the same connector session
→ no second First Touch
→ GitHub read
```

If provider conversation/session/connection identity is unavailable, the wrapper still emits exactly one unresolved capture signal per connector session and the repository preserves the Q1 fail-closed identity rule.

This wrapper is the repository-controlled integration surface. It does not modify ChatGPT's proprietary native `@GitHub` connector. A host or custom connector must invoke this governed surface instead of calling the native GitHub read directly if automatic First Touch is required.


## Canonical GSCC instrumentation binding

The generic binding point is now `gscc.instrument_tool(..., before_tool_call=...)`.

`provider_first_tool_hook.FirstTouchBeforeToolCall` is the canonical Provider First Touch adapter for that hook. One adapter instance represents one provider/client connector session and emits at most one First Touch before the first instrumented tool, regardless of whether that tool is `get_repo`, `fetch_file`, a search/read operation, or another instrumented GitHub function.

The previously added `governed_github_read_connector.py` remains a compatibility/example integration for common reads; it is not a second First Touch authority. New controlled hosts should instrument their actual tool surface through the generic GSCC hook rather than create one wrapper per tool name.


## Provider-owned context normalization

Before the first instrumented GitHub tool is executed, the provider/host adapter now normalizes the facts that only the provider can truthfully supply into a compact `provider_context` block.

The block covers request, agent/model/runtime, client, session, connection/connector and negative/security facts. A value is copied only when the host actually supplies it. Missing provider-private identifiers are materialized as `UNAVAILABLE`; they are never inferred from GitHub actor, repository, branch, SHA or other repository evidence.

The provider dispatch envelope remains compact at the top level:

```text
schema
provider
transport
repository
identity
identity_status
tool
provider_context
```

Repository-owned GitHub enrichment remains a separate phase after `gscc_provider_first_touch`. Provider facts and repository facts therefore retain distinct provenance.
