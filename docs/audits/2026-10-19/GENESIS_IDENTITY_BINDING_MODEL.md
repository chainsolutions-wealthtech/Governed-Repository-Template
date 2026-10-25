# Décision propriétaire — modèle Genesis et chaîne de rattachement

Date de consignation : 2026-10-19. Portée : espace expérimental du dépôt `chainsolutions-wealthtech/Governed-Repository-Template`. Statut : **OWNER_INTENT_RECORDED / IMPLEMENTATION_PENDING**. PR documentaire unique : [#339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339).

## Identité racine souhaitée

- Identité Genesis / espace racine : `GRT-CONT-AUDIT-STABILISATION-20261019-001`.
- Alias : `GRT-AUDIT-STABILISATION`.
- Ce nom désigne désormais le **hub général expérimental**, pas exclusivement la mission d'audit.
- Les missions (audit, reconstruction de code, LAB, comparaisons avec main, etc.) deviennent des **enfants identifiés** de cette racine.
- La PR #339 est une preuve et un espace de travail de la mission audit, **pas** une identité Genesis ni un titre d'accès.
- L'adoption du nom dans le registre canonique réel, son unicité et sa résolution automatique restent à implémenter et attester ; cette documentation n'est pas un enregistrement GACR effectif.

## Modèle de rattachement

`GENESIS_ROOT → MISSION → WORK_ITEM / LAB / PR / ARTIFACT`

En parallèle, toute intervention suit :

`CONVERSATION / CLIENT (si identifiant exposé) → AUTHENTICATED_ACTOR → ENTRY_ROUTE (A ou B) → AGENT_IDENTITY (si existante et prouvée) → CANONICAL_SESSION (si admission réelle) → BINDING_EVENT → GENESIS_ROOT → MISSION / CONTEXT`.

Un acteur peut contribuer via la Porte B **sans** être un agent GACR. Il faut distinguer `owner_actor_id`, `logical_agent_id`, `provider_session_id`, `canonical_session_id`, `continuity_id`, `mission_id`, `lab_id`, `pr_number`. Aucune assimilation implicite.

## Deux registres d'autorité, un pont de corrélation

1. **Parcours GSCC/GSE/GACR** : processus d'admission et registres existants, sans raccourci ni changement implicite.
2. **Espace Genesis / missions gouvernées** : index des demandes propriétaire, missions, analyses, code et événements ; sans duplication des autorités GACR.
3. **Pont de corrélation** : références croisées attestées, provenance, horodatage UTC, statut, et preuve des deux côtés. Ne confère aucun droit et ne crée pas de claim/session fictifs.

## Registres logiques à résoudre par le routeur

`roots`, `missions`, `agents`, `sessions`, `actors`, `entries`, `bindings`, `labs`, `tasks`, `events`, `communications`, `decisions`, `artifacts`, `audit`, `checkpoints`, `functions`.

Les noms désignent des **vues/index logiques** à raccorder aux mécanismes existants, non des nouveaux registres runtime autorisés à écrire.

## Critères de preuve

- Reprise par identifiant Genesis depuis un nouveau client autorisé.
- Vérification de l'acteur et des permissions natives, puis de la porte explicitement sélectionnée.
- Résolution unique des identités existantes ; création de session seulement par le mécanisme réellement autorisé.
- Événement de binding horodaté et vérifiable, y compris refus/absence d'identifiant client.
- Navigation Genesis → mission audit → PR #339 → preuves → dernier checkpoint.
- Appel par nom d'une fonction existante seulement si disponible, enregistrée et autorisée.
- Test de refus sans authentification et sans collision, aucun changement du control plane main.

## Limite importante

Aucune conversation ChatGPT n'est automatiquement équivalente à une session GACR. Sans identifiant de conversation exposé et sans preuve d'admission, le routeur ne doit pas fabriquer de numéro de session ou attester un rattachement inexistant.
