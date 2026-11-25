# Mémoire historique — bus, LAB, fusion et reconstruction (#198–#300)

Statut : DOCUMENTARY_EVIDENCE_INDEX / PARTIAL_EVIDENCE / NON_CANONICAL / NO_EXECUTION_AUTHORITY.
Continuité documentaire : GRT-CONT-AUDIT-STABILISATION-20261019-001.
Ce document conserve les résultats d'enquête et les intentions interprétées ; il ne crée ni identité GACR, ni session, ni claim, ni bus, ni autorisation de mutation.

## Chronologie sourcée

- #198 : blocs de preuve First Touch, portes ; #199–#200 : séparation CAPTURE → GSCC → GSE → GACR → gouvernance ; #210 et #220 : instrumentation First Touch et entrée racine.
- #257 : arrivée ATLAS ; #258 : intake non canonique sur orchestration continue, pools et dispatch ; #259 : ancrage partagé de continuité, issue-bus humain. Contrat : https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/259#issuecomment-6045991427
- #259 commentaire 6046943410 : exigence propriétaire PUSH-FIRST, enveloppe d'événement, ACK/RESPONSE, routeurs, fallback ; primitives préexistantes de webhook et contrôle, mais absence de preuve de réveil natif des conversations ChatGPT. https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/259#issuecomment-6046943410
- #262 : mandat LAB ; PR #263 : projection de coordination, bus technique, identité logique → N sessions → N contextes. Fusion au commit 47de383870a22e64b52b0e172451557acddae7c7 après autorisation explicite au SHA a2a4e0ec00ea179bfc7e0568212e40a2b391b158. https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/259#issuecomment-6086682361
- #266 : dossier mémoire, distinction PROUVÉ_LIVE / CODÉ_LAB_TESTÉ / CONTRAT_MAIN / DÉCIDÉ_DOCUMENTÉ ; #269 : intake architecture d'agents nommés, blocs et bus, non autorité.
- #272–#273 : arrivée réelle FORGE révélant régressions de rattachement alias / validation GACR ; PR #275, #276, #277 : correctifs fusionnés pour alias, persistance et assertion ACK_TIMEOUT trop stricte. https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/273
- #278–#286 : registre de construction, témoin, GENESIS, LAB indépendant, reprise et snapshot documentaire pré-fusion PR #263 (#286). https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/286
- #287–#300 : Programme Global #288, agent LAB #289, superviseur GENESIS #291, architecte CONTRACT #292, demandes d'admission et de travail ; #299 entrée invalide/supplantée, #300 nouvelle entrée.

## Invariants à préserver

1. Ne pas confondre transport de contrôle préexistant, bus humain #259, bus machine LAB #263 et réveil natif de conversation (non prouvé).
2. Séparer identité logique, session, contexte fournisseur, continuité, claim et droits d'écriture ; heartbeat individuel et appartenance persistante.
3. Ne pas déduire le fonctionnement réel d'un succès CI ; tester les arrivées, rattachements, persistances et reprises E2E avant promotion.
4. Ne pas dupliquer registres GACR, dispatcher, queue, moteur de tâches ou source d'autorité.
5. Garder les LAB isolés et ancrés au code réel ; exiger arbitrage propriétaire, HEAD exact et preuves avant promotion dans main.

## Intention propriétaire — hypothèse interprétative, non décision historique établie

L'enchaînement suggère une volonté de retrouver une construction expérimentale autonome, avec mémoire durable, agents nommés, supervision, contrats, filiation et collaboration, sans perdre les garde-fous de gouvernance ni promouvoir prématurément des mécanismes insuffisamment éprouvés. Cette interprétation doit être confrontée aux commentaires, diffs, CI et décisions explicites.

## Enquête restant à conduire

- Remonter à la première PR introduisant B12/B29, gacr_bridge_notifier.py et transports antérieurs à #259.
- Comparer le tree LAB pré-fusion #263, le tree de merge et les hotfixes #275–#277 ; caractériser les régressions, leur cause et les tests manquants.
- Lire exhaustivement les commentaires et décisions #266–#300, notamment #278/#279/#280/#286 ; retrouver les limites exactes de Genesis/Pool/LAB et des grants F1.
- Construire matrice chronologique : date, source, décision, preuve, statut VERIFIED/CLAIMED/UNKNOWN, commit, impact, correction, autorité.

Aucune conclusion « il ne fallait pas fusionner » n'est établie comme fait technique : les régressions post-fusion sont attestées, mais la décision de promotion doit être évaluée selon son périmètre et les preuves disponibles.
