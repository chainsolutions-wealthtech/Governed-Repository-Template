# Contre-expertise documentaire — modèle historique de continuité GACR après F1

**Périmètre** : observation et comparaison, aucune exécution ni claim.  
**Continuité examinée** : `GRT-CONT-20261007-2117-GMC01-DSP258-01` (ancienne, indépendante).  
**Continuité LAB qui conserve cette étude** : `GRT-CONT-20261017-F1RECOVERY-001`.  
**Mémoire du LAB** : `GRT-LABMEM-20261017-F1RECOVERY-001`.  
**HEAD de main observé lors de l'analyse** : `b41a413ba0b24278515f9cc71a718db5b32840ab`.  
**État** : `SOURCE_BACKED_HISTORICAL_MODEL_STUDY`, ni approbation de nouveau pool ni autorisation GACR.

## 1. L'origine réelle de l'ID et ses liens d'autorité

La première ancre historique retrouvée pour ce pilote est l'issue de coordination [#259](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/259). L'ID `GRT-CONT-20261007-2117-GMC01-DSP258-01` apparaît comme **clé de continuité documentaire et de projection**. Le code actuel `scripts/gacr_continuity_coordination.py::continuity_item` accepte un `continuity_id` fourni et vérifie qu'il conserve son `repository` et son `coordination_issue` : il n'est pas démontré que les segments de cet ID soient produits par un algorithme canonique automatique. Il ne faut donc pas les reconstituer comme une clé d'autorité à partir d'un simple libellé.

Origine : [#257](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/257) = arrivée GSCC d'ATLAS → [#258](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/258) = demande d'orchestration/pools → [#259](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/259) = ancrage de continuité et coordination → [#260](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/260) = arrivée du successeur FORGE → [#264](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/264) = arrivée de SENTINEL → [#262](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/262) / [PR #263](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/263) = projection de coordination lisible machine → [#266 annexe v1.4](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/266#issuecomment-6069881459) = index conceptuel du pool fondateur.

Lien au programme canonique historique : `CP-CHECKPOINT-20261007-023` → `CP-HANDOFF-20261007-023` ; `GOVERNANCE_MODEL_CATALOGUE` → `GMC-A/GMC-G01` → `GMC-01`. Ces objets étaient des références de programme/autorités distinctes de cette continuité de coordination.

La PR #263 est **effectivement MERGED**, le 9 octobre 2026 à 18:13:51Z, avec commit de fusion `47de383870a22e64b52b0e172451557acddae7c7`. Cette fusion est propre à **l'ancienne** continuité, en aucun cas à la PR #332 du LAB présent.

## 2. Rattachement technique après F1 : chaînes distinctes

```text
ARRIVÉE #257 / #260 / #264
  → GSCC First Touch et identité GSCC-ID
  → GSE / SessionTwin et qualification
  → GACR / session_id et corrélation
  → Q12 → F1 → RECEIPT → RELEASED_TO_NORMAL_GOVERNANCE
  → 00_START_HERE.md / réobservation HEAD et autorité
  → intention de continuité identifiée
  → issue de coordination #259 + continuity_id
  → projection GACR continuities + agent logique / sessions / provider_contexts
  → déclaration active de scope (SEULEMENT si réellement faite)
  → bus (SEULEMENT si participant actif et cibles valides)
  → profil disponibilité / rôle / capacité et preuve F1
  → tâches canoniques READY + dépendances + collisions
  → proposition d'offre GACR R7/R8
  → acceptation → claim → exact HEAD → exécution autorisée
  → preuves → checkpoint → handoff ou reprise
```

**F1_RELEASED n'est ni `POOL_MEMBERSHIP_ACTIVE`, ni `CLAIM_GRANTED`, ni `MUTATION_AUTHORIZED`.** Dans [#260 commentaire de release](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/260#issuecomment-6045929500), FORGE possède un `session_id`, un reçu `GSCC-EXPOSURE-ce90...`, un HEAD de release, puis passe à `00_START_HERE.md`. Un [commentaire de coordination distinct](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/260#issuecomment-6045993132) le lie ensuite à #259.

## 3. Entités enregistrées aujourd'hui (snapshot main)

Le registre [`gacr-continuities.json`](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/b41a413ba0b24278515f9cc71a718db5b32840ab/.governance/control-plane-state/gacr-continuities.json) contient l'ancienne continuité, `coordination_issue=259`, `projection_only=true`, `grants_task_authority=false`, `grants_claim=false`, `grants_mutation_authority=false`.

| Alias | `logical_agent_id` | Sessions historiques | Note |
| --- | --- | --- | --- |
| ATLAS | `GSCC-ID-16b1f46fbab319f97b7ec43f` | `session-1bb68ac942a69a77dfbb8d24` | arrivée #257, analyse GMC/architecture |
| FORGE | `GSCC-ID-b484944fc30fe55b88948f9f` | `session-ba6f8db786eb9a8aa11865f2`, `session-fb2dc33154cdcc8b282c8c02` | arrivée #260, LAB #262/#263 |
| SENTINEL | `GSCC-ID-21df6eb30456b56be12144bf` | `session-3320926e66a52ff8f4396ed2` | arrivée #264, supervision/revue |

Les objets `provider_contexts[]` portent de plus des IDs GACR-PC, connexion/client et provenance. Les références natives de conversation ChatGPT y sont nulles quand elles ne sont pas exposées.

**Observation critique dans cette entrée de registre :** `logical_agents[] = 3`, mais `participants[] = []`, `events[] = []`, `last_sequence = 0`. Donc **trois agents historiquement liés dans la projection** ≠ trois participants ayant actuellement un scope actif déclaré ≠ trois agents disposant d'une capacité live vérifiée.

Les claims globaux sur le snapshot main sont à `revision 0` avec `claims=[]` ; cela n'attribue aucun claim à cette continuité.

## 4. Comment fonctionne le modèle technique

[Source `gacr_continuity_coordination.py`](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/b41a413ba0b24278515f9cc71a718db5b32840ab/scripts/gacr_continuity_coordination.py) :
- `continuity_item` lie l'ID au dépôt et à son issue de coordination, sans octroyer d'autorité.
- `declare_scope_docs` vérifie session GACR canonique, exact HEAD, révision de coordination `GACR-CS-...`, mode de travail, collision et claims étrangers ; enregistre éventuellement un **participant de scope** `GACR-P-...`.
- `participant_id` est dérivé de `SHA-256(continuity_id|session_id|scope_id)` (12 caractères hex), `coordination_state_ref` d'une révision GACR-CS.
- `yield_scope_docs` écrit un handoff et l'état `YIELDED`, sans transférer les claims.
- [Source `gacr_continuity_bus.py`](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/b41a413ba0b24278515f9cc71a718db5b32840ab/scripts/gacr_continuity_bus.py) exige un participant actif avant d'émettre un événement du bus ; il crée des IDs d'événement et de dispatch distincts.

[Source `gacr_capacity_dispatch.py`](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/b41a413ba0b24278515f9cc71a718db5b32840ab/scripts/gacr_capacity_dispatch.py) :
- `session_capacity_projection` observe F1, rôle déclaré/attribué, capacités, disponibilité, liveness, claims et conflits ; l'absence de F1, rôle ou disponibilité requis bloque la session.
- `agent_pool_projection()` agrège les sessions d'un même agent logique pour éviter de multiplier artificiellement sa capacité.
- `parallel_work_dispatch_plan` confronte le pool dérivé aux tâches canoniques réellement READY, dépendances, collision domains, scopes et offres existantes. Offre ≠ claim ≠ permission GitHub.
- Dans notre LAB, l'audit précédent D03/D04 reste pertinent : preuve F1 interprétée localement par projection et revalidation des offres à l'acceptation doivent encore être qualifiées indépendamment.

## 5. Trois sens de « pool » déjà décrits par le propriétaire

La [mémoire du pool fondateur, annexe v1.4](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/266#issuecomment-6069881459), spécification documentaire non exécutable, distingue :
1. **Pool de coordination** : continuité durable `continuity_id`, équipe, scopes, handoffs, événements et preuves.
2. **Pool de lot/travail** : `work_package_id` et tâches canoniques, dépendances, critères d'acceptation ; vue dérivée et non nouveau moteur.
3. **Pool de disponibilité/dispatch** : capacité effective sessions/logical agents + état et contraintes du travail, calculée par GACR.

Un hypothétique futur `pool_id` dédié doit **être lié** à ces références et ne jamais renommer automatiquement `continuity_id`. Le pilote est décrit sous le nom humain **« pool fondateur »**, mais **aucun pool_id canonique autonome** n'a été créé par cette seule annexe.

## 6. Limite historique à traiter comme observation, pas correction automatique

Le [diagnostic ATLAS #257 du 9 octobre](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/257#issuecomment-6088626054) signalait un décalage : l'ancien forensic ATLAS utilisait comme checkpoint `RELEASED_TO_NORMAL_GOVERNANCE`, tandis que le mécanisme ultérieur d'attachement par alias exigeait le `continuity_id` exact dans la preuve forensic. Le code actuel [`resolve_alias_attach_proof`](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/b41a413ba0b24278515f9cc71a718db5b32840ab/scripts/gscc_session_runtime.py) vérifie encore le rapprochement au `continuity_id`.

**Verdict précis** : condition de code confirmée aujourd'hui ; incident documenté historiquement ; état actuel des forensics ATLAS et un nouvel E2E non vérifiés au cours de cette exploration. Ne pas déclarer qu'ATLAS est définitivement bloqué, ni que le problème est corrigé.

## 7. Ce que nous devons retenir pour le LAB actuel

Le futur pool minimal du LAB `GRT-CONT-20261017-F1RECOVERY-001` sera **distinct** de cette ancienne continuité et relié à une référence GACR canonique réellement attestée. La future carte doit contenir, avec type, source et chronologie :

```text
owner_requirement_id / origin_event_id
→ lab_development_continuity_id
→ lab_memory_root_id
→ lab_pool_id (non créé)
→ GACR continuity / coordination reference (non résolue)
→ agent logical ID + role + evidence
→ session ID + GSCC/GSE/F1 receipt + HEAD
→ scope participant ID (seulement s'il a été déclaré)
→ GACR bus events / provider_contexts / liveness
→ work package ID / task ID / dependencies
→ offers / claims / results / validations
→ checkpoints / handoffs / PR / real merge commit
```

**Distinction obligatoire des statuts** : historique projeté, participant déclaré, capacité effective, autorité d'exécution, résultats de tests et preuve live. Ne pas créer de participants, claims ou lien GACR fictifs pour remplir le graphe.

**Actions effectuées pour cette étude** : lecture directe GitHub uniquement ; aucune création de session/agent/pool, aucun dispatch, claim, fusion, déploiement ou changement du code GACR.