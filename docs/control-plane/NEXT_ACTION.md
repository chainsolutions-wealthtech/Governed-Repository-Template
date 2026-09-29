# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_H_VALIDATE_PERSISTENT_MCP_CAPABILITY_SNAPSHOT
STATE = FRAMEWORK_VALIDATION_REQUIRED
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Ekyc return point

The generic signed-SSH recovery is proven end-to-end:

- Template v2.8.8 merge: `7bb1199f5b7683003fa62c373a211d0736b67908`.
- Template post-merge Governance CI: `36645221136` PASS.
- Ekyc governed upgrade: `4d552458afab32df12aaafd6c7290fab6246d96b`.
- Ekyc Governance CI: `36645315558` PASS.
- Ekyc discovery retry: `36645372827`.
- Recovery state: `Q_SSH_PROFILE_RECOVERY`, revision 37.
- Signed broker evidence was used to correct the factual SSH profile through central command `5901027821`.
- Ekyc#1 is now revision 38 at `WAITING_FOR_DISCOVERY_APPROVAL / MCP_DISCOVERY_APPROVAL`.
- Because the SSH target materially changed, prior discovery approval is invalidated.
- First-agent baseline remains unapplied.

## Active Template work — C1-13-H

Validate the new persistent source-only MCP capability memory:

1. validate `CP-MCP-CAP-001` human and machine authorities;
2. validate source-only removal from generated/adopted clients;
3. validate the read-only refresh script and no-secret/no-server-coordinate persistence;
4. validate case → tool → required-authority planning;
5. validate that the model feeds the existing Loop Engineering rather than a parallel engine;
6. merge only after full Governance CI;
7. trigger one live source-only refresh from the Template;
8. verify the refresh opens a governed PR with the current MCP catalogue/resource image;
9. merge the refreshed snapshot only after its Governance CI.

## Separate Ekyc gate

The corrected BOTH plan is ready but requires explicit owner approval because its SSH target changed materially. Capability-snapshot validation does not grant or infer that approval.

## Safety boundary

- No MCP mutation.
- No new MCP intake.
- No direct Ekyc patch.
- No persisted server connection coordinates in the public Template snapshot.
- No secret value persistence.
- Snapshot/tool availability does not imply write authority.
- P12-S6 and GMC remain downstream of P12-S5.
