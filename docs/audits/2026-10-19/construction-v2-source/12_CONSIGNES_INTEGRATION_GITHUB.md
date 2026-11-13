# Consignes de publication gouvernée dans GitHub (à exécuter seulement avec droits réels)

Dépôt : `chainsolutions-wealthtech/Governed-Repository-Template` ; HEAD observé lors de la préparation : `638fcc51c77f2454990f239b8b8cca78bac8075b`.

1. Première entrée de l'agent chargé de publier : `00_GSCC_ENTRY.md` ; connexion via processus GSCC/GSE/GACR/F1, corrélation au contexte propre. Ne pas utiliser l'identité d'un autre agent.
2. Vérifier la continuité du Programme Global #288, le dossier CONTRACT #292, les décisions, le dernier checkpoint, le scope d'écriture et `NEXT_ACTION`.
3. Chercher si un dossier documentaire identique a été publié entre le HEAD référencé et le HEAD actuel. Dédupliquer avant toute écriture.
4. Vérifier que l'insertion documentaire candidate est compatible avec `CP-NAMESPACE-001`, les règles de branches/PR, et autorisée par le claim et le lease applicables.
5. Proposer un emplacement source-only en documents d'intégration de planification, **sans se substituer** à `CURRENT_STATE`, `TASKS`, au modèle GMC, aux outils d'admission ou aux namespaces.
6. Publier par branche et PR si c'est la voie gouvernée ; ne pas fusionner automatiquement. `P0` et les fichiers de runtime restent inchangés.
7. Lancer les contrôles de structure du paquet, puis les tests GitHub de gouvernance disponibles et faire vérifier par un autre rôle autorisé.
8. Rattacher les liens de PR/commit/CI/checkpoint/issue au **même** dossier existant, mettre à jour le pointeur de reprise sans seconde vérité.
9. Toujours distinguer : copie GitHub documentaire = **présence de documentation**, pas acceptation ST01, pas release GMC, pas DONE de tâches, pas autorisation d'exécuter.

## Décision de publication à date de création

`NOT_PUBLISHED_BY_THIS_PACKAGE`. Aucune mutation du dépôt distant, d'une issue, d'une branche ou d'un système serveur n'est réalisée par ce dossier.
