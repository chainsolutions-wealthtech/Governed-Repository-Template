# LAB isolé — preuve d'entrée directe propriétaire B

- **Type** : démonstration contrôlée / smoke test E.
- **Dépôt** : `chainsolutions-wealthtech/Governed-Repository-Template`.
- **Voie d'entrée sélectionnée** : `00_DIRECT_OWNER_ENTRY.md` (porte B explicite).
- **Acteur GitHub** : `Wealthtechinnovations`, réellement vérifié par la fonction GitHub authentifiée `get_user_login`.
- **Droits observés** : `pull=true`, `push=true` par API GitHub du dépôt ; droits effectifs restent soumis à GitHub pour chaque opération.
- **Mission** : `JE VIENS CODER` → `CODE_AGENT` / `CODE_CHANGE`.
- **Branche LAB** : `lab/direct-owner-entry-smoke-20261016`.
- **HEAD main de base** : `6f3f20638bc6c72b36040896a25633c90d4a5d68`.
- **Preuve d'exécution** : cette branche a été créée par une opération GitHub native authentifiée, puis ce document y a été commité via l'API GitHub directe. Aucun work-item ni claim GACR n'a été sollicité ou créé.
- **Portée** : test d'isolation sans code applicatif ; ne modifie aucun workflow, contrôle d'accès ou fichier de `main`. Aucun merge de cette branche n'est autorisé par ce test.
- **Limites** : aucune protection GitHub n'est désactivée ; pas de force push ; aucun GSCC/F1/GACR receipt forgé ; ce marqueur prouve une opération GitHub native et non un jeton d'identité du routeur CLI.
- **Critère de clôture** : branche LAB indépendante visible, fichier créé, HEAD main inchangé par ces deux opérations ; noter tout déplacement indépendant de main par d'autres workflows, sans l'attribuer au LAB.
