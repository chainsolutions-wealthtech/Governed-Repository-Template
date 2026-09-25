# AUTOMATION — Generic governed automation

## Objective

A repository instantiated from this template should require no manual bootstrap command when an allowed GitHub event starts the bootstrap workflow.

The automation is additive. The existing deterministic scripts remain the recovery and manual fallback path.

## Bootstrap event surface

`.github/workflows/governance-auto-bootstrap.yml` accepts:

- a push on `main`;
- a branch create event;
- `workflow_dispatch`;
- `repository_dispatch` with type `governance-bootstrap`.

The template repository itself is explicitly excluded from mutation.

For fully zero-touch organization-wide creation, an organization GitHub App or equivalent trusted orchestrator may emit `repository_dispatch` after a repository is created from this template.

## Automatic sequence

```text
DETECT_TEMPLATE_INSTANCE
→ INFER_REPOSITORY_METADATA
→ INITIALIZE_GOVERNANCE
→ VALIDATE
→ CREATE_INITIALIZATION_COMMIT
→ FINALIZE_BOOTSTRAP_RECEIPT
→ VALIDATE_AGAIN
→ CREATE_ATTESTATION_COMMIT
→ PUSH
→ DISCOVER_PROJECT_BASELINE
```

## Fail closed

The workflow must stop instead of guessing when:

- repository identity is unavailable;
- the template repository itself is targeted;
- validation fails;
- a protected branch rejects the push;
- a required permission is missing.

No workflow failure implies permission to weaken governance.

## Idempotency

If `.template-source` is absent and `.governance/profile.json` is already initialized, bootstrap does not recreate state.

## Authority

Automation does not grant production, legal, compliance, financial, infrastructure or destructive permissions.
