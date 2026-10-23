# Programme Continuité Canonique — feuille de route évolutive V0.1

Date : 2026-10-20 ; continuité documentaire : `GRT-CONT-AUDIT-STABILISATION-20261019-001` ; PR #339 DRAFT. Cette feuille de route ne crée pas de tâches runtime ni de grants.

| Étape | Mission | Statut au 2026-10-20 | Critère de sortie |
|---|---|---|---|
| F0-A | Mandat fondateur V0.1 | DOCUMENTED | mandat versionné dans PR #339 |
| F0-B | Registres Identification / Gouvernance | DOCUMENTED | registres existants et limites explicites |
| F1-A | Chronologie premier îlot #259 | PARTIAL_EVIDENCE | 81 commentaires indexés, preuves majeures relues ; corroboration restante |
| F1-B | Inventaire initial registres et autorités | DOCUMENTED / NON_EXHAUSTIVE | inventaire des sources principales, lacunes identifiées |
| F1-C | Recouper #257/#258/#262/#263/#266/#269/#286, commits, CI, contrats | TODO | filiation et preuves classées VERIFIED/CLAIMED/UNKNOWN |
| F1-D | Cartographier producteurs/consommateurs de registres, bus et workflows | TODO | graphe d'autorité et d'événements sans doublon |
| F2-A | Définir le journal canonique append-only et le modèle d'événements | TODO | schéma, provenance, ordre, corrections, anti-duplication |
| F2-B | Définir état courant, décisions, checkpoints et protocole de reprise | TODO | reconstruction déterministe depuis GitHub, limites provider |
| F2-C | Définir les blocs fonctionnels, dépendances, rôles et tâches candidates | TODO | architecture modulaire validable, sans création de claims |
| F2-D | Définir la procédure d'ajout d'instructions et de versions du mandat | TODO | classification, validation, historique, liens et tests documentaires |
| F3-A | Décision propriétaire sur identité HUB, rattachement GACR et entrée | PENDING_OWNER_DECISION | preuve d'identité et autorité, pas d'ID inventé |
| F3-B | Cadrage LAB isolé (branche, périmètre, collision, rollback) | TODO | mandat LAB borné et non-régression |
| F3-C | Prototype LAB sur code réel et intégration aux registres/bus existants | BLOCKED_UNTIL_AUTHORIZED | tests locaux et CI sans mutation main |
| F3-D | Essais multiagents, rejoin, perte de connexion, changement de HEAD | BLOCKED_UNTIL_LAB | preuves E2E et scénarios négatifs |
| F4-A | Audit indépendant, corrections, matrice de preuves et limites | TODO | aucune réussite inférée de CI seule |
| F4-B | Arbitrage propriétaire : poursuivre LAB, réviser ou promouvoir | PENDING_DECISION | décision explicite et SHA exact |
| F4-C | Publication de la V1 validée et protocole de maintenance | TODO | mandat, registres, mémoire, reprise, contrôles continus |

## Prochaine action unique
**F1-C** : recoupement des sources et des preuves de l'îlot fondateur, en commençant par #257/#258/#262/#263, puis #266/#269/#286. En parallèle documentaire ultérieur : F1-D.

## Règle d'évolution
Ajouter toute nouvelle instruction à la feuille de route avec ID, source, statut et dépendances ; conserver l'historique Git. Les statuts `DOCUMENTED` ne signifient pas `IMPLEMENTED` ni `TESTED`. PR #339 reste DRAFT, aucun merge ni LAB créé par ce plan.
