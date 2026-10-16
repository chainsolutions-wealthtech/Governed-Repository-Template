# LAB de continuité — inscription de lot en attente

- **ID de continuité / ID de jonction du lot** : `GRT-CONT-20261016-F1QUEUE-001`
- **Tâche canonique** : `RTE-014` (`.governance/control-plane-state/tasks.json`)
- **Issue** : https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/327
- **Branche** : `lab/direct-owner-f1queue-20261016`
- **HEAD de départ** : `6f3f20638bc6c72b36040896a25633c90d4a5d68`
- **Porte** : `00_DIRECT_OWNER_ENTRY.md` / propriétaire GitHub authentifié `Wealthtechinnovations`
- **Système de queue** : projection **existante** `scripts/gacr_capacity_dispatch.py`
- **État** : `REGISTERED_PENDING_F1 / BLOCKED / NOT_RELEASED / LAB_ONLY`
- **Session GACR / claim / release F1** : **aucun**.

## Étapes chronologiques

1. Inscrire cette identité + tâche dans le registre canonique en LAB, avec projection queue bloquée et tests.
2. Corriger F1 ultérieurement, sur nouveau mandat et preuves live, en tenant compte de l'issue #284.
3. Après preuves F1 et autorisation distincte, libérer la tâche pour la sélection de la file existante (rôle, disponibilité, capacité, dépendances, absence de collisions), puis offre, acceptation et claim.
4. **Pas maintenant** : authentifier et rattacher agent réel + session réelle à la boucle GSCC→GSE→GACR sous cet identifiant de continuité.

## Invariants

Aucun nouveau scheduler, Task Queue, dispatcher, registre de sessions, claim ou lock. La porte B ne vaut jamais F1_RELEASED. Le lot n'accorde aucune autorité de mutation. Aucune fusion implicite sur `main`, aucun déploiement. Le programme actif GMC-G01 et CHAINFLOW restent inchangés.

## Validation attendue

- `canonical_work_document()` contient `RTE-014` et `GRT-CONT-20261016-F1QUEUE-001`.
- Cette entrée est `BLOCKED`, non candidate à une offre.
- Le test de dispatch historique conserve `GMC-G01-T01` comme seul item `READY`.
- Namespace `RTE-014` respecte `CP-NAMESPACE-001`.
- Toute CI exécutée doit être vérifiée avant un changement d'état.

**Prochaine action unique** : `REVIEW_LAB_PENDING_REGISTRY_THEN_WAIT_FOR_OWNER_F1_MANDATE`.
