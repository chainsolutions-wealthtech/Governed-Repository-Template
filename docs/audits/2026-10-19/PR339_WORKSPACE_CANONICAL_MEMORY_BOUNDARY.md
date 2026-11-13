# PR #339 — frontière des mémoires et espace expérimental

**Date d'enregistrement : 2026-10-19** · **Statut : mandat documentaire** · [PR #339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339) · espace proposé `GRT-CONT-AUDIT-STABILISATION-20261019-001`.

## Décision de cadrage du propriétaire

1. **Mémoire canonique du grand projet GRT** : représente le dépôt `chainsolutions-wealthtech/Governed-Repository-Template`, son `main`, ses gouvernances, son historique, ses agents, ses continuités et ses autorités réelles. Les sources existantes font foi ; ce dossier n'est pas leur remplaçant.
2. **Mémoire canonique propre à la PR #339** : journal indépendant de l'espace de travail expérimental actuellement piloté par le propriétaire. Conserve les instructions échangées, décisions, missions, liens de preuves, checkpoints, essais, LAB, agents et sessions liés **à cet espace**, sans usurper les identités GACR. L'alias `GRT-AUDIT-STABILISATION` et l'ID `GRT-CONT-AUDIT-STABILISATION-20261019-001` restent proposés tant que leur résolution opérationnelle n'est pas validée.
3. **Mémoires des missions** : chaque mission reçoit un nom/ID, des étapes, ses propres preuves et son historique ; missions futures possibles : `AUDIT-HISTORIQUE`, `RECONSTITUTION-CODE`, `ARCHITECTURE`, `LAB-EXPERIMENTATION` (noms de catégories proposés, pas des travaux déjà lancés).
4. **LAB et sous-LAB** : isoler progressivement la reconstruction du dépôt existant et les expérimentations. La PR #339 sert d'ancrage documentaire et d'espace de continuité, **pas** de clone complet du code ou de LAB déjà provisionné. Toute création technique ultérieure sera explicitement autorisée, gouvernée et attestée.

## Deux flux distincts à rapprocher sans fusionner

- **Flux A — GSCC / GSE / GACR** : admission et processus agents existants, registres et permissions propres, étapes et gates inchangés. L'expression orale « GSSCGES, GAC » renvoie ici aux noms vérifiés dans le dépôt, sans supposer un nouveau protocole.
- **Flux B — Gouvernance du grand projet / main** : lecture, audit, reconstitution, construction expérimentale et tests pas à pas ; registres et décisions du projet existant conservés.
- **Pont A↔B** : corrélation vérifiable entre identités, sessions, tâches, preuves, artefacts et autorisations ; aucun transfert automatique de privilèges, aucun bypass, aucune duplication de registres faisant autorité.

## Première mémoire des instructions reçues

- **Mandat 1** : inventorier et analyser individuellement PR, issues, commentaires, commits et modifications de code depuis l'origine ; distinguer inventorié, lu, compris, rapproché, validé.
- **Mandat 2** : construire un résolveur et un routeur d'espace par identifiant/alias et fonctions nommées ; tester réellement la reprise inter-conversations sans prétendre disposer d'IDs ou permissions non exposés.
- **Mandat 3** : traiter l'espace comme hub d'instructions, missions et sous-espaces, avec annuaire progressif, identité, sessions, traçabilité et checkpoints.
- **Mandat 4** : séparer le flux GSCC/GSE/GACR du flux de gouvernance, avec pont de corrélation seulement.
- **Mandat 5 (présent)** : séparer strictement mémoire du grand projet et mémoire PR #339 ; reconstituer pas à pas l'existant dans un grand LAB expérimental, sans changements majeurs de `main` ni activation anticipée.

Ces lignes sont une **synthèse des instructions de l'échange**, pas une transcription intégrale ni une preuve d'exécution. Pour une histoire exhaustive, conserver les instructions et leurs sources natives à chaque nouvelle étape, sans inventer de liens vers des conversations inaccessibles.

## Convention d'annuaire cible

`PROJECT_GRT` → `WORKSPACE_PR339` → `MISSION_ID` → `LAB_ID / AGENT_ID / SESSION_ID` → `EVENT_ID / DECISION_ID / ARTIFACT_ID / CHECKPOINT_ID`.

Les IDs ci-dessus sont des **catégories de liens**, non des identités runtime attribuées. Chaque entrée future indiquera son autorité source, son statut et ses preuves.

## Garde-fous

Ne pas modifier `main`, créer d'issue/PR parallèle, fusionner, activer une admission GACR, ouvrir un LAB réel ou accorder des droits à partir du seul identifiant documentaire. Lire les portes existantes, vérifier GitHub HEAD/permissions et les règles CI avant toute mutation ultérieure. La PR #339 reste un brouillon jusqu'à instruction contraire.
