# IDENTITY, CREDENTIAL AND SECRET LIFECYCLE

Authority: `CP-IDENTITY-SECRET-001`

The governed platform has two operational planes:

```text
GITHUB PLANE
      ↕
IDENTITY / CREDENTIAL / SECRET LIFECYCLE
      ↕
SERVER / PRODUCTION PLANE
```

A project is not operationally complete merely because the repository and server exist. The Control Plane must understand **which identity is allowed to perform each action, how the needed credential is obtained or created, where it is injected, how it is verified, rotated and revoked**.

No secret value is persisted in canonical knowledge.

## GitHub plane

The model includes:

- GitHub App installation tokens, minted per target owner/repository;
- GitHub Actions repository secrets;
- GitHub Actions environment secrets;
- GitHub OIDC identities;
- deploy keys only when a short-lived/provider-native identity cannot satisfy the requirement;
- fine-grained GitHub tokens only as a bounded fallback;
- MCP auth token provisioning into target repository secrets;
- permissions required for repository creation, contents, workflows, PRs, secrets, webhooks, deployments and rulesets.

The preferred pattern is:

```text
standing GitHub App / trust configuration
→ mint short-lived installation token
→ perform exact scoped operation
→ discard token
```

For workflow-to-server identity:

```text
GitHub Actions
→ OIDC identity
→ trusted broker/provider
→ short-lived downstream credential
→ operation
→ expiry
```

## Server / production plane

The model includes:

- ephemeral SSH certificates;
- scoped server service accounts;
- application environment secrets;
- database roles/credentials;
- DNS-provider credentials;
- TLS private-key lifecycle under a certificate manager;
- runtime secret references;
- secret injection to Docker/PM2/systemd/application environments;
- rotation and revocation.

The Control Plane should know **how** each credential is created/retrieved without necessarily knowing its value.

Example:

```text
DATABASE_CREDENTIAL
→ database target known
→ derive least-privilege role
→ create role
→ generate credential
→ store in secure source
→ bind secret reference to application
→ test connection
→ never print credential
```

## Secret retrieval

“Know how to retrieve the secret” means knowing the authorized secure retrieval path:

```text
secret requirement
→ secret reference / provider
→ authority
→ runtime fetch or mint
→ inject only into consuming process
→ verify behavior
→ discard ephemeral material
```

It does not mean copying secret values into Git, issues, checkpoints, logs or the knowledge base.

## Creation, rotation and revocation

Every credential type has a full lifecycle:

```text
REQUIREMENT
→ REUSE existing valid credential/reference
   OR CREATE/MINT
→ INJECT
→ VERIFY without readback
→ ROTATE when needed
→ REVOKE when obsolete
→ persist metadata/evidence only
```

## Ekyc example

If Ekyc later becomes:

```text
GitHub repo
+ production S2
+ subdomain
+ PostgreSQL
+ governed deployment
```

the derived access plan can include:

- GitHub App installation token for repository administration/workflows;
- repository/environment secrets needed by CI/CD;
- DIRECT MCP token if that route is selected;
- GitHub OIDC → ephemeral SSH certificate for server access;
- S2 application service identity;
- PostgreSQL least-privilege application role and credential;
- DNS provider credential if DNS mutation is external/API-based;
- TLS certificate/key handled by the certificate manager;
- runtime environment secret references;
- rotation/revocation recipes for every persistent credential.

The system can then tell whether each item is:

`REUSE | CREATE | MINT | ROTATE | VERIFY | REVOKE | NOT_REQUIRED`.

## Incremental continuation

This slice only consolidates the model and recipes.

Next small slices:

- `KBI-04J` — read-only GitHub capability/secret-metadata mapping;
- `KBI-04K` — read-only S1/S2 identity/secret-store mapping;
- `KBI-04L` — E2E dry-run project → complete GitHub + server credential plan;
- `KBI-04M` — later bind provisioning/rotation/revocation to Loop Engineering under AuthorityEnvelope.

### KBI-04J — collector implemented; live metadata pending

`scripts/control_plane_github_secret_metadata.py` reads repository metadata,
repository secret names/timestamps, organization secrets shared with that
repository, deployment environment names and their secret names/timestamps. It
uses only bounded GitHub REST `GET` requests and emits allowlisted metadata to
stdout. A denied or incomplete listing stays unknown or partial; successful
read access never asserts write capability or grants execution authority.

Run from the control-plane source with a GitHub read token in the process
environment:

```bash
python3 scripts/control_plane_github_secret_metadata.py --repository OWNER/REPO
```

`GOVERNED_GITHUB_READ_TOKEN` is preferred; `GH_TOKEN` is also accepted. The
token and raw API responses are not stored. This environment did not expose a
GitHub API token to the collector, so live secret metadata remains pending.
Further server identity discovery is `KBI-04K` and is not inferred here.
