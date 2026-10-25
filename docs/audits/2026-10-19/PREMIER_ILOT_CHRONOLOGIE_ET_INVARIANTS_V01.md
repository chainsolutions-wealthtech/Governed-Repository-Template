# Premier îlot GACR — chronologie commentée et invariants V0.1

2026-10-20 — `GRT-CONT-AUDIT-STABILISATION-20261019-001` — PR #339 — **DOCUMENTARY_ONLY**.

## Corpus
Issue #259 : **81 commentaires consultés dans l'ordre retourné par GitHub** ; sélection de commentaires substantiels relue intégralement. L'issue est une trace historique, non une autorité suffisante pour créer une session ou un claim. Les preuves CI/commits sont rapportées telles que documentées, sans nouveau replay E2E indépendant.

## Chronologie et preuves
| Phase | Événements / preuves GitHub | Enseignement |
| --- | --- | --- |
| Fondation | #257 arrivée ATLAS ; #258 préparation/orchestration ; #259 ancrage commun, révisions 2–4 (#6045382867, #6045430413, #6045450679) | Continuité distincte du programme/tâche |
| Reprise | #260, successeur `session-ba6f8db786eb9a8aa11865f2`, prédécesseur expiré `session-1bb68ac942a69a77dfbb8d24` (#6045944909) | Ne pas rejouer, ne pas transférer de claim inexistant |
| Coordination | Contrat de bus #6045991427 ; retour prédécesseur #6046535915 ; séparation LAB/lecture seule #6046581041 ; heartbeat par session #6046642624 | Single-writer, périmètres disjoints, HEAD exact |
| Communication | Contact différé, challenge, ACK de reprise et relance (#6047094302, #6047541057, #6047661978) | Message durable != réveil effectif du navigateur |
| Supervision | Troisième agent superviseur #6048383479 ; invariants d'appartenance persistante #6048644397 | Membership durable != liveness ni permission |
| Identité | Modèle `logical_agent → sessions[] → provider_contexts[]` (#6049187165) | N:N avec provenance forte, pas d'identité provider inventée |
| LAB | PR #263, revues/CI/correctifs et prévention de collisions (#6049776716, #6065278813, #6065571141) | LAB séparé et revu, pas de promotion tacite |
| Décision et intégration | Autorisation propriétaire sur SHA exact #6086643832 ; attestation post-fusion #6086682361, merge commit `47de383870a22e64b52b0e172451557acddae7c7` | La preuve de test, la permission et l'intégration sont distinctes |
| Suites | Archive #266, architecture future #269, alertes de régression ATLAS #6088629191, récupération #286, synthèse historique #6206336167 | La mémoire se poursuit après la fusion ; les régressions restent visibles |

## Invariants retenus pour l'étude de notre programme
1. Continuité documentaire et appartenance persistante ; liveness et heartbeat **par session**, jamais partagés.
2. Un agent logique peut avoir plusieurs sessions et plusieurs contextes provider ; aucune corrélation sans preuve.
3. `RECONSTRUCTION != ADMISSION != SESSION_RESUME != CLAIM != MUTATION_AUTHORITY`.
4. La projection `gacr-continuities.json` ne donne aucun grant.
5. Le LAB nécessite périmètre, branche, propriétaire de collision, contrôle exact-HEAD, CI et décision de promotion.
6. La mémoire doit conserver événements, provenance, états précédents, décisions, preuves, risques et prochaine action ; les archives documentaires ne valent pas autorité runtime.
7. Les mécanismes GACR, bus, tâches et dispatch existants doivent être réutilisés ; pas de doublons.

## Périmètre restant
- Recouper #257/#258/#262/#263/#266/#269/#286 et les commits/CI, avant de prétendre à une reconstruction exhaustive.
- Cartographier les registres réels et leur hiérarchie, puis proposer un schéma de journal canonique et un LAB borné.
- Le constat de fusion PR #263 est documenté dans #259 ; il ne démontre pas à lui seul que toutes les fonctions d'échange interagents sont opérationnelles aujourd'hui.
