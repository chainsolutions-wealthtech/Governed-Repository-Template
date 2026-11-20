# PROGRAMME ISOLÉ GRT — REGISTRE 1 : IDENTIFICATION

Statut : **projection documentaire versionnée, sans autorité d'admission**. Continuité parent : `GRT-CONT-AUDIT-STABILISATION-20261019-001`. PR unique #339 ; branche `audit/20261019-histoire-identites-stabilisation`. Provenance : observation GitHub directe du 20/10/2026, PR #300–339 ; snapshot non exhaustif des discussions et diffs.

## Rattachement et identités (ne pas fusionner)
| Objet | Identifiant / source | Statut | Limite |
|---|---|---|---|
| Acteur GitHub propriétaire | `Wealthtechinnovations`, permissions admin/push/pull observées | VERIFIED à l'entrée | pas une identité GSCC |
| Porte d'entrée | `00_DIRECT_OWNER_ENTRY.md` | VERIFIED | ne crée aucune session GACR |
| Continuité documentaire | `GRT-CONT-AUDIT-STABILISATION-20261019-001` | DOCUMENTED, PR #339 | distincte du HUB racine |
| Mission audit | `MISSION-AUDIT-001` | IN_PROGRESS | pas un claim |
| Mission continuité | `MISSION-CONTINUITE-002` | DESIGN_ONLY | pas un routeur opérationnel |
| Session de cette conversation | `null` | NOT_ATTESTED | ID provider indisponible, pas d'admission fictive |
| Agent GACR de cette conversation | `null` | NOT_ATTESTED | rôle CODE_AGENT déclaré != identité |
| HUB racine | `null` | PENDING_OWNER_ID | ne pas confondre avec la continuité audit |

## Chaîne historique identité — PR 300 à 339
- #316 : correctif import harvester F1 ; #317 : alignement namespace dispatch GACR 12/16 hex ; #318 : renouvellement Q12 sur même arrivée ; #319–320 : revue HOLD et réconciliation de plan, sans grant fictif.
- #322 : candidat CODE_AGENT Q9 et alias inconnu ; #323 : alias propriétaire NOVA pour session existante ; #324 : rôle CODE_AGENT de NOVA restreint à CHAINFLOW GR-000302.
- #326 : activation de Porte B indépendante de Porte A ; #328 : continuité F1QUEUE / RTE-014 ; #330 : mécanisme LABENTRY et pool documentaire ; #332 : recovery F1 isolée ; #333 : approbation propriétaire F1 ; #335 : choix post-F1 sans claim automatique.
- #334 : CHAINFLOW PREP-003, PR toujours ouverte, aucun grant implicite ; #339 : inventaire historique et contrats de reprise, PR ouverte DRAFT.
- Numéros #300–315, #321, #325, #327, #329, #331, #336–338 : ne pas présumer PR ; plusieurs sont issues ou numéros non confirmés. Les métadonnées PR ont été interrogées ; analyse complète des commentaires/diffs/reviews **à faire**.

## Sources de vérité réutilisées
`00_GSCC_ENTRY.md`, `00_DIRECT_OWNER_ENTRY.md`, `00_START_HERE.md`, `scripts/repository_entry_router.py`, `.governance/control-plane-state/gacr-continuities.json`, `docs/GACR_AGENT_CONTINUITY_RELAY.md`, `scripts/gacr_agent_reconstruction.py`, `CONTINUITIES_AND_IDENTITIES.md`, `GACR_SESSIONS_FULL_INDEX.md`. Aucun nouveau registre d'autorité GACR, identité ou bus.

## Procédure de reprise agent
1. Résoudre dépôt et PR #339 live, relire Porte B et vérifier acteur/permissions/HEAD.
2. Lire ce registre et le registre gouvernance compagnon, puis les sources primaires ; ne pas transformer une projection en permission.
3. Chercher correspondances d'alias/ID et sessions dans autorités live ; collisions et absence de preuve = refus, `null`.
4. Reconstituer l'historique par lots, consigner preuves natives, niveaux INVENTORIED/READ/ANALYZED/CROSS_REFERENCED/VERIFIED.
5. Consigner les nouvelles instructions/checkpoints dans PR #339 ; toute activation runtime requiert mandat et périmètre distincts.

## Prochain travail non exécuté
Lire les discussions, patches, reviews et commits de chaque PR réelle de l'intervalle ; recouper avec issues #300–339 et source GACR ; vérifier liveness actuelle et construire table de filiation détaillée. Aucun résultat exhaustif revendiqué.
