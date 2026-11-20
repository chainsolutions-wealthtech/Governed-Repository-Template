# HUB racine — identité et filiation proposées

**Date de proposition : 2026-10-19** · **Statut : PROPOSED / non adopté** · **Dépôt :** `chainsolutions-wealthtech/Governed-Repository-Template` · **PR de travail unique :** [#339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339).

## Identité candidate

- Nom humain : `GRT-CANONICAL-HUB`.
- ID racine proposé : `GRT-HUB-ROOT-001`.
- Nature : espace durable de coordination, instructions, archives, reconstruction, expériences et continuités.
- `main` est **la source de référence existante**, pas une copie du HUB ni une branche à remplacer. Le HUB expérimental est initialement vide de code propre ; il peut référencer et cartographier tout `main` sans le recopier ni le modifier.
- Ancien alias `GRT-AUDIT-STABILISATION` et ID `GRT-CONT-AUDIT-STABILISATION-20261019-001` : **continuité enfant candidate**, jamais identifiant racine ni autorité GACR.
- La fixation définitive exige l'accord du propriétaire, un contrôle de collision dans les identifiants existants et une inscription dans un index approuvé ; ne pas revendiquer l'activation automatique.

## Deux domaines indépendants, un pont documentaire

**Domaine 1 — pool et parcours GSCC/GSE/GACR :** suivre la Porte A, les preuves d'identité, sessions, claims, Q12, F1, RELEASE et registres d'autorité existants. Ne jamais attribuer une admission ou un droit en inventant une session.

**Domaine 2 — gouvernance / HUB expérimental :** entrer explicitement par la Porte B lorsque demandée ; cartographier le projet, enregistrer les instructions, constituer les missions, outils, grand LAB et sous-LAB, expérimenter progressivement. Respecter les permissions GitHub natives et protections.

**Pont :** liens de provenance entre identité GitHub, intervention, mission, artefact, éventuelle identité GACR déjà prouvée, session, décision et checkpoint. Le pont ne crée aucune équivalence de droits ni deuxième registre d'autorité.

## Annuaire cible (vues sur sources natives)

- `IDENTITIES` : ID racine, alias, relations parent/enfant, preuves et statuts.
- `MISSIONS` : missions successives (première mission : audit historique), objectifs, livrables, états.
- `AGENTS_SESSIONS` : identités, rôles, sessions attestées, droits vérifiés, checkpoints.
- `LABS` : grand LAB et sous-LAB, branches et provenance.
- `HISTORY` : toutes les PR, issues, commentaires, commits, modifications de code et événements ; progression individuelle `INDEXED / READ / ANALYZED / CROSS_LINKED / VERIFIED`.
- `MEMORY` : instructions, réponses significatives, décisions, résultats, erreurs, horodatages et preuves ; ne pas prétendre posséder les conversations non archivées.
- `GOVERNANCE` : portes, règles, tâches, décisions et états autoritatifs existants.
- `GACR_BRIDGE` : corrélations documentées et contrôlées entre domaines.

Ces catégories sont des **vues d'annuaire** ; elles ne doivent pas doubler les registres source, la queue ou les autorisations GACR.

## Cycle d'une instruction

`RECEIVED → CLASSIFIED → LINKED_TO_MISSION → AUTHORIZED_OR_BLOCKED → EXECUTED → VERIFIED → CHECKPOINTED`.

Chaque entrée conserve son texte/source lorsque disponible, l'auteur prouvé ou `UNRESOLVED`, le temps UTC, le contexte, l'identifiant de mission, les preuves GitHub, les changements réalisés, les limites, la suite et le lien parent. Le journal doit être append-only ou versionné.

## Portée et non-régression

Ne pas créer de branche LAB, d'agent runtime, de session GACR ou de nouvelle PR/issue du seul fait de ce document. Ne pas modifier `main`, les portes, les contrôles d'accès ni les registres source sans mandat séparé. L'espace racine est une **proposition d'identité**, non un service déjà opérationnel.
