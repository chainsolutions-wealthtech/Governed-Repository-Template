# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_I_B_E_SELECT_EKYC_WORKFLOW_MODEL
STATE = WAITING_FOR_OWNER_WORKFLOW_MODEL
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## C1-13-I-B-D complete

The Ekyc domain-intent chain has advanced without granting execution authority.

- Owner selected `CREATE_NEW_ROOT_DOMAIN`.
- Ekyc#1 advanced to revision 43 / `Q_DOMAIN_ROOT_NAME_MODE`.
- Owner selected `DISCOVER_AVAILABLE_NAMES`.
- Ekyc#1 advanced to revision 44 / `Q_WORKFLOW_MODEL`.
- No domain registration, DNS, Plesk/vhost, TLS or S1 mutation occurred.

## Existing-host HTTP path capability

The owner clarified that a future project may also reuse an existing domain or subdomain under an HTTP path such as `/ekyc`.

That generic capability is now part of the Template:

- PR #92 merged at `8143db05b8ed412bdbc3d710f4a1fdf49f652161`;
- Template version: `2.8.27`;
- post-merge Governance CI `36880059834`: PASS;
- DNS host binding and HTTP deployment path are separate facts;
- supported mount modes: `HOST_ROOT | CREATE_PATH | REUSE_EXISTING_PATH | DECIDE_LATER`;
- `CREATE_PATH` prepares `CONFIGURE_REVERSE_PROXY` but grants no execution authority.

The current Ekyc choice remains `CREATE_NEW_ROOT_DOMAIN → DISCOVER_AVAILABLE_NAMES`; this generic extension does not change it.

## Ekyc exact current state

```text
repository = Patricked-code/Ekyc
HEAD = 4bf80309313f3d34f74ffca183bd540583d2e87f
issue = Ekyc#1
revision = 45
status = WAITING_FOR_SETUP_ANSWER
phase = Q_WORKFLOW_MODEL
production_server_selection = S1
domain_intent = CREATE_NEW_ROOT_DOMAIN
domain_root_name_mode = DISCOVER_AVAILABLE_NAMES
execution authority = false
```

Governed v2.8.27 upgrade evidence:

- Control Plane run `36880153919`: PASS.
- Ekyc Governance CI `36880223661`: PASS.
- Ekyc Governance Auto Bootstrap `36880223820`: PASS.
- Ekyc Governed Local Entry `36880228405`: PASS.
- Prior business/setup answers were preserved.

## Owner decision required

Choose the workflow model:

- `REGULATORY_AFRICAFUNDS_GOVERNED_FLOW`
- `STANDARD_GOVERNED_FLOW`

This answer selects the work model only. It does not authorize infrastructure or runtime mutation.

## Safety boundary

- Do not replay MCP discovery.
- Do not patch Ekyc directly.
- Do not mutate S1, DNS, Plesk/vhosts or TLS from a questionnaire answer.
- Preserve the current domain decision unless the owner explicitly changes it.
- P12-S6 and GMC remain downstream of P12-S5.
