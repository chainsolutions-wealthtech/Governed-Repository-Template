# MCP REPOSITORY BINDING

## Purpose

A governed repository may optionally bind to an MCP server during `FIRST_AGENT_BOOTSTRAP`.

The binding is setup assistance, not automatic production authority.

## Credential model

Secrets are never stored in Git.

Preferred direct MCP mode:

- repository variable: `GOVERNED_MCP_URL`
- repository secret: `GOVERNED_MCP_AUTH_TOKEN`

Governed SSH fallback:

- `GOVERNED_MCP_SSH_PRIVATE_KEY` secret
- `GOVERNED_MCP_SSH_HOST`, `GOVERNED_MCP_SSH_USER`, `GOVERNED_MCP_SSH_PORT` variables
- arbitrary shell is forbidden; a server-side forced-command/read-only adapter is required before SSH discovery can be considered active.

## First discovery

Direct MCP discovery is read-only and calls only:

- `ping`
- `get_project_context`
- `list_domains_s1`
- `list_domains_s2`
- `get_write_tools_context`

The objective is to discover server/domain/project facts and the MCP's own controlled write surface.

## Domain resolution

After discovery, the owner chooses:

- bind to an observed existing domain;
- request creation of a new domain after explicit approval;
- leave domain unresolved.

No domain is invented.

## Project registration

A new repository is not automatically assumed to be present in MCP write allowlists. Until the MCP proves that the project is registered, project write tools remain unavailable.

## Regulatory / AfricaFunds workflow model

The reusable work loop is:

```text
READ AUTHORITIES
→ OBSERVE GITHUB HEAD
→ OBSERVE MCP/RUNTIME WHEN RELEVANT
→ RECONCILE CURRENT STATE
→ BASELINE
→ SELECT
→ IMPACT ANALYSIS
→ VERIFY HEAD
→ SINGLE WRITER
→ IMPLEMENT
→ VERIFY
→ REGRESSION CHECK
→ PERSIST STATE
→ COMMIT
→ VERIFY REMOTE
→ DEPLOY IF AUTHORIZED
→ VERIFY PRODUCTION
→ SELECT NEXT
```

GitHub is the versioned authority. The server is the runtime authority. Their equality is never assumed.
