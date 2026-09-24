# AGENTS — Règles pour tout agent, humain ou automatisation

Ce fichier s'applique à toute intervention sur `{{REPOSITORY}}`.

## Démarrage obligatoire

1. lire `00_START_HERE.md` et l'ordre de lecture ;
2. confirmer dépôt, branche, HEAD et état du worktree ;
3. lire les fichiers directement concernés ;
4. rechercher les travaux existants ;
5. établir la baseline et les risques ;
6. vérifier les permissions et contraintes ;
7. sélectionner une action compatible avec `NEXT_ACTION.md`.

## Continuité

Il est interdit de recommencer le projet sans décision documentée, dupliquer une autorité existante, changer un contrat stable sans migration, supprimer une preuve utile ou contourner un gate de sécurité ou d'approbation.

## Zéro régression

Avant modification : identifier consommateurs, dépendances, données, contrats, tests et sorties affectés.

Après modification : exécuter les contrôles disponibles, comparer à la baseline, corriger toute régression introduite, puis vérifier à nouveau.

## Handoff

Toute interruption doit laisser le dépôt reprenable par un autre agent uniquement à partir des autorités versionnées, sans dépendre de la mémoire de la conversation.
