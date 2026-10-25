# HUB canonique — missions, séparation P0/GACR et gouvernance, apports ST01

**2026-10-20 — Mandat propriétaire consigné sur PR #339 — DOCUMENTATION UNIQUEMENT.**
**Continuité proposée** : `GRT-CONT-AUDIT-STABILISATION-20261019-001` / `GRT-AUDIT-STABILISATION`. Cette étiquette reste candidate tant que le résolveur et l'autorité de continuité ne l'ont pas reconnue.

## Instruction du propriétaire — à conserver sans interprétation d'autorité

Créer progressivement un **grand HUB de travail**, initialement vide comme espace d'expérimentation mais informé par l'ensemble de `main`. Il est un miroir de connaissance / LAB isolé, **pas** un second `main` ni une nouvelle source de vérité. Chaque instruction, réponse opérationnelle, artefact, action, échec, décision, preuve, checkpoint et handoff doit être rattaché à une mission nommée et à une provenance. Le HUB contient plusieurs missions et sous-espaces, avec un annuaire interrogeable. La reconstitution et la comparaison avec `main` précèdent toute modification éventuelle de `main`, qui nécessite une autorisation distincte.

**Deux domaines séparés** :
- **Pôle P0 / GSCC → GSE → GACR → Q12 → F1 → RELEASE** : identité et sessions gouvernées, permissions et registres existants ; respecter son processus intégral.
- **Pôle gouvernance / construction / HUB-LAB** : compréhension et indexation de `main`, dossiers, programmes, lots, code expérimental et propositions ; registre propre de traçabilité **dérivé**, non concurrent du contrôle-plane.
- **Pont** : corrélation attestée entre identifiants des deux domaines, sans transformation d'un identifiant documentaire en admission ou permission GACR, sans grande modification des autorités.

La **Porte B** reste explicitement sélectionnée via `00_DIRECT_OWNER_ENTRY.md` pour les interventions directes du propriétaire. La Porte B n'est pas une admission P0 et ne fabrique pas une session GACR. `00_LAB_ENTRY.md` est un workflow de LAB, non une porte d'admission supplémentaire.

## Annuaire minimal du HUB (candidats, non enregistrés en runtime)

| Alias d'appel | Type | Objet | État |
| --- | --- | --- | --- |
| `GRT-AUDIT-STABILISATION` | HUB / continuité | Racine du travail propriétaire | PROPOSED_DOCUMENTARY_ONLY |
| `MISSION-AUDIT-HISTORIQUE` | Mission | Examiner chaque PR, issue, commentaire, commit et diff depuis l'origine ; sourcer les relations et écarts | IN_PROGRESS_PARTIAL, exhaustivité non démontrée |
| `MISSION-IDENTITES-P0-GACR` | Mission | Inventaire et tests des autorités GSCC/GSE/GACR, sans contournement | PROPOSED |
| `MISSION-GOUVERNANCE-MAIN` | Mission | Reconstitution des architectures et continuités du dépôt `main` | PROPOSED |
| `MISSION-ROUTEUR-REPRISE` | Mission | Résolveur alias, rattachement de sessions réellement attestées, routeur de fonctions nommées et tests inter-conversations | PROPOSED / NOT_PROVEN |
| `MISSION-GRAND-LAB` | Mission | Environnement isolé d'analyse, comparaison et code pas à pas | PROPOSED / NOT_CREATED |
| `MISSION-RECONSTRUCTION-CODE` | Mission | Étudier ultérieurement les écarts et proposer des reconstructions, sans mutation implicite de `main` | FUTURE |

Les alias ci-dessus sont des **clés d'annuaire proposées**. Ils ne créent ni agent, ni session, ni LAB, ni tâche source, ni droit.

## Schéma de filiation et de traçabilité à développer

`hub_id → mission_id → instruction_id → work_item_ref → [agent_ref, session_ref, lab_ref] → artifact_ref → event_ref → evidence_ref → checkpoint_ref`.

Un événement doit conserver `timestamp_utc`, `actor_verified_or_unresolved`, `source_url`, `before_head`, `after_head`, `status`, `decision_authority`, `result`, `next_action`. L'annuaire et les vues sont **des projections indexées** des registres et objets GitHub, jamais une seconde vérité.

## Sources nouvelles fournies par le propriétaire (16 octobre 2026)

Quatre fichiers locaux ont été fournis dans la conversation du 20 octobre 2026. Ils sont **sources de travail fournies**, et **ne sont pas automatiquement publiés sur GitHub** :

1. `audit_completude_tracabilite_GRT_2026-10-16(1).md` : audit lecture seule sur `main@638fcc51c77f2454990f239b8b8cca78bac8075b`. 35 RQ, 19 lots GMC, 174 tâches atomiques PLANNED, 85 artefacts PLANNED, 188 dépendances internes, 132 work items transversaux. Verdict : graphe universel et contrat ST01 approuvé **non démontrés**. Voir notamment l'issue [#288](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/288).
2. `SYNTHESE_LIVRAISON(1).md` : synthèse de dossier directeur V2 ; 378 fiches (354 préservées, 24 candidates), 20 livrables proposés, 16 enveloppes de sprint candidates, 1 012 relations typées, 12 étapes. Tests de cohérence documentaire locale PASS ; **ni CI repo ni publication ni ST01 approuvé**.
3. `GRT_Dossier_Directeur_Construction_V2_2026-10-16(20261020-003106).zip` : archive locale de 412 entrées ZIP, contenant le dossier directeur, `README_DOSSIER_DIRECTEUR.md`, `10_AVANT_PROJET_CONTRAT_DIRECTEUR_ST01.md`, registres et fiches de lots. Le contrat ST01 est `CANDIDAT_NON_APPROUVÉ`.
4. `GRT_Publication_Candidate_ST01_2026-10-16(1).zip` : archive locale de 419 entrées ZIP, avec `MANIFESTE_IMPORT.json`, `GRT_Proposition_ST01_V2.patch`, `verifier_publication.py`, `HANDOFF_PUBLICATION.md` et dossier candidat sous `branch_files/docs/control-plane/proposals/programme-global-st01-construction-2026-10-16-v2/`. Le handoff déclare `NOT_PUBLISHED` au moment de sa rédaction, sans mutation GitHub. La réconciliation historique indiquait `main@d5b441403dbc44229d891667dc162ae97bdc572b` après quatre commits depuis `638fcc...`; ces HEAD ne sont **pas** l'état GitHub live actuel.

**Important** : la présence de ces archives et de leurs noms dans cet index ne signifie pas que les 831 entrées ZIP ont été importées ou analysées individuellement. Leurs contrôles locaux et leur état de publication ne doivent pas être présentés comme attestations GitHub live. Toute publication ultérieure nécessite inventaire des collisions et validation du mandat, sans écraser les travaux déjà présents.

## Prochaine opération documentaire et technique distincte

1. Définir l'identité définitive du HUB et vérifier la collision avec les namespaces canoniques existants.
2. Indexer les missions et les instructions, en commençant par l'audit historique ; créer un état de couverture explicite `INVENTORIED / READ / UNDERSTOOD / CROSS_LINKED / VERIFIED` pour chaque PR, issue, commentaire, commit et diff.
3. Étudier les composants existants de résolveur et de GACR ; implémenter et tester en isolation le routage des fonctions nommées et le rattachement réellement attesté, sans fausse admission.
4. Définir le grand LAB comme environnement isolé **après instruction explicite**, sans déplacement de la tâche canonique courante.
5. Conserver PR #339 comme unique fil de consolidation de cet audit ; pas de nouvelle issue/PR ou fusion automatique.

**Aucune permission, identité runtime, session, LAB ou mutation de `main` n'est créée par ce document.**
