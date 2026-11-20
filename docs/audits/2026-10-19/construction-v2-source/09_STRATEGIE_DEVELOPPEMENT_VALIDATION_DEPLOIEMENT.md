# Contrats de fabrication logicielle et de déploiement — GRT

**Ce document planifie ; il n'autorise aucune écriture, installation ni déploiement.** Priorité à la compatibilité du Control Plane existant, à l'identité P0 inchangée et à la conservation de l'histoire. Dépôt distinct `Patricked-code/MCP` : aucune modification ni assimilation au GRT.

## 1. Construction

- Entrée : ID du lot canonique, contrat accepté, HEAD frais, dépendances validées, agent/claim autorisé.
- Développement : modification minimale et additive, sans override de politiques ou de données antérieures ; gestion des conflits/concurrence.
- Emplacements : surface indiquée par l'autorité de la tâche ; pas de nouvelle source de vérité. LAB uniquement après droits LAB effectifs.
- Livrable : artefact versionné, description du diff, suite de tests, référence de commit/PR et décision.
- Tests : unitaires, contrats, contrôle négatif fail-closed, intégration, migrations, régression des cas et du parcours d'entrée.

## 2. Intégration

- Vérifier que l'artefact satisfait le contrat de sortie du lot et les interfaces des consommateurs.
- Tests de compatibilité CASE1, continuité GSCC/GSE/GACR/F1, reprise d'états anciens, migrations et old clients.
- CI PASS ne suffit pas : revue indépendante et décisions de fusion selon autorité, fraîcheur et branche.
- Revalidation obligatoire si le HEAD de base a changé.

## 3. Déploiement

| Stade | Entrée obligatoirement attestée | Preuve requise | Si échec |
|---|---|---|---|
| Packaging | SAA-011 autorisé, environnement reproductible | Build, manifest, images, SBOM si exigé | STOP / corriger |
| Staging | SAA-012 autorisé, environnement et migration connus | Smoke, E2E, traces sécurité + reset/rollback | HOLD / restaurer |
| Production | SAA-013 et droits serveur effectifs, backups vérifiés | TLS, health/ready, identité de version, rollout exact, logs | STOP / rollback gouverné |
| Recette | SAA-014 et matrice de couverture complète | 4 cas + multiagent + reprise + sécurité + audit | HOLD RELEASE |
| Release | SAA-015, approbation, zéro blocage critique | Attestation, runbooks, reprise/rollback, checkpoint | BLOCK RELEASE |

## 4. Protocole de données et d'API

- Git et les autorités canoniques restent la vérité ; PostgreSQL est une projection réconciliable (`ARCH-009`), non un pilote autonome des droits.
- L'API expose uniquement les opérations que les gates déjà validés autorisent (`ARCH-008`). Authentification ≠ gouvernance ≠ mutation.
- Le cockpit est une vue et une surface de commandes gouvernées (`ARCH-010`), pas une base parallèle.
- Secrets jamais inclus dans les artefacts, logs ou réponses API.

## 5. Limites de portée et conditions de début

1. Aucun calendrier réel possible avant estimation des efforts et ressources disponibles.
2. Pas de déclaration de `RELEASED` sans preuves de tests et validations réels.
3. Ne pas déployer au domaine `https://mcp.wealthtechinnovations.com/template` parce qu'il figure dans un document : sa mention ne donne aucun accès serveur.
4. Aucun changement de P0 ; évolution future éventuelle uniquement par mandat et autorité distincts.
5. Les tâches de **planification** restent non mutables jusqu'à leur approbation/rattachement dans le modèle canonique.
