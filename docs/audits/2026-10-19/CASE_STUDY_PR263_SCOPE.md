# Cas historique vérifié : PR #263 — autorisation du squelette vs portée de la fusion

> **Nature :** `VERIFIED_GITHUB_HISTORICAL_EVENT + DOCUMENTED_SCOPE_AMBIGUITY`, audit du **19 octobre 2026**, fondé sur la PR GitHub, son diff, les commentaires natifs #259 et les mémoires documentaires #278/#286.
>
> Ce document **ne prononce pas** une illégitimité ou une régression fonctionnelle non prouvée. Il restitue les faits du Git diff, l'autorisation textuelle, et un écart de langage/périmètre déjà soulevé par le propriétaire. **Aucun revert/force-push/fermeture d'issue.**

## 1. Chaîne de preuves et chronologie exacte UTC

| Date UTC | Événement GitHub / source | Portée ou qualification |
|---|---|---|
| **2026-10-07T20:47:51Z** | [PR #263](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/263) créée | LAB GACR pour continuité, coordination multi-agents, alias et Bus ; non juste le squelette de reconstruction |
| **2026-10-09T17:30:03Z** | [#259 commentaire 6085934242](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/259#issuecomment-6085934242) | Gate : CI et revues techniquement vertes, mais **`MERGE_AUTHORITY=NOT_OBSERVED`** à ce checkpoint |
| **2026-10-09T18:13:40Z** | [#259 commentaire 6086643832](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/259#issuecomment-6086643832) | **`OWNER CANONICAL ADOPTION AUTHORIZATION — agent reconstruction skeleton`** ; mandat de terminer/adopter le squelette, associé explicitement à `PR=263`, `EXPECTED_HEAD_SHA=a2a4e0ec00ea179bfc7e0568212e40a2b391b158`, `MERGE_METHOD=merge` |
| **2026-10-09T18:13:51Z** | [PR #263 fusionnée](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/263) | 11 secondes après le commentaire ; GitHub confirme fusion par `Wealthtechinnovations`, commit `47de383870a22e64b52b0e172451557acddae7c7` |
| **2026-10-09T18:16:10Z** | [#259 commentaire 6086682361](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/259#issuecomment-6086682361) | Attestation : `merge.tree` identique au `PR-head.tree`, CI sur tree testé, squelette source `main` reconstituable, pas de contenu changé par le mécanisme de fusion |
| **2026-10-09T21:10:52Z** | [Issue #278](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/278) créée | Registre mémoire et reconstruction historique ; section **E/F** signale l'écart `SKELETON_SCOPE != WHOLE_LAB_SCOPE` et l'intention antérieure de greffe sélective |
| **2026-10-11T18:35:15Z** | [Issue #286](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/286) créée | Snapshot historique documentaire `GRT-RECOVERY-SNAPSHOT-20261009-PREMERGE-263`, liens aux deux arbres Git immuables |

**Conversion horaire France :** 18:13:40Z = **20:13:40 CEST** le 9 octobre 2026 et 18:13:51Z = **20:13:51 CEST**, fuseau Europe/Paris. Les heures ci-dessus sont celles retournées par GitHub, pas des déductions de conversations privées.

## 2. Ce que le diff GitHub atteste

- PR #263 : **40 fichiers changés**, **8 266 lignes ajoutées**, **101 lignes supprimées** (statistiques de la PR consultée le 19 octobre 2026).
- Le code fusionné contient des changements sur deux workflows, les fichiers d'entrée `00_GSCC_ENTRY.md`, `00_START_HERE.md`, des schémas JSON et des fichiers de contrôle GACR.
- Parmi les modules livrés figuraient `scripts/gacr_agent_reconstruction.py` et ses tests, **mais aussi** `scripts/gacr_continuity_bus.py`, `scripts/gacr_continuity_coordination.py`, les adaptations d'auto-attach, de capacity dispatch, de host issue ingress, des bridges et leurs tests. Ce sont des fonctionnalités connexes (mais distinctes du seul script de reconstruction).
- La PR déclare que les gros blobs d'autorité GACR `sessions/claims/dispatches/takeovers/forensics/beacons` n'ont **pas** été modifiés par la PR ; le diff GitHub examiné confirme qu'aucun de ces fichiers n'est dans les 40 fichiers modifiés.
- Le merge commit `47de383870a22e64b52b0e172451557acddae7c7` et le HEAD autorisé `a2a4e0ec00ea179bfc7e0568212e40a2b391b158` sont attestés par la PR, les commentaires et le snapshot #286.

## 3. Précision sur l'ambiguïté de périmètre

L'**instruction textuelle** du commentaire #259/6086643832 énumère un « read-only reconstruction skeleton » et des surfaces spécifiques. Le **contrat de fusion** dans ce même commentaire vise pourtant le **SHA complet de la PR #263**. La fusion a donc été effectuée sur l'objet Git désigné exactement, et non sur un sous-ensemble de fichiers.

La mémoire documentaire #278 relève explicitement que le souhait historique du propriétaire était de conserver Pool 1 dans un LAB et d'en faire une **greffe sélective** ; elle indique que l'aval textuel à un bloc ne doit pas être automatiquement étendu à toute la branche LAB. Ce désaccord apparent concerne **la sémantique de l'approbation** et les critères de sélection du code ; l'exactitude du SHA et le résultat CI ne suffisent pas à eux seuls à trancher si le périmètre fonctionnel correspondait au souhait.

Il n'est **pas** établi :
- qu'une identité GACR ou un agent aurait obtenu indûment un permis de mutation du seul fait de cette PR ;
- que les changements non-squelette sont intrinsèquement erronés ou provoquent un incident fonctionnel actuel ;
- que le propriétaire aurait sciemment ou non autorisé seulement quatre fichiers sans accepter le reste (l'intention privée ne se déduit pas de GitHub) ;
- qu'un retour en arrière intégral serait autorisé ou judicieux.

## 4. Snapshot et conservation, sans destruction

- **`main` avant fusion** : `c4584616d7caff334b907b5eb71cc52149107dae` ; arbre `57dca1406d4ff597ceba1ebfa2eadbd82f70851e`.
- **LAB pré-fusion** : `a2a4e0ec00ea179bfc7e0568212e40a2b391b158` ; arbre `b69eb651c33f028e532947d2a7ae122be58525f4`.
- **Merge PR #263** : `47de383870a22e64b52b0e172451557acddae7c7`, arbre identique à `b69eb651c33f028e532947d2a7ae122be58525f4`.
- **Ancre de récupération** : [#286](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/286), identifiant documentaire `GRT-RECOVERY-SNAPSHOT-20261009-PREMERGE-263`.
- **Chaîne de continuité** : `GRT-CONT-20261007-2117-GMC01-DSP258-01` → référence historique, **pas attribution de droits** → `GRT-GEN-DOC-I280` / `GRT-CONT-20261010-TEMOIN-POOLGEN-I282-01`.

Ces SHAs rendent les états consultables, sans transformer le snapshot documentaire en nouvelle autorité ni recréer une branche.

## 5. Le correctif conceptuel à examiner dans l'unique PR #339

**Pas de correction de code à cette étape.** Proposer, après inventaire, un contrat de promotion distinguant obligatoirement :
1. `LAB_CONTENT_SCOPE` : tout le contenu présent dans la branche candidate ;
2. `OWNER_AUTHORIZED_SCOPE` : fichiers/fonctions/tâches précisément autorisés, avec preuve GitHub native et SHA ;
3. `DIFF_PROMOTED_SCOPE` : ce que la PR présente réellement et ce que le merge intégrera ;
4. `GOVERNANCE_ALLOW_SCOPE` : mission/identité/approvals/fichiers protégés/claims/CI/contrôles de dépendances ;
5. `REVIEWED_TESTED_TREE` : SHA de l'arbre réellement testé ;
6. `MERGE_DECISION_SCOPE` : liste exacte des composants promus au-delà d'une simple allusion à un SHA ou à un bloc.

**Critère d'acceptation cible à soumettre au propriétaire :** si la demande porte sur **un sous-ensemble du LAB**, la promotion doit préparer/revoir **un diff de sous-ensemble**, sans fusionner toute la branche par défaut. Une référence explicite à un SHA de PR globale doit provoquer une clarification de périmètre lorsque la mission textuelle est plus restreinte. Aucun système parallèle de permission ou de registre ne doit être inventé.

## 6. Pourquoi ce cas peut éclairer la stabilisation générale

Il illustre un risque précis : avoir un historique Git complet, une CI verte, une approbation propriétaire réelle et **néanmoins** un écart possible entre la **portée fonctionnelle attendue** et le **diff effectif du merge**. La solution ne passe pas par la suppression des 40 fichiers historiques mais par une gestion prouvable et datée de la chaîne :
`intention → scope → identité/permission → diff exact → tests → approbation → merge → attestation → mémoire de continuation`.

C'est **un cas d'incident historique retrouvé**, pas la preuve qu'il s'agit du « petit problème » auquel le propriétaire fait référence dans son instruction du 19 octobre 2026. Cette correspondance restera **UNCONFIRMED_BY_OWNER** tant qu'elle n'est pas explicitement identifiée.
