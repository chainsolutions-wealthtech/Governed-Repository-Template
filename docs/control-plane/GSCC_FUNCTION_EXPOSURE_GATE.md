# GSCC FUNCTION EXPOSURE / INVOCATION GATE

Authority: `GSCC-FUNCTION-GATE-001`

Status: `CANONICAL_SOURCE_CONTROL_PLANE_GATE`

## Primary invariant

```text
FUNCTION EXISTS
!=
FUNCTION IS GOVERNED-EXPOSED
!=
FUNCTION MAY BE INVOKED
!=
MUTATION AUTHORITY
```

Every function/tool used through the governed Control Plane must pass through GSCC before governed exposure and before every governed invocation.

```text
DISCOVERED / CATALOGUED FUNCTION
→ GSCC FUNCTION ENVELOPE
→ CONTRACT ATTESTATION
→ CONTEXT BINDING
→ CAPABILITY MATCH
→ AUTHORITY CLASSIFICATION
→ CLAIM / COLLISION CHECK
→ EXACT-HEAD CHECK
→ PREFLIGHT
→ INVOCATION GATE
→ EXECUTE ONLY IF SEPARATELY AUTHORIZED
→ VERIFY
→ VALIDATION RECEIPT
```

A validation receipt never grants mutation authority and never replaces task, claim, collision-domain, exact-HEAD, execution-package, approval or provider/runtime authority.

## Mandatory Actions workflow

Canonical workflow:

`.github/workflows/gscc-function-gate.yml`

The workflow is reusable by `Governed Execution` and can also receive an explicit `repository_dispatch: gscc_function_gate`.

For a governed execution package, the workflow:

1. requires canonical `main`;
2. checks the exact source HEAD supplied by the caller;
3. reads the canonical MCP capability snapshot;
4. enumerates every MCP-bound function in preflight / execute / verify / rollback phases;
5. validates the exact function contract digest and authority classification;
6. generates a complete secretless GSCC FunctionEnvelope for every invocation;
7. derives the ordered GSCC route;
8. emits a validation receipt and digest;
9. exposes that digest to the downstream execution job;
10. blocks execution if the receipt is missing or does not recompute exactly.

The downstream engine independently recomputes the expected digest before real MCP execution.

## Information systematically exposed to GSCC

For each function invocation, GSCC receives safe governed metadata including:

- repository;
- exact source HEAD;
- operation ID and intent;
- function/tool name;
- exact contract digest;
- surface classification;
- authority class;
- read-only/destructive hints when observed;
- compact input field contract;
- catalogue tags;
- capability matches;
- project scope;
- execution phase;
- argument field names;
- opaque digest of argument values;
- session ID / connection reference when available;
- MCP snapshot authority, freshness and catalogue digest;
- full ordered route.

Raw argument values are intentionally not transmitted by this envelope. Secret values, bearer credentials, cookies, private keys, raw prompts, transcripts, assistant response bodies and private reasoning are forbidden by the canonical GSCC protocol.

"Systematic exposure of all information" therefore means all governance-relevant safe metadata, not secret or private content.

## Catalogue contract

Every function in the canonical MCP snapshot carries:

```json
{
  "governed_exposure_gate": "GSCC_REQUIRED",
  "governed_exposure_status": "REQUIRES_RUNTIME_VALIDATION"
}
```

Catalogue presence is planning evidence only. It is never exposure authority.

A contract change invalidates the prior gate:

`FUNCTION_CONTRACT_MOVED → HOLD / REVALIDATE`.

Unknown function, missing contract digest, unknown surface or unknown authority class fail closed.

## Governed Execution integration

`.github/workflows/governed-execution.yml` has a mandatory `function-gate` job.

The execution job depends on that job and receives:

- `GSCC_FUNCTION_GATE_VALIDATED=true`;
- `GSCC_FUNCTION_GATE_VALIDATION_DIGEST=<digest>`.

A real MCP execution started through the CLI fails closed when these values are absent or when the digest does not match a fresh local recomputation.

## Repository arrival integration

The function gate is additive to the already-canonical arrival path:

```text
OBSERVABLE REPOSITORY ARRIVAL
→ GSCC Observable Arrival Gateway
→ Presence / Session
→ function request
→ GSCC Function Gate
→ validated route
→ execution only after independent authorities
```

The arrival gateway is generic and distributed to governed client repositories.

## Runtime boundary still to close

The source Control Plane can enforce this gate for its governed execution path, but repository code cannot intercept a direct call made straight to an independently hosted MCP runtime.

Therefore absolute universality requires the MCP provider runtime itself to implement the same invariant:

```text
MCP tools/list candidate
→ GSCC exposure validation
→ only validated tool may be advertised as governed-exposed

MCP tools/call
→ GSCC invocation event
→ mandatory governed workflow / route validation
→ invoke only after validation + independent authority
→ verification/result event
```

Until the provider runtime wrapper is implemented and live-proven, the following distinction is mandatory:

- `CONTROL_PLANE_GOVERNED_FUNCTION_GATE = ENFORCED`;
- `DIRECT_EXTERNAL_MCP_CALL_INTERCEPTION = NOT_YET_PROVEN`.

No repository-side evidence may be used to claim that an external direct MCP call was intercepted when the runtime itself did not emit that evidence.

## Safety invariants

- `CATALOGUE_PRESENCE != EXPOSURE_AUTHORITY`
- `EXPOSURE_VALIDATION != INVOCATION_AUTHORITY`
- `EXPOSURE_VALIDATION != MUTATION_AUTHORITY`
- `ROUTE_ASSIGNMENT != CLAIM_TRANSFER`
- `WORKFLOW_DELIVERY != WRITE_AUTHORITY`
- `FUNCTION_ARGUMENT_DIGEST != FUNCTION_ARGUMENT_VALUE`
- `NO GSCC RECEIPT = NO GOVERNED MCP EXECUTION`
- `CONTRACT DRIFT = REVALIDATE`
- `UNKNOWN = FAIL_CLOSED`
