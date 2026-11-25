# Référentiel proposé de 20 livrables structurants

> Les `DEL-DRAFT-*` ne sont **pas des identités canoniques**. Les références `GMA-*` et les IDs du backlog existants demeurent la source actuelle ; ce tableau propose une vue de recette produit, jamais une seconde autorité.

| Livrable candidat | Résultat | Travaux sources | Porte d'acceptation proposée |
|---|---|---|---|
| `DEL-DRAFT-01` | Cadre du Programme Global | `DRAFT-GLOBAL-CONTRACT`, `CP-ARCH-001` | `ST01_OWNER_APPROVAL` |
| `DEL-DRAFT-02` | Capsule d’entrée réutilisée | `IDN-006`, `IDN-011`, `IDN-012` | `P0_EXISTING_PROOF` |
| `DEL-DRAFT-03` | Graphe universel de construction | `GMC-G02`, `GMC-G06`, `GMC-G13`, `DRAFT-DELIVERY-REG`, `DRAFT-TRACE-E2E` | `GMC_G13_GRAPH_REVIEW` |
| `DEL-DRAFT-04` | Registres de modèle normatifs | `GMC-G03`, `GMC-G04`, `GMC-G05`, `GMC-G06`, `GMC-G07`, `GMC-G08` | `GMC_G08_OUTPUTS_VALIDATED` |
| `DEL-DRAFT-05` | Contrôles, autorité et preuve | `GMC-G09`, `GMC-G10`, `GMC-G11` | `GMC_G11_OUTPUTS_VALIDATED` |
| `DEL-DRAFT-06` | Matrice modèles → implémentations | `GMC-G12`, `GMC-G13` | `GMC_G13_OUTPUTS_VALIDATED` |
| `DEL-DRAFT-07` | Comparateur de gouvernance | `GMC-G14`, `GMC-G15` | `GMC_G15_OUTPUTS_VALIDATED` |
| `DEL-DRAFT-08` | Matérialisation sans seconde vérité | `GMC-G16`, `ARCH-004`, `ARCH-006` | `GMC_G16_CONTRACT_VALIDATED` |
| `DEL-DRAFT-09` | Consommation du modèle par le Control Plane | `GMC-G17`, `ARCH-005` | `GMC_G17_CONTRACT_VALIDATED` |
| `DEL-DRAFT-10` | Quatre cas liés au modèle | `GMC-G18`, `GMC-G19`, `ADOPT_EXISTING_REPOSITORY`, `MAP_EXISTING_PROJECT`, `LAB_EVOLUTION` | `GMC_G19_CROSS_CASE_ACCEPTANCE` |
| `DEL-DRAFT-11` | Routeur des intentions | `RTE-001`, `RTE-004`, `RTE-012` | `RTE_012_E2E_PROOF` |
| `DEL-DRAFT-12` | Mémoire et reprise des interventions | `ARCH-004`, `RTE-008`, `RTE-012`, `DRAFT-STATUS-EVENTS` | `EVENT_RECONSTRUCTION_PASS` |
| `DEL-DRAFT-13` | Distribution et claims gouvernés | `GMC-G13`, `ARCH-005`, `DRAFT-LOAD-CONTRACT` | `DISPATCH_CLAIMS_REGRESSION` |
| `DEL-DRAFT-14` | Capsule publique installable | `CAP-001`, `CAP-006`, `CAP-012` | `CAP_012_LIVE_PROOF` |
| `DEL-DRAFT-15` | API gouvernée v1 | `ARCH-008`, `SAA-002`, `SAA-006` | `OPENAPI_SECURITY_GATE` |
| `DEL-DRAFT-16` | Projection PostgreSQL | `ARCH-009`, `SAA-005` | `PARITY_AND_MIGRATION_PASS` |
| `DEL-DRAFT-17` | Cockpit d’administration | `ARCH-010`, `SAA-007`, `SAA-008`, `SAA-009` | `COCKPIT_E2E_GATE` |
| `DEL-DRAFT-18` | Sécurité et multitenancy | `SAA-001`, `SAA-004`, `SAA-010` | `SECURITY_ISOLATION_PASS` |
| `DEL-DRAFT-19` | Chaîne de livraison reproductible | `SAA-011`, `SAA-012`, `SAA-015` | `STAGING_E2E_AND_RECOVERY` |
| `DEL-DRAFT-20` | Production et release | `SAA-013`, `SAA-014`, `SAA-015` | `PRODUCTION_OWNER_AND_SAFETY_GATES` |

## Différence entre résultats, preuves et livraisons

Un `GMA-*` est un **artefact de connaissance** du modèle GMC ; un `DEL-DRAFT-*` est une **regroupement conceptuel de recette produit**. Rien ne permet d'affirmer qu'un livrable est terminé tant que son contrat, les preuves de ses composants et l'autorité de validation ne sont pas rapprochés et acceptés. Les preuves et les statuts ne peuvent pas être inventés à partir de la description du lot.
