# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_I_B_RESOLVE_EKYC_DOMAIN_BINDING
STATE = WAITING_FOR_OWNER_DOMAIN_DECISION
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## C1-13-I-A complete

The owner correction for `BOTH` is now implemented and proven.

- Template PR #70 merged: `b1fd2ca51bc53a2502972440019bdbabb036ff7b`.
- Template post-merge Governance CI `36654687133`: PASS.
- Governed Ekyc upgrade run `36654732506`: PASS.
- Ekyc upgraded to `9ace9f9882a06df69c9466cec633bd191f7cad12` / Template v2.8.14.
- Ekyc Governance CI `36654779276`: PASS.
- Ekyc Governance Auto Bootstrap `36654779302`: PASS.
- Ekyc Governed Local Entry `36654783722`: PASS.

Migrated discovery state:

```text
transport = BOTH
routing_mode = DUAL_READY_SMART_ROUTING
selected_transport = DIRECT_MCP_TOKEN
DIRECT = PASS
SSH = CONFIGURED_NOT_ATTESTED
simultaneous_execution_required = false
reused_authorized_evidence = true
```

No new MCP discovery was required.

## Ekyc current point

```text
HEAD = 9ace9f9882a06df69c9466cec633bd191f7cad12
Ekyc#1 revision = 39
status = WAITING_FOR_SETUP_ANSWER
phase = Q_DOMAIN_BINDING
```

Fresh discovery evidence contains no `Ekyc`/`eKYC` domain and no Ekyc project registration in the current MCP scoped-project registry.

Therefore existing facts resolve the factual part:

- no existing Ekyc MCP project binding was observed;
- no existing Ekyc/KYC domain was observed in the discovered S1/S2 inventory;
- the remaining question is an owner/business decision, not a technical fact.

## Owner decision required

Choose the domain-binding intent:

1. `CREATE_NEW` — create/propose a new domain for Ekyc;
2. `EXISTING` — bind to an existing domain you explicitly designate;
3. `UNRESOLVED` — keep domain selection open for later.

No domain/server mutation occurs from this answer alone; it enriches the project model and prepares later governed work.

## Safety boundary

- Do not rerun MCP discovery merely to test BOTH routes.
- Do not patch Ekyc directly.
- Do not invent a domain without owner choice.
- P12-S6 and GMC remain downstream of P12-S5.
