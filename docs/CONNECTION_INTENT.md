# CONNECTION INTENT — Why an agent is here

## Principle

A connection identity does not imply permission to code.

Every governed session has an intent:

- `OBSERVE`
- `CONTEXT_INTAKE`
- `INFORMATION_INTAKE`
- `WORK_REQUEST`
- `CODE_CHANGE`
- `REVIEW`
- `INFRASTRUCTURE`
- `UNKNOWN`

`UNKNOWN` fails closed.

## Routing

```text
OBSERVE             → observe only
CONTEXT_INTAKE      → intake
INFORMATION_INTAKE  → intake
WORK_REQUEST        → reconcile, then dispatch
CODE_CHANGE         → reconcile, then dispatch
REVIEW              → observe/review; no mutation by default
INFRASTRUCTURE      → infrastructure discovery, then governed dispatch
UNKNOWN             → resolve intent before mutable work
```

## Invariants

`CONTEXT_INTAKE != CODE_PERMISSION`

`INFORMATION_INTAKE != CODE_PERMISSION`

`INTENT != AUTHORITY`

Even a mutable intent does not grant production, secret, server, legal, financial or destructive authority.
