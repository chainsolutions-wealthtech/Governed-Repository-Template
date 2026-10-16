# MÉMOIRE CANONIQUE DU LAB — GRT-CONT-20261017-F1RECOVERY-001

> **Portée : ce LAB uniquement.** Cette mémoire est l'index de vérité **de notre travail dans la branche LAB**, pas une autorité globale sur le Control Plane de `main`. Les commits GitHub et les checkpoints de l'issue #331 assurent la reprise ; aucun registre historique n'est remplacé.

## Identité et reprise

- **Continuité de développement** : `GRT-CONT-20261017-F1RECOVERY-001`.
- **Dépôt** : `chainsolutions-wealthtech/Governed-Repository-Template`.
- **Branche** : `lab/f1-recovery-isolation-20261017`.
- **Issue chronologique** : [#331](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/331).
- **PR associée** : [#332](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/332), **DRAFT / NON FUSIONNÉE**.
- **Parent documentaire** : `GRT-CONT-20261016-F1QUEUE-001`, issue #327, PR #328 (déjà fusionnée).
- **Acteur GitHub attesté** : `Wealthtechinnovations`. **Aucun ID de session ChatGPT ou GACR ne peut être supposé**.
- **BASE** : `main@b3d7f623b443be6b0fe987dd2c527a6a4d4a53d0`.
- **LAB avant ce registre** : `6ba31d9930a477afcd7d2d4885e2eff7fe13af92`.

## Sources canoniques du LAB

| Registre | Rôle | Règle |
| --- | --- | --- |
| `OBSERVATIONS.json` | Faits observés, preuves et limites | Une nouvelle observation reçoit un nouvel ID ; jamais transformer une hypothèse en preuve en silence |
| `CHRONOLOGY.json` | Événements ordonnés, commits, commentaires et tests | Ajout chronologique, provenance des événements et pas de dates inventées |
| `DECISIONS.json` | Choix du propriétaire, politiques préservées, décisions en attente | `PENDING` n'est pas une autorisation |
| `TASK_CANDIDATES.json` | Hypothèses de travaux à analyser, sans dispatch | **Pas** une Task Queue : aucun claim ni affectation |
| `CHECKPOINT.json` | Dernier HEAD observé, prochain acte et preuve CI disponible | Snapshot révisable, Git et issue constituent l'historique |
| `MEMORY.md` | Mode d'emploi/reprise, résumé et limitations | Une nouvelle conversation doit lire les fichiers machine et le dernier commentaire d'issue |

## Chaîne de construction obligatoire

`OBSERVATION → PREUVE → INSCRIPTION CHRONOLOGIQUE → ANALYSE → VALIDATION DE DÉCISION → CANDIDAT DE TÂCHE → PROMOTION GOUVERNÉE (SEULEMENT SI AUTORISÉE) → EXÉCUTION → TESTS → CHECKPOINT`.

À chaque intervention, lire HEAD main et LAB, issue/PR, puis append les **nouveaux éléments confirmés**, ajouter des hypothèses sans les présenter comme établies et mettre à jour le checkpoint et la prochaine action. L'acte de planifier ne doit pas créer une session, un claim, un verrou ni une seconde queue.

## État de connaissance enregistré

- **F1** : correction de reprise et conservation de preuves dans PR #332, CI simulée réussie, **E2E live non prouvé**.
- **Agent sans nom** : champ alias facultatif testé en simulation, identité GSCC réelle préservée.
- **Dispatcher GACR** : audit D01–D08 dans [rapport spécifique](../GRT-CONT-20261017-F1RECOVERY-001_DISPATCHER_AUDIT.md) ; D03 provenance F1 et D04 revalidation d'offre sont des **risques ouverts**.
- **Registre préexistant** : 9 observations sourcées ; 9 événements ordonnés ; 6 candidats **non distribués**.
- **Dernier cycle CI avant mémoire** : [Governance CI #38983239494](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/actions/runs/38983239494) et trois contrôles GSCC success ; ce sont des tests de LAB, pas des validations de fusion ou de sécurité E2E.

## Anti-régression et limites

1. Lire les sources réelles, n'écrire que sur `lab/f1-recovery-isolation-20261017` et observer le HEAD avant chaque mutation ; refuser une mise à jour si la branche a bougé.
2. Un verdict de simulation qui reproduit une faille signifie **risque confirmé localement**, non **défaut corrigé**.
3. Une admission F1 propriétaire, un slot de pool, un lien d'identités ou une offre GACR ne confèrent pas des droits GitHub natifs.
4. Les travaux sans autorisation restent des candidats d'analyse. Ne pas modifier la queue canonique ni `GMC-01`.
5. Documenter l'inconnu : ID de session, limites d'E2E, preuves absentes et état des hypothèses.
6. La liaison technique identité de session ↔ continuité de développement ↔ GSCC/GSE/GACR reste **différée** jusqu'au mandat propre du propriétaire.

## Reprise universelle

Depuis une nouvelle conversation GitHub connectée, demander :

```text
Rejoins GRT-CONT-20261017-F1RECOVERY-001.
Lis l'issue #331, la PR #332 et les fichiers
docs/labs/GRT-CONT-20261017-F1RECOVERY-001/{MEMORY.md,OBSERVATIONS.json,CHRONOLOGY.json,DECISIONS.json,TASK_CANDIDATES.json,CHECKPOINT.json}.
Reobserve main et LAB HEAD. Reprends le dernier checkpoint et enrichis la mémoire
avant tout nouveau plan ou code, sans usurper une session.
```

La mémoire évolue **au rythme des interventions enregistrées**. Elle ne se complète pas en arrière-plan lorsqu'aucun agent ne travaille.
