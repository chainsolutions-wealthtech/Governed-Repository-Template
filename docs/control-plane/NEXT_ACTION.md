# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_I_B_A_FIX_FRESH_PROJECT_SERVER_BEFORE_DOMAIN_ORDER
STATE = GENERIC_FRAMEWORK_CORRECTION
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Owner sequencing correction

A fresh project with no existing infrastructure binding must not jump from MCP discovery directly to a domain decision.

Canonical order:

```text
read-only discovery
→ show observed server candidates
→ owner chooses production server
→ reuse selected-server domain inventory
→ continue domain planning
```

This is additive to the existing adaptive questionnaire and Loop Engineering.

## Ekyc evidence

```text
repository = Patricked-code/Ekyc
HEAD = 9ace9f9882a06df69c9466cec633bd191f7cad12
issue = Ekyc#1
revision = 39
architecture = NEW_EMPTY_PROJECT
infrastructure = UNKNOWN_TO_DISCOVER
current legacy phase = Q_DOMAIN_BINDING
observed server candidates = S1, S2
domain binding answer = absent
```

The generic Template correction must migrate this state to `Q_PRODUCTION_SERVER_SELECTION` without replaying discovery or losing prior answers.

## Safety boundary

- Fix Template first.
- Do not patch Ekyc directly.
- Do not rerun MCP discovery.
- Server choice is not mutation authority.
- Existing project/adoption behavior must remain unchanged.
- After merge/CI, upgrade Ekyc only through the governed Template upgrade path.
- P12-S6 and GMC remain blocked behind P12-S5.
