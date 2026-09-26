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

### Automatic direct MCP credential provisioning — V2.6.3

For repositories created or managed through the central control plane, the direct MCP token is provisioned automatically when the local first-agent state reaches the exact `CREDENTIAL_GATE`.

The central control plane:

1. verifies the target repository, local-entry issue and exact HEAD;
2. verifies that the pending requirement is specifically `GOVERNED_MCP_AUTH_TOKEN`;
3. mints a short-lived target-owner GitHub App installation token with repository `Secrets: write` plus the minimum read/dispatch permissions required by the flow;
4. writes the central `GOVERNED_MCP_AUTH_TOKEN` into the target repository as an Actions secret using GitHub's encrypted secret API path;
5. verifies only the target secret metadata;
6. dispatches the existing machine `execute` command so local discovery can continue.

The source secret value must never appear on a command line, in Git, issue comments, state markers, evidence, or logs.

For `DIRECT_MCP_TOKEN`, if the central secret is unavailable, the flow stops without advancing governed state. For `BOTH`, the direct token remains preferred, but its absence may defer direct credential provisioning and continue only through the governed GitHub OIDC SSH read-only discovery path. Missing target GitHub App permissions, HEAD mismatch, or an unsupported credential contract still fail closed.

This is a one-time control-plane configuration pattern: the control plane holds the MCP credential centrally so future governed repositories do not require manual secret copying.

For `BOTH`, provisioning is opportunistic: every governed local command may reconcile the target repository secret. If the central credential exists, it is written/attested before dispatch even when the session has already advanced beyond the historical credential gate. If it is absent, `BOTH` may continue only through the governed SSH OIDC read-only fallback.

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

If the direct credential is unavailable, `BOTH` may continue initial read-only discovery through the SSH OIDC path. In that case:
- direct evidence is recorded as `UNAVAILABLE_CREDENTIAL`;
- SSH evidence must independently provide usable `PASS` or `PARTIAL` discovery evidence;
- the combined discovery is always `PARTIAL` and marked degraded;
- no direct MCP success is inferred;
- no MCP write authority is granted by the fallback.

## Discovery failure and retry

A discovery failure on an exact current HEAD is persisted into the local governed issue instead of existing only in Actions logs.

The persisted evidence includes a stable non-secret failure code, transport, observed time and any already-observed component evidence. The local state remains retryable at `MCP_DISCOVERY`.

Examples include:
- `SSH_CERTIFICATE_BROKER_FORBIDDEN`;
- `SSH_CERTIFICATE_BROKER_UNREACHABLE`;
- `MCP_DIRECT_CREDENTIAL_MISSING`;
- required probe failures.

A later `/local-execute` may retry read-only discovery on the same exact governed state. Retry does not widen authority. A `HEAD_MOVED` condition remains fail-closed and is not persisted as if it were an external discovery failure.

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
