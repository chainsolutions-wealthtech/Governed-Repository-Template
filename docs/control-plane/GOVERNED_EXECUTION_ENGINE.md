# GOVERNED EXECUTION ENGINE

Authority: `CP-EXECUTION-001`

The Control Plane now has one governed execution adapter for GitHub and production/server operations.

It extends the existing Loop Engineering model. It is **not** a second task engine.

## Execution chain

```text
reviewed project decision / task
→ secret-free execution package
→ exact source HEAD
→ exact target HEAD when repository-scoped
→ authority grant
→ capability resolution
→ credential reference resolution
→ preflight
→ execute
→ verify
→ rollback when safe
→ redacted receipt
```

Dry-run is the default.

## Registered intents

### Server / production — 15

- CREATE_PROJECT_DIRECTORY
- CREATE_SUBDOMAIN
- CREATE_NEW_DOMAIN_BINDING
- ALLOCATE_APPLICATION_PORT
- CONFIGURE_REVERSE_PROXY
- PROVISION_TLS
- CREATE_DATABASE
- BIND_REPOSITORY_TO_SERVER_PROJECT
- DEPLOY_APPLICATION
- CONFIGURE_ENV_AND_SECRETS
- CONFIGURE_PROCESS_OR_SERVICE
- CONFIGURE_SCHEDULED_JOB
- CONFIGURE_OBSERVABILITY
- CONFIGURE_BACKUP_AND_ROLLBACK
- PRODUCTION_ATTESTATION

### Identity / secrets — 10

- DISCOVER_CREDENTIAL_REQUIREMENT
- MINT_GITHUB_APP_INSTALLATION_TOKEN
- PROVISION_GITHUB_SECRET
- MINT_EPHEMERAL_SSH_CERTIFICATE
- CREATE_OR_BIND_SERVER_APPLICATION_SECRET
- CREATE_DATABASE_CREDENTIAL
- CREATE_DNS_AUTOMATION_CREDENTIAL
- ROTATE_CREDENTIAL
- REVOKE_CREDENTIAL
- VERIFY_SECRET_OR_CREDENTIAL_WITHOUT_READBACK

### GitHub administration / delivery — 14

- GITHUB_CREATE_REPOSITORY_FROM_TEMPLATE
- GITHUB_CREATE_BRANCH
- GITHUB_UPSERT_FILE
- GITHUB_CREATE_PULL_REQUEST
- GITHUB_MERGE_PULL_REQUEST
- GITHUB_CONFIGURE_BRANCH_PROTECTION
- GITHUB_CONFIGURE_RULESET
- GITHUB_CONFIGURE_WEBHOOK
- GITHUB_CONFIGURE_ENVIRONMENT
- GITHUB_SET_ACTIONS_VARIABLE
- GITHUB_DISPATCH_WORKFLOW
- GITHUB_CREATE_DEPLOYMENT
- GITHUB_UPDATE_REPOSITORY_SETTINGS
- GITHUB_ADD_COLLABORATOR

Total: **39 intents**.

## GitHub execution

GitHub operations are implemented with explicit builders. A package cannot supply an arbitrary URL or HTTP method.

The engine builds the known endpoint, validates the parameters, executes with an ephemeral target-owner GitHub App token and performs a post-operation verification.

Examples:

```text
GITHUB_CREATE_BRANCH
→ exact repository HEAD guard
→ POST governed ref
→ GET ref
→ SHA must match
```

```text
GITHUB_MERGE_PULL_REQUEST
→ exact repository HEAD guard
→ read PR
→ PR head SHA must equal approved SHA
→ merge
→ re-read PR
→ merged=true
```

Secrets use `gh secret set` with values supplied only from runtime secret references. The value is never read back or written to a receipt.

## Server execution

Server operations execute through the current MCP capability surface.

Each MCP step in a package declares:

```json
{
  "backend": "MCP_DIRECT",
  "capability": "DEPLOYMENT_RUNTIME_CHANGE",
  "tool": "deploy_project_s2",
  "arguments": {
    "project": "brvmchainsolution"
  }
}
```

Before network execution the engine checks:

1. the capability exists in the latest canonical MCP snapshot;
2. the tool is a candidate for that capability;
3. its project scope matches;
4. all required arguments match the live MCP tool contract;
5. mutation authority is present;
6. an explicit execute step is versioned in the package.

No mutation is auto-selected merely because one MCP tool exists.

## Current MCP coverage

The execution engine is complete, but **the current MCP implementation does not yet expose every generic server mutation capability**.

For example, the latest canonical capability snapshot still marks generic:

- SERVER_FILESYSTEM_CHANGE
- WEB_HOSTING_CHANGE
- TLS_CHANGE

as not exposed.

Other future recipe requirements such as DOMAIN_DNS_CHANGE, DATABASE_CHANGE, SECRET_PROVISIONING, SERVER_RUNTIME_CHANGE, SERVER_SCHEDULER_CHANGE, OBSERVABILITY_CHANGE and BACKUP_RECOVERY_CHANGE also need explicit MCP capability surfaces before the corresponding generic recipe can execute.

This is not bypassed.

The engine returns a machine-readable `MISSING_CAPABILITY` / `MISSING_CAPABILITY_BINDING` result. A later governed process can then prepare a bounded MCP capability request only when that operation is actually needed.

Existing project-scoped surfaces such as `deploy_project_s2` can already be bound when the project is in the MCP allowlist.

## Credentials

Credential values never belong in execution packages.

Allowed references include:

```text
env:GOVERNED_MCP_AUTH_TOKEN
env:AN_AUTHORIZED_SECRET
runtime:MINTED_GITHUB_APP_TOKEN
generated:32
```

Generated values exist only in process memory.

The execution receipt contains metadata and verification evidence, not credential values.

## Central workflow

`.github/workflows/governed-execution.yml` is manual-only.

It requires:

- canonical `main`;
- exact expected source HEAD;
- a package committed under
  `.governance/control-plane-state/execution-packages/`;
- dry-run validation first;
- explicit `execute=true` for side effects.

The workflow mints the least relevant GitHub App token class it can derive from the intent and provides OIDC/MCP credentials only at runtime.

No arbitrary JSON is accepted from the workflow UI.

## Execution packages

Schema:

`schemas/governed-execution-package.schema.json`

A mutation package contains an explicit authority block and may reference an exact target repository HEAD.

Example shape:

```json
{
  "schema_version": "1.0.0",
  "operation_id": "PROJECT-DEPLOY-001",
  "intent": "DEPLOY_APPLICATION",
  "project_id": "project-id",
  "repository": "owner/repository",
  "expected_head": "40-hex-sha",
  "server_id": "S2",
  "authority": {
    "approved": true,
    "grants": ["SCOPED_DEPLOY"],
    "scope": {"project_id": "project-id", "server_id": "S2"},
    "decision_ref": "OWNER-DECISION-ID"
  },
  "parameters": {},
  "bindings": {
    "capabilities": {},
    "credentials": {
      "MCP_AUTH_TOKEN": {"secret_ref": "env:GOVERNED_MCP_AUTH_TOKEN"}
    },
    "steps": {
      "preflight": [],
      "execute": [],
      "verify": [],
      "rollback": []
    }
  }
}
```

A package with a plaintext token/password/private key is rejected.

## Failure semantics

Typical fail-closed results:

- EXECUTION_AUTHORITY_NOT_APPROVED
- EXECUTION_AUTHORITY_GRANT_MISSING
- HEAD_MOVED
- MISSING_CAPABILITY
- MISSING_CAPABILITY_BINDING
- UNMAPPED_TOOL
- CAPABILITY_PROJECT_SCOPE_MISMATCH
- MCP_TOOL_ARGUMENT_REQUIRED
- MCP_TOOL_ARGUMENT_UNKNOWN
- MCP_TOOL_ARGUMENT_ENUM
- PACKAGE_CONTAINS_SECRET_VALUE

If a mutation happened and verification then fails, configured rollback steps run. If rollback also fails or is not safely available, the receipt becomes `FAILED_MANUAL_RECOVERY_REQUIRED`.

## Ekyc implication

When Ekyc decisions later resolve production server/domain/runtime, the system can generate execution packages for the entire GitHub + production chain.

If Ekyc selects S2 + a new subdomain, the domain/vhost/TLS/filesystem recipes will remain blocked until the corresponding generic MCP capabilities are exposed. The engine already knows exactly which capabilities are missing; it must not create broad or speculative MCP intake.

## No-regression boundary

- existing Loop Engineering remains canonical;
- current CASE 1 chronology remains canonical;
- Ekyc is not mutated by this implementation;
- Patricked-code/MCP is not modified;
- execution is source-control-plane only;
- missing MCP capabilities remain explicit blockers rather than shortcuts.

## Knowledge-driven package compiler

`scripts/governed_execution_package_compiler.py` converts a project requirement into the existing secret-free execution package.

It consumes:
- the execution registry;
- the canonical MCP capability snapshot;
- the server operation model;
- optional transient S1/S2 inventory from KBI-04C;
- optional transient GitHub secret metadata from KBI-04J.

The compiler may derive deterministic facts and bindings, but it never grants authority and never creates broad MCP intake.

Current deterministic bindings include:
- an already registered S2 project → `deploy_project_s2` with `git_status_project_s2` preflight/verification;
- S1/S2 production attestation → bounded read-only disk/runtime/domain probes.

For an unregistered project such as the current fresh Ekyc case, deployment remains blocked with `PROJECT_NOT_IN_CURRENT_MCP_DEPLOY_REGISTRY` until a governed registration capability exists or is explicitly provided.
