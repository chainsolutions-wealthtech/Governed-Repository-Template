# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_I_B_B_SELECT_EKYC_PRODUCTION_SERVER
STATE = WAITING_FOR_OWNER_PRODUCTION_SERVER_DECISION
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## C1-13-I-B-A complete

The generic fresh-project ordering defect is fixed and proven.

- Template PR #88 merged at `c41afa4fdeffd5f12d6243b95f5d04083ca514e4`.
- PR #88 Governance CI `36869361015`: PASS.
- Post-merge Governance CI `36869476595`: PASS.
- Governed Ekyc upgrade run `36869574238`: PASS.
- Ekyc upgraded to `b67a4ec58d837a66f3c3dedb02caadaf044912d5` / Template v2.8.25.
- Ekyc Governance CI `36869667945`: PASS.
- Ekyc Governance Auto Bootstrap `36869667894`: PASS.
- Ekyc Governed Local Entry `36869671044`: PASS.

## Ekyc exact current state

```text
repository = Patricked-code/Ekyc
HEAD = b67a4ec58d837a66f3c3dedb02caadaf044912d5
issue = Ekyc#1
revision = 40
status = WAITING_FOR_SETUP_ANSWER
phase = Q_PRODUCTION_SERVER_SELECTION
observed servers = S1, S2
choices = S1 | S2 | PLAN_NEW_SERVER | DECIDE_LATER
domain binding = unanswered
discovery replay = not required
execution authority = not granted
```

Prior MCP evidence is preserved:

```text
transport = BOTH / DUAL_READY_SMART_ROUTING
selected route = DIRECT_MCP_TOKEN
DIRECT = PASS
SSH alternate = CONFIGURED_NOT_ATTESTED
```

## Owner decision required

Choose the production-server intent for Ekyc:

- `S1`
- `S2`
- `PLAN_NEW_SERVER`
- `DECIDE_LATER`

This answer only enriches the project model. It does not create directories, domains, DNS, TLS, runtime resources or deployment state.

After a concrete S1/S2 choice, the next questionnaire slice must reuse that server's observed domain inventory before asking domain/subdomain questions.

## Safety boundary

- Do not rerun MCP discovery.
- Do not patch Ekyc directly.
- Do not infer server choice.
- Do not mutate S1/S2 from this answer alone.
- P12-S6 and GMC remain downstream of P12-S5.
