# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_I_B_D_SELECT_EKYC_DOMAIN_INTENT
STATE = WAITING_FOR_OWNER_DOMAIN_INTENT
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## C1-13-I-B-C complete

The progressive server-scoped domain question chain is implemented and proven.

- Template PR #90 merged at `1aed2d8f1646ca4ebc6208a6c692ec8eac7d20a4`.
- PR #90 Governance CI `36874806040`: PASS.
- Post-merge Governance CI `36874904197`: PASS.
- Governed Ekyc upgrade `36875001892`: PASS.
- Ekyc upgraded to `5681e6f0815275797514ef62359ea258eb93b705` / Template v2.8.26.
- Ekyc Governance CI `36875104777`: PASS.
- Ekyc Governance Auto Bootstrap `36875104910`: PASS.
- Ekyc Governed Local Entry `36875114901`: PASS.

## Ekyc exact current state

```text
repository = Patricked-code/Ekyc
HEAD = 5681e6f0815275797514ef62359ea258eb93b705
issue = Ekyc#1
revision = 42
status = WAITING_FOR_SETUP_ANSWER
phase = Q_DOMAIN_INTENT
production_server_selection = S1
execution authority = false
```

The authorized S1 domain inventory is reused; no MCP discovery replay occurred.

Observed S1 parent-domain candidates:

- `berebytours.com`
- `niakara.com`
- `wealthtechinnovation.com`
- `wealthtechinnovations.com`

## Owner decision required

Choose the domain intent:

- `REUSE_EXISTING_DOMAIN`
- `CREATE_SUBDOMAIN`
- `CREATE_NEW_ROOT_DOMAIN`
- `CREATE_CHILD_DOMAIN`
- `NO_PUBLIC_DOMAIN`
- `DECIDE_LATER`

The answer only enriches the project model and determines the next choice/capability preparation. It does not mutate S1, DNS, Plesk/vhosts or TLS.

## Safety boundary

- Do not rerun MCP discovery.
- Do not patch Ekyc directly.
- Do not mutate S1 from a domain-intent answer alone.
- Reuse the current S1 inventory for subsequent choices.
- P12-S6 and GMC remain downstream of P12-S5.
