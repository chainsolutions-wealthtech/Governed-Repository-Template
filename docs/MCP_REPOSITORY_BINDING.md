# MCP REPOSITORY BINDING

## Purpose

A governed repository may optionally bind to the MCP server during `FIRST_AGENT_BOOTSTRAP`.

The binding assists repository setup and infrastructure discovery. It does not grant production mutation authority.

## Direct MCP credential model

Secrets are never stored in Git.

Direct MCP mode currently uses:

- endpoint captured by the governed setup questionnaire (a `GOVERNED_MCP_URL` repository variable may override it);
- repository secret `GOVERNED_MCP_AUTH_TOKEN` for direct MCP tool calls.

The token is never printed into the issue, repository state, evidence, or logs.

## Governed SSH fallback — ephemeral certificate

SSH fallback does **not** use a persistent repository private-key secret.

The governed flow is:

```text
GitHub Actions runner
→ generate ephemeral Ed25519 keypair
→ GitHub OIDC exact repository/ref/workflow
→ MCP certificate broker
→ short-lived OpenSSH user certificate (<= 10 minutes)
→ pinned S1 host key
→ StrictHostKeyChecking=yes
→ force-command read-only gateway
```

The private key remains only in the runner's temporary directory and is destroyed with the job.

The broker accepts only the public key and returns only public certificate material plus the pinned S1 host key and observed S1 connection profile.

The repository setup records only non-secret SSH context such as host/user/port. It must cross-check that context against the authenticated broker response before connecting.

No generated repository needs or may request `GOVERNED_MCP_SSH_PRIVATE_KEY`.

## SSH authority boundary

The SSH certificate is read-only. It never grants general server WRITE authority.

The force-command gateway accepts only:

- `ping`
- `project-context`
- `list-domains-s1`
- `list-domains-s2`
- `docker-status-s1`
- `docker-status-s2`
- `write-tools-context`

Arbitrary shell, PTY, agent forwarding, X11 forwarding and port forwarding are forbidden.

Any server mutation continues to use MCP scoped-write tools after project registration and explicit authority.

## One-time MCP CA bootstrap

The SSH user CA belongs to the MCP/S1 control plane, not to generated repositories.

It is initialized once through the MCP repository's manual OIDC-gated bootstrap workflow. The private CA key remains on S1 in the non-versioned MCP keys volume and is never returned to a repository.

Until the CA exists, certificate issuance fails closed.

## First discovery

The first discovery may use direct MCP, ephemeral SSH, or both according to the selected transport.

The common evidence surface covers:

- `ping`
- `get_project_context` / SSH `project-context`
- `list_domains_s1`
- `list_domains_s2`
- `get_write_tools_context` / SSH `write-tools-context`

For `BOTH`, direct MCP evidence and SSH-certificate evidence are preserved separately so disagreements can be reconciled instead of silently collapsed.

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
