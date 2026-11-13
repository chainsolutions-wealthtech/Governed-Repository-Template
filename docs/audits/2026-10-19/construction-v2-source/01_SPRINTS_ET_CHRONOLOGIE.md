# Plan de sprints candidat — aucun calendrier, claim ou exécution

Un sprint candidat est une **enveloppe de planification** ; les groupes internes conservent leur ordre de dépendance. Un numéro plus élevé n’équivaut pas automatiquement à un gate réussi. P0 entrée est hors scope et inchangé.

| Ordre | Identifiant local | Objectif | Pièces couvertes | Critère de sortie candidat |
|---:|---|---|---|---|
| 0 | `SPR-DRAFT-00` | Préparation et contrat directeur | `DRAFT-GLOBAL-CONTRACT`, `DRAFT-REQ-TRACE` | ST01 approuvé, sprints proposés rattachés aux autorités existantes |
| 1 | `SPR-DRAFT-01` | Frontières et métamodèle | `GMC-G01`, `GMC-G02` | Résultats de G01 puis G02 validés; sinon sprint fractionné |
| 2 | `SPR-DRAFT-02` | Domaines, capacités et composants | `GMC-G03`, `GMC-G04`, `GMC-G05` | Registres de domaines/capacités/composants validés |
| 3 | `SPR-DRAFT-03` | Données et états | `GMC-G06`, `GMC-G07`, `GMC-G08` | Objets, états et transitions identifiés avec preuves |
| 4 | `SPR-DRAFT-04` | Contrôles, gates et preuves | `GMC-G09`, `GMC-G10`, `GMC-G11` | Contrats de sûreté/validation complets |
| 5 | `SPR-DRAFT-05` | Traçabilité d’implémentation et dépendances | `GMC-G12`, `GMC-G13`, `DRAFT-DELIVERY-REG` | Graphes de références et dépendances contrôlés |
| 6 | `SPR-DRAFT-06` | Comparaison et applicabilité | `GMC-G14`, `GMC-G15` | Comparaisons sémantiques vérifiables |
| 7 | `SPR-DRAFT-07` | Matérialisation et quatre cas | `GMC-G16`, `GMC-G17`, `GMC-G18` | Contrats de consommation réutilisables approuvés |
| 8 | `SPR-DRAFT-08` | Validation du modèle commun | `GMC-G19`, `ARCH-006`, `DRAFT-TRACE-E2E` | Gates globaux validés; pas de release automatique |
| 9 | `SPR-DRAFT-09` | Routeur deux étages et reprise | `RTE-001`, `RTE-002`, `RTE-003`, `RTE-004`, `RTE-005`, `RTE-006`, `RTE-007`, `RTE-008`, `RTE-009`, `RTE-010`, `RTE-011`, `RTE-012` | Activation soumise aux gates et preuve RTE-012 |
| 10 | `SPR-DRAFT-10` | Capsule réutilisable | `CAP-001`, `CAP-002`, `CAP-003`, `CAP-004`, `CAP-005`, `CAP-006`, `CAP-007`, `CAP-008`, `CAP-009`, `CAP-010`, `CAP-011`, `CAP-012` | Release CAP-012 seulement après preuves et prérequis |
| 11 | `SPR-DRAFT-11` | Trois cas encore à industrialiser | `ADOPT_EXISTING_REPOSITORY`, `MAP_EXISTING_PROJECT`, `LAB_EVOLUTION` | Chaque cas avec ses propres preuves E2E; sans dépendance temporelle arbitraire |
| 12 | `SPR-DRAFT-12` | Spécifications produit et API | `SAA-001`, `SAA-002`, `SAA-003`, `SAA-004`, `SAA-005`, `SAA-006` | Contrats produit/API/services et isolation testés |
| 13 | `SPR-DRAFT-13` | Cockpit et opérations gouvernées | `SAA-007`, `SAA-008`, `SAA-009`, `SAA-010` | Cockpit complet et actions gouvernées testables |
| 14 | `SPR-DRAFT-14` | Packaging et staging | `SAA-011`, `SAA-012` | Déploiement et E2E staging validés |
| 15 | `SPR-DRAFT-15` | Production, recette et livraison | `SAA-013`, `SAA-014`, `SAA-015` | Production/recovery/release uniquement si autorisés et attestés |

## Allocation réelle future
- Capacité et vélocité : non observées.
- Dates / durée : non définies.
- Agents/sessions : attribués ultérieurement par le système déjà gouverné.
- Sans preuve READY, ces enveloppes restent des candidats, jamais des dispatchs.
- Autorisation P0 et de l’action réelle exigée au moment de toute opération.
