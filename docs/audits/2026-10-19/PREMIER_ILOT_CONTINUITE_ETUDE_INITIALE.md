# Étape F1 — Premier îlot de continuité GACR : étude initiale

Date : 2026-10-20. Statut : **PARTIAL_EVIDENCE / DOCUMENTARY_ONLY**. Programme : `GRT-CONT-AUDIT-STABILISATION-20261019-001`. PR #339.

## Source et périmètre
- Premier îlot observé : `GRT-CONT-20261007-2117-GMC01-DSP258-01` ; coordination [issue #259](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/259), 81 commentaires retournés par GitHub lors de cette lecture.
- Autorités examinées : `docs/GACR_AGENT_CONTINUITY_RELAY.md`, `docs/MULTI_AGENT_COORDINATION.md`, `.governance/control-plane-state/gacr-continuities.json` sur `main`.
- Limite : les premiers commentaires de #259 ont été examinés, **pas encore l'ensemble des 81 commentaires, ni tous les commits, tests et workflows**.

## Faits directement attestés
1. Commentaire #6045382867 : révision 2 de la continuité, HEAD historique `d1487ca7f770c2ce0a99233f3c3e36c02b37fbd9`, séparation entre travail GMC-G01 et planification #258 ; état et prochaine action conservés.
2. Commentaires #6045430413 et #6045450679 : raffinements successifs des blocages et de l'architecture ; interdiction de créer une deuxième autorité de stockage ou de remplacer les sélecteurs existants.
3. Commentaire #6045944909 : prédécesseur `session-1bb68ac942a69a77dfbb8d24` expiré, successeur `session-ba6f8db786eb9a8aa11865f2` via arrivée #260 ; reprise sans rejouer T01–T08, sans transfert de claim puisque aucun claim mutable n'était actif.
4. Commentaire #6045991427 : contrat de coordination v1 ; lecture obligatoire de #259 et du HEAD live, périmètres disjoints pour les lecteurs parallèles, protection single-writer et protocole de retour du prédécesseur.
5. `gacr-continuities.json` est une projection dérivée : `projection_only=true`, sans pouvoir de claim, tâche ou mutation. Elle ne doit pas être confondue avec une autorisation.

## Hypothèses de conception à étudier, non décisions runtime
- Distinguer : identité de continuité, identité agent, session, issue de coordination, tâche, claim, checkpoint et autorité.
- Prévoir un registre des décisions append-only, un état courant reconstructible et un protocole de reprise idempotent.
- Reprendre les mécanismes GACR existants plutôt que créer un second bus ou moteur de dispatch.
- Tester la récupération après interruption, le retour du prédécesseur, le changement de HEAD, les collisions et l'absence d'identifiant provider.

## Questions ouvertes
- Chronologie complète des 81 commentaires et rattachement des agents ATLAS/SENTINEL/FORGE.
- Historique exact de la naissance de l'ID, des décisions propriétaires et des transitions de registre.
- Preuves effectives des workflows, des tests E2E, du bus et de la récupération multiagents.
- Inventaire complet des registres GRT et de leur hiérarchie d'autorité.

## Suite
F1-A : chronologie exhaustive et preuves de #259. F1-B : cartographie des registres/autorités. F1-C : contrat mémoire canonique et proposition LAB, sous décision propriétaire séparée. Aucun runtime ou `main` modifié.
