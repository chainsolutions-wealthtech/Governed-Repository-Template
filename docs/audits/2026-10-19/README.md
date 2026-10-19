# Audit unique et progressif — mémoire historique GRT
> **19 octobre 2026 · DOCUMENTATION_ONLY · BROUILLON / ENQUÊTE EN COURS**
>
> Dépôt : `chainsolutions-wealthtech/Governed-Repository-Template` ; baseline de lecture `main@a931e76553b64d295fbc9caef098b29e1690316b`.
> **Une seule branche / PR pour cet audit ; aucune nouvelle issue ; aucune modification du runtime, des gates ou des registres canoniques ; aucun merge sans validation propriétaire.** Le présent rapport ne crée pas d'agent, de session, de claim, de continuité, d'autorité ni de permis. GitHub direct uniquement, sans Codex.

## Mandat et procédure
Le propriétaire veut comprendre et dater toutes les décisions, instructions, identités, sessions, continuités, traces, PR/issues et collisions, puis stabiliser la gouvernance au lieu d'accumuler des interventions isolées. Ne pas confondre `Patricked-code/MCP` avec ce dépôt GRT. Porte utilisée : `00_DIRECT_OWNER_ENTRY.md`, déclaration `JE VIENS CODER`, acteur authentifié `Wealthtechinnovations` (ID 94637590, permissions `admin,pull,push` consultées), trace [PR #326, commentaire #6274674525](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/326#issuecomment-6274674525). **Pas de session GSCC/GSE/GACR/F1 fabriquée par cette porte B.**

## Couverture déjà vérifiée au 19 octobre 2026
- Git tree `main` : **475 entrées, 445 blobs, 11 400 944 octets, `truncated=false`**. Le catalogue exhaustif des chemins/blob SHA est à annexer, mais ne signifie pas lecture sémantique exhaustive des fichiers.
- Historique GitHub paginé : **247 PR**, dont **230 fusionnées**, **9 fermées sans fusion**, **8 ouvertes** ; **91 issues distinctes des PR**, dont **79 ouvertes**, **12 fermées**. Première création dans l'inventaire : 25 septembre 2026. Index exhaustif des métadonnées et dates à annexer.
- GitHub Actions : 16 définitions YAML dans `.github/workflows`; un listing Actions a retourné **17 956 runs** cumulés au moment de sa lecture. Ce total ne décrit pas leur utilité ou leur conclusion. Le workflow GACR contient un cron **toutes les 10 minutes** ; auto-bootstrap un cron **toutes les 5 minutes**, chacun avec capacité de commit selon ses conditions.
- `.governance/control-plane-state/current.json` : `source_state_revision=48`, `template_version=2.8.27`, `active_program=GOVERNANCE_MODEL_CATALOGUE`, `active_work_package=GMC-A / GMC-G01`, action unique `GMC_01_SEPARATE_GOVERNANCE_MODEL_FROM_APPLICATION_STRATEGIES`.
- `.governance/control-plane-state/tasks.json` : révision 59, 133 entrées : 64 `DONE`, 1 `SUPERSEDED`, 62 `PLANNED`, 5 `FUTURE`, 1 `IN_PROGRESS` (`GMC-01`).
- `CP-CHECKPOINT-20261007-023` et `CP-HANDOFF-20261007-023` restent des ancres **du programme source**. Cela n'efface pas les travaux distincts GACR, LAB et F1 réalisés jusqu'au 19 octobre.
- Le pointeur `last_verified_main_head` interne est `63e67d76970dc4b7e8b9864567a07e7445e84bfc`, **distinct** du HEAD GitHub `a931e76553b64d295fbc9caef098b29e1690316b`. La sémantique et la fraîcheur de ce champ restent à clarifier ; interdiction de l'écraser sur simple écart.
- `gacr-continuities.json` : révision 171, **5 continuités** de coordination enregistrées en **projection dérivée** (aucun permis de mutation). `gacr-correlations.json` : révision 659, **680** corrélations. `gacr-dispatches.json` : révision 219, **29** dispatches. `gacr-takeovers.json` : révision 26, **123** `READY_FOR_RECONCILIATION` et **0** reprise acceptée, dernier scan enregistré **2026-10-16T19:00:37Z**. `gacr-forensics.json` : révision 220, **124** entrées. `gacr-claims.json` : révision 0, **0** claim.
- `.governance/sessions/sessions.json` et `.governance/agent-relay/continuities.json` sont vides (revision 0) : ils ne prouvent **pas** l'absence de sessions GACR ou de continuités projetées ailleurs.
- Les fichiers volumineux `gacr-sessions.json` (~1,3 Mo) et `gacr-beacons.json` (~2,65 Mo) n'ont pas délivré leur contenu par la lecture textuelle de ce connecteur ; toute cardinalité de leurs objets est **UNAVAILABLE** à ce stade.

## Chronologie historique de premier niveau — dates UTC
| Date | Événement et provenance |
|---|---|
| 2026-09-25 | Début des issues/PR accessibles dans le relevé GitHub paginé. |
| 2026-09-26 | Auto-gouvernance, mémoire source et architecture GRT (voir `docs/control-plane/SUIVI.md`). |
| 2026-10-02 | Travaux GACR/GSCC : présence, relais, agent sessions et intégrations (voir `GACR_PROGRAM.md`). |
| 2026-10-07 | CASE 1 clôturé, GMC-A libéré, checkpoint/handoff `-023`. |
| 2026-10-07 | Continuité GMC-G01 #259, agents ATLAS/FORGE/SENTINEL. |
| 2026-10-08 | Mémoire documentaire des identités/providers/heartbeat #266. |
| 2026-10-09 | Cartographie d'IDs #267, GENESIS documentaire #280, registre de construction #278. |
| 2026-10-10 | Continuité de coordination de l'agent témoin / pool GENESIS #282. |
| 2026-10-12 | Programme Global #288 et sa continuité GACR. |
| 2026-10-13 | CHAINFLOW expérimental, ancre #301 et demande #302. |
| 2026-10-14 | Sessions/arrivées d'agents CHAINFLOW (issues #303 à #310). |
| 2026-10-16 | NOVA, alias/rôle via PR #323/#324, issue #321 ; Porte B via PR #326 ; F1QUEUE #327 et PR #328. |
| 2026-10-17 | F1 propriétaire Porte A via PR #333 ; accès volontaire à LAB après F1 via PR #335 ; CHAINFLOW PR #334 ouverte. |
| 2026-10-19 | PR #332 (récupération F1) et PR #330 (LABENTRY) fusionnées ; issue #338 ouvre une réflexion sur `START_HERE` neutre et le catalogue d'agents. |

## Architecture : ne pas confondre les autorités
**Porte A** : `00_GSCC_ENTRY.md → GSCC → GSE → GACR → Q12 → owner F1 → RELEASE → 00_START_HERE.md`.
**Porte B** : `00_DIRECT_OWNER_ENTRY.md → login authentifié → permission native → HEAD exact → opération GitHub`, sans session GACR obligatoire ni nouvelle Task Queue.
**LAB ENTRY** : `00_LAB_ENTRY.md` et workflow `lab-entry.yml`, entrée de création de LAB qui ne vaut pas troisième porte d'admission.
**Control Plane** : `docs/control-plane/*` et projections source `.governance/control-plane-state/{current,tasks,checkpoint,handoff}.json`.
**GACR** : agent logique ≠ session ≠ provider/context ≠ participant ≠ continuité ≠ offre ≠ claim ≠ droit d'écriture. Le bus et les projections ne donnent pas d'autorisation par eux-mêmes.
**Expérimentation** : CHAINFLOW, GENESIS, LABENTRY et F1RECOVERY restent distincts du programme source `GMC-01`. Le travail sur MCP externe est hors périmètre.

## Identités à indexer et reconstruire avec provenance
- `ATLAS` → `GSCC-ID-16b1f46fbab319f97b7ec43f` → `session-1bb68ac942a69a77dfbb8d24`.
- `SENTINEL` → `GSCC-ID-21df6eb30456b56be12144bf` → `session-3320926e66a52ff8f4396ed2`.
- `FORGE` → `GSCC-ID-b484944fc30fe55b88948f9f` → `session-ba6f8db786eb9a8aa11865f2` et `session-fb2dc33154cdcc8b282c8c02`.
- `NOVA` → `GSCC-ID-68711b0e5e84a6a651d0e2a3` → `session-2f8d5707f376e4b45ab7797b` ; rôle `CODE_AGENT` propriétaire. **Aucune conversation nouvelle ne peut usurper cette session sans corrélation propre.**
- Racine documentaire `GRT-GEN-DOC-I280` et `GRT-AT-DOC-I281` ≠ identités GACR.
- Continuité LAB `GRT-CONT-20261017-F1RECOVERY-001` (#331) et LABENTRY `GRT-CONT-20261017-LABENTRY-001` (#329) ≠ preuve d'enregistrement comme continuité GACR.
- Deux participations CHAINFLOW `GACR-P-a307888885f4` et `GACR-P-623a6f43a1e0` possèdent le **même** couple superviseur/session ; scope ou doublon à qualifier, pas de suppression.

## Principaux indices de risques (tous `TO_VERIFY`)
1. Décalage de snapshot du Control Plane avec le HEAD courant.
2. Les 123 propositions de reprise GACR sans acceptation ne signifient pas que 123 sessions sont récupérables maintenant.
3. Multiplicité des projections vides vs non vides : déterminer source, cache, compatibilité et fraîcheur.
4. Boucles GitHub Actions (cron 5/10 minutes, triggers, écritures bot, concurrents) et coût/perte de lisibilité.
5. PR et issues historiques nombreuses et non classées : aucun nettoyage destructif ni fermeture en masse.
6. Issue #338 (19 octobre) : distinguer personne/mandant, agent réutilisable, catalogue, groupe/pool, session, LAB, programme et jonction `START_HERE`, sans créer de registre parallèle.
7. Vérifier le chainage de preuves `GSCC→GSE→GACR→F1→session→continuité→claim→mutation` ; ne pas déduire une capacité de l'alias.
8. Vérifier réellement les grosses bases GACR, les tests et l'ensemble du code avant toute qualification « audit fonctionnel complet ».

## Travaux restant dans **ce même dossier**, pas de nouvelles PR/issues
- Annexe intégrale et datée des 247 PR / 91 issues (métadonnées natives).
- Inventaire SHA des 445 fichiers au HEAD de référence.
- Annuaire de toutes les continuités issues des projections consultables, identités, sessions, participations et namespaces.
- Index horodaté des commentaires de gouvernance / instructions propriétaire et leur statut (proposé, adopté, exécuté, supersédé).
- Lecture sémantique progressive du code et des tests, sans prétendre qu'une liste de fichiers vaut une revue de chaque ligne.
- Vérification de la CI et des derniers runs, sans affirmer un PASS non observé.
- Plan de stabilisation soumis au propriétaire **avant** toute modification fonctionnelle.

**Règles :** enrichir uniquement cette branche, via commits datés et gardés par HEAD ; aucune fusion automatique, aucun nouveau LAB, aucune permission inventée, aucune réécriture de mémoire. Cette page n'est pas une nouvelle autorité canonique.
