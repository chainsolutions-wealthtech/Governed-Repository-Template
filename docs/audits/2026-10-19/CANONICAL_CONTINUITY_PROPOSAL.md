# Proposition de continuité canonique durable — audit et stabilisation GRT

> **Proposition documentaire, non activée** · 2026-10-19 · PR #339 · baseline de la PR `8700c4c9c6b905fca3e22de2c842b79082ae287d` avant ce document.
> Ce document ne crée **ni** identité GACR `GSCC-ID`, **ni** session `session-*`, **ni** claim, **ni** lease, **ni** permission d'écriture. Il n'est pas un second registre de gouvernance.

## 1. Référence de reprise stable proposée

- **Alias humain** : `GRT-AUDIT-STABILISATION`.
- **Identifiant documentaire de continuité proposé** : `GRT-CONT-AUDIT-STABILISATION-20261019-001`.
- **Repository strict** : `chainsolutions-wealthtech/Governed-Repository-Template`.
- **Fil de travail initial** : [PR #339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339).
- **Dossier d'archives versionné** : `docs/audits/2026-10-19/`.
- **Date de début du mandat** : 2026-10-19 ; rétrohistorique septembre–octobre 2026 ; tous les nouveaux événements seront datés UTC et reliés à une preuve GitHub.
- **Statut** : `PROPOSED_DOCUMENTARY_ONLY`, jusqu'à adoption explicite par le propriétaire et intégration dans la source de vérité GACR **si le schéma le permet**.

Le préfixe `GRT-CONT` est ici une **suggestion de libellé de reprise**. Son usage ne doit pas être interprété comme une entrée existante du registre `gacr-continuities.json`. Vérifier collisions et convention de namespace avant adoption ; une adoption devra soit l'enregistrer dans le système existant avec ses preuves, soit conserver un alias documentaire explicitement distinct, sans registre parallèle.

## 2. Contrat de résolution depuis toute nouvelle conversation

**Phrase de reprise proposée :**
> Reprends `GRT-AUDIT-STABILISATION` / `GRT-CONT-AUDIT-STABILISATION-20261019-001` sur `chainsolutions-wealthtech/Governed-Repository-Template`. Lis d'abord les portes et autorités en vigueur, puis le dossier `docs/audits/2026-10-19/` et la PR #339, son historique, ses commits, commentaires et checks. Reconstitue le dernier checkpoint, la liste des décisions, les actions terminées, les actions en cours, les blocages et le prochain pas. Réobserve les HEAD GitHub et collisions. N'invente pas de session ni d'autorisation ; ne crée pas de nouvelle issue/PR. N'écris qu'après vérification des permissions natives, du mandat et des gates.

**Résolution attendue** :
1. Résoudre le dépôt **exact** ; authentifier l'acteur et ses permissions GitHub effectives.
2. Lire `00_DIRECT_OWNER_ENTRY.md` si Porte B explicitement choisie, sinon suivre la Porte A selon sa gouvernance ; lire `00_START_HERE.md`, les autorités `CURRENT_STATE`, checkpoint, handoff et tâches.
3. Résoudre l'alias dans un index stable de continuités **existant ou approuvé** ; refuser les collisions/ambiguïtés de nom et les pointeurs morts.
4. Lire le présent dossier et l'ensemble des **commits/commentaires/checks** de PR #339 ; après fermeture de la PR, utiliser le chemin versionné canonique adopté.
5. Produire un **état de reprise vérifiable** : identifiant, HEAD, sources, dernière décision adoptée, dernier checkpoint, tâches et propriétaires, travaux bloqués, autorisations encore valables, prochaine action et limites de preuve.
6. Toute action d'écriture exige un mandat et un scope, une permission native, les gates CI/F1 applicables, une garde anti-collision et un HEAD revalidé. Le simple identifiant de continuité n'autorise rien.

**Limite du mot « automatiquement » :** la résolution peut être automatisée **lorsqu'un client dispose du connecteur GitHub et du routeur adéquat**. Une conversation isolée, non connectée ou non authentifiée ne peut ni lire des données privées ni devenir automatiquement la même session runtime qu'une autre.

## 3. Mémoire append-only et chronologie à maintenir

Pour chaque intervention future dans cette PR puis son successeur canonique :
- `event_id` stable ; `occurred_at_utc` et `recorded_at_utc` (ne pas inventer la date d'un événement ancien).
- `actor_github` / `logical_agent_id` / `session_id` **uniquement si prouvés**, sinon `UNRESOLVED`.
- `owner_request` : texte ou lien natif ; `scope`, `expected_outcome`, `restrictions`.
- `authority_source`, `decision_status` : `PROPOSED|APPROVED|EXECUTED|BLOCKED|SUPERSEDED|REJECTED|UNRESOLVED`.
- `git_before`, `git_after`, `commit`, `pr`, `issue`, `comment`, `ci_run`, `evidence_urls`.
- `work_item`, `dependencies`, `collision_domain`, `tests`, `result`, `regressions`, `rollback`.
- `checkpoint` : travaux réalisés, points non résolus, prochaines étapes et références exactes.

Ne pas recopier des secrets, tokens, empreintes de connexion, contextes privés ni le contenu intégral de conversations non exportées. **GitHub contient les traces GitHub, pas toutes les conversations ChatGPT passées** ; une histoire complète exige que chaque nouveau mandat soit écrit avec consentement dans le dossier de continuité.

## 4. Deux gouvernances, aucune confusion

- **Gouvernance du dépôt** : permissions, règles de branche, CI, GSCC/GSE/GACR/Q12/F1/RELEASE, Control Plane source et règles anti-régression ; elle prime pour les mutations.
- **Gouvernance de continuité** : filiation documentaire des décisions, sessions, agents, tâches, événements et preuves. Elle ne supplante jamais les gates du dépôt.
- `Patricked-code/MCP` est **hors périmètre** et ne doit jamais être fusionné avec ce projet.

## 5. Critères d'acceptation avant d'affirmer « reprise automatique opérationnelle »

- Le propriétaire adopte le nom et l'identifiant après vérification des collisions.
- L'index/routeur existant reconnaît ce nom et résout **un seul** dossier canonique, sans créer d'identité runtime fictive.
- Test de reprise depuis deux nouvelles conversations ou clients autorisés, avec même résumé sourcé du dernier checkpoint.
- Test d'absence de connecteur/permission : échec explicite et sûr, sans simulation d'admission.
- Test de PR fusionnée/fermée : reprise toujours possible depuis le dossier canonique.
- Test d'un événement nouveau : append-only, provenance UTC, lien de preuve, et état de reprise actualisé.
- Aucun changement de workflow, de gate, de registre source ou de `main` sans mandat spécifique et revue.

**Conclusion :** le nom et le contrat de continuité sont proposés dans la PR unique #339. L'activation d'un mécanisme de reprise inter-conversations n'est **pas** encore démontrée.
