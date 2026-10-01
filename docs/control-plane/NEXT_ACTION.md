# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_I_B_C_SPLIT_SERVER_SCOPED_DOMAIN_CHOICES
STATE = GENERIC_FRAMEWORK_CORRECTION
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Owner decision captured

The owner selected `S1` as the production-server target for Ekyc.

Governed evidence:

- source command: central issue #49 comment `5933064109`;
- Control Plane run `36873298229`: governed command dispatch accepted;
- Ekyc local-entry run `36873334194`: PASS;
- Ekyc HEAD remained `b67a4ec58d837a66f3c3dedb02caadaf044912d5`;
- Ekyc#1 advanced revision `40 → 41`;
- `production_server_selection = S1`;
- no server/domain mutation occurred.

## Generic correction now required

The legacy next question is still one coarse `domain_binding` object. The owner requires a progressive choice chain.

Target generic flow:

```text
S1 selected
→ choose DOMAIN_INTENT
→ reuse S1 observed domains
→ choose existing domain or parent when applicable
→ choose label/name
→ derive structured domain_binding
→ derive future operation/capability requirements
→ no execution authority
```

Domain-intent choices:

- `REUSE_EXISTING_DOMAIN`
- `CREATE_SUBDOMAIN`
- `CREATE_NEW_ROOT_DOMAIN`
- `CREATE_CHILD_DOMAIN`
- `NO_PUBLIC_DOMAIN`
- `DECIDE_LATER`

## Safety boundary

- Do not patch Ekyc directly.
- Do not rerun MCP discovery.
- Do not mutate S1 from the S1 choice.
- Preserve already answered legacy domain bindings in other repositories.
- Domain choices prepare work only; they do not authorize DNS/vhost/TLS/server writes.
- P12-S6 and GMC remain downstream of P12-S5.
