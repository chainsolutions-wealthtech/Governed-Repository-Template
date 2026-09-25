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


## Post-bootstrap capability discovery

V2.1 adds a non-destructive intent layer after governance bootstrap:

```text
BOOTSTRAP_ATTESTED
→ PROJECT_PROFILE_DISCOVERY
→ INFRASTRUCTURE_DISCOVERY
→ CONNECTION_INTENT_RESOLUTION
→ PROJECT_BASELINE
→ MUTABLE_WORK
```

Zero-touch creation does not provision infrastructure by itself. It records that a server, domain, directory or database may be absent and preserves a governed future provisioning path.

An explicitly supplied project profile can be passed to initialization. Without one, profile selection remains `DISCOVERY_REQUIRED`.


## Central control plane lifecycle

```text
REQUEST_CREATED
→ WAITING_FOR_ANSWER
→ PLAN_READY
→ WAITING_FOR_PLAN_APPROVAL
→ EXECUTING_PREPARATION
→ HANDOFF_READY
```

Any denied authority, failed evidence or contradiction transitions to `HOLD_FOR_REVIEW`.

GitHub issues provide persistence for the interactive request. The issue workflow never writes to another repository. Cross-repository observations and authorized mutations are executed by the connected agent and returned as structured evidence.

One state transition exposes exactly one next question, one targeted agent request, one action request, or the final handoff.


## Repository-local agent entry

Initialized target repositories include `.github/workflows/governed-local-entry.yml`. It accepts a local-entry issue or `repository_dispatch: governed_local_start`, persists one-question-at-a-time state in the issue, and applies the approved first-agent baseline under an exact-HEAD guard. The central template repository itself is excluded from local execution.
