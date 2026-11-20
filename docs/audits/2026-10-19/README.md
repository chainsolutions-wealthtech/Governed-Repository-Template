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
- **Mise à jour du 19 octobre 2026 :** les gros registres ont ensuite été récupérés intégralement **par leurs Git blob SHA** et audités sans modification. `gacr-sessions.json` = **125 sessions** (123 `STALLED`, 1 `CLOSED`, 1 `ACTIVE` au snapshot), dont **34 identités `GSCC-ID-*` distinctes** ; `gacr-beacons.json` = **680 beacons** (dont 534 `AUTO_ATTACH`, 27 `UNBOUND_ACTIVITY`, 16 `F1_RELEASED`). Inventaires exhaustifs de ces **deux blobs figés**, sans données provider privées : [GACR_SESSIONS_FULL_INDEX.md](GACR_SESSIONS_FULL_INDEX.md) et [GACR_BEACONS_FULL_INDEX.md](GACR_BEACONS_FULL_INDEX.md). La disponibilité actuelle des sessions et la validité individuelle des grants ne sont PAS démontrées par ces nombres.

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


## CHECKPOINT DOCUMENTAIRE — TOUS LES COMMENTAIRES HISTORIQUES (19 octobre 2026, UTC)

**Index intégral des commentaires des issues au snapshot : 1 413 / 1 413.** Relevé complet en six annexes, ordonné par date GitHub au sein de chaque partie, y compris la deuxième page des trois issues dépassant cent commentaires (#4, #49, #115). Chaque entrée conserve le numéro d'issue, l'identifiant natif du commentaire, la date de création et de modification retournée, l'auteur GitHub, son URL et la première ligne informative. **Toutes les 91 issues historiques sont couvertes ; aucune page de commentaire n'a échoué.**

- [Partie 1/6 — issues #1 à #189](ALL_ISSUE_COMMENTS_01.md) : **457 commentaires**.
- [Partie 2/6 — issues #192 à #258](ALL_ISSUE_COMMENTS_02.md) : **141 commentaires**.
- [Partie 3/6 — issues #259 à #280](ALL_ISSUE_COMMENTS_03.md) : **276 commentaires**.
- [Partie 4/6 — issues #281 à #296](ALL_ISSUE_COMMENTS_04.md) : **215 commentaires**.
- [Partie 5/6 — issues #297 à #312](ALL_ISSUE_COMMENTS_05.md) : **240 commentaires**.
- [Partie 6/6 — issues #313 à #338](ALL_ISSUE_COMMENTS_06.md) : **84 commentaires**.

Le fichier [ISSUE_COMMENTS.md](ISSUE_COMMENTS.md) reste l'index **prioritaire détaillé** de 16 issues centrales, désormais complété par l'archive exhaustive à six parties. Le nombre de commentaires ne signifie pas autant de décisions. Les commentaires de PR, reviews, corps de PR, GitHub Actions, codes et identités non exposées ne sont pas compris dans ce décompte et restent à examiner.

**Résultat :** le propriétaire peut désormais retrouver chacun des **247 titres de PR**, **91 titres d'issues**, **445 chemins de fichiers** et **1 413 références natives des commentaires d'issues**, avec les dates effectivement renvoyées par GitHub. Cela constitue un **index de reconstruction historique**, non un verdict de vérification de chaque instruction/code sur le fond.


## Nouvelle pièce de preuve — sessions et beacons intégraux (19 octobre 2026)

Les limites du premier accès texte à ces deux grands fichiers ont été résolues **dans cette même PR**, via `fetch_blob` sur leurs hashes immuables : [125 sessions](GACR_SESSIONS_FULL_INDEX.md) et [680 beacons](GACR_BEACONS_FULL_INDEX.md). Le registre source atteste 123 `STALLED`, 1 `CLOSED`, 1 `ACTIVE` ; les beacons 534 `AUTO_ATTACH`, 16 `F1_RELEASED` portant sur 16 sessions distinctes, et 27 `UNBOUND_ACTIVITY` sans session attachée. Ces données restent **historiques au HEAD de référence**, non des permissions ou des notifications live. Le champ `agent_identity` contient aussi des logins GitHub/bots : il est faux d'assimiler les 125 sessions à 125 identités canoniques d'agents.

[Matrice vérifiée des points d'entrée, fonctions et 16 workflows](ARCHITECTURE_CODE_CONTROL_MATRIX.md). **Governance CI SUCCESS** sur le commit `3357c64e6b3172c10da59590ac9566cc05ab365f`, [run 39308543868](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/actions/runs/39308543868). Les autres commits ultérieurs nécessitent leur propre contrôle CI.

## Pont documentaire HUB ↔ Construction GRT V2 (20 octobre 2026)

Le HUB expérimental pointe désormais vers le **système de construction V2 proposé** à travers [le contrat de liaison](HUB_CONSTRUCTION_BRIDGE_V01.md), [l'index de 378 pièces candidates](HUB_CONSTRUCTION_CROSSWALK_V01.csv), [le manifeste de provenance](HUB_CONSTRUCTION_MANIFEST_V01.json) et [les contrôles d'acceptation](HUB_CONSTRUCTION_ACCEPTANCE_V01.md). Ce rattachement renvoie au [Programme Global existant #288](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/288) et au Control Plane source, **sans nouveau moteur ni registre d'autorité**.

**Limites :** `hub_root_id=null` (proposition non adoptée) ; ST01 non validé par cet ajout ; les 378 fiches détaillées résident encore dans une archive candidate `LOCAL_ONLY`, distincte de l'index CSV désormais versionné dans la PR ; aucun statut `READY` ou droit d'exécution implicite.

## Addendum 20 octobre 2026 — fichiers détaillés V2 effectivement publiés

L'état historique `LOCAL_ONLY` pour les **378 fiches individuelles** a été remplacé par une publication du **corpus complet des 412 fichiers originaux** dans [`construction-v2-source/`](construction-v2-source/). Voir [état 412/412](construction-v2-source/README_IMPORT_STATUS.md) et [412 empreintes individuelles](HUB_CONSTRUCTION_FILE_HASHES_V01.json). Le ZIP original n'est pas déposé tel quel : ce sont ses fichiers extraits, conservés octet pour octet. L'index [HUB_CONSTRUCTION_CROSSWALK_V01.csv](HUB_CONSTRUCTION_CROSSWALK_V01.csv) reste une vue de correspondance et non un registre exécutable.

Cette correction de statut **ne valide ni ST01 #288, ni l'identité HUB runtime, ni une tâche READY, ni un agent/claim/permission**. Les mentions `LOCAL_ONLY` plus haut décrivent le snapshot de préparation précédent, non l'état du corpus extrait au terme de cet import.
