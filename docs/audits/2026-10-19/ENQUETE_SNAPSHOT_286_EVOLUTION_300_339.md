# Enquête historique — snapshot #286 et évolution #300–#339

Statut : DOCUMENTARY / PARTIAL_EVIDENCE / NON_CANONICAL. Continuité : GRT-CONT-AUDIT-STABILISATION-20261019-001. Aucune mutation runtime ni permission créée.

## Découverte #286 : le pont historique

Issue https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/286 : snapshot documentaire GRT-RECOVERY-SNAPSHOT-20261009-PREMERGE-263, de la continuité #259 vers la racine Genesis #280 et la continuité #282, sans transfert d'identité ni autorité.

Preuve exacte : main avant PR #263 c4584616d7caff334b907b5eb71cc52149107dae, tree 57dca1406d4ff597ceba1ebfa2eadbd82f70851e ; LAB PR #263 a2a4e0ec00ea179bfc7e0568212e40a2b391b158, tree b69eb651c33f028e532947d2a7ae122be58525f4 ; merge 47de383870a22e64b52b0e172451557acddae7c7, même tree LAB. Date de merge indiquée dans #286 : 2026-10-09 18:13:51 UTC. Le snapshot exige restauration non destructive, comparaison des deltas, LAB Genesis indépendant, pas de revert/force-push de main, pas d'héritage automatique de claim/lease/autorité. Le futur LAB Genesis y est déclaré non créé à cette date.

## #300–#339 — cartographie vérifiée des sujets

- #300 : arrivée corrigée du candidat codeur global après #299 invalide.
- #301 : ancre CHAINFLOW, strictement expérimentale ; #302 : demande de LAB connecté au vrai dépôt ; #303–#315 : arrivées des agents et tentatives de continuité/supervision/récupération.
- PR #316–#320 : correctifs admission F1, namespace dispatch, renouvellement Q12 de la même arrivée, examen de HOLD, prévention de recréation d'un LAB déjà fusionné. Ces cinq PR sont MERGED lors de la vérification.
- #321 et PR #322–#324 : arrivée d'un CODE_AGENT, correction Q9, alias NOVA attribué par propriétaire, rôle borné à GR-000302 ; PR #322–#324 MERGED.
- PR #326 : deuxième porte authentifiée B indépendante, Porte A préservée ; MERGED.
- #327–#328 : file RTE-014, F1 propriétaire et continuité ; PR #328 MERGED.
- #329–#330 : LAB ENTRY automatisée, pool, queue ; PR #330 MERGED (ne prouve pas activation générale E2E).
- #331–#332 : récupération F1, HEAD concurrent, nom d'agent optionnel ; PR #332 MERGED.
- PR #333 : F1 propriétaire GitHub pour admission A, B indépendante ; MERGED.
- PR #334 : réconciliation PREP-003/HEAD CHAINFLOW, OPEN et NON MERGED au contrôle.
- PR #335 : liberté de choix branche/LAB après F1 sans claim dispatcher immédiat ; MERGED.
- #336/#337 : surfaces First Touch pour tests E2E ; #338 : question ouverte sur START_HERE neutre, catalogue agents, continuités LAB ; #339 : PR DRAFT d'audit historique, NON MERGED.

## Interprétation à confirmer avec le propriétaire et les preuves

La trajectoire suggère : retrouver le caractère vivant et expérimental de l'ancien LAB, puis corriger les impasses de F1, les admissions, l'identité et les autorisations pour permettre aux agents de rejoindre/créer une continuité ou un LAB sans être contraints à un claim de travail immédiat. Cette lecture est une synthèse, non une preuve que chaque mécanisme fonctionne de bout en bout.

## Vérifications manquantes

Lire commentaires des issues #301–#339, patchs des PR #316–#335 et leurs gates CI ; vérifier régressions, statut réel des fonctions post-F1, absence de collision et preuve E2E ; distinguer PR fusionnée, code intégré, déploiement, preuve live. Comparer #286 et les trois arbres exacts avec les hotfixes #275–#277 et le code actuel. Ne jamais assimiler issue, PR ou commentaire à une autorité GACR.
