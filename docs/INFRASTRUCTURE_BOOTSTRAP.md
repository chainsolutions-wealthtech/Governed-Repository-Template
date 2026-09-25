# INFRASTRUCTURE BOOTSTRAP — Repository to deployment intent

## Principle

Infrastructure may be unknown or absent when the GitHub repository is created. Absence is represented explicitly; it is not treated as an inconsistency and must never be replaced by invented server facts.

## Planned path

```text
GITHUB_REPOSITORY
→ PROJECT_PROFILE_DISCOVERY
→ DEPLOYMENT_TARGET_DISCOVERY
→ SERVER_RESOLUTION
→ DIRECTORY_CHECK
→ PROVISION_IF_MISSING_AND_AUTHORIZED
→ REPOSITORY_SERVER_BINDING
→ DATABASE_CONFIGURATION
→ RUNTIME_CONFIGURATION
→ HEALTH_CHECKS
→ DEPLOYMENT_ATTESTATION
```

## Server access

Preferred transport: `DIRECT_MCP`.

Governed fallback: `SSH` through a GitHub OIDC-issued ephemeral certificate and a read-only force-command gateway. Persistent repository SSH private keys are forbidden.

If neither is available, state becomes `ACCESS_CONFIGURATION_REQUIRED`; agents must not fabricate a connection.

Credentials, private keys, tokens and secrets are forbidden from versioned governance files.

## Missing resources

The model supports a server, domain, directory, database or runtime that does not yet exist. Provisioning is a future governed action and requires the relevant authority.
