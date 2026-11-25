# HUB racine — cadrage et identité définitive à décider

Date de consignation : 2026-10-19. Source : instructions successives du propriétaire dans la conversation en cours. **Statut : nom définitif NON ENCORE ADOPTÉ ; architecture cible, non déployée.** Référence de travail : PR #339.

## Exigences consignées

1. Un **HUB racine permanent** représentera progressivement le projet existant sur `main`, sans copier ou modifier immédiatement son fonctionnement. L'espace de reconstruction démarre vide, puis se peuple progressivement de continuités et sous-espaces identifiés.
2. **Deux domaines distincts** : (A) parcours d'identité/admission `GSCC → GSE → GACR` avec ses propres autorités, pool et registres ; (B) gouvernance du dépôt, architecture, code, main et évolutions, avec ses propres registres. Un **pont de corrélation contrôlé** reliera les deux sans fusionner les autorités ni modifier les gates.
3. Un **grand LAB de reconstruction** peut, sur mandat futur, observer le `main` entier et contenir des LAB imbriqués, isolés, testés pas à pas. Aucune création de LAB ou changement de main n'est autorisé par le présent document.
4. Les missions successives (audit, reconstitution de code, outils, analyse, LAB, expérimentation, rapprochement de main) ont chacune ID, parent HUB, statut, responsables, sessions, livrables, preuves et checkpoints.
5. **Annuaire canonique progressif** : retrouver sur demande HUB → domaines → missions → agents → sessions → LAB → tâches → événements → décisions → artefacts, avec provenance et liens natifs.
6. **Audit exhaustif** : inventorier puis lire et rapprocher individuellement toutes les PR, issues, commentaires, commits et modifications de code depuis l'origine ; marquer séparément `INVENTORIED`, `READ`, `ANALYZED`, `CROSS_REFERENCED`, `VERIFIED`, sans prétendre à l'exhaustivité avant preuve.
7. **Mémoire des échanges** : les instructions et réponses dans le chat ne sont pas automatiquement toutes écrites dans GitHub. Chaque instruction nouvelle doit être explicitement archivée par une action attestée, avec date, auteur, résumé fidèle, liens et commit ; conserver la limite d'accès aux conversations passées.
8. **Identité définitive du HUB** : à définir explicitement avec le propriétaire. L'alias existant `GRT-AUDIT-STABILISATION` et `GRT-CONT-AUDIT-STABILISATION-20261019-001` restent un **espace/une mission de travail proposés**, et ne doivent pas être présentés comme l'identité racine définitive.
9. **Reprise et permissions** : la résolution d'un nom ne crée ni session GACR ni permission ; la Porte B exige authentification et permissions natives, la Porte A son admission complète. Toute passerelle doit être testée et attestée sans régression.

## Prochaine décision demandée au propriétaire

Valider le **nom et l'identifiant définitifs du HUB racine**, distincts de la mission d'audit. Puis préparer un registre racine et un résolveur reposant sur les mécanismes existants, sans créer d'autorité parallèle. Aucun nom définitif n'est inventé ici.
