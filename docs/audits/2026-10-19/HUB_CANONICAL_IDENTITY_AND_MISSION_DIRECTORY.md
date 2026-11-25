# HUB canonique — identité proposée, séparation des gouvernances et annuaire initial

**20 octobre 2026 — décision de cadrage documentaire, NON activée**. Dépôt exclusif : `chainsolutions-wealthtech/Governed-Repository-Template`. Ancrage de travail : [PR #339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339). Ne pas confondre avec `Patricked-code/MCP`.

## Identité racine définitive demandée — proposition soumise à validation

- **Nom proposé pour le HUB** : `GRT-CANONICAL-HUB`.
- **ID documentaire proposé** : `GRT-HUB-20261020-001`.
- **Alias historique préservé** : `GRT-AUDIT-STABILISATION`.
- **Continuité d'audit proposée préexistante** : `GRT-CONT-AUDIT-STABILISATION-20261019-001` ; devient **une mission enfant** du HUB, et non le nom de la racine générale.
- **Statut** : `PROPOSED / OWNER_CONFIRMATION_REQUIRED`. Aucune inscription dans GACR, aucune admission, session, permission ou nouvelle autorité créée.

Le HUB est un **miroir documentaire initialement vide d'exécutions propres** : il référence la totalité de `main` par des preuves et index sans en recopier aveuglément les contenus ni déclarer que `main` est déjà compris. Il se peuple progressivement par missions, analyses, sous-espaces, LAB et tests. `main` reste la source existante et n'est jamais remplacé implicitement par ce HUB.

## Deux domaines distincts, reliés par un pont d'observation

### Domaine A — parcours GSCC / GSE / GACR
- Entrée Porte A, identité agent, session, Q1–Q12, F1, release, claims et contrôles selon les autorités **existantes**.
- Son registre et ses identifiants sont propres au domaine A.
- Aucune session ou identité GACR ne peut être créée par simple déclaration documentaire ou par une conversation ChatGPT.

### Domaine B — gouvernance / espace de travail propriétaire
- Porte B explicite `00_DIRECT_OWNER_ENTRY.md` avec identité GitHub réellement authentifiée et permissions natives vérifiées.
- Registre documentaire des instructions, missions, événements, agents référencés, sessions de travail **distinctes des sessions GACR**, artefacts, LAB et checkpoints.
- Liberté de proposer et développer progressivement des LAB et outils isolés, sous les protections de branche et règles réelles ; aucune refonte anticipée de `main`.

### Pont A ↔ B
Table de correspondance **référentielle** : `hub_id`, `mission_id`, `github_actor` (si attesté), `logical_agent_id` (si attesté), `gacr_session_id` (si attesté), `work_session_id` (si matérialisé), `source_url`, `scope`, `verified_at_utc`. Une liaison ne vaut **ni** transfert d'autorité, **ni** admission GACR, **ni** permis de mutation. Refuser toute corrélation ambiguë.

## Annuaire initial des missions

| Identifiant proposé | Nom d'appel | Domaine | Mission | Statut |
|---|---|---|---|---|
| `GRT-MISSION-AUDIT-001` | `MISSION AUDIT` | B | Lire individuellement toutes PR, issues, commentaires, commits, diffs, décisions et codes ; indexer chaque preuve et les lacunes | `IN_PROGRESS / NON_EXHAUSTIVE` |
| `GRT-MISSION-RESUME-002` | `MISSION RESOLVEUR-ROUTEUR` | Pont A↔B | Résolution de l'espace, session de travail attestée et routage nominal ; réutiliser les composants existants, tester les refus | `SPECIFIED / NOT_YET_ATTESTED` |
| `GRT-MISSION-GACR-003` | `MISSION PARCOURS GACR` | A | Comprendre et tester le parcours complet GSCC/GSE/GACR séparément | `PLANNED` |
| `GRT-MISSION-LAB-004` | `MISSION GRAND LAB` | B | Concevoir un grand LAB avec sous-LAB isolés reflétant progressivement `main` et testant les changements | `PLANNED / NOT_CREATED` |
| `GRT-MISSION-RECONSTRUCTION-005` | `MISSION RECONSTRUCTION` | B | Comparer code LAB, architecture, historique et `main` ; préparer des propositions sans toucher `main` | `FUTURE / NOT_AUTHORIZED_FOR_EXECUTION` |

Les noms et numéros ci-dessus sont **des clés d'annuaire proposées**, pas des tâches GACR admises ni des autorisations.

## Règles de mémoire et de reprise

Chaque instruction utilisateur, réponse ayant valeur de décision, intervention, preuve et anomalie doit être consignée **explicitement** dans le registre du HUB à l'avenir, avec identifiant, auteur/source, date, portée, statut, références GitHub et prochain checkpoint. L'historique des conversations n'est **pas** exporté automatiquement par GitHub ; on ne doit pas prétendre avoir archivé chaque échange antérieur. Les traces disponibles dans [README.md](README.md), [GITHUB_HISTORY.md](GITHUB_HISTORY.md), [FILE_INVENTORY.md](FILE_INVENTORY.md), [CONTINUITIES_AND_IDENTITIES.md](CONTINUITIES_AND_IDENTITIES.md), [ISSUE_COMMENTS.md](ISSUE_COMMENTS.md), [CANONICAL_CONTINUITY_PROPOSAL.md](CANONICAL_CONTINUITY_PROPOSAL.md) et [OWNER_EXPERIMENTAL_WORKSPACE_MANDATE.md](OWNER_EXPERIMENTAL_WORKSPACE_MANDATE.md) restent les premiers liens d'archive.

**Commande de reprise cible** : « Rejoins `GRT-CANONICAL-HUB` / `GRT-HUB-20261020-001` dans `chainsolutions-wealthtech/Governed-Repository-Template`, affiche l'annuaire, puis reprends `MISSION AUDIT` au dernier checkpoint attesté. » Cela déclenche une recherche de preuves, **pas** une attribution automatique de permissions.

## État des travaux et prochaine action

1. HUB et annuaire : **documentés comme propositions** dans la PR #339, pas encore activés comme registre runtime.
2. Audit exhaustif : inventaires partiels et annexes existants, **pas encore une compréhension individuelle exhaustive**.
3. Résolveur / routeur et sessions inter-conversations : **non encore prouvés opérationnels**.
4. Grand LAB / sous-LAB : **non créés**.
5. **NEXT_ACTION** : vérifier conventions et collisions des identifiants, inventorier les composants de résolution/routage déjà existants, construire une matrice de raccordement non destructive ; ensuite développer et tester sur la branche de travail existante, sans toucher `main` sans mandat distinct.
