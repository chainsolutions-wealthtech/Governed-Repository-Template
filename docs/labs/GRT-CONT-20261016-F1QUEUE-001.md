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


## PHASE 2 — Correctif F1 de la porte A (candidat en LAB, sans fusion)

- Le module `scripts/gscc_owner_f1.py` produit un **reçu d'admission propriétaire F1 authentique**, `gscc-owner-f1-admission-receipt/v1`, ainsi qu'un nouveau `gscc-access-grant/v1`.
- La signature de l'événement GitHub `issue_comment` est le transport de preuve : auteur de l'issue = auteur du commentaire = `sender` = `github.actor`; `GET /users/{login}` corrobore l'ID et `GET /repos` / `GET /branches` revalident l'identité et le HEAD.
- Le module utilise l'admission persistée existante, le même `runtime_id`, la même `connection_ref`, la liaison GACR exacte à la même session, et le grant Q12 préexistant ; aucun nouveau First Touch.
- `F1 → 00_START_HERE.md` est désormais libérable **sans work item, claim, lease de travail ou attribution de tâche** quand l'acteur est un propriétaire GitHub vérifié (`Wealthtechinnovations` ou `Patricked-code`).
- Un lease de travail n'est pas une condition d'admission ; l'authenticité de la session GACR reste indispensable. En revanche, les contrôles de claim, collision et lease pour un travail dispatché ne sont pas modifiés.
- Le nouveau grant enregistre les rôles utilisables `CODE_AGENT`, `SUPERVISOR`, `INTAKER`, `REVIEWER`, `PLANNER_AGENT` et permet de changer de rôle opérationnel après l'admission selon les autorisations applicables.
- `create_branch`, `create_file`, `update_file`, `create_pull_request`, lecture, revue, supervision et intake sont enregistrées comme **éligibilité aux opérations GitHub natives** ; la permission effective reste celle de GitHub au moment de chaque opération. Il n'y a aucune élévation de privilège, exemption de CI ou contournement des protections de branche.
- Le reçu d'admission propriétaire n'est pas un faux `gscc-function-exposure-receipt/v1`. La route F1 historique et l'exposition des fonctions gouvernées des non-propriétaires restent inchangées.
- Le workflow de la porte A doit générer, publier et conserver comme artifact le véritable reçu et son access grant, puis émettre le beacon `F1_RELEASED` sur le GACR existant, **sans créer une offre de travail**.
- Ce correctif est un **candidat en LAB**. Il ne remplace pas le HEAD `main` tant que la PR #328 n'est pas examinée et fusionnée.


## Rattachement durable de cette interaction / reprise multi-conversation (preuve du 16 octobre 2026)

**CONTINUITY_ID** : `GRT-CONT-20261016-F1QUEUE-001`  
**Registre existant** : `.governance/control-plane-state/gacr-continuities.json` (projection GACR, LAB)  
**Point d'ancrage durable GitHub** : [issue #327 — commentaire #6225267797](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/327#issuecomment-6225267797)  
**Lot** : `RTE-014` ; **PR** : #328.

- La présente interaction ChatGPT a fait l'objet d'une **demande explicite du propriétaire** de l'associer à cette continuité. La preuve vérifiable de cet événement est un commentaire GitHub daté et attribué à l'acteur GitHub authentifié `Wealthtechinnovations`.
- L'ID résout un **contexte de continuité durable** pouvant référencer plusieurs travaux, lots, conversations et futures sessions. Les nouvelles interactions doivent enregistrer un autre commentaire/preuve append-only sans effacer l'attachement historique.
- **Aucun identifiant privé de la conversation ni de session ChatGPT n'est exposé**. `provider_conversation_ref`, `provider_session_id` et `gacr_session_id` de CETTE interaction restent `null / UNAVAILABLE`. Il s'agit d'un rattachement de contexte traçable, PAS d'une présence active GACR.
- Le registre GACR ne doit contenir dans `participants` que de véritables sessions existantes dans `gacr-sessions.json`, admises via `gacr_continuity_coordination.py declare` (identité, collision, exact HEAD). **Aucun faux participant, aucun claim et aucun lease** n'est créé.
- Pour reprendre : retrouver l'ID → consulter issue #327 et son dernier checkpoint/commentaire → relire `docs/labs/GRT-CONT-20261016-F1QUEUE-001.md` et `.governance/control-plane-state/gacr-continuities.json` sur la branche LAB tant que non fusionnée → inspecter PR #328/CI → revalider HEAD de `main` et du LAB → continuer au dernier point non terminé.
- Les futurs GACR `session_id` authentiques peuvent être liés à cette même continuité en tant que participants multiples, sans changer son ID.
- Un appel de cet ID **ne confère aucune permission** ; authentification GitHub, protections de branche et droits applicables restent exigés. L'identifiant seul est une clé de récupération, pas une preuve de session ou un jeton d'autorité.
- Dernier arrêt : `OWNER_F1_LAB_TESTED_NOT_MERGED`, HEAD LAB observé `ac4f769eb2acc30c90cc81b3693fd0e299747cf9` au moment du commentaire ; une preuve historique ne fige pas le HEAD futur.
