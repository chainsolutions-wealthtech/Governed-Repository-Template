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
→ VERIFY_ATTESTATION_PARENT_RELATION
→ PUSH
→ VERIFY_REMOTE_ATTESTATION_HEAD
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

## Bootstrap attestation semantics

The initialization commit is the immutable subject being attested.

The following versioned fields therefore reference the initialization commit:

- `.governance/bootstrap-receipt.json.initialization_commit_sha`;
- `.governance/bootstrap-receipt.json.attestation_subject_sha`;
- `.governance/bootstrap-state.json.attested_initialization_commit_sha`;
- `.governance/canonical-memory/current.json.bootstrap_attestation_subject_sha`.

The attestation commit is the Git child commit that contains the finalized `PASS` state. It must not attempt to embed its own SHA: doing so would be self-referential because changing the committed content changes the commit SHA.

The workflow proves the relationship externally and deterministically:

```text
INITIALIZATION_COMMIT
        ↓ parent of
ATTESTATION_COMMIT
        ↓ equals
REMOTE_HEAD_AFTER_PUSH
```

`STATUS.md` is finalized to `PASS / ATTESTED` before the attestation commit and is committed together with the machine-readable governance state.

The strict check `python3 scripts/validate_governance.py --bootstrap-attestation` is used during zero-touch bootstrap. Normal repository validation remains compatible with later project evolution after the bootstrap phase.
