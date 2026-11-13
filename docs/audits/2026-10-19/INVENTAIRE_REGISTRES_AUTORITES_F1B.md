# F1-B — Inventaire initial des registres et autorités du GRT

Date : 2026-10-20. Programme : `GRT-CONT-AUDIT-STABILISATION-20261019-001`. PR #339. Statut : **DOCUMENTARY / VERIFIED_PATHS / NON_EXHAUSTIVE**.

## Hiérarchie et sources inspectées sur main
| Domaine | Fichiers réellement lus | Autorité / usage | Limite |
|---|---|---|---|
| Orientation | `00_START_HERE.md`, `docs/control-plane/MASTER_SYSTEM_MAP.md` | navigation et priorité des sources | MASTER_SYSTEM_MAP synthèse, non autorité concurrente |
| État courant | `docs/control-plane/CURRENT_STATE.md`, `.governance/control-plane-state/current.json` | état source du contrôle central | ne pas confondre avec état de notre programme |
| Architecture | `docs/control-plane/CANONICAL_ARCHITECTURE.md` | cible acceptée `CP-ARCH-001` | architecture cible != implémentation prouvée |
| Tâches | `docs/control-plane/TASKS.md`, `docs/control-plane/NEXT_ACTION.md` | programme et prochaine action gouvernés | notre backlog documentaire ne crée pas de tâche READY |
| Décisions | `docs/control-plane/DECISIONS_LOG.md` | décisions append-only | distinguer décision propriétaire et proposition |
| Continuités | `.governance/control-plane-state/gacr-continuities.json` | projection dérivée de coordination | `projection_only=true`, aucun grant tâche/claim/mutation |
| Sessions | `.governance/control-plane-state/gacr-sessions.json` | surface de session GACR | lecture de fichier vide via connecteur ; contenu non vérifié ici |
| Claims | `.governance/control-plane-state/gacr-claims.json` | claims observés | au snapshot lu : revision 0, claims [] ; ne prouve pas absence de claims ailleurs |
| Relèves | `.governance/control-plane-state/gacr-takeovers.json` | reprise et transfert gouvernés | un takeover READY n'accorde pas le droit d'écrire |
| Coordination | `docs/GACR_AGENT_CONTINUITY_RELAY.md`, `docs/MULTI_AGENT_COORDINATION.md` | liveness, collisions, exact HEAD, handoff | heartbeat propre à chaque session |
| Reconstruction | `docs/control-plane/AGENT_RECONSTRUCTION_SKELETON.md` | reconstitution composition-only | reconstruction != admission ni reprise ni claim |
| Admission | `00_GSCC_ENTRY.md`, `00_DIRECT_OWNER_ENTRY.md` | portes A et B indépendantes | preuve d'identité/permissions requise, pas de droits inventés |

## Architecture documentaire de notre programme
- **Mandat vivant** : `PROGRAMME_CONTINUITE_CANONIQUE_MANDAT_FONDATEUR.md`.
- **Identification** : `PROGRAMME_ISOLE_REGISTRE_IDENTIFICATION.md`.
- **Gouvernance et mémoire** : `PROGRAMME_ISOLE_REGISTRE_GOUVERNANCE.md`.
- **Preuves historiques** : `PREMIER_ILOT_CONTINUITE_ETUDE_INITIALE.md`, `PREMIER_ILOT_CHRONOLOGIE_ET_INVARIANTS_V01.md`.
- **Journal événementiel append-only** : **À CONCEVOIR**, en réutilisant les événements/issue/commits existants ; aucun bus parallèle.
- **LAB** : **NON CRÉÉ** ; mandat de conception seulement.

## Règles d'autorité
1. Ne pas promouvoir les notes du programme en état GACR sans admission/approbation et preuves.
2. Les événements historiques, PR et issues sont des preuves ; ils ne remplacent pas les sources canoniques.
3. Préserver `logical_agent_id`, `session_id`, `continuity_id`, `claim_id`, `task_id` comme identifiants distincts.
4. Revoir les permissions, le HEAD, les collisions et le CI avant toute mutation runtime.
5. Aucune fusion `main`, création LAB ou modification des registres GACR par cette étape.

## Limites et contrôles ultérieurs
Inventaire **ciblé**, pas exploration exhaustive de tout le tree Git. La réponse vide sur `gacr-sessions.json` doit être réconciliée par un autre moyen autorisé avant toute conclusion. Vérifier schémas et scripts producteurs/consommateurs, bus, workflow, logs et invariants E2E avant architecture LAB.
