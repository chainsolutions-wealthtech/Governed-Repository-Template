# AUDIT GACR CAPACITY DISPATCHER — LAB F1

- Dépôt : chainsolutions-wealthtech/Governed-Repository-Template
- Continuité de développement : GRT-CONT-20261017-F1RECOVERY-001
- Issue : #331 ; PR : #332 (brouillon)
- Composant : scripts/gacr_capacity_dispatch.py, 1103 lignes
- Baseline main : b3d7f623b443be6b0fe987dd2c527a6a4d4a53d0
- Statut : AUDIT_EN_LAB / AUCUNE MODIFICATION DU DISPATCHER / PAS DE FUSION

## Rôle précis

Le dispatcher transforme un graphe canonique de tâches et un pool de sessions GACR en offres de travail. Les quatre commandes sont pool, plan-work, dispatch-work et accept-work. Il recoupe l'état et le rôle de chaque session, sa disponibilité, les beacons, les claims, les domaines de collision, les capacités et dépendances, et la preuve de libération F1.

Une offre de travail acceptée reste ACCEPTED_PENDING_CLAIM. Elle ne donne ni accès GitHub ni permission de coder : claim valide, HEAD réconcilié, autorisation et permissions natives restent distincts.

## Autorités examinées

- Tasks : .governance/control-plane-state/tasks.json
- Blueprint : .governance/control-plane-state/governance-model-execution-blueprint.json
- Sessions, beacons, claims, dispatches et continuities : répertoires .governance/control-plane-state
- Politique : .governance/agent-relay/config.json
- En source template, la politique exige F1, rôle canonique et signal explicite de disponibilité; capacité maximale automatique d'une offre par agent logique.
- Snapshot : tasks revision 59 / 133 items, dont 1 IN_PROGRESS. Dispatches revision 167 / 29 items. Claims revision 0 / aucune revendication active.

## Constats vérifiés par lecture de code et caractérisation

| ID | Gravité | Constat | Action recommandée |
| --- | --- | --- | --- |
| D01 | P1 Structurel | Source task graph codé pour l'unique GMC-01 et GMC-G01 ; les lots des nouveaux LAB ne sont pas promus automatiquement | Construire un passage contrôlé vers le graphe canonique existant sans queue parallèle |
| D02 | P1 Parcours | F1_RELEASE_NOT_VERIFIED bloque la session sans beacon F1 ; un autre agent avec F1 reste indépendant | Préserver le refus ciblé, documenter et récupérer les arrivées bloquées |
| D03 | P1 Frontière de confiance | _latest_f1_release vérifie event_type F1_RELEASED et evidence_ref non vide, sans valider lui-même une preuve signée | Auditer la validation amont et vérifier reçu/session/HEAD auprès de la source canonique ; le test ne prouve pas une falsification externe possible |
| D04 | P1 Ecart | accept_work_offer revalide disponibilité, claim logique et READY source mais ne revalide pas rôle, capacités, autorités, scope propriétaire et version de la tâche | Rejeter une acceptation si le profil ou les règles ont changé depuis l'offre |
| D05 | P2 Concurrence | dispatch_ready_work et accept_work_offer font des opérations read-modify-write sur JSON sans CAS ou lock visible dans ce module | Vérifier la sérialisation réelle des workflows et prévoir contrôle de révision atomique |
| D06 | P2 Limite | planning_only et implementation_authorized restent des métadonnées transmises à l'offre, pas une autorisation exécutable | Renforcer les gates de consommation ; ne pas déduire le droit de coder de l'offre |
| D07 | Protection conservée | Capacité par agent logique, claims, collisions et annulation ciblée des offres d'agent indisponible | Conserver et étendre les tests |
| D08 | Intégration | _cancel_stale_source_offers annule les offres non reconnues par le graphe canonique source | Un LAB doit promouvoir ses tâches, jamais écrire une deuxième queue d'offres |

## Tests de caractérisation ajoutés

scripts/test_gacr_dispatch_lab_audit.py simule six cas sans écrire aucun registre réel : F1 local, beacon non attesté dans la seule projection, acceptation d'offre périmée, annulation ciblée, file GMC-01, plan sans droits d'écriture.

**Un test vert sur D03 ou D04 confirme le comportement problématique, pas sa correction.** Ne pas utiliser le verdict CI comme autorisation de merger le dispatcher. Aucune mutation fonctionnelle du dispatcher n'est faite dans ce chantier d'audit.

## Architecture LAB cible

Entrée LAB -> ID de continuité de développement -> registre chronologique -> pool ID -> architecture -> cahier des charges -> micro-lots -> validation -> promotion dans TASKS canonique -> dispatcher GACR existant -> offre -> acceptation contrôlée -> claim -> code / tests -> revue -> PR -> fusion / déploiement distincts.

Une session conserve sa propre identité canonique ; son lien avec une continuité de développement ne crée pas une permission. La liaison technique au loop GSCC/GSE/GACR reste différée selon la décision propriétaire.

## Prochaines tâches

1. Auditer le contrôle des beacons F1 en amont.
2. Définir les refus attendus pour acceptation après changement de rôle/capacité/autorité.
3. Dessiner la promotion universelle des micro-lots LAB dans l'unique queue.
4. Évaluer la concurrence GitHub Actions / revision et les verrouillages existants.
5. Faire valider les décisions indépendamment avant toute modification du dispatcher sur son propre lot.

