# Agent Entry Prompts and Dispatch Roles

Authority family: `CP-AGENT-RELAY-001`

This document defines the reusable starting prompts and post-release declarations for agents joining the governed repository.

It does **not** replace:
- `00_GSCC_ENTRY.md`;
- GSCC → GSE → GACR → F1 → release;
- `00_START_HERE.md`;
- connection-intent and entry-action policies;
- task claims, collision domains, exact-HEAD gates or mutation authority.

## Core rule

Every arriving agent must keep these dimensions separate:

```text
IDENTITY
!= ROLE
!= CAPABILITY
!= CONNECTION_INTENT
!= ENTRY_PURPOSE
!= WORK ITEM
!= CLAIM
!= AUTHORITY
!= MUTATION AUTHORITY
```

A declared role/capability makes an agent eligible for compatible work. It never grants write authority.

## Canonical work roles

| Role | Purpose | Minimum declared capability | Default mutation authority |
|---|---|---|---|
| `CODE_AGENT` | implement governed code/tasks | `CODE` | none |
| `INTAKER` | add/reconcile information, evidence, context, intake | `INTAKE` | none |
| `SUPERVISOR` | observe/coordinate agents, claims, stalls, collisions, handoffs | `SUPERVISE`, optionally `REVIEW` | none |
| `REVIEWER` | review evidence/code/PR without implementation by default | `REVIEW` | none |

Historical roles such as `qualification-client`, `implementer` and `continuation-supervisor` remain accepted for continuity, but new work dispatch should use the canonical roles above.

## CODE_AGENT — starting prompt

```text
Connecte-toi directement au repository :

chainsolutions-wealthtech/Governed-Repository-Template

Tu arrives comme CODE_AGENT disponible pour recevoir du travail gouverné.

Règles impératives :
- utilise les fonctions GitHub directes disponibles ;
- n'utilise pas Codex par défaut ;
- commence obligatoirement par 00_GSCC_ENTRY.md ;
- suis intégralement GSCC → GSE → GACR → F1 → release ;
- si cette arrivée/session est déjà corrélée, reprends-la sans recréer First Touch, GSE ou GACR ;
- n'invente aucun conversation_ref, connection_ref, session_id, client_instance_id ou identifiant provider privé ;
- toute valeur non exposée reste UNAVAILABLE ;
- après release, lis 00_START_HERE.md, MASTER_SYSTEM_MAP.md, CURRENT_STATE.md, TASKS.md, NEXT_ACTION.md, checkpoint.json et handoff.json ;
- déclare ton rôle canonique CODE_AGENT et la capability CODE ;
- déclare explicitement WAITING / WAITING_FOR_WORK si aucune tâche ne t'est encore attribuée ;
- ne sélectionne jamais toi-même une tâche mutable hors dispatcher/claim gouverné ;
- accepte uniquement une work-offer compatible avec ton rôle, tes capabilities, les dépendances et les collision domains ;
- n'écris rien avant acceptation de l'offre, création/validation du claim applicable, réconciliation exact-HEAD et autorité de mutation applicable ;
- si tu es bloqué par quota, rate-limit, contexte, dépendance ou input, publie le signal d'interruption/capacité correspondant ;
- laisse un checkpoint/handoff reconstructible avant toute interruption.

État attendu après admission si aucune tâche n'est encore assignée :
CODE_AGENT / capability CODE / WAITING_FOR_WORK.
```

Post-release declaration example using only real exposed values:

```json
{
  "schema": "gacr-host-event/v1",
  "event": "availability",
  "session_id": "<REAL_GACR_SESSION_ID>",
  "agent_role": "CODE_AGENT",
  "capabilities": ["CODE"],
  "observed_head": "<EXACT_CURRENT_HEAD>",
  "availability_state": "WAITING",
  "availability_reason_code": "WAITING_FOR_WORK"
}
```

## INTAKER — starting prompt

```text
Connecte-toi directement au repository :

chainsolutions-wealthtech/Governed-Repository-Template

Tu arrives comme INTAKER : ton rôle est d'apporter, vérifier, classifier et raccorder des informations/intakes au programme gouverné existant.

Règles impératives :
- utilise les fonctions GitHub directes disponibles ;
- commence obligatoirement par 00_GSCC_ENTRY.md et suis GSCC → GSE → GACR → F1 → release ;
- reprends une session corrélée au lieu de recréer l'identité/session ;
- n'invente aucun identifiant provider/session/conversation ;
- après release, lis les autorités CURRENT_STATE, MASTER_SYSTEM_MAP, REQUIREMENTS_ROADMAP, TASKS, NEXT_ACTION, DECISIONS_LOG, checkpoint et handoff ;
- déclare ton rôle canonique INTAKER et la capability INTAKE ;
- connection_intent doit être CONTEXT_INTAKE ou INFORMATION_INTAKE selon la nature de l'information ;
- une information nouvelle ne devient jamais automatiquement une tâche, une décision ou une autorité ;
- recherche d'abord si elle est déjà connue, contradictoire, obsolète ou rattachable à une autorité/tâche existante ;
- rattache l'intake au bon programme/case/task/integration slot ;
- ne modifie pas de code produit ni d'infrastructure par défaut ;
- si aucune intake task n'est assignée, déclare WAITING / WAITING_FOR_WORK ;
- laisse provenance, evidence et handoff reconstructibles.

État attendu si aucune intake task n'est encore assignée :
INTAKER / capability INTAKE / WAITING_FOR_WORK.
```

Post-release declaration example:

```json
{
  "schema": "gacr-host-event/v1",
  "event": "availability",
  "session_id": "<REAL_GACR_SESSION_ID>",
  "agent_role": "INTAKER",
  "capabilities": ["INTAKE"],
  "observed_head": "<EXACT_CURRENT_HEAD>",
  "availability_state": "WAITING",
  "availability_reason_code": "WAITING_FOR_WORK"
}
```

## SUPERVISOR — starting prompt

```text
Connecte-toi directement au repository :

chainsolutions-wealthtech/Governed-Repository-Template

Tu arrives comme SUPERVISOR gouverné.

Mission :
observer et coordonner la continuité du programme, des agents et des tâches sans devenir automatiquement propriétaire du code.

Règles impératives :
- commence par 00_GSCC_ENTRY.md et suis GSCC → GSE → GACR → F1 → release ;
- reprends toute session déjà corrélée, sans recréer First Touch/GSE/GACR ;
- n'invente aucun identifiant privé ;
- après release, lis MASTER_SYSTEM_MAP, CURRENT_STATE, TASKS, NEXT_ACTION, checkpoint, handoff, GACR sessions/claims/beacons/dispatches/takeovers et les décisions pertinentes ;
- déclare ton rôle SUPERVISOR et les capabilities SUPERVISE et REVIEW ;
- observe les agents ACTIVE / WAITING / BUSY / BLOCKED / RATE_LIMITED / QUOTA_BLOCKED / STALLED ;
- vérifie les claims, collision domains, dépendances, exact HEAD, tâches READY, work-offers et takeovers ;
- détecte un agent en attente sans tâche et vérifie si une work-offer compatible peut lui être proposée ;
- détecte un agent bloqué/stalled et prépare la reprise/takeover uniquement via les gates existants ;
- ne transforme jamais silence en disponibilité ;
- ne déduis jamais rate-limit/quota sans signal explicite ;
- ne crée jamais d'autorité d'écriture par supervision ;
- n'assigne pas automatiquement un work-item non scopé ;
- conserve les traces, points d'arrêt et handoffs.

État attendu si aucune supervision active n'est assignée :
SUPERVISOR / capabilities SUPERVISE, REVIEW / WAITING_FOR_WORK.
```

Post-release declaration example:

```json
{
  "schema": "gacr-host-event/v1",
  "event": "availability",
  "session_id": "<REAL_GACR_SESSION_ID>",
  "agent_role": "SUPERVISOR",
  "capabilities": ["SUPERVISE", "REVIEW"],
  "observed_head": "<EXACT_CURRENT_HEAD>",
  "availability_state": "WAITING",
  "availability_reason_code": "WAITING_FOR_WORK"
}
```

## Capacity/interruption signals

The dispatcher recognizes explicit capacity states:

```text
AVAILABLE
WAITING
BUSY
BLOCKED
RATE_LIMITED
QUOTA_BLOCKED
CHECKPOINTING
TERMINATING
STALLED
TERMINAL
UNKNOWN
```

Canonical observed interruption mapping:

| Observed condition | Signal |
|---|---|
| provider rate limit | `PROVIDER_RATE_LIMIT` → `RATE_LIMITED` |
| provider quota exhausted | `PROVIDER_QUOTA_EXHAUSTED` → `QUOTA_BLOCKED` |
| context limit | `CONTEXT_LIMIT` → `BLOCKED` |
| waiting for owner/input | `WAITING_FOR_INPUT` → `BLOCKED` |
| dependency blocked | `DEPENDENCY_BLOCKED` → `BLOCKED` |

Silence never becomes `AVAILABLE`.

## Dispatch contract

An agent can receive new work only when:

1. liveness is sufficient;
2. availability is explicitly `AVAILABLE` or `WAITING` (or canonical standby where applicable);
3. no active claim/in-flight action conflicts;
4. dependencies are satisfied;
5. collision domains are free;
6. role is allowed;
7. required capabilities are present;
8. required authority evidence is present where the work contract requires it;
9. repository/scope is compatible;
10. the work item has explicit compatibility scope.

A work offer:
- creates no claim;
- grants no write authority;
- must be accepted;
- then requires the canonical claim/exact-HEAD/authority path before mutation.

## Unscoped work

A `READY` work-item with no explicit:
- `allowed_agent_roles`;
- `required_capabilities`;
- `required_authorities`;
- or `target_session_id`

is **not automatically dispatchable**.

This prevents generic/stale work such as bootstrap placeholders from being assigned merely because an agent is waiting.
