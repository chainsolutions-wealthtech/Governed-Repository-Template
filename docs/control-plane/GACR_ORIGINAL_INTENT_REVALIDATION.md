# GACR Original Intent Formal Revalidation

> Programme: GACR — Governed Agent Continuity Relay
>
> Gate: REALIGNMENT STEP 2
>
> Result: PASS / CLOSED
>
> Observed main HEAD: `6a32debcc96d7c33b421dc901c514f79a4d05104`
>
> Canonical historical-intent source: `docs/control-plane/GACR_ORIGINAL_INTENT.md`
>
> Source blob SHA: `29a4f35bda44132c6113ba2569e9ba70f2945212`

## 1. Purpose

This attestation closes the mandatory Step 2 formal gate by revalidating the already-canonical GACR historical intention. It does not rewrite, replace or reinterpret the historical source.

## 2. Revalidated invariants

The following remain authoritative:

- governed work continuity must survive disappearance of a provider conversation, tab, client or agent;
- provider conversations are temporary clients rather than the continuity authority;
- the two historical external limits remain richer automatic identification/correlation and actual relay/activation of compatible standby capacity;
- the intended additive architecture remains `BEACON → WATCH → CORRELATOR → DISPATCHER`;
- the Connection Envelope remains a required safe operational representation;
- `connection_fingerprint` remains an operational-correlation mechanism and is never a provider conversation identity;
- correlation quality remains explicit: `EXACT / STRONG / PROBABLE / AMBIGUOUS / UNKNOWN`;
- provider-private facts that were not supplied remain unavailable and must never be invented;
- optional Bridge/provider adapters may enrich or wake only where the provider exposes a real capability;
- Agent Context must permit deterministic reconstruction/resume;
- claims, collision domains and exact-HEAD reconciliation remain authoritative for mutable takeover;
- safe observability excludes secrets, tokens, cookies, raw transcript bodies and private reasoning;
- GACR is distinct from the global Control Plane programme and has no dependency edge from `P12-S6`;
- origin realignment cannot be declared complete before the ultimate live fresh-agent → stall → second-agent → exact-HEAD takeover → continuation scenario passes.

## 3. Non-regression boundary

This gate performs governance revalidation only. It changes no runtime, workflow, script, schema, claim/lock model, deployment or production state. R1–R6/R5-A/R6-A/R6-B/R6-C remain preserved.

## 4. Gate decision

`REALIGNMENT_STEP_2_FORMAL_GATE_REVALIDATE_EXISTING_GACR_ORIGINAL_INTENT = PASS / CLOSED`.

The historical intent source is unchanged. Step 3 — `ORIGINAL_INTENT ↔ CURRENT_IMPLEMENTATION ↔ GAP` — is now authorized.
