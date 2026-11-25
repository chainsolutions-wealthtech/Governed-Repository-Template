# Matrice de traçabilité des exigences — PROPOSITIONS

> Toutes les liaisons `RQ → travaux` ci-dessous sont une hypothèse de planification à réconcilier, **pas une validation canonique**.

| Exigence | Résumé | État constaté | Pièces candidates |
|---|---|---|---|
| `RQ-01` | Mandatory pre-entry before normal repository work | LIVE_PROVEN | `IDN-006`, `CAP-001` |
| `RQ-02` | No fabricated provider identity | LIVE_PROVEN | `IDN-001`, `CAP-011` |
| `RQ-03` | Per-arrival isolated durable state | LIVE_PROVEN | `IDN-004`, `IDN-010`, `CAP-007` |
| `RQ-04` | Correlated liveness before GSE progression | LIVE_PROVEN | `IDN-006`, `CAP-009` |
| `RQ-05` | Q10 GSE must precede Q2 GACR | LIVE_PROVEN | `IDN-006`, `CAP-001` |
| `RQ-06` | F1 validates actual requested function | LIVE_PROVEN | `IDN-006`, `CAP-009` |
| `RQ-07` | Release enters normal governance exactly once | LIVE_PROVEN | `IDN-006`, `RTE-012` |
| `RQ-08` | Four structuring cases + continuation mode remain distinct | IMPLEMENTED | `GMC-G18`, `RTE-003` |
| `RQ-09` | Connection intent is separate from authority | IMPLEMENTED | `RTE-004`, `IDN-008` |
| `RQ-10` | Role is separate from authority | PARTIAL | `ARCH-005`, `IDN-007` |
| `RQ-11` | Two-stage entry purpose routing | PLANNED_NOT_ACTIVE | `RTE-001`, `RTE-004`, `RTE-011` |
| `RQ-12` | Ask only applicable unresolved questions | IMPLEMENTED_CASE1 | `RTE-007`, `RTE-012` |
| `RQ-13` | Resume without replaying completed questions | IMPLEMENTED_CASE1 | `RTE-012`, `IDN-010` |
| `RQ-14` | Owner feedback returns to earliest affected phase only | IMPLEMENTED | `GMC-G08`, `RTE-012` |
| `RQ-15` | Durable event/evidence history | IMPLEMENTED | `GMC-G11`, `ARCH-004` |
| `RQ-16` | Agent activity/continuity is queryable | IMPLEMENTED | `IDN-010`, `GMC-G12` |
| `RQ-17` | One canonical model shared by all four cases | PLANNED | `GMC-G18`, `GMC-G19` |
| `RQ-18` | No parallel truth across architecture/program/tasks/current/handoff | PARTIAL | `ARCH-006`, `GMC-G16` |
| `RQ-19` | Reusable capsule installable outside full Template | PLANNED | `CAP-001`, `CAP-012` |
| `RQ-20` | Second provider/generic adapter parity | PLANNED | `CAP-011` |
| `RQ-21` | Clean second-repository capsule installation | PLANNED | `CAP-010` |
| `RQ-22` | Deterministic relational projection | IMPLEMENTED | `GMC-G16`, `ARCH-004` |
| `RQ-23` | PostgreSQL must remain a projection, not authority | FUTURE | `ARCH-009`, `SAA-005` |
| `RQ-24` | Governance API exposes validated semantics only | FUTURE | `ARCH-008`, `SAA-002` |
| `RQ-25` | Admin UI is downstream of workflow semantics | FUTURE | `ARCH-010`, `SAA-007` |
| `RQ-26` | Client upgrades preserve mutable client state | LIVE_PROVEN_CASE1 | `CAP-008`, `GMC-G17` |
| `RQ-27` | New information enriches existing programme | IMPLEMENTED | `RTE-006`, `GMC-G02` |
| `RQ-28` | Every meaningful interruption has checkpoint/handoff | IMPLEMENTED | `IDN-010`, `GMC-G11` |
| `RQ-29` | Complete autonomous admin cockpit | PLANNED | `SAA-007`, `SAA-008`, `SAA-009` |
| `RQ-30` | Full versioned REST/OpenAPI API | PLANNED | `SAA-002`, `SAA-006` |
| `RQ-31` | Governed backend service/microservice architecture | PLANNED | `SAA-003`, `SAA-006` |
| `RQ-32` | SaaS-ready tenancy/isolation | PLANNED | `SAA-001`, `SAA-004`, `SAA-010` |
| `RQ-33` | Reproducible production deployment | PLANNED | `SAA-011`, `SAA-012`, `SAA-013` |
| `RQ-34` | Production URL mcp.wealthtechinnovations.com/template | PLANNED | `SAA-013` |
| `RQ-35` | Operational backup/restore/upgrade/rollback | PLANNED | `SAA-010`, `SAA-015` |

Une traçabilité complète devra ajouter : `requirement_id → deliverable_id → task_id → sprint_id → event_id → evidence_id → acceptance_id → release_id`, avec cardinalités réelles. Les livrables et validations non encore enregistrés ne reçoivent pas d’ID prétendu canonique.
